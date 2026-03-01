from decimal import Decimal

from pydantic import BaseModel, Field


class PlinkoDropRequest(BaseModel):
    request_id: str = Field(min_length=6)
    drop_id: str
    user_id: str
    account_id: str
    wager: Decimal = Field(gt=0)
    risk: str = Field(default="medium")
    rows: int = Field(default=16, ge=8, le=16)
    client_seed: str
    nonce: int = Field(ge=0)


class PlinkoDropResponse(BaseModel):
    drop_id: str
    slot: int
    multiplier: Decimal
    payout: Decimal
