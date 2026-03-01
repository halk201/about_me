from dataclasses import asdict
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ledger_service import DuplicateAccountError, InMemoryLedgerRepository, LedgerService
from app.services.payments_service import PaymentsService


class PaymentRequest(BaseModel):
    request_id: str = Field(min_length=6)
    payment_id: str
    user_id: str
    account_id: str
    amount: Decimal = Field(gt=0)


router = APIRouter(prefix="/v1/payments", tags=["payments"])
ledger = LedgerService(InMemoryLedgerRepository())
service = PaymentsService(ledger)
for account_id, uid, typ, bal in [("platform", None, "PLATFORM", Decimal("1000000")), ("user-1", "u1", "USER", Decimal("1000"))]:
    try:
        ledger.create_account(account_id, uid, "USD", typ, bal)
    except DuplicateAccountError:
        pass


@router.post("/deposit")
def deposit(payload: PaymentRequest) -> dict:
    try:
        return asdict(service.deposit(**payload.model_dump()))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/withdraw")
def withdraw(payload: PaymentRequest) -> dict:
    try:
        return asdict(service.withdraw(**payload.model_dump()))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
