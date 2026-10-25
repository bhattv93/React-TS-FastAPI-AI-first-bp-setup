"""FastAPI dependencies shared by all routers."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield a database session bound to the request.

    Parameters
    ----------
    request : Request
        The current request; the session factory lives on ``app.state``.

    Yields
    ------
    AsyncSession
        A session that is closed when the request finishes.
    """
    async with request.app.state.session_factory() as session:
        yield session


async def get_current_user() -> None:
    """Placeholder for authentication.

    Replace the body with real token validation (for example Cognito/OIDC) and
    return a typed user model. Routers already depend on this function, so
    adding auth does not change their signatures. Until an auth provider is
    integrated it always returns ``None``.
    """
    return None


SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[None, Depends(get_current_user)]
