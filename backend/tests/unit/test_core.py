"""Database factory helpers, auth placeholder and model conventions."""

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session
from app.core.config import Settings
from app.core.db import create_engine, create_session_factory
from app.models import AppMeta, Base


async def test_engine_pool_depends_on_runtime(settings: Settings) -> None:
    engine = create_engine(settings)
    lambda_engine = create_engine(settings.model_copy(update={"runtime": "lambda"}))
    try:
        assert engine.pool.size() == 5  # type: ignore[attr-defined]
        assert lambda_engine.pool.size() == 1  # type: ignore[attr-defined]
    finally:
        await engine.dispose()
        await lambda_engine.dispose()


async def test_session_factory_builds_sessions(settings: Settings) -> None:
    engine = create_engine(settings)
    try:
        async with create_session_factory(engine)() as session:
            assert isinstance(session, AsyncSession)
    finally:
        await engine.dispose()


async def test_get_session_yields_from_app_state(app: FastAPI) -> None:
    class Request:
        pass

    request = Request()
    request.app = app  # type: ignore[attr-defined]
    generator = get_session(request)  # type: ignore[arg-type]
    session = await anext(generator)
    assert isinstance(session, AsyncSession)
    await generator.aclose()


async def test_current_user_is_a_placeholder() -> None:
    assert await get_current_user() is None


def test_models_follow_naming_convention() -> None:
    assert AppMeta.__tablename__ == "app_meta"
    assert Base.metadata.naming_convention["pk"] == "pk_%(table_name)s"
    assert {"key", "value", "created_at", "updated_at"} == set(
        AppMeta.__table__.columns.keys()
    )
