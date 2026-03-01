# STEP 1 — High-Level Architecture (Production Ready)

## 0) Ограничения анализа референса

Попытка автоматически проанализировать `https://stake3017.com/ru` из окружения завершилась `403 CONNECT tunnel failed`, поэтому разбор UI/UX и компонентной структуры выполнен на уровне целевой доменной модели staking/casino-платформы. Для точного pixel-level паритета на STEP 11 потребуется HTML/CSS snapshot или доступ к сайту из CI/CD среды.

## 1) Цели архитектуры

- Высокая нагрузка: >50k concurrent users (горизонтальное масштабирование stateless-слоёв).
- ACID-safe кошелёк и расчёты выплат.
- Idempotent API и replay-safe обработка событий.
- Restart-safe игровые раунды (Redis + durable DB + recovery workers).
- Provably Fair механика во всех играх (Crash, Dice, Mines, Plinko).
- Изолированные production-ready модули игр.

## 2) Технологический стек

### Backend
- **Python 3.12 + FastAPI** (REST + WS gateway).
- **SQLAlchemy 2 + Alembic** (PostgreSQL schema/migrations).
- **Redis 7** (round-state, pub/sub, distributed locks, rate limits).
- **Celery/Arq workers** (асинхронные задачи settlement/recovery).
- **Pydantic v2** (строгая типизация контрактов).

### Data
- **PostgreSQL 16**:
  - Ledger/transactions (ACID).
  - Игры, ставки, раунды, аудит, users.
- **Redis cluster**:
  - Active round snapshots.
  - Idempotency keys (TTL).
  - Real-time game channels.

### Frontend
- **React + TypeScript + Vite**.
- **Zustand** (локальные bounded stores: auth/wallet/game/ws).
- **TanStack Query** для REST и cache invalidation.
- **WebSocket client** с sequence-ack/reconnect.

### Infra
- **Docker Compose** (dev/stage parity).
- **Nginx** (TLS termination, sticky WS routing optional).
- **Prometheus + Grafana + Loki** (observability).

## 3) Логическая модульная структура

```text
platform/
  apps/
    api-gateway/          # REST API + WS handshake + auth
    game-crash/
    game-dice/
    game-mines/
    game-plinko/
    payments/
    admin-api/
    worker-settlement/
    worker-recovery/
  libs/
    provably-fair/        # seed lifecycle, HMAC formulas, verification utils
    ledger/               # wallet accounting, double-entry, idempotency
    ws-protocol/          # typed events, seq, replay, ack
    risk/                 # limits, anti-fraud checks
    shared-kernel/        # errors, logging, tracing, base schemas
  deploy/
    docker/
    nginx/
    k8s/ (optional)
```

## 4) Контракты доменных bounded contexts

1. **Identity/Auth**
   - User/session/JWT lifecycle.
   - RBAC: user, support, admin, finance.

2. **Wallet/Ledger**
   - Единственный источник истины по балансу.
   - Double-entry проводки: `DEBIT(user)` ↔ `CREDIT(platform)`.
   - Баланс считается агрегированием ledger entries.

3. **Game Engines**
   - Независимые сервисы по игре.
   - Единый протокол: place bet, settle, rollback, verify.

4. **Provably Fair**
   - Pre-commit server seed hash.
   - Client seed + nonce.
   - Reveal server seed post-round.
   - Public verification endpoint.

5. **Realtime/WS**
   - Broadcast round lifecycle.
   - Поддержка reconnect и replay from sequence.

6. **Admin**
   - Управление edge, лимитами, фичефлагами.
   - Audit trail immutable append-only.

## 5) Архитектура потоков данных

### 5.1 Place Bet
1. Client → API `POST /bets` (idempotency-key).
2. API валидирует лимиты/risk.
3. Ledger transaction (SERIALIZABLE/REPEATABLE READ + row lock).
4. Game service регистрирует bet-state.
5. Redis pub/sub → WS event `bet.accepted`.

### 5.2 Settlement
1. Game engine фиксирует финальный outcome.
2. Worker делает атомарный settlement в БД.
3. Публикуется `round.settled`, `wallet.updated`.
4. Повторный запуск worker безопасен из-за idempotency token и unique constraints.

### 5.3 Recovery
1. При старте worker читает rounds в `IN_PROGRESS`.
2. Сверяет Redis snapshot + DB state.
3. Доводит до terminal state (`SETTLED`/`CANCELLED`) c compensation flow.

## 6) Round lifecycle state machine (унифицированная)

```text
CREATED -> BETTING_OPEN -> BETTING_CLOSED -> IN_PROGRESS ->
SETTLING -> SETTLED
                       \-> CANCELLED
```

Правила:
- Переходы только вперёд (except compensation branch).
- Каждому переходу соответствует monotonic `version`.
- CAS update: `WHERE id=? AND version=?`.

## 7) Нагрузочный дизайн (>50k CCU)

- Stateless API/game pods за L4/L7 балансировщиком.
- WS масштабирование по shard key `user_id % N`.
- Redis cluster + partitioned channels per game.
- PostgreSQL:
  - Partitioning таблиц `bets`, `ledger_entries` (by month/game).
  - Read replicas для аналитики/leaderboard.
- Backpressure:
  - bounded queues, circuit breaker, overload shedding.

## 8) Надёжность и консистентность

- Idempotency:
  - `idempotency_keys` table + Redis cache.
  - Unique index: `(user_id, idempotency_key, route)`.
- Concurrency-safe payouts:
  - `SELECT ... FOR UPDATE` по wallet account.
  - Ledger append-only + atomic commit.
- Retry strategy:
  - exponential backoff + jitter.
  - dead-letter queue для ручного разбора.

## 9) Безопасность

- JWT short-lived + refresh rotation.
- WAF/rate limiting (IP + user + endpoint).
- HMAC signed internal service calls.
- Audit log на критические admin/payment действия.
- Secret management через env/vault; seed reveal только по lifecycle policy.

## 10) API/WS контракты (уровень STEP 1)

### REST (черновой контракт)
- `POST /v1/bets` — place bet (idempotent).
- `POST /v1/cashout` — manual cashout.
- `GET /v1/rounds/{game}/{round_id}` — round details.
- `GET /v1/fair/{game}/{round_id}` — verification payload.
- `GET /v1/leaderboard/{game}` — leaderboard snapshot.

### WS Events
- `round.created`
- `round.betting_open`
- `round.tick`
- `bet.accepted`
- `cashout.accepted`
- `round.settled`
- `wallet.updated`

## 11) DB верхнеуровневая схема (детализация в следующих шагах)

- `users`
- `wallet_accounts`
- `ledger_entries`
- `games`
- `rounds`
- `bets`
- `cashouts`
- `fair_seeds`
- `idempotency_keys`
- `admin_audit_log`

Ключевые индексы:
- `ledger_entries(account_id, created_at)`
- `bets(user_id, round_id)` unique where needed
- `rounds(game, state, started_at)`
- `fair_seeds(game, round_id)` unique

## 12) План следующих шагов

- **STEP 2:** Provably Fair Core + seed lifecycle + verification API.
- **STEP 3:** Ledger wallet (double-entry, ACID, idempotency).
- **STEP 4:** Crash engine + round loop + auto/manual cashout.
- **STEP 5:** Dice engine (instant rounds).
- **STEP 6:** Mines engine.
- **STEP 7:** Plinko engine.
- **STEP 8:** WS layer (typed events, replay, seq).
- **STEP 9:** Payments.
- **STEP 10:** Admin API.
- **STEP 11:** Frontend architecture + UI adaptation from reference.
- **STEP 12:** Docker + Nginx production profiles.
- **STEP 13:** Deployment runbook + SLO/SLI + incident playbooks.

## 13) Definition of Done для STEP 1

- Архитектура модульная, scoped по bounded contexts.
- Определены отказоустойчивость, консистентность, fairness и scaling patterns.
- Есть чёткий backlog шагов для последовательной delivery без пропуска.
