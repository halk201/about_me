"""WS event schemas for fair-seed lifecycle notifications."""

from __future__ import annotations

from typing import Literal, TypedDict


class FairSeedCommittedEvent(TypedDict):
    type: Literal["fair.seed.committed"]
    game: str
    round_id: str
    server_seed_hash: str
    nonce: int


class FairSeedRevealedEvent(TypedDict):
    type: Literal["fair.seed.revealed"]
    game: str
    round_id: str
    server_seed: str
    hmac_hex: str


class CrashRoundTickEvent(TypedDict):
    type: Literal["crash.round.tick"]
    round_id: str
    multiplier: float
    state: str


class CrashRoundSettledEvent(TypedDict):
    type: Literal["crash.round.settled"]
    round_id: str
    crash_point: float
    settled_bets: int

