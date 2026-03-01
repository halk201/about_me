from dataclasses import asdict
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from app.schemas.plinko import PlinkoDropRequest, PlinkoDropResponse
from app.services.ledger_service import DuplicateAccountError, InMemoryLedgerRepository, LedgerService
from app.services.plinko_service import PlinkoService

router = APIRouter(prefix="/v1/plinko", tags=["plinko"])
ledger = LedgerService(InMemoryLedgerRepository())
service = PlinkoService(ledger)
for account_id, uid, typ, bal in [("platform", None, "PLATFORM", Decimal("1000000")), ("user-1", "u1", "USER", Decimal("1000"))]:
    try:
        ledger.create_account(account_id, uid, "USD", typ, bal)
    except DuplicateAccountError:
        pass


@router.post("/drop", response_model=PlinkoDropResponse)
def drop(payload: PlinkoDropRequest) -> PlinkoDropResponse:
    try:
        d = service.drop(**payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PlinkoDropResponse(**asdict(d))
