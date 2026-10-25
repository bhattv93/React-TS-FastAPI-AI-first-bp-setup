"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create the async engine. No connection is opened until first use.

    Parameters
    ----------
    settings : Settings
        Application settings.

    Returns
    -------
    AsyncEngine
        The configured engine.
    """
    return create_async_engine(
        str(settings.database_url),
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=0 if settings.runtime == "lambda" else 10,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create the session factory bound to an engine.

    Parameters
    ----------
    engine : AsyncEngine
        The engine to bind sessions to.

    Returns
    -------
    async_sessionmaker[AsyncSession]
        A factory producing sessions that do not expire objects on commit.
    """
    return async_sessionmaker(engine, expire_on_commit=False)
