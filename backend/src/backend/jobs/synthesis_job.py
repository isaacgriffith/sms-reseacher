"""ARQ background job for SLR data synthesis (feature 007)."""

from __future__ import annotations

from typing import Any

from backend.core.config import get_logger

logger = get_logger(__name__)


async def run_synthesis(
    ctx: dict[str, Any],
    *,
    synthesis_id: int,
) -> dict[str, Any]:
    """Execute a synthesis strategy for a :class:`SynthesisResult` record.

    Fetches the :class:`SynthesisResult` by ``synthesis_id``, resolves the
    appropriate strategy via the dispatch map, calls ``strategy.run()``, and
    writes the output fields back to the record.  On error the record is
    marked ``FAILED`` and the exception message is stored in
    ``error_message``.

    Args:
        ctx: ARQ worker context dict.
        synthesis_id: Primary key of the :class:`SynthesisResult` to execute.

    Returns:
        A dict with ``{status, synthesis_id, study_id}``.

    """
    from db.models.slr import SynthesisApproach, SynthesisResult, SynthesisStatus
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal
    from backend.services.synthesis_strategies import (
        DescriptiveSynthesizer,
        MetaAnalysisSynthesizer,
        NarrativeSynthesisStrategy,
        QualitativeSynthesizer,
        SynthesisStrategy,
        ThematicAnalysisStrategy,
    )

    _STRATEGY_MAP: dict[SynthesisApproach, SynthesisStrategy] = {
        SynthesisApproach.META_ANALYSIS: MetaAnalysisSynthesizer(),
        SynthesisApproach.DESCRIPTIVE: DescriptiveSynthesizer(),
        SynthesisApproach.QUALITATIVE: QualitativeSynthesizer(),
        SynthesisApproach.NARRATIVE: NarrativeSynthesisStrategy(),
        SynthesisApproach.THEMATIC: ThematicAnalysisStrategy(),
    }

    async with _session_maker() as db:
        result = await db.execute(select(SynthesisResult).where(SynthesisResult.id == synthesis_id))
        record = result.scalar_one_or_none()
        if record is None:
            logger.error("run_synthesis: record not found", synthesis_id=synthesis_id)
            return {"status": "failed", "synthesis_id": synthesis_id, "study_id": None}

        study_id: int = record.study_id
        bound_log = logger.bind(synthesis_id=synthesis_id, study_id=study_id)

        record.status = SynthesisStatus.RUNNING
        await db.commit()

        strategy = _STRATEGY_MAP.get(record.approach)
        if strategy is None:
            bound_log.error("run_synthesis: unknown approach", approach=record.approach)
            record.status = SynthesisStatus.FAILED
            record.error_message = f"Unknown synthesis approach: {record.approach}"
            await db.commit()
            return {"status": "failed", "synthesis_id": synthesis_id, "study_id": study_id}

        try:
            output = await strategy.run(record.study_id, record.parameters or {}, db)
            record.computed_statistics = output.computed_statistics
            record.forest_plot_svg = output.forest_plot_svg
            record.funnel_plot_svg = output.funnel_plot_svg
            record.qualitative_themes = output.qualitative_themes
            record.sensitivity_analysis = output.sensitivity_analysis
            record.status = SynthesisStatus.COMPLETED
            await db.commit()
        except Exception as exc:  # noqa: BLE001
            bound_log.error(
                "run_synthesis: strategy failed",
                exc=str(exc),
            )
            record.status = SynthesisStatus.FAILED
            record.error_message = str(exc)
            await db.commit()
            return {"status": "failed", "synthesis_id": synthesis_id, "study_id": study_id}

    bound_log.info("run_synthesis: completed")
    return {"status": "completed", "synthesis_id": synthesis_id, "study_id": study_id}
