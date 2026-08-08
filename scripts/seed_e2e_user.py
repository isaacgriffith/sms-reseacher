"""Seed the data the Playwright e2e suite needs.

The e2e specs authenticate as ``E2E_USER_EMAIL`` / ``E2E_USER_PASSWORD``
(defaulting to ``testuser@example.com`` / ``testpassword``) and land on
``/groups``, so the user needs at least one group membership.

There is no registration endpoint, so this writes directly through the ORM.
Idempotent: re-running against an already-seeded database is a no-op.

Fixtures, and the journey each one exists for:

===========================  =================================================
Fixture                      Needed by
===========================  =================================================
Users, group, memberships    Every spec — logging in and reaching ``/groups``
``E2E Seed Study`` (SMS)     ``database-selection``, ``search-papers``,
                             ``screen-paper``, ``results-dashboard``
  - 3 pending candidates     ``screen-paper`` — accept/reject controls only
                             render for a queue holding pending papers
  - 2 accepted + extraction  T004 — phases 4 and 5 (extraction, validity,
                             quality report) have data to display
  - 1 conflicted candidate   T005 — the disagreement path in the reviewer panel
``E2E Tertiary Study``       T003 — the Tertiary workspace has something to open
``E2E Source Mapping Study`` T006 — Tertiary seed import has a source to offer
===========================  =================================================

Usage::

    DATABASE_URL=postgresql+asyncpg://... uv run python scripts/seed_e2e_user.py
"""

from __future__ import annotations

import asyncio
import os
import sys

from backend.core.auth import hash_password
from backend.core.encryption import encrypt_secret
from db.models import Paper, Study, StudyType
from db.models.candidate import (
    CandidatePaper,
    CandidatePaperStatus,
    PaperDecision,
    PaperDecisionType,
)
from db.models.extraction import DataExtraction, ExtractionStatus, ResearchType
from db.models.pico import PICOComponent, PICOVariant
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.study import Reviewer, ReviewerType, StudyMember, StudyMemberRole
from db.models.users import GroupMembership, GroupRole, ResearchGroup, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

EMAIL = os.environ.get("E2E_USER_EMAIL", "testuser@example.com")
PASSWORD = os.environ.get("E2E_USER_PASSWORD", "testpassword")
DISPLAY_NAME = os.environ.get("E2E_USER_DISPLAY_NAME", "Test User")
GROUP_NAME = os.environ.get("E2E_GROUP_NAME", "E2E Test Group")
STUDY_NAME = os.environ.get("E2E_STUDY_NAME", "E2E Seed Study")

# The admin specs (e2e/admin/*.spec.ts) authenticate as a second account.
ADMIN_EMAIL = os.environ.get("E2E_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("E2E_ADMIN_PASSWORD", "adminpassword")
ADMIN_DISPLAY_NAME = os.environ.get("E2E_ADMIN_DISPLAY_NAME", "Admin User")

# e2e/two-factor-auth.spec.ts logs in as a TOTP-enabled account to exercise the
# second-step prompt and the five-failure lockout. Neither test needs a *valid*
# code, so a fixed dummy secret is enough — no authenticator app required.
TOTP_EMAIL = os.environ.get("E2E_TOTP_EMAIL", "totpuser@example.com")
TOTP_PASSWORD = os.environ.get("E2E_TOTP_PASSWORD", "testpassword")
TOTP_DISPLAY_NAME = os.environ.get("E2E_TOTP_DISPLAY_NAME", "TOTP User")
# The lockout spec deliberately locks its account, and a locked account is
# refused at the password step too — so it gets its own user rather than
# poisoning the prompt spec when the two run in either order.
TOTP_LOCKOUT_EMAIL = os.environ.get("E2E_TOTP_LOCKOUT_EMAIL", "totplockout@example.com")
#: Base32, valid for pyotp — never used to produce a code in the e2e flow.
TOTP_SECRET = "JBSWY3DPEHPK3PXP"

# Feature 012 fixtures.
TERTIARY_STUDY_NAME = os.environ.get(
    "E2E_TERTIARY_STUDY_NAME", "E2E Tertiary Seed Study"
)
SOURCE_STUDY_NAME = os.environ.get("E2E_SOURCE_STUDY_NAME", "E2E Source Mapping Study")

#: Papers seeded into the screening queue so the accept/reject controls render.
SEED_PAPERS = [
    ("Continuous integration practices in agile teams", "10.1000/e2e-seed-1"),
    ("A survey of automated regression testing", "10.1000/e2e-seed-2"),
    ("Mutation testing adoption in industry", "10.1000/e2e-seed-3"),
]

#: T004 — accepted papers on the main study, so extraction and the quality
#: report have rows to display. Kept distinct from SEED_PAPERS: flipping those
#: to accepted would empty the pending queue that screen-paper.spec.ts needs.
ACCEPTED_PAPERS = [
    ("Test automation maturity: a controlled experiment", "10.1000/e2e-accepted-1"),
    ("Flaky test detection in continuous integration", "10.1000/e2e-accepted-2"),
]

#: T005 — one candidate carrying two disagreeing human decisions.
CONFLICT_PAPER = (
    "Pair programming and defect density: a replication",
    "10.1000/e2e-conflict-1",
)

#: T006 — accepted papers on the second study, which is what makes it a usable
#: seed-import source. ``TertiaryExtractionService.import_seed_study`` raises
#: ValueError when the source study holds no accepted papers.
SOURCE_PAPERS = [
    ("A systematic mapping of DevOps adoption", "10.1000/e2e-source-1"),
    ("Microservice migration patterns: a review", "10.1000/e2e-source-2"),
]


# ---------------------------------------------------------------------------
# Idempotent building blocks
#
# Every helper follows the same contract: look the row up by its natural key,
# return it if present, otherwise create and flush it. That is what makes the
# whole script re-runnable, which the e2e workflow depends on — the suite is
# run repeatedly against a database it also writes to.
# ---------------------------------------------------------------------------


async def _upsert_user(
    session: AsyncSession, email: str, password: str, name: str
) -> User:
    """Return the user with *email*, creating it if absent.

    Args:
        session: Active async session.
        email: Address to look the user up by.
        password: Plaintext password, hashed on creation.
        name: Display name used when creating.

    Returns:
        The existing or newly created user.

    """
    existing = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if existing is not None:
        print(f"user {email} already exists (id={existing.id})")
        return existing
    created = User(
        email=email, hashed_password=hash_password(password), display_name=name
    )
    session.add(created)
    await session.flush()
    print(f"created user {email} (id={created.id})")
    return created


async def _ensure_group(session: AsyncSession, name: str) -> ResearchGroup:
    """Return the research group named *name*, creating it if absent.

    Args:
        session: Active async session.
        name: Group name to look up.

    Returns:
        The existing or newly created group.

    """
    group = (
        await session.execute(select(ResearchGroup).where(ResearchGroup.name == name))
    ).scalar_one_or_none()
    if group is None:
        group = ResearchGroup(name=name)
        session.add(group)
        await session.flush()
        print(f"created group {name!r} (id={group.id})")
    return group


async def _ensure_group_membership(
    session: AsyncSession, user: User, group: ResearchGroup
) -> None:
    """Give *user* admin membership of *group* if they do not already have it.

    Args:
        session: Active async session.
        user: The user to add.
        group: The group to add them to.

    """
    existing = (
        await session.execute(
            select(GroupMembership).where(
                GroupMembership.user_id == user.id,
                GroupMembership.group_id == group.id,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        session.add(
            GroupMembership(user_id=user.id, group_id=group.id, role=GroupRole.ADMIN)
        )
        print(f"created admin membership for {user.email}")


async def _ensure_study(
    session: AsyncSession,
    *,
    name: str,
    topic: str,
    study_type: StudyType,
    group: ResearchGroup,
) -> Study:
    """Return the study named *name*, creating it in *group* if absent.

    Args:
        session: Active async session.
        name: Study name, used as the natural key.
        topic: Study topic text.
        study_type: SMS, SLR, Rapid, or Tertiary.
        group: Owning research group.

    Returns:
        The existing or newly created study.

    """
    study = (
        await session.execute(select(Study).where(Study.name == name))
    ).scalar_one_or_none()
    if study is not None:
        print(f"study {name!r} already exists (id={study.id})")
        return study
    study = Study(
        name=name, topic=topic, study_type=study_type, research_group_id=group.id
    )
    session.add(study)
    await session.flush()
    print(f"created {study_type.value} study {name!r} (id={study.id})")
    return study


async def _ensure_study_members(
    session: AsyncSession, study: Study, users: list[User]
) -> None:
    """Add every user in *users* to *study* as a lead, if not already a member.

    ``GET /studies/{id}`` joins ``StudyMember`` and 404s without a row, so group
    membership alone is not enough to open a study.

    Args:
        session: Active async session.
        study: The study to grant membership on.
        users: Users to add.

    """
    for user in users:
        existing = (
            await session.execute(
                select(StudyMember).where(
                    StudyMember.study_id == study.id,
                    StudyMember.user_id == user.id,
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(
                StudyMember(
                    study_id=study.id, user_id=user.id, role=StudyMemberRole.LEAD
                )
            )
            print(f"created study membership for {user.email} on study {study.id}")


async def _ensure_paper(session: AsyncSession, title: str, doi: str) -> Paper:
    """Return the paper with *doi*, creating it if absent.

    ``Paper`` is a globally shared bibliographic record keyed on DOI, so two
    studies citing the same work reference one row.

    Args:
        session: Active async session.
        title: Paper title, used when creating.
        doi: DOI, the natural key.

    Returns:
        The existing or newly created paper.

    """
    paper = (
        await session.execute(select(Paper).where(Paper.doi == doi))
    ).scalar_one_or_none()
    if paper is None:
        paper = Paper(
            title=title,
            doi=doi,
            abstract=f"Seed abstract for {title}.",
            year=2024,
            venue="E2E Proceedings",
        )
        session.add(paper)
        await session.flush()
    return paper


async def _ensure_search_execution(
    session: AsyncSession, study: Study, query_text: str
) -> SearchExecution:
    """Return a completed search execution for *study*, creating one if absent.

    A completed execution is what unlocks phase 3 for a mapping study, and its
    id is the ``search_execution_id`` every candidate paper needs.

    Args:
        session: Active async session.
        study: The study to attach the execution to.
        query_text: Search string text stored alongside it.

    Returns:
        The existing or newly created execution.

    """
    search_string = (
        await session.execute(
            select(SearchString).where(SearchString.study_id == study.id)
        )
    ).scalar_one_or_none()
    if search_string is None:
        search_string = SearchString(
            study_id=study.id, version=1, string_text=query_text, is_active=True
        )
        session.add(search_string)
        await session.flush()
        print(f"created search string for study {study.id} (id={search_string.id})")

    execution = (
        await session.execute(
            select(SearchExecution).where(SearchExecution.study_id == study.id)
        )
    ).scalar_one_or_none()
    if execution is None:
        execution = SearchExecution(
            study_id=study.id,
            search_string_id=search_string.id,
            status=SearchExecutionStatus.COMPLETED,
            phase_tag="initial-search",
            databases_queried=["acm", "ieee"],
        )
        session.add(execution)
        await session.flush()
        print(
            f"created completed search execution for study {study.id} (unlocks phase 3)"
        )
    return execution


async def _ensure_candidate(
    session: AsyncSession,
    study: Study,
    paper: Paper,
    execution: SearchExecution,
    status: CandidatePaperStatus,
) -> CandidatePaper:
    """Return the candidate joining *study* and *paper*, creating it if absent.

    Constructed with ``paper=`` rather than ``paper_id=`` so the composed
    bibliographic record is populated without a lazy load — see TREF7.

    Args:
        session: Active async session.
        study: Owning study.
        paper: The bibliographic record referenced.
        execution: Search execution the candidate is attributed to.
        status: Screening status to create it with.

    Returns:
        The existing or newly created candidate.

    """
    candidate = (
        await session.execute(
            select(CandidatePaper).where(
                CandidatePaper.study_id == study.id,
                CandidatePaper.paper_id == paper.id,
            )
        )
    ).scalar_one_or_none()
    if candidate is None:
        candidate = CandidatePaper(
            study_id=study.id,
            paper=paper,
            search_execution_id=execution.id,
            phase_tag="initial-search",
            current_status=status,
        )
        session.add(candidate)
        await session.flush()
        print(f"created {status.value} candidate {paper.doi} on study {study.id}")
    return candidate


async def _ensure_human_reviewer(
    session: AsyncSession, study: Study, user: User
) -> Reviewer:
    """Return *user*'s human reviewer slot on *study*, creating it if absent.

    Args:
        session: Active async session.
        study: The study the reviewer belongs to.
        user: The human behind the reviewer slot.

    Returns:
        The existing or newly created reviewer.

    """
    reviewer = (
        await session.execute(
            select(Reviewer).where(
                Reviewer.study_id == study.id,
                Reviewer.user_id == user.id,
                Reviewer.reviewer_type == ReviewerType.HUMAN,
            )
        )
    ).scalar_one_or_none()
    if reviewer is None:
        reviewer = Reviewer(
            study_id=study.id, reviewer_type=ReviewerType.HUMAN, user_id=user.id
        )
        session.add(reviewer)
        await session.flush()
        print(f"created human reviewer for {user.email} on study {study.id}")
    return reviewer


async def _ensure_pico(session: AsyncSession, study: Study) -> None:
    """Give *study* a PICO component if it has none, unlocking phase 2.

    Args:
        session: Active async session.
        study: The study to scaffold.

    """
    existing = (
        await session.execute(
            select(PICOComponent).where(PICOComponent.study_id == study.id)
        )
    ).scalar_one_or_none()
    if existing is None:
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
        print(f"created PICO component for study {study.id} (unlocks phase 2)")


# ---------------------------------------------------------------------------
# Feature 012 fixtures (T003–T006)
# ---------------------------------------------------------------------------


async def _seed_extraction_fixture(
    session: AsyncSession, study: Study, execution: SearchExecution
) -> None:
    """T004 — accepted papers plus one extraction record, so US3 has data.

    These are *additional* papers, not a re-status of ``SEED_PAPERS``: the
    screening specs need the queue to still hold pending papers, so the two
    fixtures have to coexist rather than one overwriting the other.

    One extraction is what the extraction form and quality report render. It
    also unlocks phases 4 and 5 — though see **TFIX1** in tasks.md: the gate
    query filters on status but not study, so today this unlocks those phases
    for every mapping study, not only this one.

    Args:
        session: Active async session.
        study: The mapping study to attach the fixture to.
        execution: Search execution the candidates are attributed to.

    """
    for index, (title, doi) in enumerate(ACCEPTED_PAPERS):
        paper = await _ensure_paper(session, title, doi)
        candidate = await _ensure_candidate(
            session, study, paper, execution, CandidatePaperStatus.ACCEPTED
        )

        # Only the first accepted paper gets an extraction: the second is left
        # bare on purpose, so the extraction view has both a populated row and
        # an empty one to render.
        if index != 0:
            continue

        existing = (
            await session.execute(
                select(DataExtraction).where(
                    DataExtraction.candidate_paper_id == candidate.id
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(
                DataExtraction(
                    candidate_paper_id=candidate.id,
                    research_type=ResearchType.EVALUATION,
                    venue_type="conference",
                    venue_name="E2E Proceedings",
                    summary=(
                        "A controlled experiment comparing test automation maturity "
                        "levels across twelve industrial teams."
                    ),
                    keywords=["test automation", "maturity", "controlled experiment"],
                    open_codings=["automation maturity", "team capability"],
                    extraction_status=ExtractionStatus.AI_COMPLETE,
                    extracted_by_agent="extractor",
                )
            )
            print(
                f"created extraction for candidate {candidate.id} (unlocks phases 4 and 5)"
            )


async def _seed_conflict_fixture(
    session: AsyncSession,
    study: Study,
    execution: SearchExecution,
    reviewer_a: User,
    reviewer_b: User,
) -> None:
    """T005 — one candidate carrying two disagreeing human decisions.

    Conflict detection in ``POST /papers/{id}/decisions`` counts **human**
    decisions only and flags a conflict when their outcomes differ, so both
    reviewers here are human. An AI decision against a human one would leave
    ``conflict_flag`` false however much the two disagree.

    The end state mirrors what the endpoint itself produces: the later decision
    sets ``current_status``, and ``conflict_flag`` records the disagreement.

    Args:
        session: Active async session.
        study: The study the conflicted candidate belongs to.
        execution: Search execution the candidate is attributed to.
        reviewer_a: The human who accepts.
        reviewer_b: The human who rejects.

    """
    title, doi = CONFLICT_PAPER
    paper = await _ensure_paper(session, title, doi)
    candidate = await _ensure_candidate(
        session, study, paper, execution, CandidatePaperStatus.REJECTED
    )

    already_judged = (
        (
            await session.execute(
                select(PaperDecision).where(
                    PaperDecision.candidate_paper_id == candidate.id
                )
            )
        )
        .scalars()
        .first()
    )
    if already_judged is not None:
        return

    accepting = await _ensure_human_reviewer(session, study, reviewer_a)
    rejecting = await _ensure_human_reviewer(session, study, reviewer_b)

    session.add(
        PaperDecision(
            candidate_paper_id=candidate.id,
            reviewer_id=accepting.id,
            decision=PaperDecisionType.ACCEPTED,
            reasons=["Reports empirical defect-density data"],
        )
    )
    session.add(
        PaperDecision(
            candidate_paper_id=candidate.id,
            reviewer_id=rejecting.id,
            decision=PaperDecisionType.REJECTED,
            reasons=["Replication lacks a control group"],
        )
    )
    candidate.conflict_flag = True
    print(
        f"created two disagreeing decisions on candidate {candidate.id} (conflict_flag set)"
    )


async def _seed_tertiary_study(
    session: AsyncSession, group: ResearchGroup, members: list[User]
) -> Study:
    """T003 — a Tertiary study, so the Tertiary workspace has something to open.

    Deliberately left without a protocol row. Phase 1 is always unlocked for a
    Tertiary study, and phase 2 unlocks on a *validated* ``TertiaryStudyProtocol``
    — which the US2 journey drives through the UI. Seeding a validated protocol
    would skip past the first step of the very workflow the e2e is meant to
    exercise.

    Args:
        session: Active async session.
        group: Owning research group.
        members: Users granted study membership.

    Returns:
        The Tertiary study.

    """
    study = await _ensure_study(
        session,
        name=TERTIARY_STUDY_NAME,
        topic="A tertiary review of secondary studies in software testing",
        study_type=StudyType.TERTIARY,
        group=group,
    )
    await _ensure_study_members(session, study, members)
    return study


async def _seed_seed_import_source(
    session: AsyncSession, group: ResearchGroup, members: list[User]
) -> Study:
    """T006 — a second group study holding accepted papers, as an import source.

    Two conditions make a study offerable to the Tertiary seed-import dialog,
    and both are load-bearing:

    - ``SeedImportPanel`` filters the group's studies to SMS / SLR / Rapid, so
      the source cannot itself be Tertiary.
    - ``TertiaryExtractionService.import_seed_study`` raises ``ValueError`` when
      the source holds no **accepted** papers, so a study with only pending
      candidates would list but fail on import.

    Args:
        session: Active async session.
        group: Owning research group.
        members: Users granted study membership.

    Returns:
        The source mapping study.

    """
    study = await _ensure_study(
        session,
        name=SOURCE_STUDY_NAME,
        topic="Secondary studies of DevOps and microservice adoption",
        study_type=StudyType.SMS,
        group=group,
    )
    await _ensure_study_members(session, study, members)
    execution = await _ensure_search_execution(
        session, study, '("devops" OR "microservices") AND "systematic mapping"'
    )
    for title, doi in SOURCE_PAPERS:
        paper = await _ensure_paper(session, title, doi)
        await _ensure_candidate(
            session, study, paper, execution, CandidatePaperStatus.ACCEPTED
        )
    return study


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def _seed_accounts(session: AsyncSession) -> tuple[User, User]:
    """Create the four e2e accounts and return the primary and admin users.

    Args:
        session: Active async session.

    Returns:
        The primary test user and the admin user.

    """
    user = await _upsert_user(session, EMAIL, PASSWORD, DISPLAY_NAME)
    admin = await _upsert_user(session, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_DISPLAY_NAME)

    # Two more accounts with 2FA switched on. Kept separate from the main test
    # user so every other spec can still log in with a password alone.
    for totp_email in (TOTP_EMAIL, TOTP_LOCKOUT_EMAIL):
        totp_user = await _upsert_user(
            session, totp_email, TOTP_PASSWORD, TOTP_DISPLAY_NAME
        )
        if not totp_user.totp_enabled:
            totp_user.totp_enabled = True
            totp_user.totp_secret_encrypted = encrypt_secret(TOTP_SECRET)
            print(f"enabled 2FA for {totp_email}")
        # Always clear the counters: the lockout spec deliberately fails five
        # times, so a re-run would otherwise start already locked out.
        totp_user.totp_failed_attempts = 0
        totp_user.totp_locked_until = None

    return user, admin


async def _seed_main_study(
    session: AsyncSession, group: ResearchGroup, members: list[User]
) -> Study:
    """Create the primary SMS study every existing spec points at.

    ``e2e/{database-selection,screen-paper,search-papers,results-dashboard}``
    all default to ``E2E_STUDY_ID='1'``, so this must exist. On a fresh database
    it is the first row and therefore gets id 1.

    Args:
        session: Active async session.
        group: Owning research group.
        members: Users granted study membership.

    Returns:
        The primary mapping study.

    """
    study = await _ensure_study(
        session,
        name=STUDY_NAME,
        topic="Automated testing in agile software projects",
        study_type=StudyType.SMS,
        group=group,
    )
    await _ensure_study_members(session, study, members)
    await _ensure_pico(session, study)
    execution = await _ensure_search_execution(
        session, study, '("agile" AND "automated testing")'
    )

    # Screening (phase 3) renders accept/reject controls only when the queue has
    # PENDING papers; without these the screen-paper specs skip instead of
    # asserting anything.
    for title, doi in SEED_PAPERS:
        paper = await _ensure_paper(session, title, doi)
        await _ensure_candidate(
            session, study, paper, execution, CandidatePaperStatus.PENDING
        )

    await _seed_extraction_fixture(session, study, execution)
    await _seed_conflict_fixture(session, study, execution, members[0], members[1])
    return study


async def seed() -> None:
    """Create every account, group, study, and fixture the e2e suite needs."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set", file=sys.stderr)
        raise SystemExit(1)

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        user, admin = await _seed_accounts(session)
        members = [user, admin]

        group = await _ensure_group(session, GROUP_NAME)
        for member in members:
            await _ensure_group_membership(session, member, group)

        main_study = await _seed_main_study(session, group, members)
        tertiary_study = await _seed_tertiary_study(session, group, members)
        source_study = await _seed_seed_import_source(session, group, members)

        await session.commit()

        print("\nseeded ids — export these for the e2e specs:")
        print(f"  E2E_GROUP_ID={group.id}")
        print(f"  E2E_STUDY_ID={main_study.id}")
        print(f"  E2E_TERTIARY_STUDY_ID={tertiary_study.id}")
        print(f"  E2E_SOURCE_STUDY_ID={source_study.id}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
