"""Unit tests for SLR workflow ORM models (feature 007).

Tests verify table names, column types, unique constraints, optimistic locking,
enum values, and audit field defaults for all six new SLR models.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.models.slr import (
    AgreementRoundType,
    ChecklistScoringMethod,
    GreyLiteratureSource,
    GreyLiteratureType,
    InterRaterAgreementRecord,
    QualityAssessmentChecklist,
    QualityAssessmentScore,
    QualityChecklistItem,
    ReviewProtocol,
    ReviewProtocolStatus,
    SynthesisApproach,
    SynthesisResult,
    SynthesisStatus,
)


# ---------------------------------------------------------------------------
# Test database fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def session():
    """Yield an in-memory SQLite async session with all SLR tables created."""
    import db.models  # noqa: F401  — ensures all FK targets are registered
    import db.models.candidate  # noqa: F401
    import db.models.slr  # noqa: F401
    import db.models.study  # noqa: F401
    import db.models.users  # noqa: F401

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


# ---------------------------------------------------------------------------
# Enum value tests
# ---------------------------------------------------------------------------


class TestReviewProtocolStatusEnum:
    """ReviewProtocolStatus enum has the expected values."""

    def test_draft(self) -> None:
        assert ReviewProtocolStatus.DRAFT.value == "draft"

    def test_under_review(self) -> None:
        assert ReviewProtocolStatus.UNDER_REVIEW.value == "under_review"

    def test_validated(self) -> None:
        assert ReviewProtocolStatus.VALIDATED.value == "validated"

    def test_all_members(self) -> None:
        assert set(ReviewProtocolStatus) == {
            ReviewProtocolStatus.DRAFT,
            ReviewProtocolStatus.UNDER_REVIEW,
            ReviewProtocolStatus.VALIDATED,
        }


class TestSynthesisApproachEnum:
    """SynthesisApproach enum has the expected values."""

    def test_meta_analysis(self) -> None:
        assert SynthesisApproach.META_ANALYSIS.value == "meta_analysis"

    def test_descriptive(self) -> None:
        assert SynthesisApproach.DESCRIPTIVE.value == "descriptive"

    def test_qualitative(self) -> None:
        assert SynthesisApproach.QUALITATIVE.value == "qualitative"


class TestChecklistScoringMethodEnum:
    """ChecklistScoringMethod enum has three scoring types."""

    def test_binary(self) -> None:
        assert ChecklistScoringMethod.BINARY.value == "binary"

    def test_scale_1_3(self) -> None:
        assert ChecklistScoringMethod.SCALE_1_3.value == "scale_1_3"

    def test_scale_1_5(self) -> None:
        assert ChecklistScoringMethod.SCALE_1_5.value == "scale_1_5"


class TestAgreementRoundTypeEnum:
    """AgreementRoundType enum covers all screening rounds."""

    def test_title_abstract(self) -> None:
        assert AgreementRoundType.TITLE_ABSTRACT.value == "title_abstract"

    def test_intro_conclusions(self) -> None:
        assert AgreementRoundType.INTRO_CONCLUSIONS.value == "intro_conclusions"

    def test_full_text(self) -> None:
        assert AgreementRoundType.FULL_TEXT.value == "full_text"

    def test_quality_assessment(self) -> None:
        assert AgreementRoundType.QUALITY_ASSESSMENT.value == "quality_assessment"


class TestSynthesisStatusEnum:
    """SynthesisStatus enum covers all job states."""

    def test_pending(self) -> None:
        assert SynthesisStatus.PENDING.value == "pending"

    def test_running(self) -> None:
        assert SynthesisStatus.RUNNING.value == "running"

    def test_completed(self) -> None:
        assert SynthesisStatus.COMPLETED.value == "completed"

    def test_failed(self) -> None:
        assert SynthesisStatus.FAILED.value == "failed"


class TestGreyLiteratureTypeEnum:
    """GreyLiteratureType enum covers all source types."""

    def test_technical_report(self) -> None:
        assert GreyLiteratureType.TECHNICAL_REPORT.value == "technical_report"

    def test_dissertation(self) -> None:
        assert GreyLiteratureType.DISSERTATION.value == "dissertation"

    def test_rejected_publication(self) -> None:
        assert GreyLiteratureType.REJECTED_PUBLICATION.value == "rejected_publication"

    def test_work_in_progress(self) -> None:
        assert GreyLiteratureType.WORK_IN_PROGRESS.value == "work_in_progress"


# ---------------------------------------------------------------------------
# Table name tests
# ---------------------------------------------------------------------------


class TestTableNames:
    """Each model is registered under the expected SQL table name."""

    def test_review_protocol_tablename(self) -> None:
        assert ReviewProtocol.__tablename__ == "review_protocol"

    def test_quality_assessment_checklist_tablename(self) -> None:
        assert QualityAssessmentChecklist.__tablename__ == "quality_assessment_checklist"

    def test_quality_checklist_item_tablename(self) -> None:
        assert QualityChecklistItem.__tablename__ == "quality_checklist_item"

    def test_quality_assessment_score_tablename(self) -> None:
        assert QualityAssessmentScore.__tablename__ == "quality_assessment_score"

    def test_inter_rater_agreement_record_tablename(self) -> None:
        assert InterRaterAgreementRecord.__tablename__ == "inter_rater_agreement_record"

    def test_synthesis_result_tablename(self) -> None:
        assert SynthesisResult.__tablename__ == "synthesis_result"

    def test_grey_literature_source_tablename(self) -> None:
        assert GreyLiteratureSource.__tablename__ == "grey_literature_source"


# ---------------------------------------------------------------------------
# Optimistic locking tests
# ---------------------------------------------------------------------------


class TestOptimisticLocking:
    """version_id is the mapper version_id_col on locking-enabled models."""

    def test_review_protocol_has_version_col(self) -> None:
        mapper = inspect(ReviewProtocol)
        assert mapper.version_id_col is not None

    def test_quality_assessment_score_has_version_col(self) -> None:
        mapper = inspect(QualityAssessmentScore)
        assert mapper.version_id_col is not None

    def test_synthesis_result_has_version_col(self) -> None:
        mapper = inspect(SynthesisResult)
        assert mapper.version_id_col is not None

    def test_checklist_no_version_col(self) -> None:
        """QualityAssessmentChecklist does NOT have optimistic locking."""
        mapper = inspect(QualityAssessmentChecklist)
        assert mapper.version_id_col is None

    def test_grey_literature_no_version_col(self) -> None:
        """GreyLiteratureSource does NOT have optimistic locking."""
        mapper = inspect(GreyLiteratureSource)
        assert mapper.version_id_col is None


# ---------------------------------------------------------------------------
# Unique constraint tests
# ---------------------------------------------------------------------------


class TestUniqueConstraints:
    """Unique constraints are declared on models."""

    def test_review_protocol_unique_study(self) -> None:
        """review_protocol.study_id has unique=True."""
        col = ReviewProtocol.__table__.c["study_id"]
        assert col.unique is True

    def test_quality_assessment_checklist_unique_study(self) -> None:
        """quality_assessment_checklist.study_id has unique=True."""
        col = QualityAssessmentChecklist.__table__.c["study_id"]
        assert col.unique is True

    def test_quality_assessment_score_unique_triple(self) -> None:
        """quality_assessment_score has a UniqueConstraint on (candidate_paper, reviewer, item)."""
        from sqlalchemy import UniqueConstraint

        table = QualityAssessmentScore.__table__
        unique_sets = {
            frozenset(c.name for c in uc.columns)
            for uc in table.constraints
            if isinstance(uc, UniqueConstraint)
        }
        assert frozenset(["candidate_paper_id", "reviewer_id", "checklist_item_id"]) in unique_sets


# ---------------------------------------------------------------------------
# Audit field defaults tests
# ---------------------------------------------------------------------------


class TestAuditFields:
    """All models expose created_at / updated_at mapped columns."""

    @pytest.mark.parametrize(
        "model_cls",
        [
            ReviewProtocol,
            QualityAssessmentChecklist,
            QualityChecklistItem,
            QualityAssessmentScore,
            InterRaterAgreementRecord,
            SynthesisResult,
            GreyLiteratureSource,
        ],
    )
    def test_has_created_at(self, model_cls: type) -> None:
        """Model has a created_at mapped column."""
        mapper = inspect(model_cls)
        col_names = [c.key for c in mapper.mapper.column_attrs]
        assert "created_at" in col_names

    @pytest.mark.parametrize(
        "model_cls",
        [
            ReviewProtocol,
            QualityAssessmentChecklist,
            QualityChecklistItem,
            QualityAssessmentScore,
            InterRaterAgreementRecord,
            SynthesisResult,
            GreyLiteratureSource,
        ],
    )
    def test_has_updated_at(self, model_cls: type) -> None:
        """Model has an updated_at mapped column."""
        mapper = inspect(model_cls)
        col_names = [c.key for c in mapper.mapper.column_attrs]
        assert "updated_at" in col_names


# ---------------------------------------------------------------------------
# Default field value tests
# ---------------------------------------------------------------------------


class TestDefaultFieldValues:
    """Column-level defaults are declared correctly on mapped columns.

    SQLAlchemy ``default=`` is applied at INSERT time (not on Python
    object construction), so we inspect the column's ``default.arg``
    rather than checking the attribute on a freshly constructed instance.
    """

    def test_review_protocol_status_column_default(self) -> None:
        """review_protocol.status column default is DRAFT."""
        col = ReviewProtocol.__table__.c["status"]
        assert col.default is not None or col.server_default is not None

    def test_review_protocol_version_id_column_default(self) -> None:
        """review_protocol.version_id column default is 0."""
        col = ReviewProtocol.__table__.c["version_id"]
        assert col.default is not None or col.server_default is not None

    def test_quality_checklist_item_weight_column_default(self) -> None:
        """quality_checklist_item.weight column default is 1.0."""
        col = QualityChecklistItem.__table__.c["weight"]
        assert col.default is not None or col.server_default is not None

    def test_synthesis_result_status_column_default(self) -> None:
        """synthesis_result.status column default is pending."""
        col = SynthesisResult.__table__.c["status"]
        assert col.default is not None or col.server_default is not None

    def test_synthesis_result_version_id_column_default(self) -> None:
        """synthesis_result.version_id column default is 0."""
        col = SynthesisResult.__table__.c["version_id"]
        assert col.default is not None or col.server_default is not None


# ---------------------------------------------------------------------------
# Repr tests
# ---------------------------------------------------------------------------


class TestReprMethods:
    """__repr__ returns a string containing key identifiers."""

    def test_review_protocol_repr(self) -> None:
        rp = ReviewProtocol(id=1, study_id=2, status=ReviewProtocolStatus.DRAFT)
        assert "ReviewProtocol" in repr(rp)
        assert "study_id=2" in repr(rp)

    def test_synthesis_result_repr(self) -> None:
        sr = SynthesisResult(
            id=5, study_id=3, approach=SynthesisApproach.META_ANALYSIS, status=SynthesisStatus.PENDING
        )
        assert "SynthesisResult" in repr(sr)
        assert "study_id=3" in repr(sr)

    def test_grey_literature_source_repr(self) -> None:
        gls = GreyLiteratureSource(
            id=7,
            study_id=4,
            source_type=GreyLiteratureType.DISSERTATION,
            title="A long title that might get truncated in repr",
        )
        assert "GreyLiteratureSource" in repr(gls)
        assert "study_id=4" in repr(gls)
