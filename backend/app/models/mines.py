from dataclasses import dataclass
from decimal import Decimal


@dataclass
class MinesGame:
    game_id: str
    user_id: str
    account_id: str
    wager: Decimal
    mines_count: int
    board_size: int
    opened_cells: list[int]
    hit_mine: bool
    current_multiplier: Decimal
    settled: bool
