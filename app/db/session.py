from decimal import Decimal
from functools import lru_cache

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from shared import get_logger, request_json

from app.db.base import Base
from app.db.models import PortfolioPosition, User
from app.utils.config import ProfileServiceSettings


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_async_engine(database_url, future=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _session_factory


async def initialize_database(
    settings: ProfileServiceSettings,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    logger = get_logger(settings.service_name, "db-init")
    if _engine is None:
        raise RuntimeError("Database engine not initialized")
    async with _engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    logger.info("Database schema ensured")


async def seed_demo_data(
    settings: ProfileServiceSettings,
    session_factory: async_sessionmaker[AsyncSession],
    http_client: httpx.AsyncClient,
) -> None:
    logger = get_logger(settings.service_name, "db-seed")
    async with session_factory() as session:
        existing = await session.scalar(select(User.id).limit(1))
        if existing:
            return

        users = [
            User(id="demo-user", name="Ava Patel", risk_level="medium", cash_balance=Decimal("15000.00")),
            User(id="growth-user", name="Marcus Lee", risk_level="high", cash_balance=Decimal("25000.00")),
            User(id="defensive-user", name="Nina Shah", risk_level="low", cash_balance=Decimal("18000.00")),
        ]
        session.add_all(users)
        await session.flush()

        positions = [
            PortfolioPosition(user_id="demo-user", ticker="AAPL", quantity=18, avg_price=Decimal("182.50")),
            PortfolioPosition(user_id="demo-user", ticker="NVDA", quantity=10, avg_price=Decimal("710.00")),
            PortfolioPosition(user_id="growth-user", ticker="NVDA", quantity=16, avg_price=Decimal("690.00")),
            PortfolioPosition(user_id="defensive-user", ticker="AAPL", quantity=24, avg_price=Decimal("175.00")),
        ]
        session.add_all(positions)
        await session.commit()

    logger.info("Seeded demo profile data")

    try:
        await request_json(
            client=http_client,
            method="GET",
            url=f"{settings.data_service_url.rstrip('/')}/health",
            logger=logger,
            retries=0,
        )
    except Exception:
        logger.warning("Data service unavailable during seed verification")


async def get_user_with_positions(session: AsyncSession, user_id: str) -> User | None:
    result = await session.execute(
        select(User)
        .options(selectinload(User.portfolio_positions))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def close_database() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
