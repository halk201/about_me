from decimal import Decimal

from app.services.admin_service import AdminService
from app.services.ledger_service import InMemoryLedgerRepository, LedgerService
from app.services.payments_service import PaymentsService
from app.services.ws_service import WsReplayBuffer


def test_payments_deposit_withdraw() -> None:
    ledger = LedgerService(InMemoryLedgerRepository())
    ledger.create_account("platform", None, "USD", "PLATFORM", Decimal("1000000"))
    ledger.create_account("user-1", "u1", "USD", "USER", Decimal("100"))
    p = PaymentsService(ledger)
    d = p.deposit("req-d", "p1", "u1", "user-1", Decimal("10"))
    w = p.withdraw("req-w", "p2", "u1", "user-1", Decimal("5"))
    assert d.status == "COMPLETED"
    assert w.status == "COMPLETED"


def test_admin_and_ws() -> None:
    a = AdminService()
    out = a.set_house_edge("admin", "dice", 0.02)
    assert out["edge"] == 0.02
    assert len(a.list_audit()) == 1

    ws = WsReplayBuffer()
    ws.publish("c", {"x": 1})
    ws.publish("c", {"x": 2})
    assert len(ws.replay_from(1)) == 1
