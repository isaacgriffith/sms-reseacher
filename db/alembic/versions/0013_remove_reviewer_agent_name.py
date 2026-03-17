"""remove_reviewer_agent_name

Revision ID: 0013
Revises: 0012
Create Date: 2026-03-16 00:00:00.000000

Transitional migration that removes the legacy ``agent_name`` column from the
``reviewer`` table once all rows have been migrated to use the new
``agent_id`` FK introduced in migration 0012.

Pre-conditions (enforced at upgrade time):
- All ``reviewer`` rows that previously had ``agent_name`` set must have a
  corresponding ``agent_id`` populated (or have been deleted).
- Migration 0012 must have already been applied.

The ``agent_name`` column was used in Feature 002 as a simple string tag to
identify which AI agent performed the review.  In Feature 005 this is
superseded by the proper ``Agent`` model.  This migration removes the
dead column after all application code has been updated to use ``agent_id``.

Downgrade note:
  Restoring the ``agent_name`` column does not restore any data that was
  in the column at the time of upgrade.  Historical data should be preserved
  in a backup before running this migration in production.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "0013"
down_revision: str = "0012"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Remove the legacy agent_name column from the reviewer table.

    Uses ``batch_alter_table`` for SQLite compatibility.
    """
    with op.batch_alter_table("reviewer", schema=None) as batch_op:
        batch_op.drop_column("agent_name")


def downgrade() -> None:
    """Re-add the agent_name column to reviewer (nullable, no data restored)."""
    with op.batch_alter_table("reviewer", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "agent_name",
                sa.String(length=255),
                nullable=True,
                comment="Legacy field — superseded by agent_id FK in migration 0012",
            )
        )
