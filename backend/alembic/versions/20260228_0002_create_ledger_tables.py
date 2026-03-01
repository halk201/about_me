"""create wallet and ledger tables

Revision ID: 20260228_0002
Revises: 20260228_0001
Create Date: 2026-02-28
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260228_0002"
down_revision = "20260228_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wallet_accounts",
        sa.Column("account_id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("account_type", sa.String(length=16), nullable=False),
        sa.Column("balance", sa.Numeric(24, 8), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_wallet_accounts_user_currency", "wallet_accounts", ["user_id", "currency"])

    op.create_table(
        "ledger_entries",
        sa.Column("entry_id", sa.String(length=128), primary_key=True),
        sa.Column("request_id", sa.String(length=128), nullable=False),
        sa.Column("account_id", sa.String(length=64), sa.ForeignKey("wallet_accounts.account_id"), nullable=False),
        sa.Column("amount", sa.Numeric(24, 8), nullable=False),
        sa.Column("entry_type", sa.String(length=16), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ledger_entries_account_created", "ledger_entries", ["account_id", "created_at"])
    op.create_index("ix_ledger_entries_request_id", "ledger_entries", ["request_id"])

    op.create_table(
        "idempotency_keys",
        sa.Column("request_id", sa.String(length=128), primary_key=True),
        sa.Column("route", sa.String(length=64), nullable=False),
        sa.Column("response_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("idempotency_keys")
    op.drop_index("ix_ledger_entries_request_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_account_created", table_name="ledger_entries")
    op.drop_table("ledger_entries")
    op.drop_index("ix_wallet_accounts_user_currency", table_name="wallet_accounts")
    op.drop_table("wallet_accounts")
