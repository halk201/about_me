"""Crash engine service with deterministic crash point and idempotent settlement hooks."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal, ROUND_DOWN
from threading import Lock

from app.core.provably_fair import crash_multiplier
from app.models.crash import CrashBet, CrashRound, CrashRoundState
from app.services.ledger_service import LedgerService
from app.services.seed_service import SeedService


class CrashRoundNotFoundError(Exception):
    pass


class InvalidCrashStateError(Exception):
    pass


class CrashBetNotFoundError(Exception):
    pass


class InMemoryCrashRepository:
    """Thread-safe crash round store."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.rounds: dict[str, CrashRound] = {}
        self.bets: dict[str, CrashBet] = {}
        self.bet_seq = 0

    def create_round(self, round_obj: CrashRound) -> CrashRound:
        with self._lock:
            if round_obj.round_id in self.rounds:
                raise ValueError("round already exists")
            self.rounds[round_obj.round_id] = round_obj
            return round_obj

    def get_round(self, round_id: str) -> CrashRound:
        with self._lock:
            if round_id not in self.rounds:
                raise CrashRoundNotFoundError("round not found")
            return self.rounds[round_id]

    def save_round(self, round_obj: CrashRound) -> CrashRound:
        with self._lock:
            self.rounds[round_obj.round_id] = round_obj
            return round_obj

    def create_bet(self, bet: CrashBet) -> CrashBet:
        with self._lock:
            self.bets[bet.bet_id] = bet
            return bet

    def next_bet_id(self) -> str:
        with self._lock:
            self.bet_seq += 1
            return f"crash-bet-{self.bet_seq}"

    def get_bet(self, bet_id: str) -> CrashBet:
        with self._lock:
            if bet_id not in self.bets:
                raise CrashBetNotFoundError("bet not found")
            return self.bets[bet_id]

    def list_bets_for_round(self, round_id: str) -> list[CrashBet]:
        with self._lock:
            return [b for b in self.bets.values() if b.round_id == round_id]


class CrashService:
    """Orchestrates crash lifecycle, bets, and payouts."""

    def __init__(self, repo: InMemoryCrashRepository, seed_service: SeedService, ledger_service: LedgerService) -> None:
        self.repo = repo
        self.seed_service = seed_service
        self.ledger_service = ledger_service

    @staticmethod
    def _to_money(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)

    def create_round(self, round_id: str, client_seed: str, nonce: int, house_edge: float) -> dict:
        seed = self.seed_service.commit_round_seed("crash", round_id, client_seed, nonce)
        crash = crash_multiplier(seed.encrypted_server_seed, client_seed, nonce, house_edge)
        round_obj = CrashRound(
            round_id=round_id,
            state=CrashRoundState.BETTING_OPEN,
            crash_point=Decimal(str(crash.multiplier)),
            version=1,
        )
        return asdict(self.repo.create_round(round_obj))

    def transition_round(self, round_id: str, new_state: CrashRoundState) -> dict:
        round_obj = self.repo.get_round(round_id)
        allowed = {
            CrashRoundState.BETTING_OPEN: {CrashRoundState.BETTING_CLOSED, CrashRoundState.CANCELLED},
            CrashRoundState.BETTING_CLOSED: {CrashRoundState.IN_PROGRESS, CrashRoundState.CANCELLED},
            CrashRoundState.IN_PROGRESS: {CrashRoundState.SETTLING, CrashRoundState.CANCELLED},
            CrashRoundState.SETTLING: {CrashRoundState.SETTLED},
        }
        if round_obj.state not in allowed or new_state not in allowed[round_obj.state]:
            raise InvalidCrashStateError(f"invalid transition {round_obj.state}->{new_state}")

        round_obj.state = new_state
        round_obj.version += 1
        return asdict(self.repo.save_round(round_obj))

    def place_bet(
        self,
        request_id: str,
        round_id: str,
        user_id: str,
        account_id: str,
        amount: Decimal,
        auto_cashout_multiplier: Decimal | None,
    ) -> dict:
        round_obj = self.repo.get_round(round_id)
        if round_obj.state != CrashRoundState.BETTING_OPEN:
            raise InvalidCrashStateError("betting is closed")

        self.ledger_service.transfer(
            request_id=request_id,
            from_account_id=account_id,
            to_account_id="platform",
            amount=amount,
            reference=f"crash:bet:{round_id}",
        )

        bet = CrashBet(
            bet_id=self.repo.next_bet_id(),
            round_id=round_id,
            user_id=user_id,
            account_id=account_id,
            amount=self._to_money(amount),
            auto_cashout_multiplier=auto_cashout_multiplier,
        )
        self.repo.create_bet(bet)
        return asdict(bet)

    def manual_cashout(self, request_id: str, round_id: str, bet_id: str, current_multiplier: Decimal) -> dict:
        round_obj = self.repo.get_round(round_id)
        bet = self.repo.get_bet(bet_id)
        if bet.round_id != round_id:
            raise CrashBetNotFoundError("bet is not in this round")
        if bet.is_settled:
            return asdict(bet)
        if round_obj.state != CrashRoundState.IN_PROGRESS:
            raise InvalidCrashStateError("round is not in progress")
        if current_multiplier >= round_obj.crash_point:
            raise InvalidCrashStateError("cannot cashout after crash point")

        payout = self._to_money(bet.amount * current_multiplier)
        self.ledger_service.transfer(
            request_id=request_id,
            from_account_id="platform",
            to_account_id=bet.account_id,
            amount=payout,
            reference=f"crash:cashout:{round_id}:{bet_id}",
        )
        bet.cashed_out_multiplier = self._to_money(current_multiplier)
        bet.settled_payout = payout
        bet.is_settled = True
        return asdict(bet)

    def settle_round(self, round_id: str) -> list[dict]:
        round_obj = self.repo.get_round(round_id)
        if round_obj.state != CrashRoundState.SETTLING:
            raise InvalidCrashStateError("round must be in settling state")

        settled: list[dict] = []
        for bet in self.repo.list_bets_for_round(round_id):
            if bet.is_settled:
                settled.append(asdict(bet))
                continue

            if bet.auto_cashout_multiplier and bet.auto_cashout_multiplier < round_obj.crash_point:
                payout = self._to_money(bet.amount * bet.auto_cashout_multiplier)
                self.ledger_service.transfer(
                    request_id=f"auto-{round_id}-{bet.bet_id}",
                    from_account_id="platform",
                    to_account_id=bet.account_id,
                    amount=payout,
                    reference=f"crash:auto-cashout:{round_id}:{bet.bet_id}",
                )
                bet.cashed_out_multiplier = self._to_money(bet.auto_cashout_multiplier)
                bet.settled_payout = payout
            else:
                bet.settled_payout = Decimal("0")
            bet.is_settled = True
            settled.append(asdict(bet))

        self.transition_round(round_id, CrashRoundState.SETTLED)
        return settled
