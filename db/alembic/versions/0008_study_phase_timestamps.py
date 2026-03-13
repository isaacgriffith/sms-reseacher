"""Add pico_saved_at, search_run_at, extraction_started_at to study table.

Revision ID: 0008
Revises: 0007
Create Date: 2026-03-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("study", sa.Column("pico_saved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("study", sa.Column("search_run_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "study",
        sa.Column("extraction_started_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("study", "extraction_started_at")
    op.drop_column("study", "search_run_at")
    op.drop_column("study", "pico_saved_at")
