# STEP 10 — Admin API

Реализован Admin API для управления house edge и audit trail.

- Сервис: `backend/app/services/admin_service.py`
- API: `POST /v1/admin/house-edge`, `GET /v1/admin/audit`
- Миграция: `20260228_0005_create_payments_admin_tables.py` (`admin_audit_log`)
- Тесты: `backend/tests/test_payments_admin_ws.py`
