"""Add conflict_flag column to candidate_paper.

Revision ID: 0007
Revises: 0006
Create Date: 2026-03-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "candidate_paper",
        sa.Column("conflict_flag", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("candidate_paper", "conflict_flag")
