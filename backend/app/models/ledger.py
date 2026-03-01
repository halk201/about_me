"""Domain models for wallet/ledger."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal


class AccountType(str, enum.Enum):
    USER = "USER"
    PLATFORM = "PLATFORM"
    BONUS = "BONUS"


class EntryType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


@dataclass
class WalletAccount:
    account_id: str
    user_id: str | None
    currency: str
    account_type: AccountType
    balance: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class LedgerEntry:
    entry_id: str
    request_id: str
    account_id: str
    amount: Decimal
    entry_type: EntryType
    reference: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
