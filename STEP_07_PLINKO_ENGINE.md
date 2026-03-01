# STEP 7 — Plinko Engine

Реализован отдельный Plinko-модуль с детерминированным выбором слота через HMAC и риск-таблицами коэффициентов.

- Сервис: `backend/app/services/plinko_service.py`
- API: `POST /v1/plinko/drop`
- Схемы/модель: `backend/app/schemas/plinko.py`, `backend/app/models/plinko.py`
- Миграция: `20260228_0004_create_dice_mines_plinko_tables.py` (`plinko_drops`)
- Тест: `backend/tests/test_plinko_service.py`
