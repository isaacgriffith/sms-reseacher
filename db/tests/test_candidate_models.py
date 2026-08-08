"""Unit tests for db.models.candidate — CandidatePaper, PaperDecision.

Covers PaperDecision.annotation (TFIX3): a free-text reviewer note distinct
from ``reasons``. FR-002 (specs/012-wire-up-unreachable-workflows/data-model.md)
treats them as two separate things, so the column must be nullable and must
round-trip through the database independently of ``reasons``.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.models.candidate import PaperDecision, PaperDecisionType

# ---------------------------------------------------------------------------
# Test database fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def session():
    """Yield an in-memory SQLite session with all tables created.

    Imports the full model package so every FK target table exists before
    ``paper_decision`` is created.
    """
    import db.models  # noqa: F401

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
# PaperDecision.annotation
# ---------------------------------------------------------------------------


class TestPaperDecisionAnnotation:
    """Attribute and persistence tests for PaperDecision.annotation."""

    def test_instantiates_without_annotation(self) -> None:
        """Annotation defaults to None when not supplied."""
        pd = PaperDecision(
            candidate_paper_id=1,
            reviewer_id=1,
            decision=PaperDecisionType.ACCEPTED,
        )
        assert pd.annotation is None

    @pytest.mark.asyncio
    async def test_annotation_is_nullable_after_persist(self, session) -> None:
        """A PaperDecision with no annotation persists with annotation=None."""
        pd = PaperDecision(
            candidate_paper_id=1,
            reviewer_id=1,
            decision=PaperDecisionType.REJECTED,
        )
        session.add(pd)
        await session.flush()

        assert pd.id is not None
        assert pd.annotation is None

    @pytest.mark.asyncio
    async def test_annotation_round_trips_through_persistence(self, session) -> None:
        """A set annotation is unchanged when the row is flushed and reloaded."""
        note = "Excluded: wrong venue type, not a peer-reviewed conference."
        pd = PaperDecision(
            candidate_paper_id=1,
            reviewer_id=1,
            decision=PaperDecisionType.REJECTED,
            annotation=note,
        )
        session.add(pd)
        await session.flush()
        pd_id = pd.id
        session.expunge(pd)

        reloaded = await session.get(PaperDecision, pd_id)
        assert reloaded is not None
        assert reloaded.annotation == note

    @pytest.mark.asyncio
    async def test_annotation_is_independent_of_reasons(self, session) -> None:
        """Annotation and reasons persist independently of one another."""
        pd = PaperDecision(
            candidate_paper_id=1,
            reviewer_id=1,
            decision=PaperDecisionType.ACCEPTED,
            reasons=[{"criterion_id": 1, "criterion_type": "inclusion", "text": "Peer-reviewed"}],
            annotation="Also check the replication package.",
        )
        session.add(pd)
        await session.flush()
        pd_id = pd.id
        session.expunge(pd)

        reloaded = await session.get(PaperDecision, pd_id)
        assert reloaded is not None
        assert reloaded.annotation == "Also check the replication package."
        assert reloaded.reasons == [
            {"criterion_id": 1, "criterion_type": "inclusion", "text": "Peer-reviewed"}
        ]
