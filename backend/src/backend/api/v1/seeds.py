"""Seed paper and seed author endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import audit as audit_svc
from db.models import Paper, Study
from db.models.audit import AuditAction
from db.models.pico import PICOComponent
from db.models.seeds import SeedAuthor, SeedPaper

router = APIRouter(tags=["seeds"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class PaperRef(BaseModel):
    """Minimal paper representation embedded in seed responses."""

    id: int
    title: str
    doi: str | None
    authors: list | None
    year: int | None
    venue: str | None


class SeedPaperResponse(BaseModel):
    """Response for a seed paper item."""

    id: int
    paper: PaperRef
    added_by: str  # "user" or agent name


class AddSeedPaperRequest(BaseModel):
    """Body for POST /studies/{study_id}/seeds/papers."""

    paper_id: int | None = None
    doi: str | None = None
    title: str | None = None
    authors: list | None = None
    year: int | None = None
    venue: str | None = None


class SeedAuthorResponse(BaseModel):
    """Response for a seed author item."""

    id: int
    author_name: str
    institution: str | None
    profile_url: str | None


class AddSeedAuthorRequest(BaseModel):
    """Body for POST /studies/{study_id}/seeds/authors."""

    author_name: str
    institution: str | None = None
    profile_url: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Seed Papers
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/seeds/papers",
    response_model=list[SeedPaperResponse],
    summary="List seed papers for a study",
)
async def list_seed_papers(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SeedPaperResponse]:
    """Return all seed papers for a study.

    Args:
        study_id: The study to list seeds for.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.
    """
    await require_study_member(study_id, current_user, db)

    seeds_result = await db.execute(
        select(SeedPaper, Paper)
        .join(Paper, SeedPaper.paper_id == Paper.id)
        .where(SeedPaper.study_id == study_id)
        .order_by(SeedPaper.created_at)
    )
    rows = seeds_result.all()
    return [
        SeedPaperResponse(
            id=sp.id,
            paper=PaperRef(
                id=p.id,
                title=p.title,
                doi=p.doi,
                authors=p.authors,
                year=p.year,
                venue=p.venue,
            ),
            added_by=sp.added_by_agent or "user",
        )
        for sp, p in rows
    ]


@router.post(
    "/studies/{study_id}/seeds/papers",
    response_model=SeedPaperResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a seed paper to a study",
)
async def add_seed_paper(
    study_id: int,
    body: AddSeedPaperRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SeedPaperResponse:
    """Add a paper as a seed for a study.

    Supply either ``paper_id`` (existing paper) or paper metadata fields to
    create a new paper record.

    Args:
        study_id: The study to add the seed to.
        body: Paper reference or new paper metadata.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.
    """
    await require_study_member(study_id, current_user, db)

    paper: Paper | None = None

    if body.paper_id is not None:
        paper_result = await db.execute(select(Paper).where(Paper.id == body.paper_id))
        paper = paper_result.scalar_one_or_none()
        if paper is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    elif body.doi is not None:
        paper_result = await db.execute(select(Paper).where(Paper.doi == body.doi))
        paper = paper_result.scalar_one_or_none()
        if paper is None:
            paper = Paper(
                title=body.title or body.doi,
                doi=body.doi,
                authors=body.authors,
                year=body.year,
                venue=body.venue,
            )
            db.add(paper)
            await db.flush()
    elif body.title is not None:
        paper = Paper(
            title=body.title,
            authors=body.authors,
            year=body.year,
            venue=body.venue,
        )
        db.add(paper)
        await db.flush()
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide paper_id, doi, or title",
        )

    seed = SeedPaper(
        study_id=study_id,
        paper_id=paper.id,
        added_by_user_id=current_user.user_id,
    )
    db.add(seed)
    await db.flush()
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="SeedPaper",
        entity_id=seed.id,
        action=AuditAction.CREATE,
        after_value={"paper_id": paper.id},
    )
    await db.commit()

    return SeedPaperResponse(
        id=seed.id,
        paper=PaperRef(
            id=paper.id,
            title=paper.title,
            doi=paper.doi,
            authors=paper.authors,
            year=paper.year,
            venue=paper.venue,
        ),
        added_by="user",
    )


@router.delete(
    "/studies/{study_id}/seeds/papers/{seed_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a seed paper",
)
async def delete_seed_paper(
    study_id: int,
    seed_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a seed paper from a study.

    Args:
        study_id: The study to remove the seed from.
        seed_id: The seed paper record ID to remove.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.
    """
    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(SeedPaper).where(SeedPaper.id == seed_id, SeedPaper.study_id == study_id)
    )
    seed = result.scalar_one_or_none()
    if seed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seed paper not found")

    seed_id_val = seed.id
    await db.delete(seed)
    await db.flush()
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="SeedPaper",
        entity_id=seed_id_val,
        action=AuditAction.DELETE,
    )
    await db.commit()


# ---------------------------------------------------------------------------
# Librarian trigger
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/seeds/librarian",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Librarian agent for seed suggestions",
)
async def trigger_librarian(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Call the Librarian agent to suggest seed papers and authors.

    Runs synchronously in the current version (ARQ enqueue deferred to Phase 5).

    Args:
        study_id: The study to generate suggestions for.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.

    Returns:
        ``{"suggestions": {"papers": [...], "authors": [...]}}``
    """
    await require_study_member(study_id, current_user, db)

    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    pico_result = await db.execute(
        select(PICOComponent).where(PICOComponent.study_id == study_id)
    )
    pico = pico_result.scalar_one_or_none()

    meta: dict = study.metadata_ or {}

    try:
        from agents.services.librarian import LibrarianAgent

        agent = LibrarianAgent()
        result = await agent.run(
            topic=study.topic or study.name,
            variant=pico.variant.value if pico else "PICO",
            population=pico.population if pico else None,
            intervention=pico.intervention if pico else None,
            comparison=pico.comparison if pico else None,
            outcome=pico.outcome if pico else None,
            context=pico.context if pico else None,
            objectives=meta.get("research_objectives", []),
            questions=meta.get("research_questions", []),
        )
        return {
            "suggestions": {
                "papers": [p.model_dump() for p in result.papers],
                "authors": [a.model_dump() for a in result.authors],
            }
        }
    except Exception as exc:
        logger.error("librarian_agent_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Librarian agent unavailable",
        ) from exc


# ---------------------------------------------------------------------------
# Expert agent trigger
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/seeds/expert",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Expert agent for seed paper suggestions",
)
async def trigger_expert(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Enqueue an ExpertAgent background job to suggest seed papers.

    Creates a BackgroundJob record and enqueues ``run_expert_seed_suggestion``
    via ARQ.  On completion the job inserts returned papers as :class:`SeedPaper`
    records (``added_by_agent="expert"``).  The full ExpertAgent response is
    stored in ``progress_detail`` for frontend display.

    Args:
        study_id: The study to generate expert suggestions for.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.

    Returns:
        ``{"job_id": "<uuid>"}``
    """
    await require_study_member(study_id, current_user, db)

    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    from db.models.jobs import BackgroundJob, JobStatus, JobType

    job_id = str(uuid.uuid4())

    # Try to enqueue via ARQ
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        from backend.core.config import get_settings

        settings = get_settings()
        redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        arq_job = await redis.enqueue_job("run_expert_seed_suggestion", study_id, job_id)
        await redis.aclose()
        if arq_job:
            job_id = arq_job.job_id
    except Exception as exc:
        logger.warning("trigger_expert: redis unavailable: %s", exc)

    bg_job = BackgroundJob(
        id=job_id,
        study_id=study_id,
        job_type=JobType.EXPERT_SEED,
        status=JobStatus.QUEUED,
        progress_pct=0,
    )
    db.add(bg_job)
    await db.commit()

    logger.info("expert_seed_job_queued", study_id=study_id, job_id=job_id)
    return {"job_id": job_id}


# ---------------------------------------------------------------------------
# Seed Authors
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/seeds/authors",
    response_model=list[SeedAuthorResponse],
    summary="List seed authors for a study",
)
async def list_seed_authors(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SeedAuthorResponse]:
    """Return all seed authors for a study."""
    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(SeedAuthor)
        .where(SeedAuthor.study_id == study_id)
        .order_by(SeedAuthor.created_at)
    )
    return [
        SeedAuthorResponse(
            id=sa.id,
            author_name=sa.author_name,
            institution=sa.institution,
            profile_url=sa.profile_url,
        )
        for sa in result.scalars().all()
    ]


@router.post(
    "/studies/{study_id}/seeds/authors",
    response_model=SeedAuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a seed author to a study",
)
async def add_seed_author(
    study_id: int,
    body: AddSeedAuthorRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SeedAuthorResponse:
    """Add an author as a seed for a study's search."""
    await require_study_member(study_id, current_user, db)

    author = SeedAuthor(
        study_id=study_id,
        author_name=body.author_name,
        institution=body.institution,
        profile_url=body.profile_url,
        added_by_user_id=current_user.user_id,
    )
    db.add(author)
    await db.flush()
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="SeedAuthor",
        entity_id=author.id,
        action=AuditAction.CREATE,
        after_value={"author_name": author.author_name},
    )
    await db.commit()

    return SeedAuthorResponse(
        id=author.id,
        author_name=author.author_name,
        institution=author.institution,
        profile_url=author.profile_url,
    )
