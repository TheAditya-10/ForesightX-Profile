from __future__ import annotations

from app.utils.config import ProfileServiceSettings


def test_profile_settings_normalizes_postgres_url() -> None:
    settings = ProfileServiceSettings(database_url="postgresql://user:pass@host:5432/db")
    assert settings.database_url.startswith("postgresql+psycopg://")
