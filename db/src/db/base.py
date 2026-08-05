"""Declarative base and async engine factory for SMS Researcher."""

import enum
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    """Return the *values* of ``enum_cls`` for SQLAlchemy's ``values_callable``.

    By default ``sqlalchemy.Enum(SomePyEnum)`` persists member **names**
    (``ADMIN``), but every Alembic migration creates the PostgreSQL type from
    member **values** (``admin``) — and the REST API serialises ``.value`` too.
    Without this, any insert touching an enum column fails on PostgreSQL with
    ``invalid input value for enum ...``. SQLite hides the mismatch because it
    renders enums as VARCHAR + CHECK built from the same names it sends.

    Args:
        enum_cls: The Python enumeration backing the column.

    Returns:
        The member values, in declaration order.

    """
    return [member.value for member in enum_cls]


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


def engine_factory(database_url: str, *, echo: bool = False) -> AsyncEngine:
    """Create an async SQLAlchemy engine for the given URL.

    Args:
        database_url: SQLAlchemy-compatible async database URL.
        echo: When ``True``, log all SQL statements (development only).

    Examples:
                ``sqlite+aiosqlite:///./dev.db``
                ``postgresql+asyncpg://user:pass@host/db``

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
) -> AsyncGenerator[AsyncSession]:
    """Async context manager yielding a database session.

    Args:
        engine: The async engine to bind the session to.

    Yields:
        An :class:`AsyncSession` that is closed on exit.

    """
    factory = session_factory(engine)
    async with factory() as session:
        yield session
