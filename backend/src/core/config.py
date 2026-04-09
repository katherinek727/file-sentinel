from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # PostgreSQL
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    pgport: int = 5432

    # Redis / Celery
    celery_broker_url: str = "redis://localhost:6379/0"

    # Storage
    storage_dir: str = "storage/files"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.pgport}/{self.postgres_db}"
        )

    @property
    def celery_result_backend(self) -> str:
        return self.celery_broker_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
