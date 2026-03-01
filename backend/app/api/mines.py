from dataclasses import asdict
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from app.schemas.mines import MinesCashoutRequest, MinesCreateGameRequest, MinesGameResponse, MinesOpenCellRequest
from app.services.ledger_service import DuplicateAccountError, InMemoryLedgerRepository, LedgerService
from app.services.mines_service import MinesService

router = APIRouter(prefix="/v1/mines", tags=["mines"])
ledger = LedgerService(InMemoryLedgerRepository())
service = MinesService(ledger)
for account_id, uid, typ, bal in [("platform", None, "PLATFORM", Decimal("1000000")), ("user-1", "u1", "USER", Decimal("1000"))]:
    try:
        ledger.create_account(account_id, uid, "USD", typ, bal)
    except DuplicateAccountError:
        pass


@router.post("/games", response_model=MinesGameResponse)
def create_game(payload: MinesCreateGameRequest) -> MinesGameResponse:
    try:
        g = service.create_game(**payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return MinesGameResponse(**asdict(g))


@router.post("/open", response_model=MinesGameResponse)
def open_cell(payload: MinesOpenCellRequest) -> MinesGameResponse:
    g = service.open_cell(payload.game_id, payload.cell_index)
    return MinesGameResponse(**asdict(g))


@router.post("/cashout", response_model=MinesGameResponse)
def cashout(payload: MinesCashoutRequest) -> MinesGameResponse:
    g = service.cashout(payload.request_id, payload.game_id)
    return MinesGameResponse(**asdict(g))
