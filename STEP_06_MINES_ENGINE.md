# STEP 6 — Mines Engine

Реализован отдельный Mines-модуль с состоянием игры, открытием клеток, детерминированной генерацией мин по hash(game_id), cashout и ledger settlement.

- Сервис: `backend/app/services/mines_service.py`
- API: `POST /v1/mines/games`, `POST /v1/mines/open`, `POST /v1/mines/cashout`
- Схемы/модель: `backend/app/schemas/mines.py`, `backend/app/models/mines.py`
- Миграция: `20260228_0004_create_dice_mines_plinko_tables.py` (`mines_games`)
- Тест: `backend/tests/test_mines_service.py`
