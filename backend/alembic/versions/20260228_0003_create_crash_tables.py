"""create crash engine tables

Revision ID: 20260228_0003
Revises: 20260228_0002
Create Date: 2026-02-28
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260228_0003"
down_revision = "20260228_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crash_rounds",
        sa.Column("round_id", sa.String(length=64), primary_key=True),
        sa.Column("state", sa.String(length=24), nullable=False),
        sa.Column("crash_point", sa.Numeric(24, 8), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_crash_rounds_state", "crash_rounds", ["state"])

    op.create_table(
        "crash_bets",
        sa.Column("bet_id", sa.String(length=64), primary_key=True),
        sa.Column("round_id", sa.String(length=64), sa.ForeignKey("crash_rounds.round_id"), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.String(length=64), sa.ForeignKey("wallet_accounts.account_id"), nullable=False),
        sa.Column("amount", sa.Numeric(24, 8), nullable=False),
        sa.Column("auto_cashout_multiplier", sa.Numeric(24, 8), nullable=True),
        sa.Column("cashed_out_multiplier", sa.Numeric(24, 8), nullable=True),
        sa.Column("settled_payout", sa.Numeric(24, 8), nullable=False, server_default="0"),
        sa.Column("is_settled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_crash_bets_round", "crash_bets", ["round_id"])


def downgrade() -> None:
    op.drop_index("ix_crash_bets_round", table_name="crash_bets")
    op.drop_table("crash_bets")
    op.drop_index("ix_crash_rounds_state", table_name="crash_rounds")
    op.drop_table("crash_rounds")
