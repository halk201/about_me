# STEP 5 — Dice Engine

Реализован отдельный Dice-модуль с instant-round логикой, deterministic roll/payout через Provably Fair и интеграцией с ledger.

- Сервис: `backend/app/services/dice_service.py`
- API: `POST /v1/dice/play`
- Схемы/модель: `backend/app/schemas/dice.py`, `backend/app/models/dice.py`
- Миграция: `20260228_0004_create_dice_mines_plinko_tables.py` (`dice_bets`)
- Тест: `backend/tests/test_dice_service.py`
