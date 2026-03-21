"""Service layer for SLR review protocol lifecycle management (feature 007).

Provides CRUD operations for :class:`ReviewProtocol`, AI review submission
via ARQ background job, and protocol validation.

Business rules:
- A protocol in ``validated`` state cannot be edited (raises HTTP 409).
- Submission for review validates completeness of required fields (HTTP 422).
- Validation requires that a ``review_report`` exists (HTTP 422).
"""

from __future__ import annotations

from typing import Any

import structlog
from db.models.slr import ReviewProtocol, ReviewProtocolStatus
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# Fields that must be non-empty before submitting for AI review
_REQUIRED_FIELDS: list[str] = [
    "background",
    "rationale",
    "research_questions",
    "pico_population",
    "pico_intervention",
    "pico_comparison",
    "pico_outcome",
    "search_strategy",
    "inclusion_criteria",
    "exclusion_criteria",
    "data_extraction_strategy",
    "synthesis_approach",
]


async def get_protocol(study_id: int, db: AsyncSession) -> ReviewProtocol | None:
    """Fetch the review protocol for a study, or ``None`` if it does not exist.

    Args:
        study_id: The study whose protocol to retrieve.
        db: Active async database session.

    Returns:
        The :class:`ReviewProtocol` ORM instance, or ``None``.

    """
    result = await db.execute(select(ReviewProtocol).where(ReviewProtocol.study_id == study_id))
    return result.scalar_one_or_none()


async def upsert_protocol(
    study_id: int,
    data: dict[str, Any],
    db: AsyncSession,
) -> ReviewProtocol:
    """Create or update the draft protocol for a study.

    Only protocols in ``draft`` or ``under_review`` status can be edited.
    Raises HTTP 409 if the protocol has already been ``validated``.

    Args:
        study_id: The study to create or update the protocol for.
        data: Dict of protocol field values to apply.
        db: Active async database session.

    Returns:
        The created or updated :class:`ReviewProtocol` instance.

    Raises:
        HTTPException: 409 if the protocol is already validated.

    """
    bound = logger.bind(study_id=study_id)
    protocol = await get_protocol(study_id, db)

    if protocol is not None and protocol.status == ReviewProtocolStatus.VALIDATED:
        bound.warning("upsert_protocol: attempt to edit validated protocol")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Protocol is validated and cannot be edited.",
        )

    if protocol is None:
        protocol = ReviewProtocol(study_id=study_id)
        db.add(protocol)
        bound.info("upsert_protocol: creating new protocol")
    else:
        bound.info("upsert_protocol: updating existing protocol")

    for field, value in data.items():
        if hasattr(protocol, field):
            setattr(protocol, field, value)

    await db.commit()
    await db.refresh(protocol)
    return protocol


async def submit_for_review(
    study_id: int,
    db: AsyncSession,
    arq_pool: Any,
) -> str:
    """Submit the protocol for AI review via an ARQ background job.

    Validates that all required fields are present, sets ``status`` to
    ``under_review``, and enqueues the ``run_protocol_review`` ARQ job.

    Args:
        study_id: The study whose protocol to submit.
        db: Active async database session.
        arq_pool: ARQ connection pool for job enqueueing.

    Returns:
        The ARQ job ID string.

    Raises:
        HTTPException: 404 if no protocol exists for the study.
        HTTPException: 422 if required fields are missing.

    """
    bound = logger.bind(study_id=study_id)
    protocol = await get_protocol(study_id, db)
    if protocol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No protocol found for this study.",
        )

    _validate_completeness(protocol)

    protocol.status = ReviewProtocolStatus.UNDER_REVIEW
    await db.commit()
    await db.refresh(protocol)

    job = await arq_pool.enqueue_job(
        "run_protocol_review",
        study_id=study_id,
        protocol_id=protocol.id,
    )
    job_id: str = job.job_id
    bound.info("submit_for_review: enqueued", job_id=job_id)
    return job_id


async def validate_protocol(
    study_id: int,
    db: AsyncSession,
) -> ReviewProtocol:
    """Approve and validate the reviewed protocol.

    Sets ``status`` to ``validated`` so the study can proceed to the
    search phase.

    Args:
        study_id: The study whose protocol to validate.
        db: Active async database session.

    Returns:
        The updated :class:`ReviewProtocol` instance.

    Raises:
        HTTPException: 404 if no protocol exists for the study.
        HTTPException: 422 if ``review_report`` is ``None`` (not yet reviewed).

    """
    bound = logger.bind(study_id=study_id)
    protocol = await get_protocol(study_id, db)
    if protocol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No protocol found for this study.",
        )

    if protocol.review_report is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Protocol has not been reviewed yet. Submit for AI review first.",
        )

    protocol.status = ReviewProtocolStatus.VALIDATED
    await db.commit()
    await db.refresh(protocol)
    bound.info("validate_protocol: protocol validated")
    return protocol


def _validate_completeness(protocol: ReviewProtocol) -> None:
    """Raise HTTP 422 if any required protocol field is empty.

    Args:
        protocol: The :class:`ReviewProtocol` to check.

    Raises:
        HTTPException: 422 listing the first missing required field.

    """
    for field in _REQUIRED_FIELDS:
        value = getattr(protocol, field, None)
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Required field '{field}' is missing or empty.",
            )
