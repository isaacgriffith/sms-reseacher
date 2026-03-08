"""Add validity JSON column to the study table (T111).

Revision ID: 0011
Revises: 0010
Create Date: 2026-03-12

Stores the six validity discussion dimensions as a single nullable JSON
column on the study table.  Dimensions: descriptive, theoretical,
generalizability_internal, generalizability_external, interpretive,
repeatability.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "study",
        sa.Column(
            "validity",
            sa.JSON(),
            nullable=True,
            comment=(
                "Validity discussion dimensions: descriptive, theoretical, "
                "generalizability_internal, generalizability_external, "
                "interpretive, repeatability"
            ),
        ),
    )


def downgrade() -> None:
    op.drop_column("study", "validity")
