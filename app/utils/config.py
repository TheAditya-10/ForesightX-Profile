from pathlib import Path

from pydantic import field_validator
from pydantic_settings import SettingsConfigDict

from shared import BaseServiceSettings, normalize_postgres_async_url


class ProfileServiceSettings(BaseServiceSettings):
    service_name: str = "foresightx-profile"
    port: int = 8002
    database_url: str = "postgresql://foresightx:foresightx@postgres:5432/foresightx"
    data_service_url: str = "http://data:8001"
    request_timeout_seconds: float = 8.0
    max_retries: int = 2
    seed_demo_data: bool = False
    aws_region: str = "us-east-1"
    aws_s3_bucket: str | None = None
    aws_s3_endpoint_url: str | None = None
    aws_s3_avatar_prefix: str = "avatars"
    aws_s3_signed_url_expires_seconds: int = 900
    avatar_max_bytes: int = 2 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        return normalize_postgres_async_url(value)
