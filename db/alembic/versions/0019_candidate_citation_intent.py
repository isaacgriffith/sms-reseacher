"""Add citation_intent to candidate_paper (G55).

Semantic Scholar reports why one paper cites another — methodology, background,
or result. The MCP snowball tool already requested and mapped that field, but the
screening pipeline discarded it before persistence, so snowballed candidates were
screened on title and abstract exactly like database hits.

Wohlin's backward-snowballing procedure makes examining the reference's place in
the citing text its fourth step, and the corpus calls that "the step that
distinguishes the method from mechanical reference-following". This column is
what lets that step happen.

Nullable by design: a paper found by database search has no citing context, and
recording "unknown" for it would conflate "we looked and could not tell" with
"there was nothing to look at".

Revision ID: 0019
Revises: 0018
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0019"
down_revision: str = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the nullable citation_intent column."""
    op.add_column(
        "candidate_paper",
        sa.Column("citation_intent", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    """Drop the citation_intent column."""
    op.drop_column("candidate_paper", "citation_intent")
