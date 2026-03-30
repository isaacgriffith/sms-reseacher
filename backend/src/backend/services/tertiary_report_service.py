"""Tertiary Study report generation and export service (feature 009).

Assembles a structured Tertiary Study report from the study's protocol,
synthesis results, candidate papers, and secondary-study extraction records.
The report extends the SLR report structure with a
``landscape_of_secondary_studies`` section that covers timeline, research
question evolution, and synthesis method shifts across the reviewed secondary
studies.
"""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime

import structlog
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.slr import SynthesisResult, SynthesisStatus
from db.models.tertiary import TertiaryDataExtraction, TertiaryStudyProtocol
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class LandscapeSection(BaseModel):
    """Landscape of secondary studies section of a Tertiary Report.

    Attributes:
        timeline_summary: Aggregated study period coverage across all secondary
            studies.
        research_question_evolution: Narrative of how research questions have
            shifted over time across the reviewed secondary studies.
        synthesis_method_shifts: Summary of synthesis methods used by the
            reviewed secondary studies and how they have changed.

    """

    timeline_summary: str
    research_question_evolution: str
    synthesis_method_shifts: str


class TertiaryReport(BaseModel):
    """Structured Tertiary Study report with all standard sections.

    Extends the SLR report with a
    :attr:`landscape_of_secondary_studies` section.

    Attributes:
        study_id: The integer study ID this report belongs to.
        study_name: Human-readable study name.
        generated_at: ISO-8601 datetime string of report generation.
        background: Study background / motivation.
        review_questions: List of research questions.
        protocol_summary: Summary of the review protocol.
        inclusion_exclusion_decisions: Summary of screening decisions.
        quality_assessment_results: Summary of quality assessment.
        extracted_data: Summary of extracted secondary-study fields.
        synthesis_results: Summary of synthesis outputs.
        landscape_of_secondary_studies: Timeline, RQ evolution, and synthesis
            method shifts across the reviewed secondary studies.
        recommendations: Future research directions.

    """

    study_id: int
    study_name: str
    generated_at: str
    background: str
    review_questions: list[str]
    protocol_summary: str
    inclusion_exclusion_decisions: str
    quality_assessment_results: str
    extracted_data: str
    synthesis_results: str
    landscape_of_secondary_studies: LandscapeSection
    recommendations: str

    def to_json(self) -> bytes:
        """Serialise the report to JSON bytes.

        Returns:
            UTF-8 encoded JSON representation of the report.

        """
        return self.model_dump_json().encode("utf-8")

    def to_csv(self) -> bytes:
        """Serialise the report to CSV bytes (Section, Content columns).

        Returns:
            UTF-8 encoded CSV with one row per report section.

        """
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Section", "Content"])
        rqs_text = (
            "\n".join(f"- {q}" for q in self.review_questions)
            if self.review_questions
            else "(none)"
        )
        writer.writerow(["Background", self.background])
        writer.writerow(["Research Questions", rqs_text])
        writer.writerow(["Protocol Summary", self.protocol_summary])
        writer.writerow(["Inclusion/Exclusion Decisions", self.inclusion_exclusion_decisions])
        writer.writerow(["Quality Assessment Results", self.quality_assessment_results])
        writer.writerow(["Extracted Data", self.extracted_data])
        writer.writerow(["Synthesis Results", self.synthesis_results])
        ls = self.landscape_of_secondary_studies
        writer.writerow(["Landscape: Timeline", ls.timeline_summary])
        writer.writerow(["Landscape: RQ Evolution", ls.research_question_evolution])
        writer.writerow(["Landscape: Synthesis Method Shifts", ls.synthesis_method_shifts])
        writer.writerow(["Recommendations", self.recommendations])
        return buf.getvalue().encode("utf-8")

    def to_markdown(self) -> bytes:
        """Serialise the report to Markdown bytes.

        Returns:
            UTF-8 encoded Markdown document.

        """
        rqs_text = (
            "\n".join(f"- {q}" for q in self.review_questions)
            if self.review_questions
            else "(none)"
        )
        landscape = self.landscape_of_secondary_studies
        lines = [
            f"# Tertiary Study Report: {self.study_name}\n",
            f"*Generated: {self.generated_at}*\n",
            "## Background\n",
            f"{self.background}\n",
            "## Research Questions\n",
            f"{rqs_text}\n",
            "## Protocol Summary\n",
            f"{self.protocol_summary}\n",
            "## Inclusion / Exclusion Decisions\n",
            f"{self.inclusion_exclusion_decisions}\n",
            "## Quality Assessment Results\n",
            f"{self.quality_assessment_results}\n",
            "## Extracted Data\n",
            f"{self.extracted_data}\n",
            "## Synthesis Results\n",
            f"{self.synthesis_results}\n",
            "## Landscape of Secondary Studies\n",
            "### Timeline\n",
            f"{landscape.timeline_summary}\n",
            "### Research Question Evolution\n",
            f"{landscape.research_question_evolution}\n",
            "### Synthesis Method Shifts\n",
            f"{landscape.synthesis_method_shifts}\n",
            "## Recommendations\n",
            f"{self.recommendations}\n",
        ]
        return "\n".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class TertiaryReportService:
    """Service for generating and exporting Tertiary Study reports.

    All methods are async-first and require a live :class:`AsyncSession` passed
    in by the caller.
    """

    async def generate_report(
        self,
        study_id: int,
        db: AsyncSession,
    ) -> TertiaryReport:
        """Build and return a :class:`TertiaryReport` from the study's stored data.

        Fetches the study, its tertiary protocol, the most recently completed
        :class:`SynthesisResult`, accepted candidate papers, and tertiary data
        extraction records to assemble all report sections.

        Args:
            study_id: The integer study whose report to generate.
            db: Active async database session.

        Returns:
            A fully populated :class:`TertiaryReport` instance.

        Raises:
            HTTPException: 404 if the study does not exist or is not TERTIARY type.
            HTTPException: 409 if no completed synthesis result exists (Phase 5
                not yet reached).

        """
        from db.models import Study, StudyType  # local import to avoid circular at module load

        bound = logger.bind(study_id=study_id)

        # -- Study --
        study_row = await db.get(Study, study_id)
        if study_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Study {study_id} not found.",
            )

        study_type = getattr(study_row, "study_type", None)
        if study_type is not None and study_type != StudyType.TERTIARY:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Study {study_id} is not a Tertiary Study.",
            )

        # -- Tertiary Protocol (optional) --
        protocol_result = await db.execute(
            select(TertiaryStudyProtocol).where(TertiaryStudyProtocol.study_id == study_id)
        )
        protocol: TertiaryStudyProtocol | None = protocol_result.scalar_one_or_none()

        # -- Synthesis (required for Phase 5) --
        synthesis_result = await db.execute(
            select(SynthesisResult)
            .where(
                SynthesisResult.study_id == study_id,
                SynthesisResult.status == SynthesisStatus.COMPLETED,
            )
            .order_by(SynthesisResult.created_at.desc())
            .limit(1)
        )
        synthesis: SynthesisResult | None = synthesis_result.scalar_one_or_none()
        if synthesis is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Study {study_id} has not completed synthesis. "
                    "Complete Phase 5 (Synthesis) before generating the report."
                ),
            )

        # -- Candidate papers --
        papers_result = await db.execute(
            select(CandidatePaper).where(CandidatePaper.study_id == study_id)
        )
        all_papers: list[CandidatePaper] = list(papers_result.scalars().all())
        accepted_papers = [
            p for p in all_papers if p.current_status == CandidatePaperStatus.ACCEPTED
        ]
        excluded_papers = [
            p for p in all_papers if p.current_status == CandidatePaperStatus.REJECTED
        ]

        # -- Tertiary data extractions --
        accepted_ids = [p.id for p in accepted_papers]
        extractions: list[TertiaryDataExtraction] = []
        if accepted_ids:
            ext_result = await db.execute(
                select(TertiaryDataExtraction).where(
                    TertiaryDataExtraction.candidate_paper_id.in_(accepted_ids)
                )
            )
            extractions = list(ext_result.scalars().all())

        bound.info(
            "generate_report: assembled",
            n_accepted=len(accepted_papers),
            n_excluded=len(excluded_papers),
            n_extractions=len(extractions),
        )

        # -- Assemble sections --
        study_name: str = getattr(study_row, "name", f"Study {study_id}")
        generated_at = datetime.now(tz=UTC).isoformat()

        background_text = (
            (protocol.background or "No background recorded.")
            if protocol
            else "No protocol recorded."
        )

        rqs: list[str] = []
        if protocol and protocol.research_questions:
            rqs = list(protocol.research_questions)

        protocol_summary = _build_protocol_summary(protocol)
        inclusion_exclusion = _build_inclusion_exclusion(
            len(all_papers), len(accepted_papers), len(excluded_papers), protocol
        )
        qa_results = _build_qa_results(synthesis)
        extracted_data_section = _build_extracted_data(extractions)
        synthesis_section = _build_synthesis_section(synthesis)
        landscape = _build_landscape_section(extractions)
        recommendations = _build_recommendations(synthesis, rqs)

        return TertiaryReport(
            study_id=study_id,
            study_name=study_name,
            generated_at=generated_at,
            background=background_text,
            review_questions=rqs,
            protocol_summary=protocol_summary,
            inclusion_exclusion_decisions=inclusion_exclusion,
            quality_assessment_results=qa_results,
            extracted_data=extracted_data_section,
            synthesis_results=synthesis_section,
            landscape_of_secondary_studies=landscape,
            recommendations=recommendations,
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_protocol_summary(protocol: TertiaryStudyProtocol | None) -> str:
    """Return a concise protocol summary string.

    Args:
        protocol: The :class:`TertiaryStudyProtocol` ORM row, or ``None``.

    Returns:
        A human-readable summary of the protocol.

    """
    if protocol is None:
        return "No protocol recorded for this study."
    parts = []
    if protocol.background:
        bg = protocol.background
        short = f"{bg[:120]}{'…' if len(bg) > 120 else ''}"
        parts.append(f"Background: {short}")
    if protocol.secondary_study_types:
        types_str = ", ".join(str(t) for t in protocol.secondary_study_types)
        parts.append(f"Study types reviewed: {types_str}")
    if protocol.synthesis_approach:
        parts.append(f"Synthesis approach: {protocol.synthesis_approach}")
    if protocol.recency_cutoff_year:
        parts.append(f"Recency cutoff: {protocol.recency_cutoff_year}")
    if protocol.quality_threshold is not None:
        parts.append(f"Quality threshold: {protocol.quality_threshold:.2f}")
    if not parts:
        return "Protocol exists but no details have been entered yet."
    return " | ".join(parts)


def _build_inclusion_exclusion(
    total: int,
    accepted: int,
    excluded: int,
    protocol: TertiaryStudyProtocol | None,
) -> str:
    """Summarise screening decisions.

    Args:
        total: Total candidate papers screened.
        accepted: Number accepted.
        excluded: Number excluded.
        protocol: The tertiary protocol (for criteria text), or ``None``.

    Returns:
        A human-readable inclusion/exclusion summary.

    """
    criteria_text = ""
    if protocol:
        inc = protocol.inclusion_criteria
        exc = protocol.exclusion_criteria
        if inc:
            criteria_text += f" Inclusion criteria: {'; '.join(str(c) for c in inc)}."
        if exc:
            criteria_text += f" Exclusion criteria: {'; '.join(str(c) for c in exc)}."
    return (
        f"Of {total} screened secondary studies, {accepted} were accepted "
        f"and {excluded} were excluded.{criteria_text}"
    )


def _build_qa_results(synthesis: SynthesisResult) -> str:
    """Summarise quality assessment outcomes from the synthesis.

    Args:
        synthesis: The completed :class:`SynthesisResult`.

    Returns:
        A human-readable QA summary.

    """
    if synthesis.computed_statistics:
        stats_keys = ", ".join(str(k) for k in synthesis.computed_statistics.keys())
        return f"Quality assessment was performed. Computed statistics: {stats_keys}."
    return "Quality assessment was completed. No computed statistics are available."


def _build_extracted_data(extractions: list[TertiaryDataExtraction]) -> str:
    """Summarise the tertiary extraction data.

    Args:
        extractions: List of :class:`TertiaryDataExtraction` rows for accepted papers.

    Returns:
        A human-readable extraction summary.

    """
    if not extractions:
        return "No data extractions were found for the accepted secondary studies."
    with_findings = sum(1 for e in extractions if e.key_findings)
    with_gaps = sum(1 for e in extractions if e.research_gaps)
    _done = ("validated", "human_reviewed")
    validated = sum(1 for e in extractions if e.extraction_status in _done)
    return (
        f"{len(extractions)} secondary study extraction(s) completed: "
        f"{with_findings} with key findings, {with_gaps} with research gaps, "
        f"{validated} validated by a reviewer."
    )


def _build_synthesis_section(synthesis: SynthesisResult) -> str:
    """Summarise synthesis results.

    Args:
        synthesis: The completed :class:`SynthesisResult`.

    Returns:
        A human-readable synthesis summary.

    """
    parts = [f"Synthesis approach: {synthesis.approach.value}."]
    if synthesis.qualitative_themes:
        themes = synthesis.qualitative_themes
        if "narrative" in themes:
            # Truncate the narrative for the section summary.
            narrative: str = str(themes["narrative"])
            parts.append(f"Narrative: {narrative[:200]}{'…' if len(narrative) > 200 else ''}")
        elif "themes" in themes:
            n = len(themes["themes"]) if isinstance(themes["themes"], dict) else 0
            parts.append(f"{n} thematic cluster(s) identified.")
    return " ".join(parts)


def _build_landscape_section(extractions: list[TertiaryDataExtraction]) -> LandscapeSection:
    """Derive the Landscape of Secondary Studies section from extraction records.

    Args:
        extractions: List of validated/completed :class:`TertiaryDataExtraction` rows.

    Returns:
        A :class:`LandscapeSection` with timeline, RQ evolution, and synthesis
        method shifts.

    """
    # -- Timeline summary --
    years_start: list[int] = [e.study_period_start for e in extractions if e.study_period_start]
    years_end: list[int] = [e.study_period_end for e in extractions if e.study_period_end]
    if years_start and years_end:
        earliest = min(years_start)
        latest = max(years_end)
        timeline_summary = (
            f"The secondary studies collectively span the period {earliest}–{latest}. "
            f"{len(extractions)} secondary studies were included, covering "
            f"research published over approximately {latest - earliest + 1} years."
        )
    elif extractions:
        timeline_summary = (
            f"{len(extractions)} secondary studies were included. "
            "Specific study periods were not fully recorded."
        )
    else:
        timeline_summary = (
            "No secondary study extraction records were available for timeline analysis."
        )

    # -- Research question evolution --
    all_rqs: list[str] = []
    for e in extractions:
        if e.research_questions_addressed:
            all_rqs.extend(str(rq) for rq in e.research_questions_addressed)
    unique_rqs = list(dict.fromkeys(all_rqs))  # deduplicate while preserving order
    if unique_rqs:
        sample = unique_rqs[:5]
        rq_evolution = (
            f"{len(unique_rqs)} unique research question(s) were addressed across "
            f"the {len(extractions)} secondary studies. "
            f"Representative questions include: {'; '.join(sample)}"
            f"{'…' if len(unique_rqs) > 5 else '.'}"
        )
    else:
        rq_evolution = (
            "Research questions addressed by the included secondary studies "
            "were not recorded in the extraction data."
        )

    # -- Synthesis method shifts --
    approaches: list[str] = [
        e.synthesis_approach_used for e in extractions if e.synthesis_approach_used
    ]
    if approaches:
        approach_counts: dict[str, int] = {}
        for a in approaches:
            approach_counts[a] = approach_counts.get(a, 0) + 1
        sorted_approaches = sorted(approach_counts.items(), key=lambda x: -x[1])
        top = [f"{name} ({count})" for name, count in sorted_approaches[:5]]
        method_shifts = (
            f"The {len(extractions)} secondary studies employed {len(approach_counts)} "
            f"distinct synthesis method(s). "
            f"Most common: {', '.join(top)}."
        )
    else:
        method_shifts = (
            "Synthesis methods used by the included secondary studies "
            "were not recorded in the extraction data."
        )

    return LandscapeSection(
        timeline_summary=timeline_summary,
        research_question_evolution=rq_evolution,
        synthesis_method_shifts=method_shifts,
    )


def _build_recommendations(synthesis: SynthesisResult, rqs: list[str]) -> str:
    """Build a recommendations section based on synthesis outputs.

    Args:
        synthesis: The completed synthesis result.
        rqs: Research questions addressed by the review.

    Returns:
        A human-readable recommendations string.

    """
    parts = ["Future work should address gaps identified in this tertiary review."]
    if rqs:
        parts.append(
            f"This review addressed {len(rqs)} research question(s); "
            "follow-up studies may build on these findings."
        )
    if synthesis.qualitative_themes:
        themes = synthesis.qualitative_themes
        if "themes" in themes and isinstance(themes["themes"], dict):
            n = len(themes["themes"])
            parts.append(
                f"Thematic analysis identified {n} theme(s); "
                "each represents an opportunity for targeted primary research."
            )
    return " ".join(parts)
