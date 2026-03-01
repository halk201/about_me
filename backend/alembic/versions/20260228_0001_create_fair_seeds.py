"""create fair_seeds table

Revision ID: 20260228_0001
Revises:
Create Date: 2026-02-28
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260228_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fair_seeds",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("game", sa.String(length=32), nullable=False),
        sa.Column("round_id", sa.String(length=64), nullable=False),
        sa.Column("server_seed_hash", sa.String(length=64), nullable=False),
        sa.Column("encrypted_server_seed", sa.Text(), nullable=False),
        sa.Column("revealed_server_seed", sa.Text(), nullable=True),
        sa.Column("client_seed", sa.String(length=255), nullable=False),
        sa.Column("nonce", sa.BigInteger(), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False, server_default="COMMITTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("revealed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("game", "round_id", name="uq_fair_seeds_game_round"),
    )
    op.create_index("ix_fair_seeds_game_state", "fair_seeds", ["game", "state"])


def downgrade() -> None:
    op.drop_index("ix_fair_seeds_game_state", table_name="fair_seeds")
    op.drop_table("fair_seeds")
