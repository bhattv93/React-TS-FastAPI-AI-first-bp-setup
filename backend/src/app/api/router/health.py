"""Liveness and readiness endpoints."""

import structlog
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.deps import SessionDep, SettingsDep
from app.core.errors import error_response
from app.schemas.health import HealthResponse, ReadyResponse

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDep) -> HealthResponse:
    """Report that the process is alive (no dependencies are checked).

    Parameters
    ----------
    settings : Settings
        Application settings.

    Returns
    -------
    HealthResponse
        Status, application version and environment name.
    """
    return HealthResponse(status="ok", version=settings.version, env=settings.env)


@router.get("/ready", response_model=ReadyResponse)
async def ready(session: SessionDep) -> ReadyResponse | JSONResponse:
    """Report whether the app can serve traffic (database reachable).

    Parameters
    ----------
    session : AsyncSession
        Database session for the connectivity probe.

    Returns
    -------
    ReadyResponse or JSONResponse
        ``ok`` when the database answers, otherwise a 503 error envelope.
    """
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("readiness_check_failed", error=type(exc).__name__)
        return error_response(503, "not_ready", "Database is not reachable")
    return ReadyResponse(status="ok", database="ok")
