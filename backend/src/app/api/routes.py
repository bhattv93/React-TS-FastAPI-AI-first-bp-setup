"""Aggregates every router into the API router mounted at ``/api/v1``."""

from fastapi import APIRouter

from app.api.router import health

api_router = APIRouter()
api_router.include_router(health.router)
