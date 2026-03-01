import hashlib
from decimal import Decimal, ROUND_DOWN

from app.models.mines import MinesGame
from app.services.ledger_service import LedgerService


class MinesService:
    def __init__(self, ledger_service: LedgerService) -> None:
        self.ledger = ledger_service
        self.games: dict[str, MinesGame] = {}

    @staticmethod
    def _mine_positions(game_id: str, mines_count: int, board_size: int) -> set[int]:
        seed = hashlib.sha256(game_id.encode()).hexdigest()
        nums = [int(seed[i : i + 2], 16) % board_size for i in range(0, 64, 2)]
        out: set[int] = set()
        for n in nums:
            out.add(n)
            if len(out) == mines_count:
                break
        return out

    def create_game(self, request_id: str, game_id: str, user_id: str, account_id: str, wager: Decimal, mines_count: int, board_size: int) -> MinesGame:
        self.ledger.transfer(request_id, account_id, "platform", wager, f"mines:bet:{game_id}")
        game = MinesGame(game_id, user_id, account_id, wager, mines_count, board_size, [], False, Decimal("1.00"), False)
        self.games[game_id] = game
        return game

    def open_cell(self, game_id: str, cell_index: int) -> MinesGame:
        game = self.games[game_id]
        if game.settled:
            return game
        if cell_index not in game.opened_cells:
            game.opened_cells.append(cell_index)

        mines = self._mine_positions(game_id, game.mines_count, game.board_size)
        if cell_index in mines:
            game.hit_mine = True
            game.current_multiplier = Decimal("0")
            game.settled = True
        else:
            safe_opened = len(game.opened_cells)
            game.current_multiplier = (Decimal("1") + Decimal("0.15") * Decimal(safe_opened)).quantize(
                Decimal("0.0001"), rounding=ROUND_DOWN
            )
        return game

    def cashout(self, request_id: str, game_id: str) -> MinesGame:
        game = self.games[game_id]
        if game.settled:
            return game
        payout = (game.wager * game.current_multiplier).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        self.ledger.transfer(request_id, "platform", game.account_id, payout, f"mines:cashout:{game_id}")
        game.settled = True
        return game
