"""Typed application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Values come from ``APP_*`` environment variables, falling back to a local
    ``.env`` file. Missing or invalid values fail fast at startup.
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_", env_file=".env", extra="ignore"
    )

    env: Literal["local", "test", "dev", "staging", "prod"] = "local"
    version: str = "0.0.0-dev"
    database_url: PostgresDsn
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    runtime: Literal["uvicorn", "lambda"] = "uvicorn"
    cors_origins: list[str] = []
    secret_key: SecretStr

    @property
    def db_pool_size(self) -> int:
        """Return the connection pool size for the current runtime.

        Returns
        -------
        int
            ``1`` on Lambda (the pool is per execution environment and sits
            behind RDS Proxy), otherwise ``5``.
        """
        return 1 if self.runtime == "lambda" else 5


@lru_cache
def get_settings() -> Settings:
    """Return cached settings.

    Tests override this through ``app.dependency_overrides``.

    Returns
    -------
    Settings
        The process-wide settings instance.
    """
    return Settings()
