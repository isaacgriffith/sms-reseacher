# 02 — Systematic Mapping Study

**Primary sources**: Petersen, Feldt, Mujtaba & Mattsson 2008, *Systematic Mapping Studies in
Software Engineering* (EASE'08) — the original 5-step process. Petersen, Vakkalanka & Kuzniarz 2015,
*Guidelines for conducting systematic mapping studies in SE: An update* — **the current guideline**.
**Supersedes**: `docs/systematic-mapping-studies.md`.

> **Use 2015 as the process; 2008 for the underlying concepts.** The 2015 update repairs two things
> the 2008 paper left ambiguous (what keywording actually *is*, and which facets to use) and
> reverses the goal of the search.

> **⚠ CORRECTION to the superseded doc.** Its "Evaluation of the search" rubric table is malformed —
> the score-1 row lost its label and its cells shifted, rendering with two columns instead of three.
> The corrected rubric is below.

---

## What an SMS is

A defined method to build a **classification scheme** and **structure** a field of interest. Analysis
focuses on **frequencies of publications per category**, which reveals the coverage of the field.
Facets can be combined to answer more specific questions. Less effort than an SLR; a coarser
overview.

**Four legitimate goals** (Arksey & O'Malley, as glossed for SE by Petersen et al. 2015):

| Goal | In software engineering |
| ---- | ----------------------- |
| Examine the extent, range and nature of research activity | How far different practices are studied and reported |
| Determine the value of undertaking a full systematic review | Find existing reviews; identify the evaluation/validation studies an SLR would build on; refine future SLR questions; estimate the effort a full SLR would take |
| Summarise and disseminate research findings | A comprehensive overview and an inventory of papers — particularly useful for graduate students orienting in a new area |
| Identify research gaps | Categories with very few studies, or lacking evaluation, make the need for future research apparent |

**Question granularity**: mapping questions are *less specific* than review questions — they ask
what is known about a topic, not what the evidence shows about an intervention. High-level questions
usually need breaking down to drive extraction.

---

## Phase 1 — Planning

### 1.1 Need identification and scoping

Establish the goal (one or more of the four above) and frame the mapping questions.

### 1.2 Study identification

Decomposed into four sub-activities. **The framing changed in 2015 and this is the most important
single point in the chapter:**

> In systematic reviews the goal is an exhaustive search identifying all relevant evidence. For
> mapping studies, evidence indicates **this is not a realistic goal**. Having more papers is not
> necessarily better than having fewer — what matters is whether the papers are **a good
> representation of the population**.

**Three questions for reflecting on whether you have a good sample:**
1. Are the different *a priori* known sub-areas of the field covered? Existing classifications of
   the field help, as do experts who can sketch the areas of relevance.
2. Are the main publication forums specific to the area represented, as well as general SE forums?
3. Are there explanations for major changes in the number of studies published per year? A spike may
   indicate a new sub-area missing from an earlier classification.

**The partitioning technique** (Badampudi et al., endorsed as the worked example): partition the
area by what you already know, plot which partitions your search found, then have **an independent
researcher not involved in the original search** run a database search to fill the empty partitions.
The guideline's own analogy: this is like testing, where you do not know the population of defects
while searching for them.

#### (a) Choosing the search strategy — three options

**Database search · manual search · snowballing.**

- Database search is the most frequent approach in practice.
- **Manual searches are beneficial and may be more effective** at identifying relevant studies.
- Running multiple strategies is time-intensive; **select one or a subset**, provided the overall
  conclusions about trends and gaps do not change.
- **No strategy is known to be superior**: too little evidence exists and findings may depend on the
  topic.

**Snowballing start-set advice** (Wohlin, reproduced by the guideline):
- Choose articles from **different clusters/communities that are unlikely to cite each other**, and
  therefore cannot be found through citation relationships
- The start set should **not be too small** — size depends on the focus and size of the area, which
  may not be known beforehand
- Cover **different authors, years and publishers**. Choosing the same authors limits breadth,
  because authors know their own work
- **Keywords from the research question** form the base for the start set

#### (b) Developing the search — five options

PICO(C) · consult librarians and experts · iteratively improve the search · keywords from known
papers · use standards, encyclopedias and thesauri.

> **⚠ CAVEAT — use only P and I.** PICO(C) is useful for reflecting on what a good population is,
> but **comparison, outcome and context may restrict the search too much and remove articles from
> the topic area**. For mapping studies, use Population and Intervention only. (This matches
> Petersen 2008's practice and Kitchenham's amendment 1 against mechanical string construction.)

**Sources for keywords in SE**: IEEE and ISO/IEC standards; **SWEBOK**, which provides a widely known
structure of the field.

**Database selection**: IEEE and ACM plus two indexing databases (e.g. Inspec/Compendex and Scopus)
is sufficient — the same set Kitchenham recommends.

**On noise**: if a search returns a very large number of irrelevant hits, consider restricting it,
e.g. by making the population more precise.

These activities are **not time-intensive and may greatly improve search quality**; early quality
assurance saves rework later and reduces noise, making selection more efficient.

#### (c) Evaluating the search — four options

**Test-set of known papers · expert evaluates the result · search web pages of key authors ·
test–retest.**

A practical form: ask an expert for **ten papers that should be found**. With no expert available,
key researchers' web pages often list the articles that ought to be retrieved. After the search, an
expert can evaluate the result.

**Stopping rules** (Petticrew & Roberts) — a stoppage criterion is legitimate and should be defined:
- If a complementary strategy (manual search, snowballing) **adds fewer than a specified number of
  new articles** to the database search, stop; or
- Set a **time budget** based on available funds, include what was identified, and **list the
  articles that were not considered**.

> **⚙ IMPLEMENTATION.** A stopping rule is a first-class protocol field, not an implicit behaviour.
> The platform's snowball threshold is one instance; the general form needs a rule type
> (marginal-yield or time-budget), a threshold, and — for the time-budget form — a record of what was
> left unassessed. That last part matters: an unassessed paper is not an excluded paper.

#### (d) Inclusion and exclusion

Criteria may address: topic relevance · publication venue · time period · requirements on evaluation
· language restrictions.

> **⚠ CAVEAT.** **Requirements on evaluation should be avoided in a mapping study**, so that recent
> trends which have not yet matured into evaluated work are still visible. This is the same trap
> Petersen 2008 warns about — restricting to methodologically rigorous papers biases the map,
> because some sub-areas are easier to study empirically than others.

**The study selection process**, in order (Ali & Petersen):
1. Specify selection criteria in the review protocol
2. **Review of selection criteria** among the researchers → may update criteria
3. **"Think-aloud" application** — one reviewer narrates their inclusion/exclusion reasoning on a
   single study, to align understanding → may update criteria
4. **Pilot selection on a subset** → may update criteria
5. Analyse disagreements and calculate inter-rater agreement
6. **Gate: is agreement acceptable?** No → loop back and update criteria. Yes → proceed
7. Perform selection — each researcher rates each study **include / exclude / uncertain** — and apply
   the decision rules
8. Calculate inter-rater agreement again

**Decision-rule combinations for two reviewers:**

|  | R2 = Include | R2 = Uncertain | R2 = Exclude |
| --- | --- | --- | --- |
| **R1 = Include** | A | B | D |
| **R1 = Uncertain** | B | C | E |
| **R1 = Exclude** | D | E | F |

The most inclusive strategy carries A–E forward and excludes only F immediately. Measured trade-off:
**A+B+C+D+E finds all relevant studies but incurs 25% more overhead than A+B+C+D, which found 94% of
them.** Overhead is the percentage of irrelevant articles that had to be analysed.

> **⚙ IMPLEMENTATION.** This is a concrete, encodable decision-rule catalogue with published
> cost/recall trade-offs — directly relevant to gap **G5**, which records that no decision-rule
> concept exists in the platform. The three-valued vote (include/exclude/**uncertain**) is a schema
> requirement: a binary decision cannot express cell C.

**Quality assessment inside a mapping study**: sometimes useful — e.g. to ensure enough information
is present to extract at all — but **it should not impose high requirements on primary studies**,
because the goal is a broad overview.

### 1.3 Data extraction and classification

**Two extraction process options:**
1. More than one researcher: the second either **checks** the outcome or **extracts independently**,
   with a consensus meeting if needed. *(This is the most common strategy.)*
2. Objectivity of criteria assessed on a **pilot set** and/or **post-extraction**.

Mapping studies **support agreement measurement** particularly well, because papers are classified
into categories.

#### Topic-independent facets

Five exist: **venue · research type · research method · study focus · contribution type**.

> **⚠ CORRECTION to Petersen 2008.** The 2008 paper emphasised **contribution type**; the 2015 study
> found it used by only 6 of 52 mapping studies *(derived)* and concluded it "appears to not be of
> high relevance". **The current recommendation is venue, research type, and research method.** Three
> facets absent from the 2008 guideline — venue, study focus, research method — are introduced.

Consistency is the point: only by using the same or similar schemes can mapping studies be compared.

**Venue** — the guideline adopts the Finnish Ministry of Education classification, because it derives
from actual publication activity. Top level: *Peer-reviewed* (refereed journal article; review or
literature review; book section; conference proceedings; non-refereed variants; edited book) ·
*Professional communities* (trade journal; professional manuals; professional proceedings; published
development or research report; general public: popularised article or monograph; **thesis: BSc,
MSc, Lic./MPhil, doctoral dissertation**) · *Public artistic and design activity* (independent work
of art; audiovisual material; **ICT software**; **patents**). Also useful when deciding which venues
to include or exclude during selection.

**Study focus** — the context studied: academic, industrial, government, project, organisation.

**Contribution type** — the type of intervention: process, method, model, tool, metric.

**Research type** — Wieringa's six categories, with Petersen's decision table:

| Condition | R1 | R2 | R3 | R4 | R5 | R6 |
| --- | --- | --- | --- | --- | --- | --- |
| Used in practice | T | | T | F | F | F |
| Novel solution | | T | F | | F | F |
| Empirical evaluation | T | F | F | T | F | F |
| Conceptual framework | | | | | T | F |
| Opinion about something | F | F | F | F | F | T |
| Authors' experience | | | T | | F | F |
| **Decision** | **Evaluation research** | **Solution proposal** | **Experience paper** | **Validation research** | **Philosophical paper** | **Opinion paper** |

*The printed table's column-to-label alignment for R3/R5/R6 did not survive text extraction; the
mapping above follows the paper's prose. Verify against the PDF before encoding.*

> **The substantive refinement — read this before implementing the classifier.** The main confusion
> is between **validation** and **evaluation** research. Novelty is **not** the criterion. Both
> require empirical evaluation; the distinction is **where**: validation is done in the lab,
> evaluation happens in a real-world industrial context. And a new solution reported as used in
> practice **is still a solution proposal if the empirical evaluation is missing**.

**Research method** must be consistent with research type — and the same method can fall either side:

| Research type | Methods |
| ------------- | ------- |
| **Evaluation research** | Industrial case study; controlled experiment with practitioners; practitioner-targeted survey; action research; ethnography |
| **Validation research** | Simulation as an empirical method; laboratory experiments (machine or human); prototyping; mathematical analysis and proof of properties; academic case study, e.g. with students |

Worked instance: **experiments with students are validation research; experiments with practitioners
are evaluation research.**

#### Topic-specific classification — two alternatives

**Use an existing scheme** where one is available — it supports comparability between mapping
studies. IEEE and ISO/IEC standards and SWEBOK are sources; consult experts to identify existing
schemes before starting.

**Or build an emerging scheme by keywording.**

> **⚠ CLARIFICATION — what keywording actually is.** Petersen 2008 described keywording without
> defining the mechanism, and the 2015 paper concedes the process "is not clear" as originally
> written. **It was intended to be open coding from grounded theory.** The corrected procedure:
> 1. Assign labels/keywords to concepts found in the text
> 2. Put the resulting open codes into an overall structure
> 3. **Merge or rename** codes representing categories as the structure settles
> 4. Sort the papers into the identified categories
> 5. Report the number of studies per category
>
> Apply to abstracts where abstract quality permits; **fall back to introduction and conclusion when
> abstracts are not clear**. This is the "adaptive reading depth" rule from 2008 — reading depth is a
> per-paper property that escalates when classification is uncertain, not a global setting.

### 1.4 Visualisation

Six types: **line diagram · pie diagram · bar plot · bubble plot · Venn diagram · heatmap.** Most
common are bubble plots, bar plots and pie diagrams.

**For the number of studies at a combination of categories — e.g. topic category × research type —
bubble plots and heatmaps are particularly suited.**

The bubble plot (Petersen 2008): two x-y scatterplots sharing an axis, bubbles at category
intersections sized proportionally to the number of articles, with the two halves placed in
different quadrants of one diagram so a third facet is visible at once. Report **count and
percentage** per category with facet totals.

### 1.5 Validity threats

Validity must be discussed in a mapping study as in any empirical study — it is itself a quality
criterion during study selection. See [09-threats-to-validity.md](./09-threats-to-validity.md).

---

## Phase 2 — Conducting the mapping

Implement the planned process. Record information **at all stages**. **The process is iterative and
may require revisions.** Tools for recording data — spreadsheets, reference managers — are useful.

From Petersen 2008: when sorting papers into the scheme, **record a short rationale for why each
paper belongs in its category**. The scheme itself evolves during extraction; adding, merging and
splitting categories is expected.

---

## Phase 3 — Reporting the mapping

Aim for the **same structure and style in every systematic map**, so they can be evaluated and
compared:

| Section | Content |
| ------- | ------- |
| Introduction | Background of the topic; the need for the mapping; its usefulness |
| Related work | Existing secondary and tertiary studies in the area |
| Research method | In separate subsections: research question · search · study selection · data extraction (and quality assessment if conducted) · analysis and classification · validity evaluation, discussing the different types |
| Results | Structured with respect to the mapping questions |
| Discussion / Conclusions | — |
| Appendix | **Included papers and excluded borderline papers** |

See [10-reporting-and-evaluation.md](./10-reporting-and-evaluation.md) for SEGRESS, which marks
which of its items apply to mapping studies specifically.

---

## Phase 4 — Evaluate the mapping process

Evaluating the evidence-based process is itself a step of evidence-based software engineering. A
recurring request in the community is a **pocket guide** supporting researchers during design and
reviewers during assessment.

Petersen 2015 supplies **a 26-action checklist** and **five scoring rubrics** for exactly this. The
rubrics already in the superseded repo document are these — now with their source and with the
malformed table repaired:

| Rubric | Scale |
| ------ | ----- |
| Need for review | 0 = not motivated, goal not stated · 1 = motivations and questions provided · 2 = provided **and defined in correspondence with the target audience** |
| Choosing the search strategy | 0 = only one type of search · 1 = two strategies · 2 = all three strategies |
| Evaluating the search | 0 = no actions reported to improve reliability of search or of inclusion/exclusion · 1 = at least one action for search **xor** inclusion/exclusion · 2 = at least one action for search **and** inclusion/exclusion · 3 = all identified actions taken |
| Extraction and classification | 0 = no actions reported · 1 = at least one action to increase extraction reliability · 2 = that, **and** research type and method classified · 3 = all identified actions taken |
| Study validity | 0 = no threats or limitations described · 1 = threats and limitations described |

> **⚙ IMPLEMENTATION.** These map directly onto the platform's LLM-as-judge quality evaluation. Note
> the rubrics score **process actions taken**, not output prose — so the evaluator needs access to
> what the study *did*, not just what it *wrote*. That is an argument for scoring against recorded
> execution state rather than against the generated report.

---

## SMS versus SLR — the decision

| Dimension | Systematic Map | Systematic Review |
| --------- | -------------- | ----------------- |
| Goal | Classification, thematic analysis, identifying publication fora | Establishing the state of evidence |
| Shared goal | Identifying research gaps | Identifying research gaps |
| Kind of gap found | Which topic areas and research types are under-published | Where evidence is missing or insufficiently reported — **not possible with a map** |
| Quality evaluation | **Papers are not evaluated for quality** (2008); if used at all, requirements must stay low (2015) | Central |
| Search goal | A good, representative sample | Exhaustive |
| Question scope | Broad, often several | Narrow, focused |
| Extraction | Classification into a scheme | Detailed extraction, often numeric |
| Analysis | Frequencies per category | Synthesis of findings |
| Research-approach classification | High-level — 6 categories | Detailed — e.g. Glass et al.'s 20+ methods |

**They compose.** A map can precede a review: structure the area first, then investigate a specific
focus in depth. But **a mapping study has value on its own** — it identifies gaps with comparatively
little effort.

> **⚠ CAVEAT — do not build an SLR directly on a map.** Mapping studies "may miss significant
> numbers of relevant papers and **should not be the basis for SRs without additional more focused
> searches**". They also cannot be guaranteed complete and may quickly become out of date.

> **⚠ CAVEAT — selection is *harder* in a map, not easier.** It is harder to define
> inclusion/exclusion criteria for broad topic areas, and it is genuinely difficult to decide how to
> treat papers that mention the topic in passing rather than as their main focus. Petersen 2008's
> heuristic — exclude papers where the concept appears only in introductory sentences of the abstract
> — was piloted before being trusted, and that piloting is the part to copy.

> **⚠ CAVEAT — authors mislabel their own papers.** One study found **73% of papers were designated
> incorrectly**, e.g. claiming an experiment that was not one; the term "experiment" is often used
> inconsistently with controlled-experiment definitions. Classification from shallow reading
> therefore carries real judgement error. This is the reason the research-type decision table exists,
> and the reason reading depth must be allowed to escalate.

---

## No single guideline is sufficient

An empirical finding worth acting on: **24 of the mapping studies surveyed used more than one
guideline**, because the guidelines differ in what they recommend. Petersen 2015's own conclusion is
that individual guidelines "do not appear to be complete enough to characterize the whole mapping
process."

> **⚙ IMPLEMENTATION.** This document exists partly to resolve that — it is the merged position. Where
> guidelines conflict, this document records the conflict rather than silently choosing.
