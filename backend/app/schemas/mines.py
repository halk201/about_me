from decimal import Decimal

from pydantic import BaseModel, Field


class MinesCreateGameRequest(BaseModel):
    request_id: str = Field(min_length=6)
    game_id: str
    user_id: str
    account_id: str
    wager: Decimal = Field(gt=0)
    mines_count: int = Field(ge=1, le=24)
    board_size: int = Field(default=25, ge=9, le=25)


class MinesOpenCellRequest(BaseModel):
    game_id: str
    cell_index: int = Field(ge=0, le=24)


class MinesCashoutRequest(BaseModel):
    request_id: str = Field(min_length=6)
    game_id: str


class MinesGameResponse(BaseModel):
    game_id: str
    opened_cells: list[int]
    hit_mine: bool
    current_multiplier: Decimal
    settled: bool
