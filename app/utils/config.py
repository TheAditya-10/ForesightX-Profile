from shared import BaseServiceSettings


class ProfileServiceSettings(BaseServiceSettings):
    service_name: str = "foresightx-profile"
    port: int = 8002
    database_url: str = "postgresql+asyncpg://foresightx:foresightx@postgres:5432/foresightx"
    data_service_url: str = "http://data:8001"
    request_timeout_seconds: float = 8.0
    max_retries: int = 2
