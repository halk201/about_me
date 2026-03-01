from decimal import Decimal

from app.models.crash import CrashRoundState
from app.services.crash_service import CrashService, InMemoryCrashRepository
from app.services.ledger_service import InMemoryLedgerRepository, LedgerService
from app.services.seed_service import InMemorySeedRepository, SeedService


def _build_service() -> CrashService:
    ledger_repo = InMemoryLedgerRepository()
    ledger = LedgerService(ledger_repo)
    ledger.create_account("platform", None, "USD", "PLATFORM", Decimal("1000000"))
    ledger.create_account("user-1", "u1", "USD", "USER", Decimal("1000"))

    seed = SeedService(InMemorySeedRepository())
    crash_repo = InMemoryCrashRepository()
    return CrashService(crash_repo, seed, ledger)


def test_crash_round_lifecycle_and_auto_cashout() -> None:
    service = _build_service()
    round_obj = service.create_round("r1", "client-seed", 1, 0.01)

    assert round_obj["state"] == CrashRoundState.BETTING_OPEN

    bet = service.place_bet("req-bet-1", "r1", "u1", "user-1", Decimal("10"), Decimal("1.20"))
    assert bet["amount"] == Decimal("10.00000000")

    service.transition_round("r1", CrashRoundState.BETTING_CLOSED)
    service.transition_round("r1", CrashRoundState.IN_PROGRESS)
    service.transition_round("r1", CrashRoundState.SETTLING)

    settled = service.settle_round("r1")
    assert len(settled) == 1
    assert settled[0]["is_settled"] is True


def test_manual_cashout_marks_bet_as_settled() -> None:
    service = _build_service()
    round_obj = service.create_round("r2", "client-seed", 2, 0.01)

    bet = service.place_bet("req-bet-2", "r2", "u1", "user-1", Decimal("5"), None)
    service.transition_round("r2", CrashRoundState.BETTING_CLOSED)
    service.transition_round("r2", CrashRoundState.IN_PROGRESS)

    current_multiplier = min(Decimal("1.5"), Decimal(round_obj["crash_point"]) - Decimal("0.01"))
    if current_multiplier <= Decimal("1"):
        current_multiplier = Decimal("1.01")

    cashed = service.manual_cashout("req-cashout-1", "r2", bet["bet_id"], current_multiplier)
    assert cashed["is_settled"] is True
    assert cashed["settled_payout"] > Decimal("0")
