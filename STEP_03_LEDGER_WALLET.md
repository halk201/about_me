# STEP 3 — Ledger Wallet (ACID-safe, idempotent, double-entry)

Реализован базовый модуль кошелька и ledger c фокусом на корректность проводок и безопасные повторы запросов.

## Реализовано

- Модели кошелька и проводок:
  - `WalletAccount`
  - `LedgerEntry`
  - типы `AccountType`, `EntryType`
- Сервис `LedgerService` + thread-safe репозиторий `InMemoryLedgerRepository`:
  - создание аккаунта
  - получение баланса
  - перевод (double-entry: debit+credit)
  - idempotent replay по `request_id`
- API:
  - `POST /v1/wallet/accounts`
  - `GET /v1/wallet/{account_id}/balance`
  - `POST /v1/wallet/transfer`
- Alembic migration:
  - `wallet_accounts`
  - `ledger_entries`
  - `idempotency_keys`
- Тесты:
  - идемпотентность перевода
  - защита от недостатка средств
  - ошибка при запросе несуществующего счёта

## Production notes

- В продакшене операции перевода должны выполняться в транзакции PostgreSQL (`SERIALIZABLE` или `REPEATABLE READ` + `SELECT FOR UPDATE`).
- `idempotency_keys` хранит response payload, чтобы повторный запрос возвращал тот же результат без повторного списания.
- Баланс в продакшене можно считать либо из ledger (source of truth), либо держать materialized balance c reconciliation job.
