from decimal import Decimal

from app.services.ledger_service import InMemoryLedgerRepository, LedgerService
from app.services.mines_service import MinesService


def test_mines_open_and_cashout() -> None:
    ledger = LedgerService(InMemoryLedgerRepository())
    ledger.create_account("platform", None, "USD", "PLATFORM", Decimal("1000000"))
    ledger.create_account("user-1", "u1", "USD", "USER", Decimal("100"))
    service = MinesService(ledger)

    game = service.create_game("req-1", "g1", "u1", "user-1", Decimal("10"), 3, 25)
    assert game.game_id == "g1"
    game = service.open_cell("g1", 1)
    if not game.hit_mine:
        game = service.cashout("req-2", "g1")
    assert game.settled is True
