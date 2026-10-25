"""Shared fixtures for unit and integration tests."""

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test"


@pytest.fixture
def settings() -> Settings:
    """Return settings that never read a ``.env`` file or the real environment."""
    return Settings(
        _env_file=None,  # type: ignore[call-arg]
        env="test",
        database_url=TEST_DATABASE_URL,  # type: ignore[arg-type]
        secret_key="test-secret",  # type: ignore[arg-type]
    )


@pytest.fixture
async def app(settings: Settings) -> AsyncIterator[FastAPI]:
    """Return the application with its lifespan (engine) started."""
    application = create_app(settings)
    async with application.router.lifespan_context(application):
        yield application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Return an HTTP client wired to the application, without a network."""
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
