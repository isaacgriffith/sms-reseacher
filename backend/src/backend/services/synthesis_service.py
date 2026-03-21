"""Synthesis service for SLR workflow (feature 007).

Provides high-level helpers to list, create, and retrieve
:class:`SynthesisResult` records.  Job enqueuing is handled via the ARQ
pool so the actual synthesis computation runs outside the request cycle.
"""

from __future__ import annotations

from typing import Any

import structlog
from db.models.slr import SynthesisApproach, SynthesisResult, SynthesisStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


async def list_results(
    study_id: int,
    db: AsyncSession,
) -> list[SynthesisResult]:
    """Return all synthesis results for a study ordered by creation time.

    Args:
        study_id: The study whose results to retrieve.
        db: Active async database session.

    Returns:
        All :class:`SynthesisResult` rows ordered oldest-first.

    """
    result = await db.execute(
        select(SynthesisResult)
        .where(SynthesisResult.study_id == study_id)
        .order_by(SynthesisResult.created_at)
    )
    return list(result.scalars().all())


async def start_synthesis(
    study_id: int,
    approach: str,
    parameters: dict[str, Any],
    db: AsyncSession,
    arq_pool: Any,
) -> SynthesisResult:
    """Create a PENDING :class:`SynthesisResult` and enqueue the ARQ job.

    The ``model_type`` field is extracted from ``parameters`` when present
    so it is visible at a glance on the record without parsing the full JSON.

    Args:
        study_id: The study the synthesis belongs to.
        approach: One of ``"meta_analysis"``, ``"descriptive"``,
            ``"qualitative"``.
        parameters: Synthesis configuration dict passed verbatim to the job.
        db: Active async database session.
        arq_pool: An active ARQ Redis pool used to enqueue the background job.

    Returns:
        The newly created :class:`SynthesisResult` with ``status=PENDING``.

    """
    bound = logger.bind(study_id=study_id, approach=approach)

    model_type: str | None = parameters.get("model_type") if parameters else None

    record = SynthesisResult(
        study_id=study_id,
        approach=SynthesisApproach(approach),
        status=SynthesisStatus.PENDING,
        model_type=model_type,
        parameters=parameters,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await arq_pool.enqueue_job("run_synthesis", synthesis_id=record.id)

    bound.info("start_synthesis: enqueued", synthesis_id=record.id)
    return record


async def get_result(
    synthesis_id: int,
    db: AsyncSession,
) -> SynthesisResult | None:
    """Fetch a single :class:`SynthesisResult` by primary key.

    Args:
        synthesis_id: Primary key of the :class:`SynthesisResult`.
        db: Active async database session.

    Returns:
        The :class:`SynthesisResult` if found, else ``None``.

    """
    result = await db.execute(select(SynthesisResult).where(SynthesisResult.id == synthesis_id))
    return result.scalar_one_or_none()
