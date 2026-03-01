"""Pydantic contracts for fair verification endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CrashVerifyResponse(BaseModel):
    game: str = Field(default="crash")
    round_id: str
    server_seed_hash: str
    server_seed: str
    client_seed: str
    nonce: int
    multiplier: float
    hmac_hex: str


class DiceVerifyResponse(BaseModel):
    game: str = Field(default="dice")
    round_id: str
    server_seed_hash: str
    server_seed: str
    client_seed: str
    nonce: int
    target: float
    roll: float
    payout: float
    hmac_hex: str
