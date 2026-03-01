"""Crash game API endpoints."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, HTTPException

from app.models.crash import CrashRoundState
from app.schemas.crash import (
    CrashBetResponse,
    CrashRoundResponse,
    CreateCrashRoundRequest,
    ManualCashoutRequest,
    PlaceCrashBetRequest,
)
from app.services.crash_service import (
    CrashBetNotFoundError,
    CrashRoundNotFoundError,
    CrashService,
    InMemoryCrashRepository,
    InvalidCrashStateError,
)
from app.services.ledger_service import DuplicateAccountError, InMemoryLedgerRepository, LedgerService
from app.services.seed_service import InMemorySeedRepository, SeedService

router = APIRouter(prefix="/v1/crash", tags=["crash"])

ledger_repo = InMemoryLedgerRepository()
ledger_service = LedgerService(ledger_repo)
seed_repo = InMemorySeedRepository()
seed_service = SeedService(seed_repo)
crash_repo = InMemoryCrashRepository()
crash_service = CrashService(crash_repo, seed_service, ledger_service)

try:
    ledger_service.create_account("platform", None, "USD", "PLATFORM", Decimal("1000000"))
except DuplicateAccountError:
    pass


@router.post("/rounds", response_model=CrashRoundResponse)
def create_round(payload: CreateCrashRoundRequest) -> CrashRoundResponse:
    try:
        result = crash_service.create_round(
            round_id=payload.round_id,
            client_seed=payload.client_seed,
            nonce=payload.nonce,
            house_edge=payload.house_edge,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return CrashRoundResponse(**result)


@router.post("/rounds/{round_id}/state", response_model=CrashRoundResponse)
def change_round_state(round_id: str, state: CrashRoundState) -> CrashRoundResponse:
    try:
        result = crash_service.transition_round(round_id, state)
    except CrashRoundNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidCrashStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return CrashRoundResponse(**result)


@router.post("/bets", response_model=CrashBetResponse)
def place_bet(payload: PlaceCrashBetRequest) -> CrashBetResponse:
    try:
        result = crash_service.place_bet(
            request_id=payload.request_id,
            round_id=payload.round_id,
            user_id=payload.user_id,
            account_id=payload.account_id,
            amount=payload.amount,
            auto_cashout_multiplier=payload.auto_cashout_multiplier,
        )
    except (CrashRoundNotFoundError, CrashBetNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidCrashStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return CrashBetResponse(**result)


@router.post("/cashout", response_model=CrashBetResponse)
def manual_cashout(payload: ManualCashoutRequest) -> CrashBetResponse:
    try:
        result = crash_service.manual_cashout(
            request_id=payload.request_id,
            round_id=payload.round_id,
            bet_id=payload.bet_id,
            current_multiplier=payload.current_multiplier,
        )
    except (CrashRoundNotFoundError, CrashBetNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidCrashStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return CrashBetResponse(**result)


@router.post("/rounds/{round_id}/settle")
def settle_round(round_id: str) -> list[CrashBetResponse]:
    try:
        settled = crash_service.settle_round(round_id)
    except CrashRoundNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidCrashStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return [CrashBetResponse(**item) for item in settled]
