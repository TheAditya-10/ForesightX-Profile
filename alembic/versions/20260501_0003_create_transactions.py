"""create portfolio transactions table

Revision ID: 20260501_0003
Revises: 20260430_0002
Create Date: 2026-05-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260501_0003"
down_revision: str | None = "20260430_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "portfolio_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("action", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("realized_pnl", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_portfolio_transactions_user_id"), "portfolio_transactions", ["user_id"], unique=False)
    op.create_index(op.f("ix_portfolio_transactions_ticker"), "portfolio_transactions", ["ticker"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_portfolio_transactions_ticker"), table_name="portfolio_transactions")
    op.drop_index(op.f("ix_portfolio_transactions_user_id"), table_name="portfolio_transactions")
    op.drop_table("portfolio_transactions")
