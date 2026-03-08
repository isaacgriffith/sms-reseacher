"""Search string versioning, generation, test, and approval endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import audit as audit_svc
from db.models.audit import AuditAction
from db.models.criteria import ExclusionCriterion, InclusionCriterion
from db.models.pico import PICOComponent
from db.models import Study
from db.models.search import SearchString, SearchStringIteration

router = APIRouter(tags=["search_strings"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class IterationResponse(BaseModel):
    """One test-retest iteration result."""

    id: int
    iteration_number: int
    result_set_count: int
    test_set_recall: float
    ai_adequacy_judgment: str | None
    human_approved: bool | None


class SearchStringResponse(BaseModel):
    """Response for a search string."""

    id: int
    study_id: int
    version: int
    string_text: str
    is_active: bool
    created_by_agent: str | None
    iterations: list[IterationResponse]


class CreateSearchStringRequest(BaseModel):
    """Body for manual POST /studies/{study_id}/search-strings."""

    string_text: str


class ApproveIterationRequest(BaseModel):
    """Body for PATCH /studies/{study_id}/search-strings/{id}/iterations/{iter_id}."""

    human_approved: bool


class TestSearchRequest(BaseModel):
    """Body for POST /studies/{study_id}/search-strings/{id}/test."""

    databases: list[str] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _build_response(ss: SearchString, db: AsyncSession) -> SearchStringResponse:
    """Build a SearchStringResponse including iterations."""
    iters_result = await db.execute(
        select(SearchStringIteration)
        .where(SearchStringIteration.search_string_id == ss.id)
        .order_by(SearchStringIteration.iteration_number)
    )
    iterations = [
        IterationResponse(
            id=it.id,
            iteration_number=it.iteration_number,
            result_set_count=it.result_set_count,
            test_set_recall=it.test_set_recall,
            ai_adequacy_judgment=it.ai_adequacy_judgment,
            human_approved=it.human_approved,
        )
        for it in iters_result.scalars().all()
    ]
    return SearchStringResponse(
        id=ss.id,
        study_id=ss.study_id,
        version=ss.version,
        string_text=ss.string_text,
        is_active=ss.is_active,
        created_by_agent=ss.created_by_agent,
        iterations=iterations,
    )


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/search-strings",
    response_model=list[SearchStringResponse],
    summary="List search strings for a study",
)
async def list_search_strings(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SearchStringResponse]:
    """Return all search strings for a study, newest first."""
    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(SearchString)
        .where(SearchString.study_id == study_id)
        .order_by(SearchString.version.desc())
    )
    strings = result.scalars().all()
    return [await _build_response(ss, db) for ss in strings]


# ---------------------------------------------------------------------------
# Manual create
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/search-strings",
    response_model=SearchStringResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manually create a search string",
)
async def create_search_string(
    study_id: int,
    body: CreateSearchStringRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SearchStringResponse:
    """Create a new search string manually (no AI generation)."""
    await require_study_member(study_id, current_user, db)

    # Determine next version number
    existing = await db.execute(
        select(SearchString).where(SearchString.study_id == study_id).order_by(SearchString.version.desc())
    )
    latest = existing.scalars().first()
    next_version = (latest.version + 1) if latest else 1

    ss = SearchString(
        study_id=study_id,
        version=next_version,
        string_text=body.string_text,
        is_active=False,
        created_by_user_id=current_user.user_id,
    )
    db.add(ss)
    await db.flush()
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="SearchString",
        entity_id=ss.id,
        action=AuditAction.CREATE,
        after_value={"version": next_version, "string_text": body.string_text},
    )
    await db.commit()

    return await _build_response(ss, db)


# ---------------------------------------------------------------------------
# AI generate
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/search-strings/generate",
    response_model=SearchStringResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a search string with AI",
)
async def generate_search_string(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SearchStringResponse:
    """Call SearchStringBuilderAgent to generate a Boolean search string.

    Retrieves the study's PICO/C component and inclusion/exclusion criteria,
    calls the AI agent, creates a SearchString record, and computes recall
    against the seed paper test set as the first SearchStringIteration.
    """
    await require_study_member(study_id, current_user, db)

    # Load study
    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    # Load PICO
    pico_result = await db.execute(
        select(PICOComponent).where(PICOComponent.study_id == study_id)
    )
    pico = pico_result.scalar_one_or_none()
    if pico is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PICO/C component must be saved before generating a search string",
        )

    # Load criteria
    inc_result = await db.execute(
        select(InclusionCriterion)
        .where(InclusionCriterion.study_id == study_id)
        .order_by(InclusionCriterion.order_index)
    )
    exc_result = await db.execute(
        select(ExclusionCriterion)
        .where(ExclusionCriterion.study_id == study_id)
        .order_by(ExclusionCriterion.order_index)
    )
    inclusion = [c.description for c in inc_result.scalars().all()]
    exclusion = [c.description for c in exc_result.scalars().all()]

    meta: dict = study.metadata_ or {}

    try:
        from agents.services.search_builder import SearchStringBuilderAgent

        agent = SearchStringBuilderAgent()
        result = await agent.run(
            topic=study.topic or study.name,
            variant=pico.variant.value,
            population=pico.population,
            intervention=pico.intervention,
            comparison=pico.comparison,
            outcome=pico.outcome,
            context=pico.context,
            extra_fields=pico.extra_fields,
            objectives=meta.get("research_objectives", []),
            questions=meta.get("research_questions", []),
            inclusion_criteria=inclusion,
            exclusion_criteria=exclusion,
        )
    except Exception as exc:
        logger.error("search_builder_agent_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search string builder agent unavailable",
        ) from exc

    # Determine next version
    existing = await db.execute(
        select(SearchString)
        .where(SearchString.study_id == study_id)
        .order_by(SearchString.version.desc())
    )
    latest = existing.scalars().first()
    next_version = (latest.version + 1) if latest else 1

    ss = SearchString(
        study_id=study_id,
        version=next_version,
        string_text=result.search_string,
        is_active=False,
        created_by_agent="search-builder",
    )
    db.add(ss)
    await db.flush()

    # Create first iteration with 0 recall (test run not yet executed)
    iteration = SearchStringIteration(
        search_string_id=ss.id,
        iteration_number=1,
        result_set_count=0,
        test_set_recall=0.0,
        ai_adequacy_judgment=result.expansion_notes,
    )
    db.add(iteration)
    await db.flush()
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="SearchString",
        entity_id=ss.id,
        action=AuditAction.CREATE,
        after_value={"version": next_version, "created_by_agent": "search-builder"},
    )
    await db.commit()

    return await _build_response(ss, db)


# ---------------------------------------------------------------------------
# Get single search string
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/search-strings/{search_string_id}",
    response_model=SearchStringResponse,
    summary="Get a specific search string",
)
async def get_search_string(
    study_id: int,
    search_string_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SearchStringResponse:
    """Return a single search string with all iterations."""
    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(SearchString).where(
            SearchString.id == search_string_id,
            SearchString.study_id == study_id,
        )
    )
    ss = result.scalar_one_or_none()
    if ss is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search string not found")

    return await _build_response(ss, db)


# ---------------------------------------------------------------------------
# Update iterations (approve/reject)
# ---------------------------------------------------------------------------


@router.patch(
    "/studies/{study_id}/search-strings/{search_string_id}/iterations/{iteration_id}",
    response_model=IterationResponse,
    summary="Approve or reject a search string iteration",
)
async def update_iteration(
    study_id: int,
    search_string_id: int,
    iteration_id: int,
    body: ApproveIterationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IterationResponse:
    """Set human_approved on a SearchStringIteration."""
    await require_study_member(study_id, current_user, db)

    # Verify search string belongs to study
    ss_result = await db.execute(
        select(SearchString).where(
            SearchString.id == search_string_id,
            SearchString.study_id == study_id,
        )
    )
    ss = ss_result.scalar_one_or_none()
    if ss is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search string not found")

    iter_result = await db.execute(
        select(SearchStringIteration).where(
            SearchStringIteration.id == iteration_id,
            SearchStringIteration.search_string_id == search_string_id,
        )
    )
    iteration = iter_result.scalar_one_or_none()
    if iteration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Iteration not found")

    iteration.human_approved = body.human_approved
    if body.human_approved:
        ss.is_active = True
    # TODO(T123): record AuditRecord(entity_type="SearchString", action="update",
    #   field_name="is_active", after_value=True) once the audit trail model exists.
    await db.commit()

    return IterationResponse(
        id=iteration.id,
        iteration_number=iteration.iteration_number,
        result_set_count=iteration.result_set_count,
        test_set_recall=iteration.test_set_recall,
        ai_adequacy_judgment=iteration.ai_adequacy_judgment,
        human_approved=iteration.human_approved,
    )


# ---------------------------------------------------------------------------
# Test search (enqueue ARQ job)
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/search-strings/{search_string_id}/test",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a test search for a search string",
)
async def test_search_string(
    study_id: int,
    search_string_id: int,
    body: TestSearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Enqueue a test-search ARQ job to evaluate recall against the seed test set.

    Returns the job ID for polling. The job will create a new
    SearchStringIteration with recall metrics when complete.
    """
    await require_study_member(study_id, current_user, db)

    ss_result = await db.execute(
        select(SearchString).where(
            SearchString.id == search_string_id,
            SearchString.study_id == study_id,
        )
    )
    ss = ss_result.scalar_one_or_none()
    if ss is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search string not found")

    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        from backend.core.config import get_settings

        settings = get_settings()
        redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        job = await redis.enqueue_job(
            "run_test_search",
            study_id,
            search_string_id,
            body.databases or [],
        )
        await redis.aclose()
        return {"job_id": job.job_id if job else None, "search_string_id": search_string_id}
    except Exception as exc:
        logger.error("test_search_enqueue_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job queue unavailable",
        ) from exc
