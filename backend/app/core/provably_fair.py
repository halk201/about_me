"""Provably Fair primitives for Crash and Dice.

This module is deterministic, side-effect free, and safe to call from workers/API handlers.
"""

from __future__ import annotations

import hmac
import math
from dataclasses import dataclass
from hashlib import sha256

TWO_POW_52 = 2**52
TWO_POW_32 = 2**32


@dataclass(frozen=True)
class CrashResult:
    """Crash deterministic output."""

    hmac_hex: str
    hash_int: int
    x: float
    multiplier: float


@dataclass(frozen=True)
class DiceResult:
    """Dice deterministic output."""

    hmac_hex: str
    roll: float
    payout: float


def build_hmac(server_seed: str, client_seed: str, nonce: int) -> str:
    """Return HMAC-SHA256 hex digest.

    Args:
        server_seed: Secret server seed.
        client_seed: User-provided seed.
        nonce: Monotonic round/bet nonce.
    """
    payload = f"{client_seed}:{nonce}".encode("utf-8")
    key = server_seed.encode("utf-8")
    return hmac.new(key, payload, sha256).hexdigest()


def crash_multiplier(server_seed: str, client_seed: str, nonce: int, house_edge: float) -> CrashResult:
    """Compute Crash multiplier using the required deterministic formula."""
    if not 0 <= house_edge < 1:
        raise ValueError("house_edge must be in [0, 1)")

    hmac_hex = build_hmac(server_seed, client_seed, nonce)
    hash_int = int(hmac_hex[:13], 16)
    x = hash_int / TWO_POW_52

    # multiplier = max(1.00, floor((100*(1-house_edge))/(1-X))/100)
    raw = math.floor((100 * (1 - house_edge)) / (1 - x)) / 100
    multiplier = max(1.00, raw)

    return CrashResult(hmac_hex=hmac_hex, hash_int=hash_int, x=x, multiplier=multiplier)


def dice_roll_and_payout(
    server_seed: str,
    client_seed: str,
    nonce: int,
    target: float,
    house_edge: float,
) -> DiceResult:
    """Compute Dice roll and payout using the required deterministic formula."""
    if not 0 < target <= 100:
        raise ValueError("target must be in (0, 100]")
    if not 0 <= house_edge < 1:
        raise ValueError("house_edge must be in [0, 1)")

    hmac_hex = build_hmac(server_seed, client_seed, nonce)
    roll = (int(hmac_hex[:8], 16) / TWO_POW_32) * 100
    payout = round((100 / target) * (1 - house_edge), 4)

    return DiceResult(hmac_hex=hmac_hex, roll=roll, payout=payout)
