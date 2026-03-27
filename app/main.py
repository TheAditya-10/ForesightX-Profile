from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache

from fastapi import FastAPI

from shared import ServiceHealth, build_async_client, configure_logging, get_logger

from app.db.session import check_database_connection, close_database, get_session_factory, seed_demo_data
from app.routers.profile import router as profile_router
from app.utils.config import ProfileServiceSettings


@lru_cache(maxsize=1)
def get_settings() -> ProfileServiceSettings:
    return ProfileServiceSettings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.service_name, settings.log_level)
    logger = get_logger(settings.service_name, "startup")

    session_factory = get_session_factory(settings.database_url)
    http_client = build_async_client(timeout=settings.request_timeout_seconds)
    await check_database_connection(settings.database_url)
    if settings.seed_demo_data:
        await seed_demo_data(settings=settings, session_factory=session_factory, http_client=http_client)

    app.state.settings = settings
    app.state.session_factory = session_factory
    app.state.http_client = http_client
    logger.info("Profile service startup complete")
    try:
        yield
    finally:
        await http_client.aclose()
        await close_database()
        logger.info("Profile service shutdown complete")


app = FastAPI(title="ForesightX Profile Service", version="0.1.0", lifespan=lifespan)
app.include_router(profile_router)


@app.get("/health", response_model=ServiceHealth)
async def healthcheck() -> ServiceHealth:
    settings = get_settings()
    return ServiceHealth(
        service=settings.service_name,
        status="ok",
        timestamp=datetime.now(timezone.utc),
    )
