"""Shared fixtures for backend integration tests."""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.core.auth import hash_password
from backend.core.database import get_db
from backend.main import create_app
from db.base import Base

# Side-effect imports: register all ORM table definitions on Base.metadata before
# create_all is called. Ordering ensures FK targets are defined before referencing tables.
import db.models  # noqa: F401
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.pico  # noqa: F401
import db.models.seeds  # noqa: F401
import db.models.criteria  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.jobs  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.audit  # noqa: F401
import db.models.extraction  # noqa: F401
import db.models.results  # noqa: F401

from db.models.users import GroupMembership, GroupRole, ResearchGroup, User


@pytest_asyncio.fixture
async def db_engine():
    """Provide a per-test in-memory SQLite engine with all tables created.

    Uses ``StaticPool`` so every SQLAlchemy session shares the same underlying
    connection, which is required for SQLite in-memory databases to persist
    data across sessions within a single test.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_engine):
    """Return an httpx AsyncClient backed by the test FastAPI app.

    The ``get_db`` dependency is overridden to use the per-test in-memory
    SQLite database so no external infrastructure is required.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)

    async def _override_get_db():
        async with maker() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def _insert_user(
    db_engine,
    *,
    email: str,
    display_name: str,
    plain_password: str = "password123",
) -> tuple[User, str]:
    """Insert a user row and return (user, plain_password).

    Args:
        db_engine: The async engine to insert into.
        email: The user's email address.
        display_name: The user's display name.
        plain_password: Plaintext password; bcrypt-hashed before insertion.

    Returns:
        A tuple of the persisted :class:`User` ORM object and the plain password.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        user = User(
            email=email,
            hashed_password=hash_password(plain_password),
            display_name=display_name,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user, plain_password


@pytest_asyncio.fixture
async def alice(db_engine) -> tuple[User, str]:
    """Return (alice_user, plain_password) after inserting alice into the test DB."""
    return await _insert_user(db_engine, email="alice@example.com", display_name="Alice")


@pytest_asyncio.fixture
async def bob(db_engine) -> tuple[User, str]:
    """Return (bob_user, plain_password) after inserting bob into the test DB."""
    return await _insert_user(db_engine, email="bob@example.com", display_name="Bob")
