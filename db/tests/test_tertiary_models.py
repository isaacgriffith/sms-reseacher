"""Unit tests for Tertiary Study workflow ORM models (feature 009).

Regression coverage for `TertiaryStudyProtocol.synthesis_approach`, whose
column enumerated only three of `SynthesisApproach`'s five members while the
`synthesis_approach_enum` Postgres type carried all five and
`TertiaryProtocolForm.tsx` offered all five as options.

The failure was read-side, not write-side, which is why every test here reads
the value back. `Enum` defaults to `validate_strings=False`, so a hand-listed
string enum passes an unknown value straight through on the way in and only
raises `LookupError` when SQLAlchemy processes the result — including on the
`db.refresh()` that follows the write. A protocol saved as `narrative` or
`thematic` therefore appeared to save and then raised on every subsequent read,
permanently. That is SQLAlchemy-layer behaviour, so SQLite reproduces it
exactly and no PostgreSQL is required to pin it.

Nothing in `db/tests/` referenced `synthesis_approach` before this file, which
is how the defect survived from feature 009 to feature 012.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.models.slr import SynthesisApproach
from db.models.tertiary import TertiaryProtocolStatus, TertiaryStudyProtocol

# ---------------------------------------------------------------------------
# Test database fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def session():
    """Yield an in-memory SQLite async session with all tertiary tables created."""
    import db.models  # noqa: F401  — ensures all FK targets are registered
    import db.models.candidate  # noqa: F401
    import db.models.slr  # noqa: F401
    import db.models.study  # noqa: F401
    import db.models.tertiary  # noqa: F401
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
# synthesis_approach round-trip
# ---------------------------------------------------------------------------


class TestSynthesisApproachRoundTrip:
    """Every SynthesisApproach member survives a write and a read back."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("approach", list(SynthesisApproach))
    async def test_round_trips_every_member(self, session, approach) -> None:
        """A protocol stores and reloads each approach the form can select."""
        # Arrange — study_id is left unconstrained; SQLite does not enforce
        # foreign keys by default, matching test_slr_models.py's approach.
        protocol = TertiaryStudyProtocol(
            study_id=1,
            status=TertiaryProtocolStatus.DRAFT,
            synthesis_approach=approach.value,
        )
        session.add(protocol)
        await session.commit()
        session.expunge_all()

        # Act — the read is the point: the defect passed the write through
        # untouched and raised LookupError only when the result was processed.
        stored = (
            await session.execute(
                select(TertiaryStudyProtocol).where(TertiaryStudyProtocol.study_id == 1)
            )
        ).scalar_one()

        # Assert
        assert stored.synthesis_approach == approach.value

    def test_column_enumerates_every_member(self) -> None:
        """The column's enum lists all five members, not a hand-written subset.

        The round-trip above covers today's members. This pins the column to
        the enum itself, so adding a member to `SynthesisApproach` cannot
        silently leave this column behind again.
        """
        # Arrange
        column = TertiaryStudyProtocol.__table__.c.synthesis_approach

        # Act
        declared = set(column.type.enums)

        # Assert
        assert declared == {member.value for member in SynthesisApproach}
