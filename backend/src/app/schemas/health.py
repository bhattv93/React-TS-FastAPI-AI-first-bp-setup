"""Schemas for the health and readiness endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness payload."""

    status: str
    version: str
    env: str


class ReadyResponse(BaseModel):
    """Readiness payload."""

    status: str
    database: str
