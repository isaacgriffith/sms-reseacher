"""SLR report generation and export service (feature 007, Phase 8).

Assembles a structured SLR report from a study's protocol, synthesis
results, candidate papers, and data extractions, then exports it in one of
four formats: Markdown, LaTeX, JSON, or CSV.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime

import structlog
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.extraction import DataExtraction
from db.models.slr import GreyLiteratureSource, ReviewProtocol, SynthesisResult, SynthesisStatus
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schema
# ---------------------------------------------------------------------------


class SLRReport(BaseModel):
    """Structured SLR report with all ten standard sections.

    Attributes:
        study_id: The integer study ID this report belongs to.
        study_name: Human-readable study name.
        generated_at: ISO-8601 datetime string of report generation.
        background: Study background / motivation.
        review_questions: List of research questions.
        protocol_summary: Summary of the review protocol.
        search_process: Description of the search process.
        inclusion_exclusion_decisions: Summary of screening decisions.
        quality_assessment_results: Summary of quality assessment.
        extracted_data: Summary of extracted data fields.
        synthesis_results: Summary of synthesis outputs.
        validity_discussion: Threats to validity discussion.
        recommendations: Future research directions and recommendations.

    """

    study_id: int
    study_name: str
    generated_at: str
    background: str
    review_questions: list[str]
    protocol_summary: str
    search_process: str
    inclusion_exclusion_decisions: str
    quality_assessment_results: str
    extracted_data: str
    synthesis_results: str
    validity_discussion: str
    recommendations: str


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------


async def generate_report(study_id: int, db: AsyncSession) -> SLRReport:
    """Build and return an :class:`SLRReport` from the study's stored data.

    Fetches the study, its protocol, the most recently completed
    :class:`SynthesisResult`, grey literature sources, candidate papers, and
    data extractions.

    Args:
        study_id: The integer study whose report to generate.
        db: Active async database session.

    Returns:
        A fully populated :class:`SLRReport` instance.

    Raises:
        HTTPException: 404 if the study does not exist.
        HTTPException: 422 if no completed synthesis result exists.

    """
    from db.models import Study  # local import to avoid circular at module load

    bound = logger.bind(study_id=study_id)

    # -- Study --
    study_row = await db.get(Study, study_id)
    if study_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found.",
        )

    # -- Protocol (optional) --
    protocol_result = await db.execute(
        select(ReviewProtocol).where(ReviewProtocol.study_id == study_id)
    )
    protocol: ReviewProtocol | None = protocol_result.scalar_one_or_none()

    # -- Synthesis (required) --
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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "No completed synthesis result found for study "
                f"{study_id}. Complete the synthesis phase before exporting the report."
            ),
        )

    # -- Grey literature sources --
    grey_result = await db.execute(
        select(GreyLiteratureSource).where(GreyLiteratureSource.study_id == study_id)
    )
    grey_sources: list[GreyLiteratureSource] = list(grey_result.scalars().all())

    # -- Candidate papers --
    papers_result = await db.execute(
        select(CandidatePaper).where(CandidatePaper.study_id == study_id)
    )
    all_papers: list[CandidatePaper] = list(papers_result.scalars().all())
    accepted_papers = [p for p in all_papers if p.current_status == CandidatePaperStatus.ACCEPTED]
    excluded_papers = [p for p in all_papers if p.current_status == CandidatePaperStatus.REJECTED]

    # -- Data extractions --
    accepted_ids = [p.id for p in accepted_papers]
    extractions: list[DataExtraction] = []
    if accepted_ids:
        ext_result = await db.execute(
            select(DataExtraction).where(DataExtraction.candidate_paper_id.in_(accepted_ids))
        )
        extractions = list(ext_result.scalars().all())

    bound.info(
        "generate_report: assembled",
        n_accepted=len(accepted_papers),
        n_excluded=len(excluded_papers),
        n_extractions=len(extractions),
        n_grey=len(grey_sources),
    )

    # -- Assemble sections --
    study_name: str = getattr(study_row, "name", f"Study {study_id}")
    generated_at = datetime.now(tz=UTC).isoformat()

    background_text = (
        (protocol.background or "No background recorded.") if protocol else "No protocol recorded."
    )

    rqs: list[str] = []
    if protocol and protocol.research_questions:
        rqs = list(protocol.research_questions)
    else:
        # Try to pull research_questions from study metadata_ if available
        metadata = getattr(study_row, "metadata_", None) or {}
        rqs_from_meta = metadata.get("research_questions", []) if isinstance(metadata, dict) else []
        if rqs_from_meta:
            rqs = list(rqs_from_meta)

    protocol_summary = _build_protocol_summary(protocol)
    search_process = _build_search_process(grey_sources, len(all_papers))
    inclusion_exclusion = _build_inclusion_exclusion(
        len(all_papers), len(accepted_papers), len(excluded_papers), protocol
    )
    qa_results = _build_qa_results(synthesis)
    extracted_data_section = _build_extracted_data(extractions)
    synthesis_section = _build_synthesis_section(synthesis)
    validity = _build_validity(protocol)
    recommendations = _build_recommendations(synthesis, rqs)

    return SLRReport(
        study_id=study_id,
        study_name=study_name,
        generated_at=generated_at,
        background=background_text,
        review_questions=rqs,
        protocol_summary=protocol_summary,
        search_process=search_process,
        inclusion_exclusion_decisions=inclusion_exclusion,
        quality_assessment_results=qa_results,
        extracted_data=extracted_data_section,
        synthesis_results=synthesis_section,
        validity_discussion=validity,
        recommendations=recommendations,
    )


def export_report(report: SLRReport, format: str) -> tuple[bytes, str, str]:
    """Serialise a report to bytes in the requested format.

    Supported formats:
    - ``"markdown"`` — plain text Markdown document.
    - ``"latex"``    — minimal LaTeX article document.
    - ``"json"``     — JSON object (Pydantic model dump).
    - ``"csv"``      — two-column CSV (Section, Content).

    Args:
        report: The assembled :class:`SLRReport` to serialise.
        format: One of ``"markdown"``, ``"latex"``, ``"json"``, ``"csv"``.

    Returns:
        A 3-tuple of ``(content_bytes, mime_type, filename)``.

    Raises:
        HTTPException: 400 if an unknown format is requested.

    """
    rqs_text = (
        "\n".join(f"- {q}" for q in report.review_questions)
        if report.review_questions
        else "(none)"
    )

    if format == "markdown":
        lines = [
            f"# SLR Report: {report.study_name}\n",
            f"*Generated: {report.generated_at}*\n",
            "## Background\n",
            f"{report.background}\n",
            "## Research Questions\n",
            f"{rqs_text}\n",
            "## Protocol Summary\n",
            f"{report.protocol_summary}\n",
            "## Search Process\n",
            f"{report.search_process}\n",
            "## Inclusion / Exclusion Decisions\n",
            f"{report.inclusion_exclusion_decisions}\n",
            "## Quality Assessment Results\n",
            f"{report.quality_assessment_results}\n",
            "## Extracted Data\n",
            f"{report.extracted_data}\n",
            "## Synthesis Results\n",
            f"{report.synthesis_results}\n",
            "## Validity Discussion\n",
            f"{report.validity_discussion}\n",
            "## Recommendations\n",
            f"{report.recommendations}\n",
        ]
        content = "\n".join(lines).encode("utf-8")
        return content, "text/markdown", f"slr-report-{report.study_id}.md"

    if format == "latex":
        rqs_latex = (
            "\n".join(f"  \\item {q}" for q in report.review_questions)
            if report.review_questions
            else "  \\item (none)"
        )

        def _esc(text: str) -> str:
            """Escape common LaTeX special characters."""
            for ch, repl in [
                ("\\", "\\textbackslash{}"),
                ("&", "\\&"),
                ("%", "\\%"),
                ("$", "\\$"),
                ("#", "\\#"),
                ("_", "\\_"),
                ("{", "\\{"),
                ("}", "\\}"),
                ("~", "\\textasciitilde{}"),
                ("^", "\\textasciicircum{}"),
            ]:
                text = text.replace(ch, repl)
            return text

        doc = (
            "\\documentclass{article}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\usepackage[T1]{fontenc}\n"
            "\\begin{document}\n\n"
            f"\\title{{SLR Report: {_esc(report.study_name)}}}\n"
            f"\\date{{{_esc(report.generated_at)}}}\n"
            "\\maketitle\n\n"
            "\\section{Background}\n"
            f"{_esc(report.background)}\n\n"
            "\\section{Research Questions}\n"
            "\\begin{itemize}\n"
            f"{rqs_latex}\n"
            "\\end{itemize}\n\n"
            "\\section{Protocol Summary}\n"
            f"{_esc(report.protocol_summary)}\n\n"
            "\\section{Search Process}\n"
            f"{_esc(report.search_process)}\n\n"
            "\\section{Inclusion / Exclusion Decisions}\n"
            f"{_esc(report.inclusion_exclusion_decisions)}\n\n"
            "\\section{Quality Assessment Results}\n"
            f"{_esc(report.quality_assessment_results)}\n\n"
            "\\section{Extracted Data}\n"
            f"{_esc(report.extracted_data)}\n\n"
            "\\section{Synthesis Results}\n"
            f"{_esc(report.synthesis_results)}\n\n"
            "\\section{Validity Discussion}\n"
            f"{_esc(report.validity_discussion)}\n\n"
            "\\section{Recommendations}\n"
            f"{_esc(report.recommendations)}\n\n"
            "\\end{document}\n"
        )
        return doc.encode("utf-8"), "application/x-latex", f"slr-report-{report.study_id}.tex"

    if format == "json":
        content = report.model_dump_json().encode("utf-8")
        return content, "application/json", f"slr-report-{report.study_id}.json"

    if format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Section", "Content"])
        writer.writerow(["Background", report.background])
        writer.writerow(["Research Questions", rqs_text])
        writer.writerow(["Protocol Summary", report.protocol_summary])
        writer.writerow(["Search Process", report.search_process])
        writer.writerow(["Inclusion/Exclusion Decisions", report.inclusion_exclusion_decisions])
        writer.writerow(["Quality Assessment Results", report.quality_assessment_results])
        writer.writerow(["Extracted Data", report.extracted_data])
        writer.writerow(["Synthesis Results", report.synthesis_results])
        writer.writerow(["Validity Discussion", report.validity_discussion])
        writer.writerow(["Recommendations", report.recommendations])
        content = buf.getvalue().encode("utf-8")
        return content, "text/csv", f"slr-report-{report.study_id}.csv"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported export format '{format}'. Choose from: markdown, latex, json, csv.",
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_protocol_summary(protocol: ReviewProtocol | None) -> str:
    """Return a concise protocol summary string.

    Args:
        protocol: The :class:`ReviewProtocol` ORM row, or ``None``.

    Returns:
        A human-readable summary of the protocol.

    """
    if protocol is None:
        return "No protocol recorded for this study."
    parts = []
    if protocol.rationale:
        parts.append(f"Rationale: {protocol.rationale}")
    if protocol.synthesis_approach:
        parts.append(f"Synthesis approach: {protocol.synthesis_approach}")
    if protocol.data_extraction_strategy:
        parts.append(f"Extraction strategy: {protocol.data_extraction_strategy}")
    if protocol.dissemination_strategy:
        parts.append(f"Dissemination: {protocol.dissemination_strategy}")
    if not parts:
        return "Protocol exists but no details have been entered yet."
    return " | ".join(parts)


def _build_search_process(
    grey_sources: list[GreyLiteratureSource],
    total_papers: int,
) -> str:
    """Summarise the search process including grey literature.

    Args:
        grey_sources: Grey literature sources collected for the study.
        total_papers: Total candidate papers retrieved from databases.

    Returns:
        A human-readable search process summary.

    """
    summary = f"A total of {total_papers} candidate paper(s) were identified via database search."
    if grey_sources:
        types = [s.source_type.value for s in grey_sources]
        summary += (
            f" Additionally, {len(grey_sources)} grey literature source(s) were tracked"
            f" ({', '.join(types)})."
        )
    return summary


def _build_inclusion_exclusion(
    total: int,
    accepted: int,
    excluded: int,
    protocol: ReviewProtocol | None,
) -> str:
    """Summarise screening decisions.

    Args:
        total: Total candidate papers screened.
        accepted: Number accepted.
        excluded: Number excluded.
        protocol: The review protocol (for criteria text), or ``None``.

    Returns:
        A human-readable inclusion/exclusion summary.

    """
    criteria_text = ""
    if protocol:
        inc = protocol.inclusion_criteria
        exc = protocol.exclusion_criteria
        if inc:
            criteria_text += f" Inclusion criteria applied: {'; '.join(inc)}."
        if exc:
            criteria_text += f" Exclusion criteria applied: {'; '.join(exc)}."
    return (
        f"Of {total} screened papers, {accepted} were accepted and {excluded} were excluded."
        f"{criteria_text}"
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
        return f"Quality assessment was performed. Computed statistics include: {stats_keys}."
    return "Quality assessment was completed. No computed statistics are available."


def _build_extracted_data(extractions: list[DataExtraction]) -> str:
    """Summarise the extracted data.

    Args:
        extractions: List of :class:`DataExtraction` rows for accepted papers.

    Returns:
        A human-readable extraction summary.

    """
    if not extractions:
        return "No data extractions were found for the accepted papers."
    with_summary = sum(1 for e in extractions if e.summary)
    return (
        f"{len(extractions)} data extraction(s) were completed,"
        f" {with_summary} of which have a textual summary."
    )


def _build_synthesis_section(synthesis: SynthesisResult) -> str:
    """Summarise synthesis results.

    Args:
        synthesis: The completed :class:`SynthesisResult`.

    Returns:
        A human-readable synthesis summary.

    """
    parts = [f"Synthesis approach: {synthesis.approach.value}."]
    if synthesis.computed_statistics:
        parts.append(
            f"Key statistics computed: {json.dumps(synthesis.computed_statistics, default=str)}."
        )
    if synthesis.qualitative_themes:
        n = len(synthesis.qualitative_themes)
        parts.append(f"{n} qualitative theme(s) identified.")
    return " ".join(parts)


def _build_validity(protocol: ReviewProtocol | None) -> str:
    """Produce a threats-to-validity discussion section.

    Args:
        protocol: The review protocol, or ``None``.

    Returns:
        A human-readable validity discussion.

    """
    base = (
        "Potential threats to validity include publication bias, database "
        "coverage limitations, and inter-rater variability during screening."
    )
    if protocol and protocol.search_strategy:
        base += f" The search strategy was: {protocol.search_strategy}."
    return base


def _build_recommendations(synthesis: SynthesisResult, rqs: list[str]) -> str:
    """Build a recommendations section based on synthesis outputs.

    Args:
        synthesis: The completed synthesis result.
        rqs: Research questions addressed by the review.

    Returns:
        A human-readable recommendations string.

    """
    parts = ["Future work should address gaps identified in this review."]
    if rqs:
        parts.append(
            f"This review addressed {len(rqs)} research question(s);"
            " follow-up studies may build on these findings."
        )
    if synthesis.sensitivity_analysis:
        parts.append(
            "Sensitivity analysis was performed; results should be interpreted with caution."
        )
    return " ".join(parts)
