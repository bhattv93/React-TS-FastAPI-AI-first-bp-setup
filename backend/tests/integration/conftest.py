"""Fixtures that start a real PostgreSQL with Testcontainers.

The migrations in ``db/migrations`` are applied by executing the same SQL files that
Flyway runs in CI and on AWS, in version order.
"""

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import asyncpg
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

MIGRATIONS_DIR = Path(__file__).parents[2] / "db" / "migrations"


def _docker_available() -> bool:
    try:
        import docker  # pylint: disable=import-outside-toplevel

        docker.from_env().ping()
    except Exception:  # pylint: disable=broad-exception-caught
        return False
    return True


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    """Start Postgres once per test session and yield its asyncpg SQLAlchemy URL."""
    if not _docker_available():
        pytest.skip("Docker is not available; integration tests need Postgres")
    # Ryuk (the cleanup sidecar) cannot map its port on some Windows Docker setups;
    # the `with` block below already stops the container.
    os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")
    from testcontainers.community.postgres import (  # pylint: disable=import-outside-toplevel
        PostgresContainer,
    )

    with PostgresContainer("postgres:16-alpine", driver=None) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(5432)
        yield (
            f"postgresql+asyncpg://{container.username}:{container.password}"
            f"@{host}:{port}/{container.dbname}"
        )


@pytest.fixture(scope="session")
async def migrated_url(postgres_url: str) -> str:
    """Apply every ``V*.sql`` migration and return the database URL."""
    dsn = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
    connection = await asyncpg.connect(dsn)
    try:
        for migration in sorted(MIGRATIONS_DIR.glob("V*.sql")):
            await connection.execute(migration.read_text(encoding="utf-8"))
    finally:
        await connection.close()
    return postgres_url


@pytest.fixture
async def engine(migrated_url: str) -> AsyncIterator[AsyncEngine]:
    """Return an engine connected to the migrated database."""
    async_engine = create_async_engine(migrated_url)
    yield async_engine
    await async_engine.dispose()
