"""create profile tables

Revision ID: 20260328_0001
Revises:
Create Date: 2026-03-28 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260328_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("cash_balance", sa.Numeric(precision=14, scale=2), nullable=False, server_default="10000.00"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "portfolio_positions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("avg_price", sa.Numeric(precision=14, scale=4), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "ticker", name="uq_portfolio_positions_user_ticker"),
    )
    op.create_index(op.f("ix_portfolio_positions_ticker"), "portfolio_positions", ["ticker"], unique=False)
    op.create_index(op.f("ix_portfolio_positions_user_id"), "portfolio_positions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_portfolio_positions_user_id"), table_name="portfolio_positions")
    op.drop_index(op.f("ix_portfolio_positions_ticker"), table_name="portfolio_positions")
    op.drop_table("portfolio_positions")
    op.drop_table("users")
