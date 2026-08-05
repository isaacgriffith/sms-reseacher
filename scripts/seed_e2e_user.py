"""Seed the minimum data the Playwright e2e suite needs to log in.

The e2e specs authenticate as ``E2E_USER_EMAIL`` / ``E2E_USER_PASSWORD``
(defaulting to ``testuser@example.com`` / ``testpassword``) and land on
``/groups``, so the user needs at least one group membership.

There is no registration endpoint, so this writes directly through the ORM.
Idempotent: re-running against an already-seeded database is a no-op.

Usage::

    DATABASE_URL=postgresql+asyncpg://... uv run python scripts/seed_e2e_user.py
"""

from __future__ import annotations

import asyncio
import os
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.core.auth import hash_password
from db.models.users import GroupMembership, GroupRole, ResearchGroup, User

EMAIL = os.environ.get("E2E_USER_EMAIL", "testuser@example.com")
PASSWORD = os.environ.get("E2E_USER_PASSWORD", "testpassword")
DISPLAY_NAME = os.environ.get("E2E_USER_DISPLAY_NAME", "Test User")
GROUP_NAME = os.environ.get("E2E_GROUP_NAME", "E2E Test Group")


async def seed() -> None:
    """Create the e2e user, a research group, and an admin membership."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set", file=sys.stderr)
        raise SystemExit(1)

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        user = (await session.execute(select(User).where(User.email == EMAIL))).scalar_one_or_none()
        if user is None:
            user = User(
                email=EMAIL,
                hashed_password=hash_password(PASSWORD),
                display_name=DISPLAY_NAME,
            )
            session.add(user)
            await session.flush()
            print(f"created user {EMAIL} (id={user.id})")
        else:
            print(f"user {EMAIL} already exists (id={user.id})")

        group = (
            await session.execute(select(ResearchGroup).where(ResearchGroup.name == GROUP_NAME))
        ).scalar_one_or_none()
        if group is None:
            group = ResearchGroup(name=GROUP_NAME)
            session.add(group)
            await session.flush()
            print(f"created group {GROUP_NAME!r} (id={group.id})")

        membership = (
            await session.execute(
                select(GroupMembership).where(
                    GroupMembership.user_id == user.id,
                    GroupMembership.group_id == group.id,
                )
            )
        ).scalar_one_or_none()
        if membership is None:
            session.add(GroupMembership(user_id=user.id, group_id=group.id, role=GroupRole.ADMIN))
            print("created admin membership")

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
