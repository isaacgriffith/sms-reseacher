"""Async database session dependency for FastAPI routes."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from db.base import engine_factory, session_factory

_settings = get_settings()
_engine = engine_factory(_settings.database_url)
_session_maker = session_factory(_engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for use in FastAPI dependencies.

    Yields:
        An :class:`AsyncSession` that is closed after the request completes.
    """
    async with _session_maker() as session:
        yield session
