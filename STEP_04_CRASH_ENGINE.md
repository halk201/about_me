# STEP 4 — Crash Engine

Реализован production-oriented модуль Crash как отдельный движок с состояниями раунда, ставками, manual/auto cashout и settlement.

## Что добавлено

- Доменные модели Crash:
  - `CrashRoundState`
  - `CrashRound`
  - `CrashBet`
- Сервис `CrashService`:
  - `create_round` (через Provably Fair seed commit + deterministic crash multiplier)
  - lifecycle transitions (`BETTING_OPEN -> BETTING_CLOSED -> IN_PROGRESS -> SETTLING -> SETTLED`)
  - `place_bet` (списание в platform через ledger)
  - `manual_cashout` (выплата из platform пользователю)
  - `settle_round` (auto-cashout + проигрыш неуспевших ставок)
- API:
  - `POST /v1/crash/rounds`
  - `POST /v1/crash/rounds/{round_id}/state`
  - `POST /v1/crash/bets`
  - `POST /v1/crash/cashout`
  - `POST /v1/crash/rounds/{round_id}/settle`
- WS event contracts:
  - `crash.round.tick`
  - `crash.round.settled`
- Alembic migration:
  - `crash_rounds`
  - `crash_bets`

## Надёжность/конкурентность

- Сервис проектирует идемпотентные точки интеграции через ledger `request_id`.
- Переходы состояний валидируются allow-list матрицей переходов.
- Settlement выполняется только из состояния `SETTLING`.

## Далее

STEP 5 — Dice Engine как независимый модуль c instant rounds и интеграцией с ledger/fair core.
