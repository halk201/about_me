from decimal import Decimal, ROUND_DOWN

from app.core.provably_fair import build_hmac
from app.models.plinko import PlinkoDrop
from app.services.ledger_service import LedgerService


PLINKO_TABLE = {
    "low": [Decimal("0.5"), Decimal("0.7"), Decimal("1.0"), Decimal("1.4"), Decimal("2.0")],
    "medium": [Decimal("0.2"), Decimal("0.5"), Decimal("1.0"), Decimal("2.5"), Decimal("5.0")],
    "high": [Decimal("0.1"), Decimal("0.3"), Decimal("1.0"), Decimal("4.0"), Decimal("10.0")],
}


class PlinkoService:
    def __init__(self, ledger_service: LedgerService) -> None:
        self.ledger = ledger_service

    def drop(self, request_id: str, drop_id: str, user_id: str, account_id: str, wager: Decimal, risk: str, rows: int, client_seed: str, nonce: int) -> PlinkoDrop:
        self.ledger.transfer(request_id, account_id, "platform", wager, f"plinko:bet:{drop_id}")
        h = build_hmac("server", client_seed, nonce)
        slot = int(h[:4], 16) % 5
        multiplier = PLINKO_TABLE.get(risk, PLINKO_TABLE["medium"])[slot]
        payout = (wager * multiplier).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        if payout > 0:
            self.ledger.transfer(f"{request_id}:payout", "platform", account_id, payout, f"plinko:payout:{drop_id}")
        return PlinkoDrop(drop_id, user_id, account_id, wager, risk, rows, slot, multiplier, payout)
