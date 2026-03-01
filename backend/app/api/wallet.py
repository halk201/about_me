"""Wallet/Ledger API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.ledger import (
    BalanceResponse,
    CreateAccountRequest,
    TransferRequest,
    TransferResponse,
)
from app.services.ledger_service import (
    AccountNotFoundError,
    DuplicateAccountError,
    InMemoryLedgerRepository,
    InsufficientFundsError,
    LedgerService,
)

router = APIRouter(prefix="/v1/wallet", tags=["wallet"])
repo = InMemoryLedgerRepository()
service = LedgerService(repo)


@router.post("/accounts")
def create_account(payload: CreateAccountRequest) -> dict:
    try:
        return service.create_account(
            account_id=payload.account_id,
            user_id=payload.user_id,
            currency=payload.currency,
            account_type=payload.account_type,
            initial_balance=payload.initial_balance,
        )
    except DuplicateAccountError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{account_id}/balance", response_model=BalanceResponse)
def get_balance(account_id: str) -> BalanceResponse:
    try:
        return BalanceResponse(**service.get_balance(account_id))
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/transfer", response_model=TransferResponse)
def transfer(payload: TransferRequest) -> TransferResponse:
    try:
        result = service.transfer(
            request_id=payload.request_id,
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
            amount=payload.amount,
            reference=payload.reference,
        )
        return TransferResponse(**result)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InsufficientFundsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
