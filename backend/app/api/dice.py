from dataclasses import asdict
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from app.schemas.dice import DicePlayRequest, DicePlayResponse
from app.services.dice_service import DiceService
from app.services.ledger_service import DuplicateAccountError, InMemoryLedgerRepository, LedgerService
from app.services.seed_service import InMemorySeedRepository, SeedService

router = APIRouter(prefix="/v1/dice", tags=["dice"])

ledger = LedgerService(InMemoryLedgerRepository())
seed = SeedService(InMemorySeedRepository())
service = DiceService(ledger, seed)

for account_id, uid, typ, bal in [("platform", None, "PLATFORM", Decimal("1000000")), ("user-1", "u1", "USER", Decimal("1000"))]:
    try:
        ledger.create_account(account_id, uid, "USD", typ, bal)
    except DuplicateAccountError:
        pass


@router.post("/play", response_model=DicePlayResponse)
def play(payload: DicePlayRequest) -> DicePlayResponse:
    try:
        bet = service.play(**payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return DicePlayResponse(
        bet_id=bet.bet_id,
        roll=bet.roll,
        target=bet.target,
        win=bet.win,
        payout_multiplier=bet.payout_multiplier,
        payout_amount=bet.payout_amount,
    )
