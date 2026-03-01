from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AdminAuditEvent:
    actor: str
    action: str
    payload: dict
    created_at: datetime


class AdminService:
    def __init__(self) -> None:
        self.house_edges: dict[str, float] = {"crash": 0.01, "dice": 0.01, "mines": 0.01, "plinko": 0.01}
        self.audit: list[AdminAuditEvent] = []

    def set_house_edge(self, actor: str, game: str, edge: float) -> dict:
        if not 0 <= edge < 1:
            raise ValueError("edge must be in [0,1)")
        self.house_edges[game] = edge
        ev = AdminAuditEvent(actor, "set_house_edge", {"game": game, "edge": edge}, datetime.now(timezone.utc))
        self.audit.append(ev)
        return {"game": game, "edge": edge}

    def list_audit(self) -> list[dict]:
        return [{"actor": x.actor, "action": x.action, "payload": x.payload, "created_at": x.created_at.isoformat()} for x in self.audit]
