"""Crash game domain models and state machine enums."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal


class CrashRoundState(str, enum.Enum):
    CREATED = "CREATED"
    BETTING_OPEN = "BETTING_OPEN"
    BETTING_CLOSED = "BETTING_CLOSED"
    IN_PROGRESS = "IN_PROGRESS"
    SETTLING = "SETTLING"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"


@dataclass
class CrashRound:
    round_id: str
    state: CrashRoundState
    crash_point: Decimal
    version: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CrashBet:
    bet_id: str
    round_id: str
    user_id: str
    account_id: str
    amount: Decimal
    auto_cashout_multiplier: Decimal | None = None
    cashed_out_multiplier: Decimal | None = None
    settled_payout: Decimal = Decimal("0")
    is_settled: bool = False
