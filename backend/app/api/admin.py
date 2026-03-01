from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.admin_service import AdminService


class SetEdgeRequest(BaseModel):
    actor: str
    game: str
    edge: float = Field(ge=0, lt=1)


router = APIRouter(prefix="/v1/admin", tags=["admin"])
service = AdminService()


@router.post("/house-edge")
def set_house_edge(payload: SetEdgeRequest) -> dict:
    try:
        return service.set_house_edge(payload.actor, payload.game, payload.edge)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/audit")
def audit() -> list[dict]:
    return service.list_audit()
