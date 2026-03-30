"""Unit tests for TertiaryReportService.generate_report (feature 009, T043).

Tests cover:
- generate_report returns TertiaryReport with all sections populated.
- generate_report raises HTTPException(404) when study not found.
- generate_report raises HTTPException(409) when no completed synthesis.
- landscape_of_secondary_studies section derives from extraction records.
- landscape timeline uses study_period_start/end from extraction records.
- landscape RQ evolution reflects research_questions_addressed values.
- landscape synthesis_method_shifts reflects synthesis_approach_used values.
- to_json() serialises to valid UTF-8 JSON bytes.
- to_csv() serialises to CSV bytes with Section/Content columns.
- to_markdown() serialises to Markdown bytes with expected headings.
"""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
import db.models  # noqa: F401
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.slr  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.tertiary  # noqa: F401


@pytest_asyncio.fixture
async def db_session():
    """Provide a per-test in-memory SQLite session with all tables.

    Yields:
        An :class:`~sqlalchemy.ext.asyncio.AsyncSession` backed by SQLite
        in-memory storage.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session

    await engine.dispose()


async def _insert_tertiary_study(db: AsyncSession, name: str = "Tertiary Report Test") -> int:
    """Insert a Tertiary Study and return its id.

    Args:
        db: Active async database session.
        name: Study name.

    Returns:
        Integer study id.
    """
    from db.models.users import ResearchGroup
    from db.models import Study, StudyType, StudyStatus

    group = ResearchGroup(name=f"Group {name}")
    db.add(group)
    await db.flush()

    study = Study(
        name=name,
        research_group_id=group.id,
        study_type=StudyType.TERTIARY,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


async def _insert_completed_synthesis(db: AsyncSession, study_id: int) -> int:
    """Insert a completed SynthesisResult and return its id.

    Args:
        db: Active async database session.
        study_id: The study to attach the synthesis to.

    Returns:
        Integer synthesis result id.
    """
    from db.models.slr import SynthesisResult, SynthesisApproach, SynthesisStatus

    sr = SynthesisResult(
        study_id=study_id,
        approach=SynthesisApproach.DESCRIPTIVE,
        status=SynthesisStatus.COMPLETED,
        computed_statistics={"n_studies": 3},
    )
    db.add(sr)
    await db.commit()
    await db.refresh(sr)
    return sr.id


async def _insert_accepted_candidate_paper(db: AsyncSession, study_id: int, doi: str) -> int:
    """Insert a Paper and an accepted CandidatePaper, return candidate paper id.

    Args:
        db: Active async database session.
        study_id: The study the paper belongs to.
        doi: DOI for the paper.

    Returns:
        Integer candidate paper id.
    """
    from db.models import Paper
    from db.models.candidate import CandidatePaper, CandidatePaperStatus
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution, SearchExecutionStatus

    # Re-use existing search execution if available; otherwise create one.
    from sqlalchemy import select

    se_result = await db.execute(
        select(SearchExecution).where(SearchExecution.study_id == study_id).limit(1)
    )
    se = se_result.scalar_one_or_none()
    if se is None:
        ss = SearchString(study_id=study_id, version=1, string_text="sentinel", is_active=False)
        db.add(ss)
        await db.flush()
        se = SearchExecution(
            study_id=study_id,
            search_string_id=ss.id,
            status=SearchExecutionStatus.COMPLETED,
        )
        db.add(se)
        await db.flush()

    paper = Paper(title=f"Paper {doi}", doi=doi)
    db.add(paper)
    await db.flush()

    cp = CandidatePaper(
        study_id=study_id,
        paper_id=paper.id,
        search_execution_id=se.id,
        phase_tag="phase2",
        current_status=CandidatePaperStatus.ACCEPTED,
    )
    db.add(cp)
    await db.flush()
    return cp.id


async def _insert_extraction(
    db: AsyncSession,
    candidate_paper_id: int,
    *,
    study_period_start: int | None = None,
    study_period_end: int | None = None,
    research_questions_addressed: list[str] | None = None,
    synthesis_approach_used: str | None = None,
    key_findings: str | None = None,
    research_gaps: str | None = None,
    extraction_status: str = "validated",
) -> int:
    """Insert a TertiaryDataExtraction, return its id.

    Args:
        db: Active async database session.
        candidate_paper_id: FK to the candidate paper.
        study_period_start: Start year of the study period.
        study_period_end: End year of the study period.
        research_questions_addressed: List of RQ strings.
        synthesis_approach_used: Synthesis method label.
        key_findings: Key findings text.
        research_gaps: Research gaps text.
        extraction_status: Status string (default "validated").

    Returns:
        Integer extraction id.
    """
    from db.models.tertiary import TertiaryDataExtraction

    ext = TertiaryDataExtraction(
        candidate_paper_id=candidate_paper_id,
        study_period_start=study_period_start,
        study_period_end=study_period_end,
        research_questions_addressed=research_questions_addressed,
        synthesis_approach_used=synthesis_approach_used,
        key_findings=key_findings,
        research_gaps=research_gaps,
        extraction_status=extraction_status,
    )
    db.add(ext)
    await db.flush()
    return ext.id


# ---------------------------------------------------------------------------
# Tests: generate_report
# ---------------------------------------------------------------------------


class TestGenerateReport:
    """TertiaryReportService.generate_report correctness."""

    @pytest.mark.asyncio
    async def test_returns_tertiary_report_all_sections(self, db_session) -> None:
        """generate_report returns a TertiaryReport with all required sections."""
        from backend.services.tertiary_report_service import TertiaryReportService, TertiaryReport

        study_id = await _insert_tertiary_study(db_session)
        await _insert_completed_synthesis(db_session, study_id)

        svc = TertiaryReportService()
        report = await svc.generate_report(study_id, db_session)

        assert isinstance(report, TertiaryReport)
        assert report.study_id == study_id
        assert isinstance(report.study_name, str)
        assert isinstance(report.generated_at, str)
        assert isinstance(report.background, str)
        assert isinstance(report.review_questions, list)
        assert isinstance(report.protocol_summary, str)
        assert isinstance(report.inclusion_exclusion_decisions, str)
        assert isinstance(report.quality_assessment_results, str)
        assert isinstance(report.extracted_data, str)
        assert isinstance(report.synthesis_results, str)
        assert report.landscape_of_secondary_studies is not None
        assert isinstance(report.landscape_of_secondary_studies.timeline_summary, str)
        assert isinstance(report.landscape_of_secondary_studies.research_question_evolution, str)
        assert isinstance(report.landscape_of_secondary_studies.synthesis_method_shifts, str)
        assert isinstance(report.recommendations, str)

    @pytest.mark.asyncio
    async def test_raises_404_when_study_not_found(self, db_session) -> None:
        """generate_report raises HTTPException(404) when study does not exist."""
        from fastapi import HTTPException
        from backend.services.tertiary_report_service import TertiaryReportService

        svc = TertiaryReportService()
        with pytest.raises(HTTPException) as exc_info:
            await svc.generate_report(99999, db_session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_409_when_no_completed_synthesis(self, db_session) -> None:
        """generate_report raises HTTPException(409) when synthesis not completed."""
        from fastapi import HTTPException
        from backend.services.tertiary_report_service import TertiaryReportService

        study_id = await _insert_tertiary_study(db_session)
        svc = TertiaryReportService()

        with pytest.raises(HTTPException) as exc_info:
            await svc.generate_report(study_id, db_session)

        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Tests: landscape_of_secondary_studies
# ---------------------------------------------------------------------------


class TestLandscapeSection:
    """landscape_of_secondary_studies is derived from extraction records."""

    @pytest.mark.asyncio
    async def test_timeline_uses_study_period_years(self, db_session) -> None:
        """Timeline summary includes the correct earliest and latest years."""
        from backend.services.tertiary_report_service import TertiaryReportService

        study_id = await _insert_tertiary_study(db_session)
        await _insert_completed_synthesis(db_session, study_id)

        cp1 = await _insert_accepted_candidate_paper(db_session, study_id, "10.0/p1")
        cp2 = await _insert_accepted_candidate_paper(db_session, study_id, "10.0/p2")
        await _insert_extraction(db_session, cp1, study_period_start=2010, study_period_end=2018)
        await _insert_extraction(db_session, cp2, study_period_start=2015, study_period_end=2023)
        await db_session.commit()

        svc = TertiaryReportService()
        report = await svc.generate_report(study_id, db_session)
        timeline = report.landscape_of_secondary_studies.timeline_summary

        assert "2010" in timeline
        assert "2023" in timeline

    @pytest.mark.asyncio
    async def test_rq_evolution_reflects_research_questions(self, db_session) -> None:
        """RQ evolution includes research questions from extraction records."""
        from backend.services.tertiary_report_service import TertiaryReportService

        study_id = await _insert_tertiary_study(db_session)
        await _insert_completed_synthesis(db_session, study_id)

        cp = await _insert_accepted_candidate_paper(db_session, study_id, "10.0/rqp")
        await _insert_extraction(
            db_session,
            cp,
            research_questions_addressed=["RQ1: Effect of TDD", "RQ2: Code quality"],
        )
        await db_session.commit()

        svc = TertiaryReportService()
        report = await svc.generate_report(study_id, db_session)
        rq_evo = report.landscape_of_secondary_studies.research_question_evolution

        assert "RQ1" in rq_evo or "research question" in rq_evo.lower()

    @pytest.mark.asyncio
    async def test_synthesis_method_shifts_reflect_approaches(self, db_session) -> None:
        """Synthesis method shifts section includes the recorded synthesis approaches."""
        from backend.services.tertiary_report_service import TertiaryReportService

        study_id = await _insert_tertiary_study(db_session)
        await _insert_completed_synthesis(db_session, study_id)

        cp1 = await _insert_accepted_candidate_paper(db_session, study_id, "10.0/sm1")
        cp2 = await _insert_accepted_candidate_paper(db_session, study_id, "10.0/sm2")
        await _insert_extraction(db_session, cp1, synthesis_approach_used="meta-analysis")
        await _insert_extraction(db_session, cp2, synthesis_approach_used="narrative")
        await db_session.commit()

        svc = TertiaryReportService()
        report = await svc.generate_report(study_id, db_session)
        shifts = report.landscape_of_secondary_studies.synthesis_method_shifts

        assert "meta-analysis" in shifts or "narrative" in shifts


# ---------------------------------------------------------------------------
# Tests: serialisation methods
# ---------------------------------------------------------------------------


class TestSerialisationMethods:
    """to_json, to_csv, and to_markdown produce correct byte outputs."""

    def _make_report(self) -> "TertiaryReport":
        """Return a minimal TertiaryReport for serialisation tests.

        Returns:
            A fully populated :class:`TertiaryReport`.
        """
        from backend.services.tertiary_report_service import TertiaryReport, LandscapeSection

        return TertiaryReport(
            study_id=1,
            study_name="Serialisation Test",
            generated_at="2026-01-01T00:00:00+00:00",
            background="Some background.",
            review_questions=["RQ1: What is X?"],
            protocol_summary="Protocol summary here.",
            inclusion_exclusion_decisions="3 accepted, 1 rejected.",
            quality_assessment_results="QA completed.",
            extracted_data="2 extractions completed.",
            synthesis_results="Synthesis approach: descriptive.",
            landscape_of_secondary_studies=LandscapeSection(
                timeline_summary="Studies span 2010–2023.",
                research_question_evolution="RQs evolved over time.",
                synthesis_method_shifts="Meta-analysis was most common.",
            ),
            recommendations="Future work should address gap X.",
        )

    def test_to_json_returns_valid_json_bytes(self) -> None:
        """to_json() returns UTF-8 bytes parseable as JSON."""
        report = self._make_report()
        data = report.to_json()
        assert isinstance(data, bytes)
        parsed = json.loads(data)
        assert parsed["study_id"] == 1
        assert parsed["study_name"] == "Serialisation Test"

    def test_to_json_includes_landscape_section(self) -> None:
        """to_json() includes the landscape_of_secondary_studies field."""
        report = self._make_report()
        parsed = json.loads(report.to_json())
        assert "landscape_of_secondary_studies" in parsed
        ls = parsed["landscape_of_secondary_studies"]
        assert "timeline_summary" in ls

    def test_to_csv_returns_bytes_with_section_content_columns(self) -> None:
        """to_csv() returns bytes with Section and Content header row."""
        report = self._make_report()
        data = report.to_csv()
        assert isinstance(data, bytes)
        assert b"Section" in data
        assert b"Content" in data
        assert b"Background" in data

    def test_to_csv_includes_landscape_rows(self) -> None:
        """to_csv() includes rows for all three landscape sub-fields."""
        report = self._make_report()
        data = report.to_csv()
        assert b"Landscape" in data

    def test_to_markdown_returns_bytes_with_h1_heading(self) -> None:
        """to_markdown() returns UTF-8 bytes with a top-level heading."""
        report = self._make_report()
        data = report.to_markdown()
        assert isinstance(data, bytes)
        assert b"# Tertiary Study Report" in data

    def test_to_markdown_includes_landscape_heading(self) -> None:
        """to_markdown() contains the Landscape of Secondary Studies heading."""
        report = self._make_report()
        data = report.to_markdown()
        assert b"Landscape of Secondary Studies" in data

    def test_to_markdown_includes_research_questions(self) -> None:
        """to_markdown() renders research questions as list items."""
        report = self._make_report()
        data = report.to_markdown()
        assert b"RQ1" in data
