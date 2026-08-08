"""Add annotation to paper_decision (TFIX3).

FR-002 (specs/012-wire-up-unreachable-workflows/data-model.md) describes a
paper decision as carrying "one or more reasons drawn from the study's
criteria, and ... a free-text annotation" — two distinct things. The data
model doc has always documented an `annotation` column, but `PaperDecision`
never had one: the frontend instead smuggled free-text notes into the
`reasons` JSON array as a synthetic entry shaped like
`{"criterion_type": "annotation", "text": "..."}`.

That encoding is wrong for the same reason a comment is not a line of code: a
free-text note is not a criterion, and counting it as one silently inflates
any analysis that treats `reasons` as "the criteria this decision cited" —
criteria-frequency tallies and criteria-based inter-rater-agreement in
particular. The spec already named the fix; the code just never caught up.
This migration adds the column the spec always described.

Nullable by design, matching every other free-text/optional column added in
this series (see 0019's `citation_intent`): most decisions carry no note, and
a default of `""` would be indistinguishable from "the reviewer wrote
nothing".

Existing rows that already carry a note inside `reasons` are left as-is —
migrating that data out is out of scope here, and every read path continues
to return `reasons` untouched, so those rows keep displaying exactly as they
do today. Only new writes use this column.

Revision ID: 0020
Revises: 0019
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0020"
down_revision: str = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the nullable annotation column to paper_decision."""
    op.add_column(
        "paper_decision",
        sa.Column("annotation", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Drop the annotation column."""
    op.drop_column("paper_decision", "annotation")
