"""add profile details

Revision ID: 20260430_0002
Revises: 20260328_0001
Create Date: 2026-04-30 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260430_0002"
down_revision: str | None = "20260328_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("pan", sa.String(length=16), nullable=True))
    op.add_column("users", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("photo", sa.String(length=4096), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "photo")
    op.drop_column("users", "city")
    op.drop_column("users", "pan")
    op.drop_column("users", "phone")
    op.drop_column("users", "email")
