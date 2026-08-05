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

from backend.core.auth import hash_password
from db.models import Study, StudyType
from db.models.pico import PICOComponent, PICOVariant
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.study import StudyMember, StudyMemberRole
from db.models.users import GroupMembership, GroupRole, ResearchGroup, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

EMAIL = os.environ.get("E2E_USER_EMAIL", "testuser@example.com")
PASSWORD = os.environ.get("E2E_USER_PASSWORD", "testpassword")
DISPLAY_NAME = os.environ.get("E2E_USER_DISPLAY_NAME", "Test User")
GROUP_NAME = os.environ.get("E2E_GROUP_NAME", "E2E Test Group")
STUDY_NAME = os.environ.get("E2E_STUDY_NAME", "E2E Seed Study")

# The admin specs (e2e/admin/*.spec.ts) authenticate as a second account.
ADMIN_EMAIL = os.environ.get("E2E_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("E2E_ADMIN_PASSWORD", "adminpassword")
ADMIN_DISPLAY_NAME = os.environ.get("E2E_ADMIN_DISPLAY_NAME", "Admin User")


async def seed() -> None:
    """Create the e2e user, a research group, and an admin membership."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set", file=sys.stderr)
        raise SystemExit(1)

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def upsert_user(
        session: object, email: str, password: str, name: str
    ) -> User:
        """Return the user with *email*, creating it if absent."""
        existing = (
            await session.execute(select(User).where(User.email == email))  # type: ignore[attr-defined]
        ).scalar_one_or_none()
        if existing is not None:
            print(f"user {email} already exists (id={existing.id})")
            return existing
        created = User(
            email=email,
            hashed_password=hash_password(password),
            display_name=name,
        )
        session.add(created)  # type: ignore[attr-defined]
        await session.flush()  # type: ignore[attr-defined]
        print(f"created user {email} (id={created.id})")
        return created

    async with session_factory() as session:
        user = await upsert_user(session, EMAIL, PASSWORD, DISPLAY_NAME)
        admin = await upsert_user(
            session, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_DISPLAY_NAME
        )

        group = (
            await session.execute(
                select(ResearchGroup).where(ResearchGroup.name == GROUP_NAME)
            )
        ).scalar_one_or_none()
        if group is None:
            group = ResearchGroup(name=GROUP_NAME)
            session.add(group)
            await session.flush()
            print(f"created group {GROUP_NAME!r} (id={group.id})")

        for member in (user, admin):
            membership = (
                await session.execute(
                    select(GroupMembership).where(
                        GroupMembership.user_id == member.id,
                        GroupMembership.group_id == group.id,
                    )
                )
            ).scalar_one_or_none()
            if membership is None:
                session.add(
                    GroupMembership(
                        user_id=member.id, group_id=group.id, role=GroupRole.ADMIN
                    )
                )
                print(f"created admin membership for {member.email}")

        # e2e/{database-selection,screen-paper,search-papers,results-dashboard}
        # all default to E2E_STUDY_ID='1', so a study must exist. On a fresh
        # database this is the first row and therefore gets id 1.
        study = (
            await session.execute(select(Study).where(Study.name == STUDY_NAME))
        ).scalar_one_or_none()
        if study is None:
            study = Study(
                name=STUDY_NAME,
                topic="Automated testing in agile software projects",
                study_type=StudyType.SMS,
                research_group_id=group.id,
            )
            session.add(study)
            await session.flush()
            print(f"created study {STUDY_NAME!r} (id={study.id})")
        else:
            print(f"study {STUDY_NAME!r} already exists (id={study.id})")

        # GET /studies/{id} joins StudyMember and 404s without a row, so group
        # membership alone is not enough to open the study.
        for member in (user, admin):
            study_member = (
                await session.execute(
                    select(StudyMember).where(
                        StudyMember.study_id == study.id,
                        StudyMember.user_id == member.id,
                    )
                )
            ).scalar_one_or_none()
            if study_member is None:
                session.add(
                    StudyMember(
                        study_id=study.id,
                        user_id=member.id,
                        role=StudyMemberRole.LEAD,
                    )
                )
                print(f"created study membership for {member.email}")

        # Unlock phases 2 and 3 (see backend/services/phase_gate.py):
        #   phase 2 requires a PICOComponent
        #   phase 3 requires a COMPLETED SearchExecution
        # Without these the Search and Screening tabs never render, which is
        # what database-selection / search-papers / screen-paper wait on.
        pico = (
            await session.execute(
                select(PICOComponent).where(PICOComponent.study_id == study.id)
            )
        ).scalar_one_or_none()
        if pico is None:
            session.add(
                PICOComponent(
                    study_id=study.id,
                    variant=PICOVariant.PICO,
                    population="Agile software teams",
                    intervention="Automated testing practices",
                    comparison="Manual testing",
                    outcome="Defect detection rate",
                )
            )
            print("created PICO component (unlocks phase 2)")

        search_string = (
            await session.execute(
                select(SearchString).where(SearchString.study_id == study.id)
            )
        ).scalar_one_or_none()
        if search_string is None:
            search_string = SearchString(
                study_id=study.id,
                version=1,
                string_text='("agile" AND "automated testing")',
                is_active=True,
            )
            session.add(search_string)
            await session.flush()
            print(f"created search string (id={search_string.id})")

        execution = (
            await session.execute(
                select(SearchExecution).where(SearchExecution.study_id == study.id)
            )
        ).scalar_one_or_none()
        if execution is None:
            session.add(
                SearchExecution(
                    study_id=study.id,
                    search_string_id=search_string.id,
                    status=SearchExecutionStatus.COMPLETED,
                    phase_tag="initial-search",
                    databases_queried=["acm", "ieee"],
                )
            )
            print("created completed search execution (unlocks phase 3)")

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
