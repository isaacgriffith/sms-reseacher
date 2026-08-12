"""The Ampatzoglou TV1–TV22 catalogue as data (TFIX15 part 1).

Ampatzoglou's four-step author procedure (`09-threats-to-validity.md` 165-173)
puts **step 3** as "**check every threat** for whether it pertains to the
study". The platform encoded three catalogue entries, so 30 threats were never
put in front of anyone and step 3 could not be performed at all.

Two things the chapter says, which pull in different directions and are both
honoured here:

- Threats "should be **derived from the protocol configuration** rather than
  presented as a flat checklist" (ch.09 90-92) — so anything computable is
  computed, and the researcher is not asked about it.
- Step 3 requires *every* threat to be checked — so what cannot be computed is
  still presented, and is answered by the author rather than silently skipped.

:data:`CATALOGUE` therefore carries all 39 rows of the chapter's three tables,
of which six are group umbrellas and 33 are individually assessable.

**On reporting categories.** Only a few entries carry one. ch.09 220-223 gives
exactly three worked Ampatzoglou→Petersen pairings, and ch.09 206-210 attaches
an extraction caveat to everything else: the source's Tables IV and V "were
**displaced by one row** in text extraction … the cell-by-cell cross-mapping
must be verified against the PDF before being quoted". Assigning the rest from
inference would be manufacturing a mapping the corpus does not contain. The
researcher files those headings themselves, which is consistent with ch.09
217-218 describing Petersen & Gencel as "the reporting taxonomy" — a decision
about the write-up rather than about the study.

@module validity_catalogue
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from db.models.validity import ValidityCategory, ValidityThreatId


class ThreatPhase(StrEnum):
    """The chapter's three catalogue categories (ch.09 51, 94, 136)."""

    STUDY_SELECTION = "study_selection"
    DATA = "data"
    RESEARCH = "research"


class Derivation(StrEnum):
    """How a threat's applicability is settled.

    ``ASK`` is not a failure state. It is what step 3 requires for anything the
    configuration cannot answer, and marking it explicitly is what keeps the
    derived set honest.
    """

    #: Computed from configuration; the researcher is not asked.
    DERIVED = "derived"
    #: Put to the researcher, because nothing in the configuration decides it.
    ASK = "ask"
    #: A group umbrella. Not assessable — its children are.
    GROUP = "group"


@dataclass(frozen=True)
class ThreatDefinition:
    """One row of the Ampatzoglou catalogue.

    Attributes:
        threat_id: The catalogue identifier.
        label: The chapter's short name for the threat.
        what_goes_wrong: The chapter's own description.
        phase: Which of the three categories it belongs to.
        derivation: Whether the platform computes applicability or asks.
        parent: The group this is a sub-threat of, if any.
        reporting_category: Petersen & Gencel heading, **only** where ch.09
            states the pairing. ``None`` means the researcher files it.
        category_source: Why :attr:`reporting_category` is what it is. ``None``
            when there is no category.

    """

    threat_id: ValidityThreatId
    label: str
    what_goes_wrong: str
    phase: ThreatPhase
    derivation: Derivation
    parent: ValidityThreatId | None = None
    reporting_category: ValidityCategory | None = None
    category_source: str | None = None


_C1 = ThreatPhase.STUDY_SELECTION
_C2 = ThreatPhase.DATA
_C3 = ThreatPhase.RESEARCH
_ASK = Derivation.ASK
_DERIVED = Derivation.DERIVED
_GROUP = Derivation.GROUP

#: ch.09 220-221: TV1.2 "is discussed under **theoretical validity**, because it
#: concerns whether the study captured what it intended to". Stated for TV1.2
#: alone — deliberately not extended to its TV1 siblings, because the chapter
#: does not extend it.
_SRC_TV1_2 = "ch.09 220-221"

#: ch.09 222: "TV13 (extraction bias) is filed under **descriptive validity**."
#: Applied to the TV13 sub-threats because they *are* TV13.
_SRC_TV13 = "ch.09 222"

#: ch.09 223: "TV22 (generalizability) maps to **generalizability** directly."
#: :class:`ValidityCategory` splits that into internal and external, so the
#: chapter's word alone does not pick a member. TV22.2's own text — "not
#: applicable to other **domains/organisations**" — is what selects external.
_SRC_TV22_2 = "ch.09 223 + TV22.2's own wording"

CATALOGUE: tuple[ThreatDefinition, ...] = (
    # --- Category 1 — Study Selection Validity (ch.09 51-66) ---------------
    ThreatDefinition(
        ValidityThreatId.TV1,
        "Adequacy of relevant publication identification",
        "The umbrella for five search-process failures.",
        _C1,
        _GROUP,
    ),
    ThreatDefinition(
        ValidityThreatId.TV1_1,
        "Construction of search string",
        "Returns far too many irrelevant studies, or too few, missing relevant ones.",
        _C1,
        _ASK,
        parent=ValidityThreatId.TV1,
    ),
    ThreatDefinition(
        ValidityThreatId.TV1_2,
        "Selection of digital libraries",
        "Libraries too specific, too broad, or not credible.",
        _C1,
        _DERIVED,
        parent=ValidityThreatId.TV1,
        reporting_category=ValidityCategory.THEORETICAL,
        category_source=_SRC_TV1_2,
    ),
    ThreatDefinition(
        ValidityThreatId.TV1_3,
        "Selection of publication venues",
        (
            "Choosing specific venues over broad engines — usually because the "
            "topic is broad or only high-quality work is wanted — and missing "
            "relevant studies."
        ),
        _C1,
        _DERIVED,
        parent=ValidityThreatId.TV1,
    ),
    ThreatDefinition(
        ValidityThreatId.TV1_4,
        "Definition of starting year",
        (
            "An arbitrary start date drops earlier work. Only acceptable if you "
            "can say why it does not affect results."
        ),
        _C1,
        _ASK,
        parent=ValidityThreatId.TV1,
    ),
    ThreatDefinition(
        ValidityThreatId.TV1_5,
        "Search engine inefficiencies",
        (
            "Engine limitations (e.g. cannot search abstract-only) cause misses "
            "or an unmanageably large corpus."
        ),
        _C1,
        _ASK,
        parent=ValidityThreatId.TV1,
    ),
    ThreatDefinition(
        ValidityThreatId.TV2,
        "Limited journals/conferences",
        "Primary studies confined to few venues implies a narrow scope and a low yield.",
        _C1,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV3,
        "Missing non-English papers",
        (
            "Only a real threat where an active community publishes high-quality "
            "work in another language."
        ),
        _C1,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV4,
        "Paper inaccessibility",
        "Full texts unobtainable; if many, the retrieved set is unrepresentative.",
        _C1,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV5,
        "Handling of duplicate articles",
        "Conference and extended journal versions double-counted.",
        _C1,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV6,
        "Inclusion/exclusion of grey literature",
        "Either choice can be a threat — it depends on the study's goal.",
        _C1,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV7,
        "Study inclusion/exclusion",
        "Conflicting or over-generic criteria applied during filtering.",
        _C1,
        _DERIVED,
    ),
    # --- Category 2 — Data Validity (ch.09 94-115) -------------------------
    ThreatDefinition(
        ValidityThreatId.TV8,
        "Small sample size",
        "Results prone to bias, not statistically significant, unsafe to generalise.",
        _C2,
        _GROUP,
    ),
    ThreatDefinition(
        ValidityThreatId.TV8_1,
        "Small sample size",
        "As the group above.",
        _C2,
        _ASK,
        parent=ValidityThreatId.TV8,
    ),
    ThreatDefinition(
        ValidityThreatId.TV8_2,
        "Primary study heterogeneity",
        "Highly heterogeneous data cannot be synthesised without heavy subjectivity.",
        _C2,
        _ASK,
        parent=ValidityThreatId.TV8,
    ),
    ThreatDefinition(
        ValidityThreatId.TV9,
        "Choice of variables to extract",
        "Variables that do not answer the research questions; prone to researcher bias.",
        _C2,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV10,
        "Publication bias",
        ("Most primary studies from one venue, so the dataset reflects one community's beliefs."),
        _C2,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV11,
        "Lack of relationships",
        "Data with no relations in it cannot yield a conclusion.",
        _C2,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV12,
        "Validity of primary studies",
        ("Inaccurate primary results bias the review. Negative results are less likely published."),
        _C2,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV13,
        "Data extraction bias",
        "One of the most common threats in SE.",
        _C2,
        _GROUP,
        reporting_category=ValidityCategory.DESCRIPTIVE,
        category_source=_SRC_TV13,
    ),
    ThreatDefinition(
        ValidityThreatId.TV13_1,
        "Data extraction bias",
        "Open questions in collected variables, handling not specified in the protocol.",
        _C2,
        _ASK,
        parent=ValidityThreatId.TV13,
        reporting_category=ValidityCategory.DESCRIPTIVE,
        category_source=_SRC_TV13,
    ),
    ThreatDefinition(
        ValidityThreatId.TV13_2,
        "Quality assessment subjectivity",
        "Only relevant where primary-study quality is evaluated.",
        _C2,
        _DERIVED,
        parent=ValidityThreatId.TV13,
        reporting_category=ValidityCategory.DESCRIPTIVE,
        category_source=_SRC_TV13,
    ),
    ThreatDefinition(
        ValidityThreatId.TV13_3,
        "Data extraction inaccuracies",
        "The same concept classified inconsistently across studies.",
        _C2,
        _ASK,
        parent=ValidityThreatId.TV13,
        reporting_category=ValidityCategory.DESCRIPTIVE,
        category_source=_SRC_TV13,
    ),
    ThreatDefinition(
        ValidityThreatId.TV13_4,
        "Unverified data extraction",
        "Not validated by external or internal review.",
        _C2,
        _DERIVED,
        parent=ValidityThreatId.TV13,
        reporting_category=ValidityCategory.DESCRIPTIVE,
        category_source=_SRC_TV13,
    ),
    ThreatDefinition(
        ValidityThreatId.TV13_5,
        "Misclassification of primary studies",
        "Mostly a mapping-study threat.",
        _C2,
        _DERIVED,
        parent=ValidityThreatId.TV13,
        reporting_category=ValidityCategory.DESCRIPTIVE,
        category_source=_SRC_TV13,
    ),
    ThreatDefinition(
        ValidityThreatId.TV14,
        "Lack of statistical analysis",
        "Sometimes unavoidable — e.g. all data items categorical.",
        _C2,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV15,
        "Bias of classification schema",
        "Mapping studies using an inadequate schema or attribute framework.",
        _C2,
        _GROUP,
    ),
    ThreatDefinition(
        ValidityThreatId.TV15_1,
        "Robustness of initial classification",
        "A pre-existing schema that does not fit the domain and resists tailoring.",
        _C2,
        _ASK,
        parent=ValidityThreatId.TV15,
    ),
    ThreatDefinition(
        ValidityThreatId.TV15_2,
        "Construction of attribute framework",
        "Attribute values not discrete and comprehensive, giving an insufficient dataset.",
        _C2,
        _ASK,
        parent=ValidityThreatId.TV15,
    ),
    ThreatDefinition(
        ValidityThreatId.TV16,
        "Researcher bias",
        "Bias in interpreting or synthesising — including only one author doing the synthesis.",
        _C2,
        _DERIVED,
    ),
    # --- Category 3 — Research Validity (ch.09 136-148) --------------------
    ThreatDefinition(
        ValidityThreatId.TV17,
        "Repeatability",
        "Cannot replicate the study — usually from a missing detailed protocol.",
        _C3,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV18,
        "Research method bias",
        "Wrong method chosen, or deviation from the established process.",
        _C3,
        _GROUP,
    ),
    ThreatDefinition(
        ValidityThreatId.TV18_1,
        "Chosen research method",
        "SMS and SLR serve different goals; the wrong one was picked.",
        _C3,
        _ASK,
        parent=ValidityThreatId.TV18,
    ),
    ThreatDefinition(
        ValidityThreatId.TV18_2,
        "Review process deviation",
        "Departing from the guidelines requires strong argumentation.",
        _C3,
        _ASK,
        parent=ValidityThreatId.TV18,
    ),
    ThreatDefinition(
        ValidityThreatId.TV19,
        "Coverage of research questions",
        "Questions do not fulfil the study goal — too generic a goal, or poor decomposition.",
        _C3,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV20,
        "Lack of comparable studies",
        "No related work to compare findings against.",
        _C3,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV21,
        "Unfamiliarity with the research field",
        (
            "Non-expert reviewers omit well-known studies, synthesise poorly, "
            "cannot reason about findings. ch.09 157-162: automation that "
            "removes the need to become familiar does not mitigate this threat "
            "— it conceals it."
        ),
        _C3,
        _ASK,
    ),
    ThreatDefinition(
        ValidityThreatId.TV22,
        "Generalizability",
        "Results not generalisable — e.g. only part of the literature was found.",
        _C3,
        _GROUP,
    ),
    ThreatDefinition(
        ValidityThreatId.TV22_2,
        "Not applicable to other domains/organisations",
        "The frequently reported special case.",
        _C3,
        _ASK,
        parent=ValidityThreatId.TV22,
        reporting_category=ValidityCategory.GENERALIZABILITY_EXTERNAL,
        category_source=_SRC_TV22_2,
    ),
)

#: Catalogue keyed by id, for lookup.
BY_ID: dict[ValidityThreatId, ThreatDefinition] = {d.threat_id: d for d in CATALOGUE}

#: The entries a researcher can be asked about. Group umbrellas are excluded:
#: they organise their children and are not separately assessable.
ASSESSABLE: tuple[ThreatDefinition, ...] = tuple(
    d for d in CATALOGUE if d.derivation is not Derivation.GROUP
)
