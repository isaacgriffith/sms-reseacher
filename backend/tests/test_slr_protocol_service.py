"""Unit tests for backend.services.slr_protocol_service (feature 007).

Tests cover:
- upsert_protocol creates a new protocol when none exists.
- upsert_protocol updates an existing draft protocol.
- upsert_protocol raises HTTP 409 when editing a validated protocol.
- submit_for_review sets status to under_review and enqueues ARQ job.
- submit_for_review raises HTTP 422 when required fields are missing.
- validate_protocol sets status to validated.
- validate_protocol raises HTTP 422 when review_report is None.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
import db.models  # noqa: F401
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.slr  # noqa: F401

from db.models.slr import ReviewProtocol, ReviewProtocolStatus


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


async def _insert_study(db: AsyncSession) -> int:
    """Insert a minimal Study and ResearchGroup, returning the study id."""
    from db.models.users import ResearchGroup
    from db.models import Study, StudyType, StudyStatus

    group = ResearchGroup(name="Test Group")
    db.add(group)
    await db.flush()

    study = Study(
        name="Test SLR",
        research_group_id=group.id,
        study_type=StudyType.SLR,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


_VALID_DATA: dict = {
    "background": "Background text",
    "rationale": "Rationale text",
    "research_questions": ["RQ1"],
    "pico_population": "Population",
    "pico_intervention": "Intervention",
    "pico_comparison": "Comparison",
    "pico_outcome": "Outcome",
    "search_strategy": "Strategy",
    "inclusion_criteria": ["IC1"],
    "exclusion_criteria": ["EC1"],
    "data_extraction_strategy": "Extract effect sizes",
    "synthesis_approach": "descriptive",
}


class TestUpsertProtocol:
    """upsert_protocol creates and updates draft protocols."""

    @pytest.mark.asyncio
    async def test_creates_new_protocol(self, db_session) -> None:
        """upsert_protocol creates a new ReviewProtocol when none exists."""
        from backend.services.slr_protocol_service import upsert_protocol

        study_id = await _insert_study(db_session)
        protocol = await upsert_protocol(study_id, {"background": "New background"}, db_session)
        assert protocol.id is not None
        assert protocol.study_id == study_id
        assert protocol.background == "New background"
        assert protocol.status == ReviewProtocolStatus.DRAFT

    @pytest.mark.asyncio
    async def test_updates_existing_protocol(self, db_session) -> None:
        """upsert_protocol updates fields on an existing draft protocol."""
        from backend.services.slr_protocol_service import upsert_protocol

        study_id = await _insert_study(db_session)
        await upsert_protocol(study_id, {"background": "Old"}, db_session)
        updated = await upsert_protocol(study_id, {"background": "New"}, db_session)
        assert updated.background == "New"

    @pytest.mark.asyncio
    async def test_raises_409_on_validated_protocol(self, db_session) -> None:
        """upsert_protocol raises HTTP 409 when the protocol is validated."""
        from fastapi import HTTPException

        from backend.services.slr_protocol_service import upsert_protocol

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(study_id=study_id, status=ReviewProtocolStatus.VALIDATED)
        db_session.add(protocol)
        await db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            await upsert_protocol(study_id, {"background": "Edit attempt"}, db_session)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_partial_update_preserves_other_fields(self, db_session) -> None:
        """upsert_protocol only changes the fields included in data."""
        from backend.services.slr_protocol_service import upsert_protocol

        study_id = await _insert_study(db_session)
        await upsert_protocol(study_id, {"background": "B", "rationale": "R"}, db_session)
        updated = await upsert_protocol(study_id, {"background": "B2"}, db_session)
        assert updated.background == "B2"
        assert updated.rationale == "R"


class TestSubmitForReview:
    """submit_for_review validates, updates status, and enqueues an ARQ job."""

    def _make_arq_pool(self, job_id: str = "job-123") -> MagicMock:
        """Return a mock ARQ pool that returns a job with the given id."""
        job = MagicMock()
        job.job_id = job_id
        pool = MagicMock()
        pool.enqueue_job = AsyncMock(return_value=job)
        return pool

    @pytest.mark.asyncio
    async def test_sets_status_to_under_review(self, db_session) -> None:
        """submit_for_review sets protocol status to under_review."""
        from backend.services.slr_protocol_service import submit_for_review, upsert_protocol

        study_id = await _insert_study(db_session)
        await upsert_protocol(study_id, _VALID_DATA, db_session)

        pool = self._make_arq_pool()
        await submit_for_review(study_id, db_session, pool)

        from backend.services.slr_protocol_service import get_protocol

        protocol = await get_protocol(study_id, db_session)
        assert protocol is not None
        assert protocol.status == ReviewProtocolStatus.UNDER_REVIEW

    @pytest.mark.asyncio
    async def test_enqueues_arq_job(self, db_session) -> None:
        """submit_for_review enqueues run_protocol_review job."""
        from backend.services.slr_protocol_service import submit_for_review, upsert_protocol

        study_id = await _insert_study(db_session)
        await upsert_protocol(study_id, _VALID_DATA, db_session)

        pool = self._make_arq_pool("my-job")
        job_id = await submit_for_review(study_id, db_session, pool)

        assert job_id == "my-job"
        pool.enqueue_job.assert_called_once()
        call_kwargs = pool.enqueue_job.call_args
        assert call_kwargs[0][0] == "run_protocol_review"

    @pytest.mark.asyncio
    async def test_raises_422_on_missing_required_field(self, db_session) -> None:
        """submit_for_review raises HTTP 422 when a required field is empty."""
        from fastapi import HTTPException

        from backend.services.slr_protocol_service import submit_for_review, upsert_protocol

        study_id = await _insert_study(db_session)
        # background is empty
        incomplete = {k: v for k, v in _VALID_DATA.items() if k != "background"}
        await upsert_protocol(study_id, incomplete, db_session)

        pool = self._make_arq_pool()
        with pytest.raises(HTTPException) as exc_info:
            await submit_for_review(study_id, db_session, pool)
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_raises_404_when_no_protocol(self, db_session) -> None:
        """submit_for_review raises HTTP 404 when no protocol exists."""
        from fastapi import HTTPException

        from backend.services.slr_protocol_service import submit_for_review

        pool = self._make_arq_pool()
        with pytest.raises(HTTPException) as exc_info:
            await submit_for_review(9999, db_session, pool)
        assert exc_info.value.status_code == 404


class TestValidateProtocol:
    """validate_protocol sets status to validated."""

    @pytest.mark.asyncio
    async def test_sets_status_to_validated(self, db_session) -> None:
        """validate_protocol sets protocol status to validated."""
        from backend.services.slr_protocol_service import upsert_protocol, validate_protocol

        study_id = await _insert_study(db_session)
        protocol = await upsert_protocol(study_id, _VALID_DATA, db_session)

        # Manually set review_report so validation succeeds
        protocol.review_report = {"issues": [], "overall_assessment": "Good."}
        await db_session.commit()

        validated = await validate_protocol(study_id, db_session)
        assert validated.status == ReviewProtocolStatus.VALIDATED

    @pytest.mark.asyncio
    async def test_raises_422_when_no_review_report(self, db_session) -> None:
        """validate_protocol raises HTTP 422 when review_report is None."""
        from fastapi import HTTPException

        from backend.services.slr_protocol_service import upsert_protocol, validate_protocol

        study_id = await _insert_study(db_session)
        await upsert_protocol(study_id, _VALID_DATA, db_session)

        with pytest.raises(HTTPException) as exc_info:
            await validate_protocol(study_id, db_session)
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_raises_404_when_no_protocol(self, db_session) -> None:
        """validate_protocol raises HTTP 404 when no protocol exists."""
        from fastapi import HTTPException

        from backend.services.slr_protocol_service import validate_protocol

        with pytest.raises(HTTPException) as exc_info:
            await validate_protocol(9999, db_session)
        assert exc_info.value.status_code == 404
