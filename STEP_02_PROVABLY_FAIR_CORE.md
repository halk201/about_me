# STEP 2 — Provably Fair Core + Seed Management

Этот шаг добавляет production-oriented ядро Provably Fair для Crash и Dice:

- Детерминированные формулы из ТЗ:
  - Crash: HMAC -> `hash[:13]` -> `X = hash_int / 2^52` -> multiplier.
  - Dice: HMAC -> `hash[:8]` -> roll -> payout.
- Seed lifecycle: commit (hash before round), reveal (после round), verify (публичный API).
- WebSocket event contracts для `fair.seed.committed` и `fair.seed.revealed`.
- Alembic migration для таблицы `fair_seeds`.

## Что добавлено

- `backend/app/core/provably_fair.py` — формулы и типизированные результаты.
- `backend/app/services/seed_service.py` — lifecycle сервис seed-ов (idempotent reveal semantics).
- `backend/app/api/fair.py` — REST endpoints commit/verify.
- `backend/app/schemas/fair.py` — response contracts.
- `backend/app/ws/events.py` — WS event schema.
- `backend/alembic/versions/20260228_0001_create_fair_seeds.py` — миграция.
- `backend/tests/test_provably_fair.py` — детерминизм формул.

## API

- `POST /v1/fair/{game}/{round_id}/commit?client_seed=...&nonce=...`
- `GET /v1/fair/crash/{round_id}?house_edge=0.01`
- `GET /v1/fair/dice/{round_id}?target=50&house_edge=0.01`

## Дальше

STEP 3 будет строить ACID-safe ledger/wallet с idempotent posting, чтобы ставки/выплаты шли через double-entry.
