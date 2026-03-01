from decimal import Decimal

from pydantic import BaseModel, Field


class DicePlayRequest(BaseModel):
    request_id: str = Field(min_length=6)
    user_id: str
    account_id: str
    amount: Decimal = Field(gt=0)
    target: Decimal = Field(gt=0, le=100)
    client_seed: str
    nonce: int = Field(ge=0)
    house_edge: float = Field(default=0.01, ge=0, lt=1)


class DicePlayResponse(BaseModel):
    bet_id: str
    roll: Decimal
    target: Decimal
    win: bool
    payout_multiplier: Decimal
    payout_amount: Decimal
