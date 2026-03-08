"""Declarative base and async engine factory for SMS Researcher."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


def engine_factory(database_url: str, *, echo: bool = False) -> AsyncEngine:
    """Create an async SQLAlchemy engine for the given URL.

    Args:
        database_url: SQLAlchemy-compatible async database URL.
            Examples:
                ``sqlite+aiosqlite:///./dev.db``
                ``postgresql+asyncpg://user:pass@host/db``
        echo: When ``True``, log all SQL statements (development only).

    Returns:
        A configured :class:`AsyncEngine` instance.
    """
    return create_async_engine(database_url, echo=echo)


def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Return a session maker bound to *engine*.

    Args:
        engine: The async engine returned by :func:`engine_factory`.

    Returns:
        An :class:`async_sessionmaker` producing :class:`AsyncSession` instances.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Async context manager yielding a database session.

    Args:
        engine: The async engine to bind the session to.

    Yields:
        An :class:`AsyncSession` that is closed on exit.
    """
    factory = session_factory(engine)
    async with factory() as session:
        yield session
