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
from db.models.slr import (
    ChecklistScoringMethod,
    QualityAssessmentChecklist,
    QualityAssessmentScore,
    QualityChecklistItem,
    ReviewProtocol,
    ReviewProtocolStatus,
    SynthesisApproach,
)
from db.models.study import Reviewer, ReviewerType, StudyMember, StudyMemberRole
from db.models.tertiary import (
    SecondaryStudySeedImport,
    SecondaryStudyType,
    TertiaryDataExtraction,
    TertiaryProtocolStatus,
    TertiaryStudyProtocol,
)
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


async def reset_tertiary_workspace(session: AsyncSession, study: Study) -> None:
    """Undo the state T025 (``tertiary-workflow.spec.ts``) writes through the UI.

    The same class of problem ``reset_screening_queue`` exists for (T025/T026
    write real state, and the suite runs repeatedly against a database it also
    writes to — see that function's docstring) applies here too, for two
    actions the Tertiary journey performs that ``reset_screening_queue`` does
    not touch:

    - **Protocol validation.** ``_seed_tertiary_study`` deliberately seeds no
      ``TertiaryStudyProtocol`` row so the US2 journey can create and validate
      one through the UI. Once validated, ``TertiaryProtocolForm`` goes
      read-only (see its ``isReadOnly`` check), so a second run without this
      reset would have nothing to fill in or validate.
    - **Seed import.** ``SeedImportPanel``'s dialog disables a source study
      once it appears in ``existingSourceIds``, so a second import attempt at
      the same source has nothing clickable to select.

    Deletes the protocol row, the seed-import audit rows, the candidates those
    imports created (identified by ``phase_tag == "seed-import"``, disjoint
    from the ``"initial-search"`` tag the study's own fixture candidates
    carry), and the sentinel ``SearchExecution``/``SearchString`` pair
    ``TertiaryExtractionService._get_or_create_seed_import_execution`` creates
    on the first import — so a reseed always starts the journey from the same
    protocol-less, import-less state ``_seed_tertiary_study`` documents.

    That sentinel pair is not optional cleanup: ``ensure_search_execution``
    (used below, for the study's own ``"initial-search"`` execution) looks up
    *at most one* ``SearchString`` and *at most one* ``SearchExecution`` per
    study and raises ``MultipleResultsFound`` the moment a second row of
    either exists — which is exactly what an unreset seed-import sentinel
    leaves behind.

    Args:
        session: Active async session.
        study: The Tertiary study to reset.

    """
    protocol_result = await session.execute(
        delete(TertiaryStudyProtocol).where(TertiaryStudyProtocol.study_id == study.id)
    )
    protocol_count: int = protocol_result.rowcount  # type: ignore[attr-defined]
    import_result = await session.execute(
        delete(SecondaryStudySeedImport).where(
            SecondaryStudySeedImport.target_study_id == study.id
        )
    )
    import_count: int = import_result.rowcount  # type: ignore[attr-defined]
    candidate_result = await session.execute(
        delete(CandidatePaper).where(
            CandidatePaper.study_id == study.id,
            CandidatePaper.phase_tag == "seed-import",
        )
    )
    imported_candidates: int = candidate_result.rowcount  # type: ignore[attr-defined]

    sentinel_execution = (
        await session.execute(
            select(SearchExecution).where(
                SearchExecution.study_id == study.id,
                SearchExecution.phase_tag == "seed-import",
            )
        )
    ).scalar_one_or_none()
    sentinel_count = 0
    if sentinel_execution is not None:
        sentinel_string_id = sentinel_execution.search_string_id
        await session.delete(sentinel_execution)
        await session.flush()
        await session.execute(
            delete(SearchString).where(SearchString.id == sentinel_string_id)
        )
        sentinel_count = 1

    await session.flush()
    if protocol_count or import_count or imported_candidates or sentinel_count:
        print(
            f"reset tertiary workspace on study {study.id} "
            f"({protocol_count} protocol, {import_count} seed imports, "
            f"{imported_candidates} imported candidates, "
            f"{sentinel_count} seed-import search execution cleared)"
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


async def ensure_validated_tertiary_protocol(
    session: AsyncSession, study: Study
) -> TertiaryStudyProtocol:
    """Return *study*'s Tertiary protocol, creating a **validated** one if absent.

    Exists for exactly one reason: giving T026's Tertiary screening test in
    ``screen-paper.spec.ts`` its own study, separate from ``E2E Tertiary Seed
    Study``. Both files reach a Tertiary study's phase 3, and both write a
    real, one-way protocol-validation transition — T025
    (``tertiary-workflow.spec.ts``) *through the UI*, as the very journey it
    exists to exercise, and T026 needed it *already true* as a precondition
    for a screen it isn't testing. Pointing both at the same row raced them:
    whichever file's process got there first left the other looking at an
    already-validated, read-only form. Verified empirically, not assumed —
    even `--workers=1` (no cross-file parallelism at all) still failed
    tertiary-workflow.spec.ts deterministically, because `screen-paper.spec.ts`
    sorts before `tertiary-workflow.spec.ts` and so always ran, and validated,
    first.

    Mirrors `ensure_validated_review_protocol`'s reasoning for the SLR study
    exactly: the study this creates a protocol for exists to be screened, not
    to have its protocol-validation journey re-tested.

    Args:
        session: Active async session.
        study: The Tertiary study to scaffold.

    Returns:
        The existing or newly created protocol.

    """
    protocol = (
        await session.execute(
            select(TertiaryStudyProtocol).where(
                TertiaryStudyProtocol.study_id == study.id
            )
        )
    ).scalar_one_or_none()
    if protocol is None:
        protocol = TertiaryStudyProtocol(
            study_id=study.id,
            status=TertiaryProtocolStatus.VALIDATED,
            background="Seeded protocol for the e2e Tertiary screening journey.",
            research_questions=[
                "Which secondary study designs report the strongest evidence?"
            ],
            synthesis_approach=SynthesisApproach.DESCRIPTIVE.value,
        )
        session.add(protocol)
        await session.flush()
        print(
            f"created validated tertiary protocol for study {study.id} (unlocks phases 2-3)"
        )
    elif protocol.status != TertiaryProtocolStatus.VALIDATED:
        protocol.status = TertiaryProtocolStatus.VALIDATED
        print(f"set tertiary protocol {protocol.id} to validated")
    return protocol


async def ensure_quality_checklist(
    session: AsyncSession, study: Study, *, name: str, description: str | None = None
) -> QualityAssessmentChecklist:
    """Return *study*'s quality assessment checklist, creating one if absent.

    A study has at most one checklist (``study_id`` is unique), so the
    checklist itself is the natural key here.

    Args:
        session: Active async session.
        study: The study to scaffold.
        name: Checklist name, used when creating.
        description: Optional checklist description, used when creating.

    Returns:
        The existing or newly created checklist.

    """
    checklist = (
        await session.execute(
            select(QualityAssessmentChecklist).where(
                QualityAssessmentChecklist.study_id == study.id
            )
        )
    ).scalar_one_or_none()
    if checklist is None:
        checklist = QualityAssessmentChecklist(
            study_id=study.id, name=name, description=description
        )
        session.add(checklist)
        await session.flush()
        print(f"created quality checklist {name!r} for study {study.id}")
    return checklist


async def ensure_quality_checklist_item(
    session: AsyncSession,
    checklist: QualityAssessmentChecklist,
    *,
    order: int,
    question: str,
    scoring_method: ChecklistScoringMethod = ChecklistScoringMethod.BINARY,
    weight: float = 1.0,
) -> QualityChecklistItem:
    """Return the item at *order* on *checklist*, creating it if absent.

    ``order`` is the natural key within a checklist: nothing else uniquely
    identifies an item, and re-running with the same *order* must not create
    a duplicate row.

    Args:
        session: Active async session.
        checklist: Owning checklist.
        order: Display order within the checklist.
        question: Item question text, used when creating.
        scoring_method: Scoring input type, used when creating.
        weight: Weight applied to this item's score, used when creating.

    Returns:
        The existing or newly created item.

    """
    item = (
        await session.execute(
            select(QualityChecklistItem).where(
                QualityChecklistItem.checklist_id == checklist.id,
                QualityChecklistItem.order == order,
            )
        )
    ).scalar_one_or_none()
    if item is None:
        item = QualityChecklistItem(
            checklist_id=checklist.id,
            order=order,
            question=question,
            scoring_method=scoring_method,
            weight=weight,
        )
        session.add(item)
        await session.flush()
        print(f"created checklist item {order} for checklist {checklist.id}")
    return item


async def ensure_quality_score(
    session: AsyncSession,
    candidate: CandidatePaper,
    reviewer: Reviewer,
    item: QualityChecklistItem,
    score_value: float,
) -> QualityAssessmentScore:
    """Return the (candidate, reviewer, item) score row, creating it if absent.

    The natural key matches ``uq_quality_assessment_score`` on
    ``QualityAssessmentScore`` — the same triple the unique constraint uses.

    Args:
        session: Active async session.
        candidate: The candidate paper being scored.
        reviewer: The reviewer submitting the score.
        item: The checklist item scored.
        score_value: The score, used when creating.

    Returns:
        The existing or newly created score.

    """
    score = (
        await session.execute(
            select(QualityAssessmentScore).where(
                QualityAssessmentScore.candidate_paper_id == candidate.id,
                QualityAssessmentScore.reviewer_id == reviewer.id,
                QualityAssessmentScore.checklist_item_id == item.id,
            )
        )
    ).scalar_one_or_none()
    if score is None:
        score = QualityAssessmentScore(
            candidate_paper_id=candidate.id,
            reviewer_id=reviewer.id,
            checklist_item_id=item.id,
            score_value=score_value,
        )
        session.add(score)
        await session.flush()
        print(
            f"created quality score for candidate {candidate.id} "
            f"(reviewer {reviewer.id}, item {item.id}) — unlocks tertiary phase 4"
        )
    return score


async def ensure_validated_tertiary_extraction(
    session: AsyncSession, candidate: CandidatePaper, *, key_findings: str
) -> TertiaryDataExtraction:
    """Return *candidate*'s tertiary extraction forced to ``validated``.

    No UI path ever writes ``extraction_status="validated"`` — see TFIX8 in
    ``tasks.md`` — so this is the only writer of that state, and it is a
    seeding compromise rather than a stand-in for a reachable feature. Read
    that caveat before treating an e2e pass through tertiary phase 5 as proof
    a user can produce this state themselves.

    Args:
        session: Active async session.
        candidate: The candidate paper (an included secondary study) to extract.
        key_findings: Summary text, used when creating.

    Returns:
        The existing or newly created extraction, with status ``validated``.

    """
    extraction = (
        await session.execute(
            select(TertiaryDataExtraction).where(
                TertiaryDataExtraction.candidate_paper_id == candidate.id
            )
        )
    ).scalar_one_or_none()
    if extraction is None:
        extraction = TertiaryDataExtraction(
            candidate_paper_id=candidate.id,
            secondary_study_type=SecondaryStudyType.SMS,
            key_findings=key_findings,
            extraction_status="validated",
        )
        session.add(extraction)
        await session.flush()
        print(
            f"created validated tertiary extraction for candidate {candidate.id} "
            "(unlocks tertiary phase 5 with a second one)"
        )
    elif extraction.extraction_status != "validated":
        extraction.extraction_status = "validated"
        print(f"set tertiary extraction {extraction.id} to validated")
    return extraction
