"""create dice mines plinko tables

Revision ID: 20260228_0004
Revises: 20260228_0003
Create Date: 2026-02-28
"""

from alembic import op
import sqlalchemy as sa

revision = "20260228_0004"
down_revision = "20260228_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dice_bets",
        sa.Column("bet_id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Numeric(24, 8), nullable=False),
        sa.Column("target", sa.Numeric(8, 4), nullable=False),
        sa.Column("roll", sa.Numeric(8, 4), nullable=False),
        sa.Column("payout_amount", sa.Numeric(24, 8), nullable=False),
    )
    op.create_table(
        "mines_games",
        sa.Column("game_id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("wager", sa.Numeric(24, 8), nullable=False),
        sa.Column("mines_count", sa.Integer(), nullable=False),
        sa.Column("board_size", sa.Integer(), nullable=False),
        sa.Column("opened_cells", sa.JSON(), nullable=False),
        sa.Column("hit_mine", sa.Boolean(), nullable=False),
        sa.Column("current_multiplier", sa.Numeric(12, 4), nullable=False),
        sa.Column("settled", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "plinko_drops",
        sa.Column("drop_id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("wager", sa.Numeric(24, 8), nullable=False),
        sa.Column("risk", sa.String(length=16), nullable=False),
        sa.Column("rows", sa.Integer(), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("multiplier", sa.Numeric(12, 4), nullable=False),
        sa.Column("payout", sa.Numeric(24, 8), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("plinko_drops")
    op.drop_table("mines_games")
    op.drop_table("dice_bets")
