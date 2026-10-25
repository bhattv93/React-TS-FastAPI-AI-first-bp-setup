"""Application factory. Run with ``uvicorn --factory app.main:create_app``.

The factory form means importing this module never reads the environment, so
tests and tooling can import it freely.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import health
from app.api.routes import api_router
from app.core.config import Settings, get_settings
from app.core.db import create_engine, create_session_factory
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import REQUEST_ID_HEADER, RequestIdMiddleware

API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application.

    Parameters
    ----------
    settings : Settings, optional
        Settings to use. Defaults to the cached environment-based settings.

    Returns
    -------
    FastAPI
        The configured application.
    """
    settings = settings or get_settings()
    configure_logging(settings.log_level, json_logs=settings.env != "local")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Create the database engine on startup and dispose it on shutdown.

        Parameters
        ----------
        app : FastAPI
            The application whose state receives the engine and session factory.

        Yields
        ------
        None
            Control to the running application.
        """
        engine = create_engine(settings)
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(title="AI-First Backend", version=settings.version, lifespan=lifespan)
    app.dependency_overrides[get_settings] = lambda: settings
    app.add_middleware(RequestIdMiddleware)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=[REQUEST_ID_HEADER],
        )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=API_PREFIX)
    # Root-level probes for load balancers; kept out of the public OpenAPI schema.
    app.include_router(health.router, include_in_schema=False)
    return app
