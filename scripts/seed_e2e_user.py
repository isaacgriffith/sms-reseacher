"""Seed the data the Playwright e2e suite needs.

The e2e specs authenticate as ``E2E_USER_EMAIL`` / ``E2E_USER_PASSWORD``
(defaulting to ``testuser@example.com`` / ``testpassword``) and land on
``/groups``, so the user needs at least one group membership.

There is no registration endpoint, so this writes directly through the ORM.
Idempotent: re-running against an already-seeded database is a no-op. The
generic row factories live in :mod:`seed_helpers`; what follows is the
study-specific fixtures and the entry point.

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

from backend.core.encryption import encrypt_secret
from db.models import Study, StudyType
from db.models.candidate import (
    CandidatePaperStatus,
    PaperDecision,
    PaperDecisionType,
)
from db.models.extraction import DataExtraction, ExtractionStatus, ResearchType
from db.models.search_exec import SearchExecution
from db.models.users import ResearchGroup, User
from seed_helpers import (
    ensure_candidate,
    ensure_group,
    ensure_group_membership,
    ensure_human_reviewer,
    ensure_paper,
    ensure_pico,
    ensure_search_execution,
    ensure_study,
    ensure_study_members,
    upsert_user,
)
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
        paper = await ensure_paper(session, title, doi)
        candidate = await ensure_candidate(
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
    paper = await ensure_paper(session, title, doi)
    candidate = await ensure_candidate(
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

    accepting = await ensure_human_reviewer(session, study, reviewer_a)
    rejecting = await ensure_human_reviewer(session, study, reviewer_b)

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
    study = await ensure_study(
        session,
        name=TERTIARY_STUDY_NAME,
        topic="A tertiary review of secondary studies in software testing",
        study_type=StudyType.TERTIARY,
        group=group,
    )
    await ensure_study_members(session, study, members)
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
    study = await ensure_study(
        session,
        name=SOURCE_STUDY_NAME,
        topic="Secondary studies of DevOps and microservice adoption",
        study_type=StudyType.SMS,
        group=group,
    )
    await ensure_study_members(session, study, members)
    execution = await ensure_search_execution(
        session, study, '("devops" OR "microservices") AND "systematic mapping"'
    )
    for title, doi in SOURCE_PAPERS:
        paper = await ensure_paper(session, title, doi)
        await ensure_candidate(
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
    user = await upsert_user(session, EMAIL, PASSWORD, DISPLAY_NAME)
    admin = await upsert_user(session, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_DISPLAY_NAME)

    # Two more accounts with 2FA switched on. Kept separate from the main test
    # user so every other spec can still log in with a password alone.
    for totp_email in (TOTP_EMAIL, TOTP_LOCKOUT_EMAIL):
        totp_user = await upsert_user(
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
    study = await ensure_study(
        session,
        name=STUDY_NAME,
        topic="Automated testing in agile software projects",
        study_type=StudyType.SMS,
        group=group,
    )
    await ensure_study_members(session, study, members)
    await ensure_pico(session, study)
    execution = await ensure_search_execution(
        session, study, '("agile" AND "automated testing")'
    )

    # Screening (phase 3) renders accept/reject controls only when the queue has
    # PENDING papers; without these the screen-paper specs skip instead of
    # asserting anything.
    for title, doi in SEED_PAPERS:
        paper = await ensure_paper(session, title, doi)
        await ensure_candidate(
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

        group = await ensure_group(session, GROUP_NAME)
        for member in members:
            await ensure_group_membership(session, member, group)

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
