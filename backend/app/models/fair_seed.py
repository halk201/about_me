"""DB model definitions for provably-fair seed lifecycle."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone


class SeedState(str, enum.Enum):
    """Seed lifecycle state."""

    COMMITTED = "COMMITTED"
    REVEALED = "REVEALED"
    RETIRED = "RETIRED"


@dataclass
class FairSeedRecord:
    """Storage-agnostic fair-seed record.

    In production, map this dataclass to SQLAlchemy ORM model.
    """

    id: str
    game: str
    round_id: str
    server_seed_hash: str
    encrypted_server_seed: str
    client_seed: str
    nonce: int
    state: SeedState = SeedState.COMMITTED
    revealed_server_seed: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    revealed_at: datetime | None = None
