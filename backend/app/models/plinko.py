from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PlinkoDrop:
    drop_id: str
    user_id: str
    account_id: str
    wager: Decimal
    risk: str
    rows: int
    slot: int
    multiplier: Decimal
    payout: Decimal
