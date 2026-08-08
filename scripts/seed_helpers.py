"""Idempotent building blocks shared by the e2e seed fixtures.

Split out of ``seed_e2e_user.py`` when that file crossed the 800-line maximum.
The division is by role, not by size: everything here is a **generic** row
factory that knows nothing about which journey needs it, while
``seed_e2e_user.py`` keeps the study-specific fixtures and the entry point.

Every helper follows the same contract: look the row up by its natural key,
return it if present, otherwise create and flush it. That is what makes the
whole script re-runnable, which the e2e workflow depends on — the suite is run
repeatedly against a database it also writes to.

Not a package, and deliberately so: ``scripts/`` is a flat directory of
standalone entry points, and running ``python scripts/seed_e2e_user.py`` puts
``scripts/`` on ``sys.path`` so a plain ``import seed_helpers`` resolves.
"""

from __future__ import annotations

from backend.core.auth import hash_password
from db.models import Paper, Study, StudyType
from db.models.candidate import CandidatePaper, CandidatePaperStatus, PaperDecision
from db.models.criteria import ExclusionCriterion, InclusionCriterion
from db.models.pico import PICOComponent, PICOVariant
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.slr import ReviewProtocol, ReviewProtocolStatus, SynthesisApproach
from db.models.study import Reviewer, ReviewerType, StudyMember, StudyMemberRole
from db.models.users import GroupMembership, GroupRole, ResearchGroup, User
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def upsert_user(
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


async def ensure_group(session: AsyncSession, name: str) -> ResearchGroup:
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


async def ensure_group_membership(
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


async def ensure_study(
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


async def ensure_study_members(
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


async def ensure_paper(session: AsyncSession, title: str, doi: str) -> Paper:
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


async def ensure_search_execution(
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


async def ensure_candidate(
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


async def ensure_human_reviewer(
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


async def ensure_pico(session: AsyncSession, study: Study) -> None:
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


async def ensure_criteria(
    session: AsyncSession,
    study: Study,
    inclusion: list[str],
    exclusion: list[str],
) -> None:
    """Give *study* screening criteria if it has none.

    ``ReviewerPanel`` renders its reason selector only when
    ``/criteria/{inclusion,exclusion}`` returns rows, so without these a
    reviewer can record a decision but cannot attach a reason to it — and
    FR-002 requires reasons "drawn from the study's criteria".

    Args:
        session: Active async session.
        study: The study to scaffold.
        inclusion: Inclusion criterion descriptions, in display order.
        exclusion: Exclusion criterion descriptions, in display order.

    """
    for model, descriptions in (
        (InclusionCriterion, inclusion),
        (ExclusionCriterion, exclusion),
    ):
        existing = (
            (await session.execute(select(model).where(model.study_id == study.id)))
            .scalars()
            .first()
        )
        if existing is not None:
            continue
        for order_index, description in enumerate(descriptions):
            session.add(
                model(
                    study_id=study.id,
                    description=description,
                    order_index=order_index,
                )
            )
        print(
            f"created {len(descriptions)} {model.__tablename__} rows "
            f"for study {study.id}"
        )


async def reset_screening_queue(
    session: AsyncSession, study: Study, dois: list[str]
) -> None:
    """Return the candidates for *dois* to an undecided, pending state.

    ``screen-paper.spec.ts`` records real decisions, and the suite is run
    repeatedly against a database it also writes to. Without this, run 2 submits
    against a candidate that already holds the reviewer's decision and gets the
    409 ``unacknowledged_prior_decision`` that FR-022 requires — so the spec
    would have to branch on which run it is, and Principle VI forbids the
    conditional that would take.

    Resetting rather than branching follows the precedent already in this
    script: the TOTP counters are cleared on every run because the lockout spec
    deliberately locks its account.

    Scoped to *dois* deliberately. The conflict fixture's two disagreeing
    decisions are the subject of their own assertions and must survive.

    Args:
        session: Active async session.
        study: The study whose queue is reset.
        dois: DOIs of the candidates to return to pending.

    """
    candidates = (
        (
            await session.execute(
                select(CandidatePaper)
                .join(Paper, CandidatePaper.paper_id == Paper.id)
                .where(CandidatePaper.study_id == study.id, Paper.doi.in_(dois))
            )
        )
        .scalars()
        .all()
    )
    if not candidates:
        return

    candidate_ids = [c.id for c in candidates]
    stale = (
        await session.execute(
            select(func.count())
            .select_from(PaperDecision)
            .where(PaperDecision.candidate_paper_id.in_(candidate_ids))
        )
    ).scalar_one()
    if not stale:
        return

    await session.execute(
        delete(PaperDecision).where(PaperDecision.candidate_paper_id.in_(candidate_ids))
    )
    for candidate in candidates:
        candidate.current_status = CandidatePaperStatus.PENDING
        candidate.conflict_flag = False
    await session.flush()
    print(
        f"reset {len(candidates)} queue candidates on study {study.id} "
        f"({stale} decisions cleared)"
    )


async def ensure_validated_review_protocol(
    session: AsyncSession, study: Study
) -> ReviewProtocol:
    """Return *study*'s SLR protocol, creating a **validated** one if absent.

    ``slr_phase_gate.get_slr_unlocked_phases`` returns ``[1]`` and stops unless
    a protocol exists with ``status == VALIDATED``, so screening on an SLR
    study is unreachable without this. Unlike the Tertiary fixture — which
    deliberately omits its protocol so the US2 journey can create one through
    the UI — the SLR study exists to be screened, and driving protocol
    validation first would put phase 1 in the way of every screening spec.

    Args:
        session: Active async session.
        study: The SLR study to scaffold.

    Returns:
        The existing or newly created protocol.

    """
    protocol = (
        await session.execute(
            select(ReviewProtocol).where(ReviewProtocol.study_id == study.id)
        )
    ).scalar_one_or_none()
    if protocol is None:
        protocol = ReviewProtocol(
            study_id=study.id,
            status=ReviewProtocolStatus.VALIDATED,
            background="Seeded protocol for the e2e screening journey.",
            research_questions=["How effective is code review at scale?"],
            pico_population="Industrial software teams",
            pico_intervention="Modern code review",
            pico_outcome="Defect detection rate",
            synthesis_approach=SynthesisApproach.DESCRIPTIVE,
        )
        session.add(protocol)
        await session.flush()
        print(f"created validated review protocol for study {study.id} (unlocks 2-3)")
    return protocol
