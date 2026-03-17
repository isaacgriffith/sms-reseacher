"""Integration tests for Alembic migration 0012_models_and_agents — T070.

Covers:
- upgrade() creates provider, available_model, and agent tables.
- upgrade() adds agent_id column to reviewer table.
- Seed records are present after upgrade (when ANTHROPIC_API_KEY is set).
- downgrade() removes the three tables and agent_id column cleanly.

Note: These tests use a PostgreSQL-compatible migration path. The real
migration adds a FK-constrained column to ``reviewer``, which is not
supported by SQLite's ALTER TABLE. Tests are skipped when a PostgreSQL
URL is not available (DATABASE_URL env var with ``postgresql`` scheme).

For local runs with a live PostgreSQL:
    DATABASE_URL=postgresql+asyncpg://... uv run pytest db/tests/integration/
"""

from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy import inspect, text
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# PostgreSQL-only guard
# ---------------------------------------------------------------------------

_DB_URL = os.environ.get("DATABASE_URL", "")
_REQUIRES_POSTGRES = pytest.mark.skipif(
    "postgresql" not in _DB_URL,
    reason="Migration test requires a live PostgreSQL database (set DATABASE_URL)",
)

# Fixed seed UUIDs from the migration (deterministic)
_PROVIDER_ID = uuid.UUID("00000000-0000-0000-0001-000000000001")
_MODEL_ID = uuid.UUID("00000000-0000-0000-0001-000000000002")
_AGENT_GENERATOR_ID = uuid.UUID("00000000-0000-0000-0002-000000000001")
_SCREENER_AGENT_ID = uuid.UUID("00000000-0000-0000-0002-000000000002")
_EXTRACTOR_AGENT_ID = uuid.UUID("00000000-0000-0000-0002-000000000003")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sync_engine():
    """Create a synchronous engine for Alembic ops.

    Uses DATABASE_URL when set (PostgreSQL in CI), otherwise falls back to
    an in-memory SQLite engine (sufficient for table-structure tests that
    don't require FK ALTER TABLE support).
    """
    db_url = os.environ.get("DATABASE_URL", "")
    if "postgresql" in db_url:
        # Strip async driver prefix for sync Alembic operations
        sync_url = db_url.replace("+asyncpg", "").replace("+aiosqlite", "")
        return sa.create_engine(sync_url)
    return sa.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _table_names(conn) -> set[str]:
    """Return set of table names present in the DB."""
    inspector = inspect(conn)
    return set(inspector.get_table_names())


def _column_names(conn, table: str) -> set[str]:
    """Return set of column names for a table."""
    inspector = inspect(conn)
    return {col["name"] for col in inspector.get_columns(table)}


def _run_alembic_upgrade(engine, target: str = "0012") -> None:
    """Apply Alembic migration up to *target* on *engine*."""
    from alembic.config import Config
    from alembic.runtime.environment import EnvironmentContext
    from alembic.script import ScriptDirectory

    cfg = Config()
    cfg.set_main_option("script_location", "db/alembic")
    cfg.set_main_option("sqlalchemy.url", str(engine.url))

    script = ScriptDirectory.from_config(cfg)

    def run_upgrade(rev, context):  # noqa: ANN001
        return script._upgrade_revs(target, rev)

    with EnvironmentContext(cfg, script, fn=run_upgrade, as_sql=False) as env_ctx:
        with engine.connect() as connection:
            env_ctx.configure(
                connection=connection,
                target_metadata=None,
                render_as_batch=True,  # required for SQLite column ops
            )
            with env_ctx.begin_transaction():
                env_ctx.run_migrations()


def _run_alembic_downgrade(engine, target: str = "0011") -> None:
    """Revert Alembic migration back to *target* on *engine*."""
    from alembic.config import Config
    from alembic.runtime.environment import EnvironmentContext
    from alembic.script import ScriptDirectory

    cfg = Config()
    cfg.set_main_option("script_location", "db/alembic")
    cfg.set_main_option("sqlalchemy.url", str(engine.url))

    script = ScriptDirectory.from_config(cfg)

    def run_downgrade(rev, context):  # noqa: ANN001
        return script._downgrade_revs(target, rev)

    with EnvironmentContext(cfg, script, fn=run_downgrade, as_sql=False) as env_ctx:
        with engine.connect() as connection:
            env_ctx.configure(
                connection=connection,
                target_metadata=None,
                render_as_batch=True,
            )
            with env_ctx.begin_transaction():
                env_ctx.run_migrations()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def migrated_engine():
    """Engine with all migrations up to 0012 applied.

    Requires PostgreSQL (see module-level note). Tests using this fixture are
    skipped when DATABASE_URL does not point to PostgreSQL.
    """
    engine = _make_sync_engine()
    _run_alembic_upgrade(engine, target="0012")
    yield engine
    engine.dispose()


# ---------------------------------------------------------------------------
# T070a: upgrade() creates the three new tables
# ---------------------------------------------------------------------------


@_REQUIRES_POSTGRES
class TestUpgradeCreatesNewTables:
    """Verify that upgrade creates provider, available_model, and agent tables."""

    def test_provider_table_exists(self, migrated_engine) -> None:
        """upgrade() creates the 'provider' table."""
        with migrated_engine.connect() as conn:
            tables = _table_names(conn)
        assert "provider" in tables

    def test_available_model_table_exists(self, migrated_engine) -> None:
        """upgrade() creates the 'available_model' table."""
        with migrated_engine.connect() as conn:
            tables = _table_names(conn)
        assert "available_model" in tables

    def test_agent_table_exists(self, migrated_engine) -> None:
        """upgrade() creates the 'agent' table."""
        with migrated_engine.connect() as conn:
            tables = _table_names(conn)
        assert "agent" in tables

    def test_reviewer_has_agent_id_column(self, migrated_engine) -> None:
        """upgrade() adds 'agent_id' column to the reviewer table."""
        with migrated_engine.connect() as conn:
            cols = _column_names(conn, "reviewer")
        assert "agent_id" in cols


# ---------------------------------------------------------------------------
# T070b: upgrade() creates expected columns in each table
# ---------------------------------------------------------------------------


@_REQUIRES_POSTGRES
class TestUpgradeTableColumns:
    """Verify critical columns in the new tables."""

    def test_provider_columns(self, migrated_engine) -> None:
        """provider table has id, provider_type, display_name, is_enabled."""
        with migrated_engine.connect() as conn:
            cols = _column_names(conn, "provider")
        assert {"id", "provider_type", "display_name", "is_enabled"}.issubset(cols)

    def test_available_model_columns(self, migrated_engine) -> None:
        """available_model table has id, provider_id, model_identifier, display_name."""
        with migrated_engine.connect() as conn:
            cols = _column_names(conn, "available_model")
        assert {"id", "provider_id", "model_identifier", "display_name"}.issubset(cols)

    def test_agent_columns(self, migrated_engine) -> None:
        """agent table has required identity and template columns."""
        with migrated_engine.connect() as conn:
            cols = _column_names(conn, "agent")
        assert {
            "id",
            "task_type",
            "role_name",
            "role_description",
            "persona_name",
            "persona_description",
            "system_message_template",
            "model_id",
            "provider_id",
            "is_active",
            "version_id",
        }.issubset(cols)

    def test_agent_has_undo_buffer_column(self, migrated_engine) -> None:
        """agent table has system_message_undo_buffer for undo functionality."""
        with migrated_engine.connect() as conn:
            cols = _column_names(conn, "agent")
        assert "system_message_undo_buffer" in cols


# ---------------------------------------------------------------------------
# T070c: Seed records present after upgrade (ANTHROPIC_API_KEY gated)
# ---------------------------------------------------------------------------


@_REQUIRES_POSTGRES
class TestSeedRecords:
    """Seed data written by upgrade() is present in the DB."""

    def test_agent_generator_seed_exists(self, migrated_engine) -> None:
        """Seed AgentGenerator agent row is always inserted."""
        with migrated_engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, task_type FROM agent WHERE id = :id"),
                {"id": str(_AGENT_GENERATOR_ID)},
            ).fetchone()
        assert result is not None
        assert result[1] == "agent_generator"

    def test_screener_seed_exists(self, migrated_engine) -> None:
        """Seed Screener agent row is always inserted."""
        with migrated_engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, task_type FROM agent WHERE id = :id"),
                {"id": str(_SCREENER_AGENT_ID)},
            ).fetchone()
        assert result is not None
        assert result[1] == "screener"

    def test_extractor_seed_exists(self, migrated_engine) -> None:
        """Seed Extractor agent row is always inserted."""
        with migrated_engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, task_type FROM agent WHERE id = :id"),
                {"id": str(_EXTRACTOR_AGENT_ID)},
            ).fetchone()
        assert result is not None
        assert result[1] == "extractor"

    def test_provider_and_model_seeded_when_api_key_set(self, migrated_engine) -> None:
        """Provider and model seed rows present when ANTHROPIC_API_KEY env var is set."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set — provider seed skipped by migration")

        with migrated_engine.connect() as conn:
            provider_row = conn.execute(
                text("SELECT id FROM provider WHERE id = :id"),
                {"id": str(_PROVIDER_ID)},
            ).fetchone()
            model_row = conn.execute(
                text("SELECT id FROM available_model WHERE id = :id"),
                {"id": str(_MODEL_ID)},
            ).fetchone()

        assert provider_row is not None
        assert model_row is not None


# ---------------------------------------------------------------------------
# T070d: downgrade() removes tables and agent_id column
# ---------------------------------------------------------------------------


@_REQUIRES_POSTGRES
class TestDowngrade:
    """downgrade() removes everything added by upgrade()."""

    def test_downgrade_removes_agent_table(self) -> None:
        """downgrade() drops the 'agent' table."""
        engine = _make_sync_engine()
        _run_alembic_upgrade(engine, target="0012")
        _run_alembic_downgrade(engine, target="0011")

        with engine.connect() as conn:
            tables = _table_names(conn)

        engine.dispose()
        assert "agent" not in tables

    def test_downgrade_removes_available_model_table(self) -> None:
        """downgrade() drops the 'available_model' table."""
        engine = _make_sync_engine()
        _run_alembic_upgrade(engine, target="0012")
        _run_alembic_downgrade(engine, target="0011")

        with engine.connect() as conn:
            tables = _table_names(conn)

        engine.dispose()
        assert "available_model" not in tables

    def test_downgrade_removes_provider_table(self) -> None:
        """downgrade() drops the 'provider' table."""
        engine = _make_sync_engine()
        _run_alembic_upgrade(engine, target="0012")
        _run_alembic_downgrade(engine, target="0011")

        with engine.connect() as conn:
            tables = _table_names(conn)

        engine.dispose()
        assert "provider" not in tables

    def test_downgrade_removes_agent_id_from_reviewer(self) -> None:
        """downgrade() removes the agent_id column from reviewer."""
        engine = _make_sync_engine()
        _run_alembic_upgrade(engine, target="0012")
        _run_alembic_downgrade(engine, target="0011")

        with engine.connect() as conn:
            cols = _column_names(conn, "reviewer")

        engine.dispose()
        assert "agent_id" not in cols
