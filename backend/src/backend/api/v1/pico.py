"""PICO/C component endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import audit as audit_svc
from backend.services.phase_gate import compute_current_phase
from db.models import Study
from db.models.audit import AuditAction
from db.models.pico import PICOComponent, PICOVariant

router = APIRouter(tags=["pico"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class PICORequest(BaseModel):
    """Body for PUT /studies/{study_id}/pico."""

    variant: str
    population: str | None = None
    intervention: str | None = None
    comparison: str | None = None
    outcome: str | None = None
    context: str | None = None
    extra_fields: dict | None = None


class PICOResponse(BaseModel):
    """PICO/C component response."""

    id: int
    study_id: int
    variant: str
    population: str | None
    intervention: str | None
    comparison: str | None
    outcome: str | None
    context: str | None
    extra_fields: dict | None
    ai_suggestions: dict | None
    updated_at: str


class RefineRequest(BaseModel):
    """Body for POST /studies/{study_id}/pico/refine."""

    component: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------



def _pico_to_response(pico: PICOComponent) -> PICOResponse:
    return PICOResponse(
        id=pico.id,
        study_id=pico.study_id,
        variant=pico.variant.value,
        population=pico.population,
        intervention=pico.intervention,
        comparison=pico.comparison,
        outcome=pico.outcome,
        context=pico.context,
        extra_fields=pico.extra_fields,
        ai_suggestions=pico.ai_suggestions,
        updated_at=pico.updated_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/pico",
    response_model=PICOResponse,
    summary="Get the PICO/C components for a study",
)
async def get_pico(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PICOResponse:
    """Return the current PICO/C component record for a study.

    Args:
        study_id: The study to retrieve PICO for.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`PICOResponse` with all component fields.

    Raises:
        HTTPException: 404 if the study or PICO record is not found.
    """
    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(PICOComponent).where(PICOComponent.study_id == study_id)
    )
    pico = result.scalar_one_or_none()
    if pico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PICO not yet defined for this study"
        )
    return _pico_to_response(pico)


@router.put(
    "/studies/{study_id}/pico",
    response_model=PICOResponse,
    summary="Create or replace PICO/C components",
)
async def upsert_pico(
    study_id: int,
    body: PICORequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PICOResponse:
    """Create or replace the PICO/C components for a study.

    Saving PICO unlocks Phase 2 of the study.

    Args:
        study_id: The study to update PICO for.
        body: PICO/C component values.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.

    Returns:
        The saved :class:`PICOResponse`.

    Raises:
        HTTPException: 404 if the study is not found.
        HTTPException: 422 if the variant is invalid.
    """
    await require_study_member(study_id, current_user, db)

    try:
        variant = PICOVariant(body.variant)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid PICO variant: {body.variant}",
        )

    result = await db.execute(
        select(PICOComponent).where(PICOComponent.study_id == study_id)
    )
    pico = result.scalar_one_or_none()

    is_create = pico is None
    if pico is None:
        pico = PICOComponent(
            study_id=study_id,
            variant=variant,
            population=body.population,
            intervention=body.intervention,
            comparison=body.comparison,
            outcome=body.outcome,
            context=body.context,
            extra_fields=body.extra_fields,
        )
        db.add(pico)
    else:
        pico.variant = variant
        pico.population = body.population
        pico.intervention = body.intervention
        pico.comparison = body.comparison
        pico.outcome = body.outcome
        pico.context = body.context
        pico.extra_fields = body.extra_fields

    # Update study's current_phase via phase gate and stamp pico_saved_at
    new_phase = await compute_current_phase(study_id, db)
    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    if study is not None:
        study.current_phase = max(study.current_phase, new_phase)
        study.pico_saved_at = datetime.now(UTC)

    await db.flush()
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="PICOComponent",
        entity_id=pico.id,
        action=AuditAction.CREATE if is_create else AuditAction.UPDATE,
        after_value={"variant": variant.value, "population": body.population,
                     "intervention": body.intervention, "outcome": body.outcome},
    )
    await db.commit()
    logger.info("pico_saved", study_id=study_id, variant=variant.value)
    return _pico_to_response(pico)


@router.post(
    "/studies/{study_id}/pico/refine",
    response_model=dict,
    summary="Get AI suggestions for a PICO/C component",
)
async def refine_pico(
    study_id: int,
    body: RefineRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Call the Librarian agent for AI suggestions on a PICO/C component.

    Args:
        study_id: The study to refine PICO for.
        body: Which component to refine (population, intervention, etc.).
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.

    Returns:
        ``{"suggestions": ["...", "..."]}``

    Raises:
        HTTPException: 404 if the study or PICO record is not found.
    """
    await require_study_member(study_id, current_user, db)

    pico_result = await db.execute(
        select(PICOComponent).where(PICOComponent.study_id == study_id)
    )
    pico = pico_result.scalar_one_or_none()
    if pico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Save PICO/C before requesting refinement"
        )

    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    meta: dict = study.metadata_ or {}

    try:
        from agents.services.librarian import LibrarianAgent

        agent = LibrarianAgent()
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
        )

        # Extract suggestions for the requested component from paper rationales
        suggestions = [p.rationale for p in result.papers[:5]]

        # Persist ai_suggestions on the pico record
        pico.ai_suggestions = pico.ai_suggestions or {}
        pico.ai_suggestions[body.component] = suggestions
        await db.commit()

        return {"suggestions": suggestions}
    except Exception as exc:
        logger.error("pico_refine_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI refinement service unavailable",
        ) from exc
