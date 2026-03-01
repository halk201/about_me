from dataclasses import dataclass
from decimal import Decimal


@dataclass
class DiceBet:
    bet_id: str
    user_id: str
    account_id: str
    amount: Decimal
    target: Decimal
    roll: Decimal
    payout_multiplier: Decimal
    payout_amount: Decimal
    win: bool
