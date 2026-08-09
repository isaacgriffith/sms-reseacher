"""Add the DARE quality instrument's storage requirements (TFIX7 part 3).

Two changes, both needed before a tertiary study can record a DARE assessment.

**1. ``checklist_scoring_method_enum`` gains ``yes_partial_no``.**

DARE scores each question Y = 1, P = 0.5, N = 0 (``docs/methodology/04-tertiary.md``
2.3).  None of the three existing methods can express that: ``binary`` has no
middle value, and ``scale_1_3``/``scale_1_5`` both start at 1, so DARE's "N = 0"
is unreachable.  Until this value exists the instrument the corpus assigns to
tertiary studies cannot be stored at all.

**2. ``quality_checklist_item`` gains ``anchors``.**

DARE supplies three anchor descriptions per question, and the corpus is explicit
that they "provide support for the assessment; it is not a strict mutually
exclusive classification process" — which only helps if the reviewer can read
the anchor beside the option it describes.  Nullable, because ``binary`` and
scale items generally carry none, and because a default of ``{}`` would be
indistinguishable from "this item has no anchors" (the same reasoning as 0020's
``annotation`` column).

The column is deliberately generic rather than DARE-specific: Garousi's 20-item
grey-literature instrument and the Petersen 2015 rubrics are both anchored, and
both are already named in the gap catalogue.

**Downgrade removes the column but leaves the enum value.** PostgreSQL has no
``ALTER TYPE ... DROP VALUE``; removing one means recreating the type and
rewriting every dependent column.  0016 made the same call for
``inclusion_status_enum`` and this follows it.  The consequence is worth stating
plainly: after a downgrade, rows may still carry ``scoring_method =
'yes_partial_no'`` while nothing can render their anchors.

Revision ID: 0021
Revises: 0020
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0021"
down_revision: str = "0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the yes_partial_no scoring method and the anchors column."""
    # IF NOT EXISTS keeps this idempotent.  PostgreSQL 12+ permits ADD VALUE
    # inside a transaction provided the new value is not *used* in the same
    # transaction — this migration only adds a column, so that holds.
    op.execute("ALTER TYPE checklist_scoring_method_enum ADD VALUE IF NOT EXISTS 'yes_partial_no'")

    op.add_column(
        "quality_checklist_item",
        sa.Column("anchors", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    """Drop the anchors column.

    The ``yes_partial_no`` enum value is intentionally left in place —
    PostgreSQL does not support ``ALTER TYPE ... DROP VALUE``.
    """
    op.drop_column("quality_checklist_item", "anchors")
