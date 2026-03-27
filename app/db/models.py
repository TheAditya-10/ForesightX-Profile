from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    # Cash is persisted on the user record because orchestration risk checks need liquid balance quickly.
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("10000.00"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    portfolio_positions: Mapped[list["PortfolioPosition"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions"
    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_portfolio_positions_user_ticker"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    avg_price: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="portfolio_positions")
