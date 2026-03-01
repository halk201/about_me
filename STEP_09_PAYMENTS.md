# STEP 9 — Payments

Реализован payments-модуль (deposit/withdraw) через ledger posting.

- Сервис: `backend/app/services/payments_service.py`
- API: `POST /v1/payments/deposit`, `POST /v1/payments/withdraw`
- Миграция: `20260228_0005_create_payments_admin_tables.py` (`payments`)
- Тесты: `backend/tests/test_payments_admin_ws.py`
