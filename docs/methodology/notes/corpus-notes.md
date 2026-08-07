# Corpus notes — running file

Per-paper extraction notes. Kitchenham & Charters 2007 is in its own file
(`kitchenham_guidelines_2007.md`) because of its size. Everything else appends here.

**Reconcile against:** `docs/systematic-literature-reviews.md`, `docs/systematic-mapping-studies.md`,
`docs/rapid-reviews.md`, `docs/tertiary-studies.md` already exist in the repo — the deliverable
must ground/supersede those rather than duplicate them.

<!-- APPEND-MARKER -->

---

# RECONCILIATION STATE — existing repo docs (surveyed 2026-08-07)

User decision: **ground and supersede** the four existing study-type docs.

| Doc | Lines | State |
|---|---:|---|
| `docs/systematic-literature-reviews.md` | 374 | Substantial. Sections: The Process · Need for a Review · Review Questions (Population examples, PICO example) · Review Protocol · Research Identification (Manual Search, Database Search, Search String, Database Selection, Search Execution, Snowball Sampling) · Primary Study Selection · Inclusion/Exclusion Criteria · Publication Bias · Study Quality Assessment · Data Extraction · Data Synthesis · Document Review · Reporting the Review · References |
| `docs/systematic-mapping-studies.md` | 503 | **Most developed.** 5 phases: Need for the Map · Study Identification (Choose Search Strategy, Develop the Search, Evaluate the Search, Inclusion/Exclusion, Paper Search, Tracking Progress, Essential Search Processes, Search Metrics) · Data Extraction (Venue Type Classification, Research Classification, Decision Rules for Research Type Classification, Venue, Domain Modelling, Classification Scheme) · Validity Discussion · Study Quality Evaluation (5 scored rubrics). Clearly derived from **Petersen 2015** (rubrics) and **Petersen & Gencel 2013** (validity classes). |
| `docs/rapid-reviews.md` | 208 | Moderate. Key Differences vs SR · Process · Planning (Demand, Problem, RQs, Stakeholder Roles, Protocol) · Conducting (Search Strategy, Selection, Quality Appraisal, Extraction, Synthesis) · Reporting (Evidence Briefings). Mirrors **Cartaxo 2020** §4 structure. |
| `docs/tertiary-studies.md` | **0 — EMPTY FILE** | **Genuine gap.** `all-together.md` defines a tertiary study as "Systematic Literature Reviews of Systematic Literature Reviews", conducted "when a significant number of secondary studies are found during the course of conducting a Systematic Mapping Study." Nothing else. Batch 2 (kitchenham_systematic_2010/2009/2013) must supply this. |

## Validity classes already encoded in the SMS doc (Petersen & Gencel)
Descriptive Validity · Theoretical Validity (→ Construct) · Generalizability (→ internal = within a
group, external = between groups/organizations) · Interpretive Validity (→ Conclusion) ·
Repeatability. Verify definitions against `petersen_worldviews_2013` in batch 8.

## Rubrics already encoded (Petersen 2015) — verify wording and scoring against source
- **Need for review** 0–2 · **Choosing the search strategy** 0–2 (one/two/all three strategies) ·
  **Evaluation of the search** 0–3 · **Extraction and classification** 0–3 · **Study validity** 0–1.
- ⚠ **DEFECT in the existing doc:** the "Evaluation of the search" table has a malformed row — the
  score-1 row is missing its Evaluation label ("Minimal evaluation") and its cells are shifted, so
  the table renders with 2 columns on that row instead of 3. Fix when superseding.

## Project framing from `docs/all-together.md`
- Secondary studies = SLR, SMS, Rapid Review. Tertiary = review of secondary studies.
- SLR "typically conducted **after** a Systematic Mapping Study, if a significant number of
  high-quality empirical studies are found".
- SMS "utilize the same techniques as SLRs but tend to analyze studies beyond those with higher
  empirical value".
- Rapid Reviews "the least rigorous of the three… more restrictive context and timeframes, leading
  to a more relaxed protocol."
- Primary / Secondary / Tertiary definitions given explicitly.
> These framings are the project's own and should be **checked against the sources**, not assumed —
> e.g. Cartaxo frames RR as *practitioner-demand-driven*, not merely "less rigorous", and Garousi
> frames MLR as orthogonal to SLR/SMS rather than a fourth type.

---

# Petersen, Feldt, Mujtaba & Mattsson (2008) — Systematic Mapping Studies in SE (EASE'08)

**Role in corpus:** THE canonical SMS process. Defines the 5-step process, the keywording
technique, the research-type facet, and the bubble plot. Base process for SMS.

## Definition
"A software engineering systematic map is a defined method to build a **classification scheme**
and **structure** a software engineering field of interest. The analysis of results focuses on
**frequencies of publications for categories within the scheme**. Thereby the coverage of the
research field can be determined. Different facets of the scheme can also be combined to answer
more specific research questions." Requires **less effort** than an SLR, gives a **more
coarse-grained overview**.

## THE 5-STEP PROCESS (Figure 1) — each step has a named outcome
| # | Process step | Outcome |
|---|---|---|
| 1 | Definition of Research Question | Review Scope |
| 2 | Conduct Search | All Papers |
| 3 | Screening of Papers | Relevant Papers |
| 4 | Keywording using Abstracts | Classification Scheme |
| 5 | Data Extraction and Mapping Process | Systematic Map |

### Step 1 — Research questions (→ Review Scope)
Main goal: **overview of a research area; identify the quantity and type of research and results
available.** Often map **frequencies of publication over time to see trends**. Secondary goal:
**identify the publication fora**.
Example RQs — OO Design Map: which journals include papers on software design? most investigated
topics and how changed over time? most frequently applied research methods and study context?
SPL Variability Map: what areas are addressed and how many articles cover each? what types of
papers, and what type of evaluation and novelty do they constitute?

### Step 2 — Conduct search (→ All Papers)
Search strings on databases **or manual browsing** of relevant proceedings/journals. "A good way
to create the search string is to structure them in terms of **population, intervention,
comparison, and outcome**" — driven by the RQs.

> **KEY SMS-vs-SLR DIFFERENCE:** the SPL map **deliberately did not consider specific outcomes or
> experimental designs** — "We avoided this restriction since we wanted a broad overview of the
> research area as a whole. If we had only considered certain types of studies the overview could
> have been biased and the map incomplete. Some sub-topics might be over- or under-represented for
> certain study methods." I.e. an SMS typically uses **only Population + Intervention**.

Database scope may legitimately be narrow (main fora only), since the main forum is "a good
starting point to determine the classification scheme and distribution of articles".

### Step 3 — Screening (→ Relevant Papers)
Criteria driven by the RQs.
**Useful technique:** exclude papers mentioning the focal concept **only in introductory sentences
of the abstract** — needed because a central concept appears in many abstracts without the paper
addressing it. "We prototyped this technique and did not find any misclassifications because of
it." ← pilot an exclusion heuristic before trusting it.
Example criteria may explicitly admit **books, papers, technical reports and grey literature**;
where several papers report the same study include only the most recent; **where several studies
are reported in the same paper, each relevant study is treated separately** ← study ≠ paper (G6).
Exclusions: outside SE domain; concept not part of contributions; literature available only as
abstracts or PowerPoint presentations.

### Step 4 — Keywording of abstracts (→ Classification Scheme) — the distinctive SMS technique
1. **Reviewers read abstracts and look for keywords and concepts reflecting the contribution**,
   and identify the **context** of the research.
2. **Combine keyword sets from different papers** into a high-level understanding of the nature
   and contribution of the research → categories **representative of the underlying population**.
   Cluster the final keyword set to form the map's categories.
*Fallback:* "When abstracts are of too poor quality to allow meaningful keywords to be chosen,
reviewers can choose to study also the introduction or conclusion sections."
**The scheme evolves during extraction** (feedback loop "Update Scheme"): sorting articles can
add new categories or merge/split existing ones.

**Three facets:**
1. **Topic facet** — domain specific, derived from the keywords
2. **Contribution facet** — process, method, tool, model, metric…
3. **Research facet** — **general and independent of the focus area**; use Wieringa et al. (2006)

#### Research Type Facet (Wieringa et al. 2006) — verbatim definitions
| Category | Description |
|---|---|
| **Validation Research** | Techniques investigated are novel and have not yet been implemented in practice. Techniques used are for example experiments, i.e. work done in the lab. |
| **Evaluation Research** | Techniques are implemented in practice and an evaluation of the technique is conducted. That means, it is shown how the technique is implemented in practice (**solution implementation**) and what are the consequences of the implementation in terms of benefits and drawbacks (**implementation evaluation**). This also includes to identify problems in industry. |
| **Solution Proposal** | A solution for a problem is proposed; the solution can be either novel or a significant extension of an existing technique. The potential benefits and the applicability of the solution is shown by a small example or a good line of argumentation. |
| **Philosophical Papers** | These papers sketch a new way of looking at existing things by structuring the field in form of a taxonomy or conceptual framework. |
| **Opinion Papers** | These papers express the personal opinion of somebody whether a certain technique is good or bad, or how things should been done. They do not rely on related work and research methodologies. |
| **Experience Papers** | Experience papers explain on what and how something has been done in practice. It has to be the personal experience of the author. |

**Operational classification heuristics** (why the facet works without deep reading):
- **Evaluation research** can be excluded **if no industry cooperation or real-world project is
  mentioned**
- **Validation research** is easy to pinpoint by checking whether the paper **states hypotheses,
  uses summary statistics** (scatter diagrams, histograms) **and describes the main components of
  an experimental setup**
- The scheme deliberately **allows classification of non-empirical research** — essential, since
  "the majority of papers was related to the non-empirical category"
> **IMPL:** directly encodable as screening/classification agent rules.

### Step 5 — Data extraction and mapping (→ Systematic Map)
Sort relevant articles into the scheme; the scheme evolves as you go. They used an **Excel table
with a column per category**, and **"provided a short rationale why the paper should be in a
certain category"** ← rationale-per-classification is an auditability requirement. From the final
table, frequencies per category are calculated.

**Analysis = frequencies of publications per category**, to see which categories have been
emphasised and thus **identify gaps and possibilities for future research**.

**Visualisation — the bubble plot:** "basically two x-y scatterplots with bubbles in category
intersections. The **size of a bubble is proportional to the number of articles** that are in the
pair of categories corresponding to the bubble coordinates. The same idea is used two times, **in
different quadrants of the same diagram**, to show the intersection with the third facet." More
than three facets → additional bubble plots in the same diagram, or multiple diagrams. Rationale:
"easier to consider different facets simultaneously… more powerful in giving a quick overview."
Frequencies shown as **count + percentage** per category, with facet totals.

## SMS vs SLR — the comparison
| Dimension | Systematic Map | Systematic Review |
|---|---|---|
| **Goals** | Classification, thematic analysis, identifying publication fora | Establishing the **state of evidence**; identifying best/typical practices |
| **Shared goal** | Both aim to **identify research gaps** | " |
| **Gap type found** | Which topic areas / research types are under-published (by graphing) | Where evidence is **missing or insufficiently reported** — *"This is not possible with systematic maps"* |
| **Quality evaluation** | **Articles are NOT evaluated regarding their quality** | Quality assessment central |
| **Data extraction** | Thematic analysis / categorisation | Meta-analysis requires **another level of data extraction** |
| **Breadth/depth** | More articles, less detail; larger field structured; search uses only population + intervention | Narrower, deeper; outcome + quality assessment increase effort |
| **Research-approach classification** | **High-level** (Wieringa: 6 categories) | **Detailed** — e.g. Glass et al.: >22 research methods, 13 research approaches |

> **RESOLVES THE OPEN QUESTION FROM KITCHENHAM 2007:** Petersen states explicitly that in maps
> "the articles are not evaluated regarding their quality." Authority for SMS omitting quality
> assessment.

"We see no reason for why not several different methods of analysis could be applied in the same
study. A thematic summary leading to a map could be the first steps in a more detailed systematic
review."

### Validity considerations raised — CAVEATS
- **Restricting to methodologically rigorous papers biases the map.** Mendes: "only 5% of the
  studies are considered rigorous methodologically". Restricting to such a small portion risks an
  incomplete overview; "it is likely that it is also relatively easier to do empirical research in
  some sub-areas than in others", so method-restricted reviews **introduce bias when presenting
  the overall research area**.
- **Papers are frequently mislabelled by their own authors.** Mendes: **73% of the papers were
  designated incorrectly** — e.g. "promised an experiment which was no experiment". Jørgensen &
  Shepperd: "the term experiment was not always used in line with the definition of controlled
  experiments." So **classification into detailed categories from shallow reading risks judgmental
  errors.** Partially offset in maps by the larger sample.
- **Industrial accessibility:** practitioners find SLRs "too detailed and hard to access"; the
  **visual appeal of systematic maps** made it "easier to spark interest."

## FOUR EXPLICIT GUIDELINES FOR SYSTEMATIC MAPS (§4)
1. **Use methods complementarity.** Goals partly contradict — "a good structure of the topic area
   is hindered by excluding the majority of articles due to lack of empirical evidence" — so
   different search strategies and inclusion/exclusion criteria must be applied. An SMS should be
   a **first step toward an SLR**. *But:* "a systematic map without conducting a successive
   systematic review has a value in itself."
2. **Adaptive reading depth for classification.** Against the view that maps use abstracts alone:
   **"abstracts are often misleading and lack important information."** Structured abstracts help
   and should be mandated more widely. When unavailable: **"do not pre-specify that only certain
   parts of a paper can be read. Instead, allow more detailed study of papers for which it is not
   clear how they should be classified."** More parts read → more effort, higher validity. **"A
   mapping study that goes deeper into the papers can become more like a systematic review. The
   two types of studies can be considered as different points on a continuum."**
   > **IMPL:** reading depth is a per-paper, escalatable property — not a global setting.
3. **Classify papers based on evidence and novelty.** High-level schemes remain valid without
   detailed method evaluation. **The scheme must provide categories for non-empirical research.**
   Wieringa et al. recommended. Possible refinement: subdivide by evidence level and novelty type.
4. **Visualise your data.** Frequencies are usually tables or bar plots, but the **bubble plot**
   combines categories so "the relative emphasis of research on categories is visible from the
   plot itself." Explore animated bubble plots over time for trends.

## Means-of-analysis taxonomy (§3.1) — useful vocabulary
- **Meta studies** — integrate several studies through statistical analysis of quantitative data
- **Comparative analysis** — logical simplification and confidence assessment theories
- **Thematic analysis** — counts papers related to specific themes or categories
- **Narrative summaries** — qualitative review and narrative explanations
(All 10 SE SLRs surveyed used *some form of* narrative summary; 2 thematic, 2 meta-analysis, 1
comparative.)
**Research-goal taxonomy:** Identify Best and Typical Practices · Classification and Taxonomy ·
Emphasis on Topic Categories · Identify Publication Fora.
