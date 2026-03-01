from decimal import Decimal

from app.services.ledger_service import InMemoryLedgerRepository, LedgerService
from app.services.plinko_service import PlinkoService


def test_plinko_drop() -> None:
    ledger = LedgerService(InMemoryLedgerRepository())
    ledger.create_account("platform", None, "USD", "PLATFORM", Decimal("1000000"))
    ledger.create_account("user-1", "u1", "USD", "USER", Decimal("100"))
    service = PlinkoService(ledger)

    drop = service.drop("req-1", "d1", "u1", "user-1", Decimal("5"), "medium", 16, "client", 7)
    assert 0 <= drop.slot <= 4
    assert drop.payout >= Decimal("0")
