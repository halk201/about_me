"""API contracts for Crash engine."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CreateCrashRoundRequest(BaseModel):
    round_id: str = Field(min_length=3, max_length=64)
    client_seed: str = Field(min_length=1, max_length=255)
    nonce: int = Field(ge=0)
    house_edge: float = Field(default=0.01, ge=0, lt=1)


class PlaceCrashBetRequest(BaseModel):
    request_id: str = Field(min_length=6, max_length=128)
    round_id: str
    user_id: str
    account_id: str
    amount: Decimal = Field(gt=0)
    auto_cashout_multiplier: Decimal | None = Field(default=None, gt=1)


class ManualCashoutRequest(BaseModel):
    request_id: str = Field(min_length=6, max_length=128)
    round_id: str
    bet_id: str
    current_multiplier: Decimal = Field(gt=1)


class CrashRoundResponse(BaseModel):
    round_id: str
    state: str
    crash_point: Decimal
    version: int


class CrashBetResponse(BaseModel):
    bet_id: str
    round_id: str
    user_id: str
    amount: Decimal
    auto_cashout_multiplier: Decimal | None
    cashed_out_multiplier: Decimal | None
    settled_payout: Decimal
    is_settled: bool
