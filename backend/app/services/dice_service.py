from decimal import Decimal, ROUND_DOWN

from app.core.provably_fair import dice_roll_and_payout
from app.models.dice import DiceBet
from app.services.ledger_service import LedgerService
from app.services.seed_service import SeedService


class DiceService:
    def __init__(self, ledger_service: LedgerService, seed_service: SeedService) -> None:
        self.ledger_service = ledger_service
        self.seed_service = seed_service
        self.seq = 0

    def play(
        self,
        request_id: str,
        user_id: str,
        account_id: str,
        amount: Decimal,
        target: Decimal,
        client_seed: str,
        nonce: int,
        house_edge: float,
    ) -> DiceBet:
        self.seq += 1
        bet_id = f"dice-{self.seq}"
        self.ledger_service.transfer(request_id, account_id, "platform", amount, f"dice:bet:{bet_id}")

        self.seed_service.commit_round_seed("dice", bet_id, client_seed, nonce)
        result = dice_roll_and_payout("server", client_seed, nonce, float(target), house_edge)
        roll = Decimal(str(result.roll)).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
        multiplier = Decimal(str(result.payout))
        win = roll < target
        payout = (amount * multiplier).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN) if win else Decimal("0")

        if payout > 0:
            self.ledger_service.transfer(f"{request_id}:payout", "platform", account_id, payout, f"dice:payout:{bet_id}")

        return DiceBet(
            bet_id=bet_id,
            user_id=user_id,
            account_id=account_id,
            amount=amount,
            target=target,
            roll=roll,
            payout_multiplier=multiplier,
            payout_amount=payout,
            win=win,
        )
