from decimal import Decimal

from app.services.dice_service import DiceService
from app.services.ledger_service import InMemoryLedgerRepository, LedgerService
from app.services.seed_service import InMemorySeedRepository, SeedService


def test_dice_play_runs_and_returns_deterministic_fields() -> None:
    ledger = LedgerService(InMemoryLedgerRepository())
    ledger.create_account("platform", None, "USD", "PLATFORM", Decimal("1000000"))
    ledger.create_account("user-1", "u1", "USD", "USER", Decimal("100"))
    service = DiceService(ledger, SeedService(InMemorySeedRepository()))

    bet = service.play("req-1", "u1", "user-1", Decimal("10"), Decimal("50"), "client", 1, 0.01)
    assert bet.bet_id.startswith("dice-")
    assert bet.target == Decimal("50")
    assert bet.payout_multiplier > Decimal("0")
