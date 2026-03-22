from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    # Cash is persisted on the user record because orchestration risk checks need liquid balance quickly.
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("10000.00"))

    portfolio_positions: Mapped[list["PortfolioPosition"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class PortfolioPosition(Base):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    avg_price: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=Decimal("0"))

    user: Mapped[User] = relationship(back_populates="portfolio_positions")
