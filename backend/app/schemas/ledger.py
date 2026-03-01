"""Pydantic schemas for wallet/ledger API."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CreateAccountRequest(BaseModel):
    account_id: str = Field(min_length=3, max_length=64)
    user_id: str | None = Field(default=None, max_length=64)
    currency: str = Field(default="USD", min_length=3, max_length=8)
    account_type: str
    initial_balance: Decimal = Field(default=Decimal("0"), ge=0)


class TransferRequest(BaseModel):
    request_id: str = Field(min_length=6, max_length=128)
    from_account_id: str
    to_account_id: str
    amount: Decimal = Field(gt=0)
    reference: str = Field(min_length=1, max_length=255)


class BalanceResponse(BaseModel):
    account_id: str
    currency: str
    balance: Decimal


class TransferResponse(BaseModel):
    request_id: str
    from_account_id: str
    to_account_id: str
    amount: Decimal
    from_balance: Decimal
    to_balance: Decimal
    idempotent_replay: bool
