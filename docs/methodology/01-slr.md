# 01 — Systematic Literature Review

**Primary source**: Kitchenham & Charters 2007, *Guidelines for performing Systematic Literature
Reviews in Software Engineering*, EBSE-2007-01 v2.3.
**Amended by**: Kitchenham et al. 2013, *A systematic review of systematic review process research
in SE* — eleven numbered changes its own authors recommend.
**Supersedes**: `docs/systematic-literature-reviews.md`.

> **Read the amendments first.** The 2007 guidelines are the foundation, but two of their most
> distinctive recommendations were later withdrawn by the same authors. Encoding the 2007 text
> unmodified would encode advice that has been retracted.

---

## The eleven amendments (Kitchenham et al. 2013)

Numbered as the source numbers them. Paraphrased; consult the source for exact wording.

| # | Amendment | Effect on this platform |
| - | --------- | ----------------------- |
| 1 | **Remove** constructing structured questions and using them to build search strings. It does not work for mapping studies and is of limited value to SLRs generally — it produces very complex strings needing per-library adaptation | PICOC stays useful for *scoping the question*; it must **not** be the mechanical source of the search string |
| 2 | **Add** the quasi-gold standard approach, to integrate manual and automated search and measure search effectiveness | Directly implementable — see [06](./06-search-and-selection.md) |
| 3 | **Add** consideration of textual analysis tools to check consistency of inclusion/exclusion decisions and categorisations | An automation opening this platform is well placed to fill |
| 4 | **Remove** the reference to using a data extractor and a data checker | ⚠ Note the conflict recorded below |
| 5 | **Add** more on data synthesis, especially qualitative and mixed-methods studies | See [08](./08-extraction-and-synthesis.md) |
| 6 | **Add** more advice on mapping studies, or produce separate guidelines | Petersen 2015 did this — see [02](./02-sms.md) |
| 7 | **Add** the need to report how duplicate studies are handled | A reportable field, not just an internal dedup step |
| 8 | **Emphasise** keeping records of the conduct of the study | Argues for an immutable audit log |
| 9 | **Add** citation-based search strategies (snowballing) | See [06](./06-search-and-selection.md) |
| 10 | **Add** more examples and advice on constructing protocols | |
| 11 | **Add** references to SE study-specific checklists | |

On quality checklists the same paper is blunt: the discussion in the current guidelines is not
useful, and **"the current unhelpful guidelines should be removed but it is not clear what should
replace them."** See [07](./07-quality-assessment.md) for what the field offers instead.

> **◐ DISPUTED — extractor/checker.** Amendment 4 removes it. But Kitchenham et al. also report that
> two papers recommended an extractor and a checker, while one paper that used the approach felt it
> **allowed invalid data collection to go unnoticed**. The 2007 guidelines recommend it and give a
> worked example including a conflict-of-interest rule (the extractor was never a co-author of the
> primary study). This platform should support the pattern but not mandate it, and should record
> which pattern a study used.

---

## Phase 1 — Planning

### 1.1 Identify the need for a review

Establish that the review is necessary by finding and evaluating any **existing** reviews of the
same phenomenon.

**Two instruments for that evaluation**, both reusable later to evaluate your own report:

**DARE — 4 questions, scored** (the version used throughout the SE tertiary studies; half points are
allowed, so the scale is effectively 0–4 in 0.5 steps):
1. Are the review's inclusion and exclusion criteria described and appropriate?
2. Is the literature search likely to have covered all relevant studies?
3. Did the reviewers assess the quality/validity of the included studies?
4. Were the basic data/studies adequately described?

**CRD — 9 questions**, longer: objectives; sources searched and restrictions; inclusion/exclusion
criteria and their application; quality criteria used; how quality criteria were applied; how data
were extracted; how data were synthesised; how differences between studies were investigated and
whether combining was reasonable; whether conclusions follow from the evidence.

**Consumes**: topic, initial scope. **Produces**: justification, and a decision to proceed or not.

> **⚙ IMPLEMENTATION.** DARE is a 4-item scored rubric over an existing structured report object —
> the cheapest useful evaluator this platform could build, and it serves double duty as the
> need-for-review gate and the report self-check. Relevant to gap **G10**.

### 1.2 Commission the review *(optional)*

Only when an external body requests it. The commissioning document covers: title, background,
review questions, advisory/steering group membership (researchers, practitioners, lay members,
policy makers), methods, timetable, dissemination strategy, support infrastructure, budget,
references.

> **⚠ CAVEAT.** If commissioning is skipped — the normal case for a research team or a PhD — the
> **dissemination strategy must move into the protocol**. It is otherwise silently lost, and it is
> the step that decides whether practitioners ever see the result.

### 1.3 Specify the research questions

The single most important activity. The questions drive everything downstream: search must find
studies that address them, extraction must capture what answers them, synthesis must combine so
they *can* be answered.

**Question types in SE** (adapted from six healthcare types; SE has no clear analogue of
diagnostic-test performance):
- Effect of a software engineering technology
- Frequency or rate of a project development factor (adoption, success/failure)
- Cost and risk factors associated with a technology
- Impact of technologies on reliability, performance and cost models
- Cost-benefit analysis of employing a technology

**A good question** is meaningful to practitioners as well as researchers; leads either to a change
in practice or to increased confidence in current practice; and identifies discrepancies between
common belief and reality. Researcher-facing questions (scoping future work, positioning a PhD) are
legitimate but should be recognised as such.

**PICOC** — for *framing*, no longer for string construction (amendment 1):

| Element | In SE | Trap |
| ------- | ----- | ---- |
| **Population** | Role (tester, manager), experience level, application area, industry group | Medicine narrows population to cut study counts. **SE has too few studies — do not restrict population** until considering practical implications |
| **Intervention** | The method / tool / technology / procedure | |
| **Comparison** | The control treatment | **"Not using the intervention" is an inadequate control description.** SE techniques require training, so users-vs-non-users confounds technique with training — acute with students |
| **Outcome** | Reliability, cost, time to market — things practitioners care about | **Surrogate measures are endemic** (defects in system test for quality; coupling for design quality). Conclusions resting on surrogates are weaker |
| **Context** | Academia vs industry; practitioners vs students; task scale | Academic + student + small-scale is unrepresentative — but in SE it may be all that exists |

**Study designs**: medicine can restrict to RCTs. SE's scarcity of primary studies means protocols
usually must **aggregate across widely different study types**.

> **⚠ CAVEAT (Staples & Niazi).** Also write down the **complementary questions you are deliberately
> not answering**. Their worked example distinguished *why organisations adopt* CMM-based SPI from
> *what motivates individuals*, *why they should*, and *what benefits they got*. They report this
> directly improved and clarified both selection and extraction. Neither this nor the **unit of
> analysis** appears in the 2007 guidelines, and both are needed.

> **⚙ IMPLEMENTATION.** Complementary questions and unit of analysis are protocol fields the
> platform does not model. Unit of analysis connects to gap **G6** — a paper is not a study, and the
> guidelines never say which one you are counting.

### 1.4 Develop the review protocol

The instrument that reduces researcher bias: without it, selection or analysis may be driven by
researcher expectations.

**Ten components**: background/rationale · research questions · search strategy (terms and
resources) · study selection criteria · study selection procedures (how many assessors, how
disagreements resolve) · quality assessment checklists and procedures · data extraction strategy
(including a validation process where data require manipulation or inference) · synthesis strategy
(whether meta-analysis is intended, and which techniques) · dissemination strategy · timetable.

> **⚠ CAVEATS on protocol construction.**
> - A **pre-review mapping study** may be needed to scope the questions at all.
> - **Expect to revise the questions during protocol development.** Multiple sources report the
>   protocol takes a long time and will be revised.
> - **Every team member must take part in developing it** — otherwise they will not understand the
>   extraction process they are about to perform.
> - **Piloting is essential.** It finds mistakes in collection and aggregation and may force changes
>   to extraction forms and synthesis methods.
> - Limit scope by choosing **clear and narrow** questions.

### 1.5 Evaluate the protocol

Independent experts if funded; supervisors for a PhD. Reuse the DARE/CRD questions, plus three
**internal consistency checks**:
1. Are the search strings appropriately derived from the research questions?
2. Will the data to be extracted properly address the research questions?
3. Is the data analysis procedure appropriate to answer the research questions?

> **⚙ IMPLEMENTATION.** These three are mechanically checkable and map onto the existing
> `ProtocolReviewerAgent`. They are traceability checks — question → string, question → field,
> question → analysis — not prose review.

---

## Phase 2 — Conducting

### 2.1 Identification of research

The rigour of the search is what distinguishes an SLR from a traditional review. See
[06-search-and-selection.md](./06-search-and-selection.md) for the full treatment, including
snowballing, quasi-gold standards, and the evidence that database search alone is inadequate.

**In brief**: build the strategy iteratively; run preliminary searches to find existing reviews and
gauge volume; trial strings; **check trial strings against a set of already-known papers**; consult
experts. Digital libraries alone are **not sufficient** — also search reference lists, journals and
proceedings, grey literature, research registers, the web, and approach researchers directly.

**Recommended database set** (Kitchenham 2013, for automated string-based search): **IEEE and ACM,
plus at least two general indexing systems** such as SCOPUS, EI Compendex or Web of Science.

**Documenting the search** — must be transparent and replicable: record it **as it occurs**, note
and justify changes, and **retain the unfiltered results** for reanalysis. Per source type record
database name, the per-database strategy, date of search, and years covered; for hand searches the
journal, years, and any issues skipped; for unpublished-work efforts the groups and researchers
contacted and sites searched with dates and URLs.

**Publication bias**: positive results are likelier to be published; worse for formal experiments,
and worst where an influential body sponsors the technology. Counter by scanning grey literature and
proceedings, contacting researchers for unpublished results, and testing statistically with funnel
plots.

### 2.2 Study selection

**Multistage.** Interpret criteria **liberally** at first — get the full text unless a paper is
clearly excludable on title and abstract.

> **⚠ CAVEAT.** "The standard of IT and software engineering abstracts is too poor to rely on when
> selecting primary studies. You should also review the conclusions." This is repeated by multiple
> independent papers and is one of the most consistently reported traps in the corpus.

Then apply practical criteria: language, journal, authors, setting, participants, research design,
sampling method, publication date. Optionally add a third stage on detailed quality criteria.

**Excluded-study logging.** Textbooks say log everything excluded. Kitchenham's practical amendment:
log exclusions **only after the totally irrelevant papers are removed** — record those excluded by
the *detailed* criteria, where the reason is informative.

**Masking authors/institutions is not worth it** — evidence suggests it does not improve reviews and
it costs time.

**Reliability of inclusion decisions**: two or more researchers, agreement measured with **Cohen's
Kappa**, and the *initial* Kappa reported. Every disagreement must be discussed and resolved.
Residual uncertainty feeds sensitivity analysis. **A single researcher must use test–retest**:
re-evaluate a random sample of already-screened papers to check their own consistency.

> **⚙ IMPLEMENTATION.** Test–retest for the single-reviewer case is gap **G4**. The platform
> supports single-reviewer studies (Rapid Review explicitly) with no reliability evidence at all.

See [06](./06-search-and-selection.md) for selection decision rules when reviewers disagree.

### 2.3 Study quality assessment

Full treatment in [07-quality-assessment.md](./07-quality-assessment.md). The essentials:

**Five purposes**: finer inclusion/exclusion; testing whether quality explains differing results;
weighting during synthesis; guiding interpretation and strength of inference; guiding
recommendations for future research.

**Quality = minimising bias and maximising internal and external validity.** Internal validity is a
prerequisite for external validity.

**Two uses with different data flows** — this distinction is load-bearing:
1. **To select studies** → quality data are inclusion/exclusion criteria and **must be collected
   before main extraction, on separate forms**.
2. **To analyse** → quality data identify subsets to test against outcomes and **may be collected
   with the main extraction, on a joint form**.

> **⚠ CAVEATS.**
> - **Do not infer that unreported means not done.** Ask the authors.
> - Checklists must assess **methodological quality, not reporting quality**. Where both are scored,
>   keep them as separate metrics rather than one number.
> - **Weighting meta-analysis by quality score is not recommended by any medical guideline.**
> - Mixed study types need an instrument per type; qualitative and quantitative reviews need
>   different checklists outright.
> - Quality scores are only comparable **between studies of the same type and size** — small studies
>   can score well while providing limited evidence.
> - A checklist will not catch an invalid practice it does not ask about.

### 2.4 Data extraction

Forms are **defined and piloted when the protocol is defined**. They must capture everything needed
for the questions and the quality criteria. Numerical data are a **prerequisite for meta-analysis**.

**Standard fields beyond the question-specific ones**: reviewer name, extraction date, full
bibliographic details, and space for notes.

**Procedures**: two or more researchers extract independently where feasible; compare; resolve by
consensus or by an independent arbitrator; **use a separate form to record and correct
disagreements**; unresolved uncertainty feeds sensitivity analysis. Where double extraction is
unaffordable, have **a random sample extracted by everyone** to measure consistency. A lone
researcher uses supervisor cross-check on a sample, or test–retest.

**Duplicate publications**: never include the same data twice — it seriously biases results. Contact
authors to confirm. Use the **most complete** report, but consult all versions to obtain all data.
**Amendment 7 requires reporting how duplicates were handled.**

**Missing or manipulated data**: contact authors. If data must be reconstructed, **report as
published first**, then subject the manipulated version to sensitivity analysis.

> **⚠ CAVEAT — against automated extraction.** Kitchenham et al. distrust automatic extraction of
> results unless quality evaluation improves first: extracting from studies without checking whether
> a study used an invalid metric yields results "very quickly but will be wrong". **This is the
> sharpest methodological warning in the corpus for a platform like this one.** It does not forbid
> automation; it forbids extraction decoupled from appraisal.

Full treatment in [08-extraction-and-synthesis.md](./08-extraction-and-synthesis.md).

### 2.5 Data synthesis

Specified in the protocol, but refined once data exist — subset analysis for heterogeneity is
pointless if no heterogeneity appears.

**Descriptive/narrative**: tabulate intervention, population, context, sample sizes, outcomes and
quality, structured to expose similarities and differences and potential sources of heterogeneity.
Useful patterns: tabulate **by outcome**; flag replications that add no independent evidence; code
studies **chronologically** to expose trends over time.

**Quantitative**: effect measures for binary outcomes (odds, risk, odds ratio, relative risk,
absolute risk reduction) and continuous outcomes (mean difference, weighted mean difference,
standardised mean difference).

**Presentation**: forest plot for effects; funnel plot for publication bias.

**Anti-fishing rule**: identify possible sources of heterogeneity **in the protocol**, not post hoc.

**Sensitivity analysis** is required whether synthesis is quantitative or descriptive.

> **⚠ CAVEATS.**
> - SE SLRs are **usually descriptive**, not quantitative.
> - **Meta-analysis is often impossible** because reporting varies too much between studies.
> - Tabulation aggregates, but **you must explain how the tabulated data answer the questions** —
>   otherwise no synthesis has occurred. Nearly half of SE "systematic reviews" fail this bar.

Full treatment, including thematic synthesis and metasummary, in
[08-extraction-and-synthesis.md](./08-extraction-and-synthesis.md).

---

## Phase 3 — Reporting

Full treatment in [10-reporting-and-evaluation.md](./10-reporting-and-evaluation.md). In brief:

**Plan dissemination early** — in the commissioning document or the protocol. To reach practitioners
you need more than journals: practitioner magazines, press releases, summary leaflets, posters, web
pages, and direct communication to affected bodies. (Cartaxo's **Evidence Briefings** are the
worked-out form of this; see [03](./03-rapid-review.md).)

**Two output formats**: a technical report or thesis chapter carrying full detail, and a
journal/conference paper. Because papers have length limits, **the paper must reference the full
report** so readers can judge rigour.

**Report structure** follows SEGRESS (see [10](./10-reporting-and-evaluation.md)), which supersedes
the CRD-derived structure in the 2007 guidelines. Two items from the older structure are worth
keeping explicitly: **a flow diagram** of inclusion/exclusion (studies leave at different stages for
different reasons), and a **conflict of interest** declaration.

> **⚠ CAVEATS.** Keep a detailed record of decisions throughout, and **report deviations from the
> protocol**. The protocol is not a promise; failing to report where you departed from it is the
> defect.

---

## Effort, and who can do this

- Three PhD students each took **8–9 months** to perform an SLR — considered reasonable in a PhD.
- **MSc timescales of 2–3 months are likely insufficient** both to learn the process and to produce
  a high-quality study.
- **Repeatability depends on experience.** Two expert groups produced 9 of 10 identical studies and
  the same conclusions; two research associates produced different studies from each other and from
  a prior expert review. Reliable, auditable, consistent results are only likely "when SRs are
  undertaken by experienced researchers with domain knowledge."

> **⚙ IMPLEMENTATION.** This is the strongest argument for the platform's agent-assisted model: the
> evidence says outcome quality tracks reviewer experience, so encoded guidance and enforced gates
> are worth most precisely to the inexperienced reviewers who currently do worst. It is also a
> warning — automation that hides the process from a novice will reproduce the novice's error at
> speed.

---

## The three dominant reported problems

Ranked by how often practitioners and lessons-learnt papers raise them:
1. **Digital libraries in SE are not well-suited to complex automated searches.**
2. **The time and effort needed.**
3. **Quality assessment of papers using different research methods.**

Also recurrent: poor abstracts; qualitative studies complicating procedures; difficulty defining
research questions; extraction forms changing mid-extraction; papers omitting information; SE
keywords not being standardised; and the absence of tool support.
