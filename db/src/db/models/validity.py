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
    """The full Ampatzoglou TV1–TV22 catalogue.

    TFIX15. This was previously a **partial** encoding of three entries, on the
    reasoning that a member without a derivation rule would be the flat
    checklist the chapter argues against. That reasoning was half right and made
    the catalogue fail Ampatzoglou's own **step 3** — "**check every threat** for
    whether it pertains to the study" (ch.09 169). A threat that is never
    presented is never checked, so a three-entry catalogue cannot perform step 3
    however well it derives those three.

    What the chapter actually argues against is asking the author about threats
    the platform could have answered itself: threats "should be *derived from
    the protocol configuration* rather than presented as a flat checklist"
    (ch.09 90-92). Derivation and coverage are therefore both required, and
    :mod:`backend.services.validity_catalogue` records which entries the
    platform derives and which it must ask about.

    **Count.** ch.09 40 quotes the source as "22 top-level threats … expanding
    to **34 distinct named threats**". The tables below yield 39 rows, six of
    them group umbrellas, so **33** are individually assessable. The difference
    is not an omission here: ch.09 43-46 records that the source's own figures
    duplicate the labels "TV1.3" and "TV15", and states that the chapter's
    numbering "follows the checklist, which is internally consistent". These
    members follow the chapter's tables for that reason. Do not invent a
    ``TV22_1`` to reconcile the arithmetic — the source's missing label is a
    recorded defect, not a gap to fill.
    """

    # --- Category 1 — Study Selection Validity (ch.09 51-66) ---------------

    TV1 = "tv1"
    """*Group.* Adequacy of relevant publication identification — the umbrella
    for five search-process failures."""

    TV1_1 = "tv1_1"
    """Construction of search string — "returns far too many irrelevant studies,
    or too few, missing relevant ones"."""

    TV1_2 = "tv1_2"
    """Selection of digital libraries — "libraries too specific, too broad, or
    not credible"."""

    TV1_3 = "tv1_3"
    """Selection of publication venues — choosing specific venues over broad
    engines and missing relevant studies. Subject to the mutual-exclusivity rule
    at ch.09 85-88."""

    TV1_4 = "tv1_4"
    """Definition of starting year — "an arbitrary start date drops earlier
    work. **Only acceptable if you can say why it does not affect results**"."""

    TV1_5 = "tv1_5"
    """Search engine inefficiencies — engine limitations cause misses or an
    unmanageably large corpus."""

    TV2 = "tv2"
    """Limited journals/conferences — primary studies confined to few venues
    implies a narrow scope and a low yield."""

    TV3 = "tv3"
    """Missing non-English papers — "only a real threat where an active community
    publishes high-quality work in another language"."""

    TV4 = "tv4"
    """Paper inaccessibility — full texts unobtainable; if many, the retrieved
    set is unrepresentative."""

    TV5 = "tv5"
    """Handling of duplicate articles — conference and extended journal versions
    double-counted."""

    TV6 = "tv6"
    """Inclusion/exclusion of grey literature — "either choice can be a threat —
    it depends on the study's goal"."""

    TV7 = "tv7"
    """Study inclusion/exclusion — conflicting or over-generic criteria applied
    during filtering."""

    # --- Category 2 — Data Validity (ch.09 94-115) -------------------------

    TV8 = "tv8"
    """*Group.* Small sample size — results prone to bias, not statistically
    significant, unsafe to generalise."""

    TV8_1 = "tv8_1"
    """Small sample size."""

    TV8_2 = "tv8_2"
    """Primary study heterogeneity — "highly heterogeneous data cannot be
    synthesised without heavy subjectivity"."""

    TV9 = "tv9"
    """Choice of variables to extract — variables that do not answer the research
    questions; prone to researcher bias."""

    TV10 = "tv10"
    """Publication bias — most primary studies from one venue, so the dataset
    reflects one community's beliefs."""

    TV11 = "tv11"
    """Lack of relationships — data with no relations in it cannot yield a
    conclusion."""

    TV12 = "tv12"
    """Validity of primary studies — inaccurate primary results bias the review;
    negative results are less likely published."""

    TV13 = "tv13"
    """*Group.* Data extraction bias — "**one of the most common**" threats in
    SE."""

    TV13_1 = "tv13_1"
    """Data extraction bias — open questions in collected variables, handling not
    specified in the protocol."""

    TV13_2 = "tv13_2"
    """Quality assessment subjectivity — "only relevant where primary-study
    quality is evaluated"."""

    TV13_3 = "tv13_3"
    """Data extraction inaccuracies — the same concept classified inconsistently
    across studies."""

    TV13_4 = "tv13_4"
    """Unverified data extraction — "not validated by external or internal
    review"."""

    TV13_5 = "tv13_5"
    """Misclassification of primary studies — "mostly a mapping-study threat"."""

    TV14 = "tv14"
    """Lack of statistical analysis — "sometimes unavoidable — e.g. all data
    items categorical"."""

    TV15 = "tv15"
    """*Group.* Bias of classification schema — mapping studies using an
    inadequate schema or attribute framework."""

    TV15_1 = "tv15_1"
    """Robustness of initial classification — a pre-existing schema that does not
    fit the domain and resists tailoring."""

    TV15_2 = "tv15_2"
    """Construction of attribute framework — attribute values not discrete and
    comprehensive, giving an insufficient dataset."""

    TV16 = "tv16"
    """Researcher bias — bias in interpreting or synthesising, "including **only
    one author doing the synthesis**"."""

    # --- Category 3 — Research Validity (ch.09 136-148) --------------------

    TV17 = "tv17"
    """Repeatability — "cannot replicate the study — usually from a missing
    detailed protocol"."""

    TV18 = "tv18"
    """*Group.* Research method bias — wrong method chosen, or deviation from the
    established process."""

    TV18_1 = "tv18_1"
    """Chosen research method — "SMS and SLR serve different goals; the wrong one
    was picked"."""

    TV18_2 = "tv18_2"
    """Review process deviation — departing from the guidelines "**requires
    strong argumentation**"."""

    TV19 = "tv19"
    """Coverage of research questions — questions do not fulfil the study goal."""

    TV20 = "tv20"
    """Lack of comparable studies — no related work to compare findings
    against."""

    TV21 = "tv21"
    """Unfamiliarity with the research field — non-expert reviewers omit
    well-known studies, synthesise poorly, cannot reason about findings.

    ch.09 157-162 flags this as "the threat this platform most directly
    addresses, and most directly risks", because "automation that removes the
    need to become familiar does not mitigate this threat — it conceals it".
    """

    TV22 = "tv22"
    """*Group.* Generalizability — results not generalisable, e.g. only part of
    the literature was found."""

    TV22_2 = "tv22_2"
    """Not applicable to other domains/organisations — "the frequently reported
    special case". There is no ``TV22_1``; see the class docstring."""


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

    Rows are materialised for the whole catalogue so Ampatzoglou's **step 3** —
    "check every threat for whether it pertains to the study" — can actually be
    performed. Re-derivation is idempotent via the ``(study_id, threat_id)``
    unique constraint. What the researcher supplies is the step-4 outcome:
    :attr:`mitigation` or :attr:`acknowledgement`.

    :attr:`is_applicable` is a flag rather than a delete so that a threat which
    stops applying — a second reviewer joins — does not take the researcher's
    recorded text with it. Reviewer rows are created lazily when a member first
    records a decision, so applicability genuinely does change mid-study.

    TFIX15. :attr:`is_applicable` is **nullable**, and the three states are
    distinct: ``True`` applies, ``False`` was checked and ruled out, ``None`` has
    not been checked yet. Step 3 is a check, and a check that cannot record
    "not yet looked at" cannot report its own completeness — the previous
    two-valued column made an unexamined threat indistinguishable from one
    deliberately dismissed.
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
    validity_category: Mapped[ValidityCategory | None] = mapped_column(
        Enum(ValidityCategory, values_callable=enum_values, name="validity_category_enum"),
        nullable=True,
        comment=(
            "Petersen & Gencel reporting heading. NULL until filed — ch.09 "
            "sources only three pairings and warns the rest must be checked "
            "against the PDF first."
        ),
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
    is_applicable: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=None,
        comment=(
            "Step 3 applicability. True applies, False was checked and ruled "
            "out, NULL has not been checked yet."
        ),
    )
    applicability_is_derived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment=(
            "True when the platform computed is_applicable from configuration; "
            "False when a researcher answered it. Keeps derivation from "
            "silently overwriting a human judgement."
        ),
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
