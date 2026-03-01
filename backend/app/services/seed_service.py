"""Seed management service (idempotent + restart-safe design hooks)."""

from __future__ import annotations

import secrets
from hashlib import sha256
from threading import Lock

from app.core.provably_fair import crash_multiplier, dice_roll_and_payout
from app.models.fair_seed import FairSeedRecord, SeedState


class InMemorySeedRepository:
    """Thread-safe repository for local development and tests."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._records: dict[tuple[str, str], FairSeedRecord] = {}

    def create(self, record: FairSeedRecord) -> FairSeedRecord:
        with self._lock:
            key = (record.game, record.round_id)
            if key in self._records:
                raise ValueError("seed already exists")
            self._records[key] = record
            return record

    def get(self, game: str, round_id: str) -> FairSeedRecord:
        with self._lock:
            key = (game, round_id)
            if key not in self._records:
                raise KeyError("seed not found")
            return self._records[key]

    def reveal(self, game: str, round_id: str, server_seed: str) -> FairSeedRecord:
        with self._lock:
            key = (game, round_id)
            record = self._records[key]
            if record.state == SeedState.REVEALED:
                return record
            record.revealed_server_seed = server_seed
            record.state = SeedState.REVEALED
            self._records[key] = record
            return record


class SeedService:
    """Fair-seed lifecycle orchestration."""

    def __init__(self, repo: InMemorySeedRepository) -> None:
        self.repo = repo

    @staticmethod
    def _hash_seed(server_seed: str) -> str:
        return sha256(server_seed.encode("utf-8")).hexdigest()

    def commit_round_seed(self, game: str, round_id: str, client_seed: str, nonce: int) -> FairSeedRecord:
        """Create seed commit before round starts."""
        server_seed = secrets.token_hex(32)
        server_seed_hash = self._hash_seed(server_seed)

        record = FairSeedRecord(
            id=secrets.token_hex(16),
            game=game,
            round_id=round_id,
            server_seed_hash=server_seed_hash,
            encrypted_server_seed=server_seed,  # replace with KMS envelope encryption in production
            client_seed=client_seed,
            nonce=nonce,
        )
        return self.repo.create(record)

    def verify_crash(self, round_id: str, house_edge: float) -> dict:
        """Reveal and verify crash round deterministically."""
        record = self.repo.get("crash", round_id)
        result = crash_multiplier(
            server_seed=record.encrypted_server_seed,
            client_seed=record.client_seed,
            nonce=record.nonce,
            house_edge=house_edge,
        )
        self.repo.reveal("crash", round_id, record.encrypted_server_seed)
        return {
            "round_id": round_id,
            "server_seed_hash": record.server_seed_hash,
            "server_seed": record.encrypted_server_seed,
            "client_seed": record.client_seed,
            "nonce": record.nonce,
            "multiplier": result.multiplier,
            "hmac_hex": result.hmac_hex,
        }

    def verify_dice(self, round_id: str, target: float, house_edge: float) -> dict:
        """Reveal and verify dice round deterministically."""
        record = self.repo.get("dice", round_id)
        result = dice_roll_and_payout(
            server_seed=record.encrypted_server_seed,
            client_seed=record.client_seed,
            nonce=record.nonce,
            target=target,
            house_edge=house_edge,
        )
        self.repo.reveal("dice", round_id, record.encrypted_server_seed)
        return {
            "round_id": round_id,
            "server_seed_hash": record.server_seed_hash,
            "server_seed": record.encrypted_server_seed,
            "client_seed": record.client_seed,
            "nonce": record.nonce,
            "target": target,
            "roll": result.roll,
            "payout": result.payout,
            "hmac_hex": result.hmac_hex,
        }
