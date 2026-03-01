from decimal import Decimal

import pytest

from app.services.ledger_service import (
    AccountNotFoundError,
    InMemoryLedgerRepository,
    InsufficientFundsError,
    LedgerService,
)


def test_transfer_is_idempotent_and_double_entry() -> None:
    repo = InMemoryLedgerRepository()
    service = LedgerService(repo)

    service.create_account("platform", None, "USD", "PLATFORM", Decimal("1000"))
    service.create_account("user-1", "u1", "USD", "USER")

    service.transfer("req-bootstrap", "platform", "user-1", Decimal("100"), "fund user")
    first = service.transfer("req-1", "user-1", "platform", Decimal("10"), "bet")
    replay = service.transfer("req-1", "user-1", "platform", Decimal("10"), "bet")

    assert first["idempotent_replay"] is False
    assert replay["idempotent_replay"] is True
    assert first["from_balance"] == replay["from_balance"] == Decimal("90")

    req1_entries = [e for e in repo.entries if e.request_id == "req-1"]
    assert len(req1_entries) == 2
    assert sum((e.amount for e in req1_entries), start=Decimal("0")) == Decimal("20")


def test_transfer_rejects_insufficient_funds() -> None:
    repo = InMemoryLedgerRepository()
    service = LedgerService(repo)

    service.create_account("platform", None, "USD", "PLATFORM", Decimal("1000"))
    service.create_account("user-1", "u1", "USD", "USER")

    with pytest.raises(InsufficientFundsError):
        service.transfer("req-2", "user-1", "platform", Decimal("1"), "bet")


def test_balance_raises_for_missing_account() -> None:
    repo = InMemoryLedgerRepository()
    service = LedgerService(repo)

    with pytest.raises(AccountNotFoundError):
        service.get_balance("missing")
