"""Unit tests for backend.services.slr_report_service (feature 007, T082).

Tests cover:
- generate_report returns SLRReport with all 10 sections populated.
- generate_report raises HTTPException(422) when no completed synthesis.
- generate_report raises HTTPException(404) when study not found.
- export_report with format="markdown" returns text/markdown MIME.
- export_report with format="latex" returns application/x-latex MIME.
- export_report with format="json" returns application/json MIME.
- export_report with format="csv" returns text/csv MIME.
- export_report with unknown format raises HTTPException(400).
"""

from __future__ import annotations

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
import db.models.pico  # noqa: F401
import db.models.seeds  # noqa: F401
import db.models.criteria  # noqa: F401
import db.models.extraction  # noqa: F401
import db.models.results  # noqa: F401
import db.models.audit  # noqa: F401
import db.models.jobs  # noqa: F401
import db.models.backup_codes  # noqa: F401
import db.models.security_audit  # noqa: F401
import db.models.search_integrations  # noqa: F401


@pytest_asyncio.fixture
async def db_session():
    """Provide a per-test in-memory SQLite session with all tables."""
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _insert_study(db: AsyncSession) -> int:
    """Insert a minimal Study and ResearchGroup, returning the study id."""
    from db.models.users import ResearchGroup
    from db.models import Study, StudyType, StudyStatus

    group = ResearchGroup(name="Report Test Group")
    db.add(group)
    await db.flush()

    study = Study(
        name="Report Test SLR",
        research_group_id=group.id,
        study_type=StudyType.SLR,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


async def _insert_completed_synthesis(db: AsyncSession, study_id: int) -> int:
    """Insert a completed SynthesisResult for the given study, returning its id."""
    from db.models.slr import SynthesisResult, SynthesisApproach, SynthesisStatus

    sr = SynthesisResult(
        study_id=study_id,
        approach=SynthesisApproach.DESCRIPTIVE,
        status=SynthesisStatus.COMPLETED,
        computed_statistics={"n_studies": 5, "mean_effect": 0.42},
    )
    db.add(sr)
    await db.commit()
    await db.refresh(sr)
    return sr.id


# ---------------------------------------------------------------------------
# Tests: generate_report
# ---------------------------------------------------------------------------


class TestGenerateReport:
    """generate_report produces a fully populated SLRReport."""

    @pytest.mark.asyncio
    async def test_returns_slr_report_all_sections(self, db_session) -> None:
        """generate_report returns SLRReport with all 10 sections populated."""
        from backend.services.slr_report_service import generate_report, SLRReport

        study_id = await _insert_study(db_session)
        await _insert_completed_synthesis(db_session, study_id)

        report = await generate_report(study_id, db_session)

        assert isinstance(report, SLRReport)
        assert report.study_id == study_id
        assert report.study_name == "Report Test SLR"
        assert isinstance(report.generated_at, str)
        assert len(report.generated_at) > 0
        assert isinstance(report.background, str)
        assert isinstance(report.review_questions, list)
        assert isinstance(report.protocol_summary, str)
        assert isinstance(report.search_process, str)
        assert isinstance(report.inclusion_exclusion_decisions, str)
        assert isinstance(report.quality_assessment_results, str)
        assert isinstance(report.extracted_data, str)
        assert isinstance(report.synthesis_results, str)
        assert isinstance(report.validity_discussion, str)
        assert isinstance(report.recommendations, str)

    @pytest.mark.asyncio
    async def test_raises_422_when_no_completed_synthesis(self, db_session) -> None:
        """generate_report raises HTTPException(422) when no completed synthesis."""
        from fastapi import HTTPException
        from backend.services.slr_report_service import generate_report

        study_id = await _insert_study(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await generate_report(study_id, db_session)

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_raises_404_when_study_not_found(self, db_session) -> None:
        """generate_report raises HTTPException(404) when study does not exist."""
        from fastapi import HTTPException
        from backend.services.slr_report_service import generate_report

        with pytest.raises(HTTPException) as exc_info:
            await generate_report(99999, db_session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_includes_protocol_data_when_present(self, db_session) -> None:
        """generate_report includes protocol background when protocol exists."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus
        from backend.services.slr_report_service import generate_report

        study_id = await _insert_study(db_session)
        await _insert_completed_synthesis(db_session, study_id)

        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
            background="This review examines testing practices.",
            research_questions=["RQ1: What are testing practices?"],
        )
        db_session.add(protocol)
        await db_session.commit()

        report = await generate_report(study_id, db_session)
        assert "testing practices" in report.background
        assert len(report.review_questions) == 1

    @pytest.mark.asyncio
    async def test_includes_grey_literature_in_search_process(self, db_session) -> None:
        """generate_report mentions grey literature sources in search_process."""
        from db.models.slr import GreyLiteratureSource, GreyLiteratureType
        from backend.services.slr_report_service import generate_report

        study_id = await _insert_study(db_session)
        await _insert_completed_synthesis(db_session, study_id)

        grey = GreyLiteratureSource(
            study_id=study_id,
            source_type=GreyLiteratureType.TECHNICAL_REPORT,
            title="Grey Lit Example",
        )
        db_session.add(grey)
        await db_session.commit()

        report = await generate_report(study_id, db_session)
        assert "grey literature" in report.search_process.lower()

    @pytest.mark.asyncio
    async def test_synthesis_results_section_mentions_approach(self, db_session) -> None:
        """generate_report synthesis_results section contains the approach name."""
        from backend.services.slr_report_service import generate_report

        study_id = await _insert_study(db_session)
        await _insert_completed_synthesis(db_session, study_id)

        report = await generate_report(study_id, db_session)
        assert "descriptive" in report.synthesis_results.lower()


# ---------------------------------------------------------------------------
# Tests: export_report
# ---------------------------------------------------------------------------


class TestExportReport:
    """export_report serialises the report in the requested format."""

    def _make_report(self) -> "SLRReport":
        """Return a minimal SLRReport for export tests."""
        from backend.services.slr_report_service import SLRReport

        return SLRReport(
            study_id=1,
            study_name="Test Study",
            generated_at="2025-01-01T00:00:00+00:00",
            background="Some background.",
            review_questions=["RQ1"],
            protocol_summary="Protocol summary.",
            search_process="Search process.",
            inclusion_exclusion_decisions="Inc/exc decisions.",
            quality_assessment_results="QA results.",
            extracted_data="Extracted data.",
            synthesis_results="Synthesis results.",
            validity_discussion="Validity discussion.",
            recommendations="Recommendations.",
        )

    def test_markdown_returns_correct_mime_type(self) -> None:
        """export_report with format='markdown' returns text/markdown MIME."""
        from backend.services.slr_report_service import export_report

        report = self._make_report()
        content, mime, filename = export_report(report, "markdown")

        assert mime == "text/markdown"
        assert filename.endswith(".md")
        assert b"## Background" in content
        assert b"Some background." in content

    def test_latex_returns_correct_mime_type(self) -> None:
        """export_report with format='latex' returns application/x-latex MIME."""
        from backend.services.slr_report_service import export_report

        report = self._make_report()
        content, mime, filename = export_report(report, "latex")

        assert mime == "application/x-latex"
        assert filename.endswith(".tex")
        assert b"\\documentclass" in content
        assert b"\\section{Background}" in content

    def test_json_returns_correct_mime_type(self) -> None:
        """export_report with format='json' returns application/json MIME."""
        import json as _json
        from backend.services.slr_report_service import export_report

        report = self._make_report()
        content, mime, filename = export_report(report, "json")

        assert mime == "application/json"
        assert filename.endswith(".json")
        parsed = _json.loads(content)
        assert parsed["study_id"] == 1
        assert parsed["study_name"] == "Test Study"

    def test_csv_returns_correct_mime_type(self) -> None:
        """export_report with format='csv' returns text/csv MIME."""
        from backend.services.slr_report_service import export_report

        report = self._make_report()
        content, mime, filename = export_report(report, "csv")

        assert mime == "text/csv"
        assert filename.endswith(".csv")
        assert b"Section" in content
        assert b"Background" in content

    def test_unknown_format_raises_400(self) -> None:
        """export_report raises HTTPException(400) for unknown formats."""
        from fastapi import HTTPException
        from backend.services.slr_report_service import export_report

        report = self._make_report()
        with pytest.raises(HTTPException) as exc_info:
            export_report(report, "docx")

        assert exc_info.value.status_code == 400
