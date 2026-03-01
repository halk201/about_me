"""Provably Fair HTTP endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.schemas.fair import CrashVerifyResponse, DiceVerifyResponse
from app.services.seed_service import InMemorySeedRepository, SeedService

router = APIRouter(prefix="/v1/fair", tags=["fair"])
repo = InMemorySeedRepository()
service = SeedService(repo)


@router.post("/{game}/{round_id}/commit")
def commit_seed(game: str, round_id: str, client_seed: str, nonce: int) -> dict:
    """Commit fair seed hash for an upcoming round."""
    try:
        record = service.commit_round_seed(game=game, round_id=round_id, client_seed=client_seed, nonce=nonce)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "game": record.game,
        "round_id": record.round_id,
        "server_seed_hash": record.server_seed_hash,
        "client_seed": record.client_seed,
        "nonce": record.nonce,
        "state": record.state,
    }


@router.get("/crash/{round_id}", response_model=CrashVerifyResponse)
def verify_crash(round_id: str, house_edge: float = Query(default=0.01, ge=0, lt=1)) -> CrashVerifyResponse:
    """Reveal/verify Crash result for completed round."""
    try:
        payload = service.verify_crash(round_id=round_id, house_edge=house_edge)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="round seed not found") from exc
    return CrashVerifyResponse(**payload)


@router.get("/dice/{round_id}", response_model=DiceVerifyResponse)
def verify_dice(
    round_id: str,
    target: float = Query(default=50.0, gt=0, le=100),
    house_edge: float = Query(default=0.01, ge=0, lt=1),
) -> DiceVerifyResponse:
    """Reveal/verify Dice result for completed round."""
    try:
        payload = service.verify_dice(round_id=round_id, target=target, house_edge=house_edge)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="round seed not found") from exc
    return DiceVerifyResponse(**payload)
