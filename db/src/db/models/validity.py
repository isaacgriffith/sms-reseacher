"""Study-generic threats-to-validity records (TFIX11).

Implements the two frameworks that ``docs/methodology/09-threats-to-validity.md``
keeps deliberately separate:

- **Framework A — Ampatzoglou et al.**: the *catalogue*. Which specific things
  can go wrong, encoded as :class:`ValidityThreatId`.
- **Framework B — Petersen & Gencel**: the *reporting taxonomy*. Which heading
  each acknowledged threat is filed under, encoded as :class:`ValidityCategory`
  and matching the six keys already used by ``Study.validity``.

**Rapid Reviews are out of scope here, by design.** The chapter assigns Rapid
Cartaxo's disclosure regime — "every methodological concession is itself a
threat" — which :class:`~db.models.rapid_review.RRThreatToValidity` already
implements with its own concession-shaped vocabulary. SLR, SMS and Tertiary get
Ampatzoglou. Merging the two into one enum would conflate frameworks the source
holds apart.

**Why this is not a copy of ``RRThreatToValidity``.** Ampatzoglou's four-step
author-side procedure ends at step 4: for each identified threat, either report
a mitigation action *or* acknowledge that the threat is not (fully) mitigated.
The chapter singles this out as the enforceable one — "an identified threat with
neither a mitigation nor an explicit acknowledgement is an incomplete study".
``RRThreatToValidity`` carries neither column, so copying it would have
reproduced that omission on three more study types.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, enum_values


class ValidityThreatId(str, enum.Enum):
    """Ampatzoglou catalogue entries the platform derives automatically.

    This is a **partial** encoding, not the full TV1–TV22 catalogue. Only the
    entries the platform can derive from configuration appear, because a member
    with no derivation rule behind it would be a checklist item the chapter
    explicitly argues against: threats "should be *derived from the protocol
    configuration* rather than presented as a flat checklist".

    ``docs/methodology/09-threats-to-validity.md`` remains the source of truth
    for the catalogue; add a member here only alongside the rule that derives it.
    """

    TV7 = "tv7"
    """Study inclusion/exclusion — conflicting or over-generic criteria applied
    during filtering. Category 1, Study Selection Validity."""

    TV13_4 = "tv13_4"
    """Unverified data extraction — "not validated by external or internal
    review". A sub-threat of TV13, which the chapter calls "one of the most
    common" threats in SE. Category 2, Data Validity."""

    TV16 = "tv16"
    """Researcher bias — bias in interpreting or synthesising, which the chapter
    defines as "including **only one author doing the synthesis**". Category 2,
    Data Validity."""


class ValidityCategory(str, enum.Enum):
    """Petersen & Gencel reporting categories (Maxwell's classification).

    Deliberately identical to the six keys of the ``Study.validity`` JSON column
    rendered by ``ValidityForm``, so a threat can be filed under the heading its
    discussion already lives in.

    The chapter recommends Maxwell over the classical Cook & Campbell set
    because the classical categories are positivist and quantitative, whereas
    software engineering research is in practice pragmatist and multi-method.
    """

    DESCRIPTIVE = "descriptive"
    THEORETICAL = "theoretical"
    GENERALIZABILITY_INTERNAL = "generalizability_internal"
    GENERALIZABILITY_EXTERNAL = "generalizability_external"
    INTERPRETIVE = "interpretive"
    REPEATABILITY = "repeatability"


class StudyValidityThreat(Base):
    """One identified threat to validity for a non-Rapid study.

    Rows are **derived from configuration**, not entered by hand, and
    re-derivation is idempotent via the ``(study_id, threat_id)`` unique
    constraint. What the researcher supplies is the step-4 outcome:
    :attr:`mitigation` or :attr:`acknowledgement`.

    :attr:`is_applicable` is a flag rather than a delete so that a threat which
    stops applying — a second reviewer joins — does not take the researcher's
    recorded text with it. Reviewer rows are created lazily when a member first
    records a decision, so applicability genuinely does change mid-study.
    """

    __tablename__ = "study_validity_threat"
    __table_args__ = (UniqueConstraint("study_id", "threat_id", name="uq_study_validity_threat"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    threat_id: Mapped[ValidityThreatId] = mapped_column(
        Enum(ValidityThreatId, values_callable=enum_values, name="validity_threat_id_enum"),
        nullable=False,
    )
    validity_category: Mapped[ValidityCategory] = mapped_column(
        Enum(ValidityCategory, values_callable=enum_values, name="validity_category_enum"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_detail: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="What in the configuration produced this threat, e.g. '1 human reviewer'",
    )
    mitigation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Step 4, first outcome: an action taken to reduce the threat",
    )
    acknowledgement: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Step 4, second outcome: the threat is accepted and not (fully) mitigated",
    )
    is_applicable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
        comment="False once the configuration that derived this threat no longer holds",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @property
    def is_addressed(self) -> bool:
        """Return whether this threat satisfies Ampatzoglou's step 4.

        Either outcome counts, and neither ranks above the other — a lone
        researcher who cannot mitigate must still be able to complete the
        study by acknowledging, because the corpus permits single-reviewer
        work and forbids only doing it silently.

        Whitespace does not count: a gate that a space bar satisfies is not
        a gate.

        Returns:
            ``True`` when a non-blank mitigation or acknowledgement is present.

        """
        return bool((self.mitigation or "").strip() or (self.acknowledgement or "").strip())

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<StudyValidityThreat study={self.study_id} threat={self.threat_id} "
            f"addressed={self.is_addressed}>"
        )
