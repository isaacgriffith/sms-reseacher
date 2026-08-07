# 06 — Search and Selection

**Primary sources**: Wohlin 2014 (snowballing), Wohlin 2016 (second-generation studies), Wohlin et
al. 2013 (reliability), Badampudi et al. 2015 (snowballing vs database search), Bailey et al. 2007
(search-engine overlap), Mourão et al. 2017 (hybrid strategy), Kitchenham et al. 2013 (quasi-gold
standard), Petersen et al. 2015 (selection decision rules), Petersen & Bin Ali 2011 (selection
strategies), Dybå et al. 2007.

---

## The headline: database search alone is not adequate

This is the best-evidenced claim in the corpus, from four independent studies.

| Study | Finding |
| ----- | ------- |
| **Badampudi 2015** | Snowballing found **83%** of relevant papers; database search **45.9%**. **9 of 15 study conclusions would have failed on database search alone — against 1 on snowballing alone** |
| **Bailey 2007** | Of 71 papers on one topic: Web of Science found 43 (**12 uniquely**), ScienceDirect 29 (**7 uniquely**), IEEE 13 (**5 uniquely**), Google Scholar 39 (**0 uniquely**), CiteSeer 6 (1), ACM 5 (0) — and **4 papers came only from following references**. Root cause: **SE keywords are not standardised** |
| **Wohlin 2013** | Two independent mapping studies on the same topic shared only **33 of a possible 44** papers — a 25% divergence — and **16 of 21 missed papers were simply absent from the databases searched** |
| **Mourão 2017** | A hybrid strategy (one database as seed set + snowballing both directions) achieved **100% relative recall on a narrow SE topic but only 81% on a cross-disciplinary one** |

> **⚙ IMPLEMENTATION.** Three consequences. (1) Multi-database fan-out is necessary but not
> sufficient — **snowballing is not an optional extra**, and gap **G22**'s fix made it startable for
> the first time. (2) Per-database provenance matters: which source contributed which paper uniquely
> is the evidence that a search was adequate, and gap **G13c** records that the platform stores one
> merged count. (3) Google Scholar contributing **zero unique papers** in Bailey's study is a caution
> against treating it as a sufficient single source, despite Cartaxo permitting exactly that for a
> Rapid Review.

---

## Choosing a strategy

Three options, and Petersen 2015 is explicit that **no strategy is known to be superior** — too
little evidence exists, and findings may depend on the topic.

| Strategy | Strengths | Weaknesses |
| -------- | --------- | ---------- |
| **Database search** | Broad, reproducible, tool-supported | SE libraries are poorly suited to complex queries; strings need per-engine adaptation; misses non-standard terminology |
| **Manual search** | Evidence shows it is beneficial and **may be more effective** | Expensive; scope-limited |
| **Snowballing** | Highest recall in the studies above; finds papers absent from every index | **Entirely dependent on the start set** |

**Running several is time-intensive.** Petersen 2015 permits selecting one or a subset, provided the
overall conclusions about trends and gaps do not change.

> **◐ DISPUTED — how noisy is snowballing?** Badampudi et al. report **98.23%** of examined papers
> were excluded; Jalali & Wohlin describe the noise as "relatively less". Both are in the corpus and
> they disagree. Wohlin's own efficiency figures — **3.7% of examined papers included, 6.8% excluding
> trivial exclusions** — are closer to Badampudi. Plan for high exclusion rates.

---

## Snowballing (Wohlin 2014)

### The start set — the single point of failure

**Criteria:**
- Draw from **different clusters or communities that are unlikely to cite each other**, since papers
  that never cite one another cannot be reached through citation relationships
- **Not too small** — the size depends on the focus and size of the area, which may not be known
  beforehand
- Cover **different authors, years and publishers**. Choosing the same authors limits breadth,
  because authors know their own work
- **Keywords from the research question** are the base for finding the start set
- Use **Google Scholar for the start set specifically, to avoid publisher bias**

> **⚠ CAVEAT.** Badampudi's snowballing missed an entire category of papers **because the start set
> contained none of it**. Wohlin's clustering criterion exists precisely for this. A start set drawn
> from one community produces a review of one community.

**The partitioning check** (Badampudi, endorsed by Petersen 2015): partition the area by what you
already know, plot which partitions your snowballing reached, then have **an independent researcher
not involved in the snowballing** run a database search to fill the empty partitions.

### The iteration

**Backward snowballing** — examine the reference list of each included paper, screening in cascade:
1. Exclude on **year and publication type** where the protocol restricts them
2. Exclude papers **already seen**
3. Screen on **title**, then venue and authors
4. **Examine the place of the reference in the text and its surrounding context** — this is the step
   that distinguishes the method from mechanical reference-following, because it tells you *why* the
   paper was cited
5. Retrieve and assess the paper itself

**Forward snowballing** — find papers citing the included paper, via Google Scholar. Practical note:
**remove quotation marks** from the query.

**Include before snowballing, with rollback.** A paper is included and then snowballed from; if it is
later excluded, the papers found from it must be reconsidered.

> **⚙ IMPLEMENTATION.** That rollback rule is exactly gap **G1** — the discovery DAG. Without an edge
> recording which paper a candidate was found from, excluding a paper silently orphans its
> descendants, and you cannot tell a descendant with a second surviving parent from one without.

**Stopping rule**: continue iterations until **an iteration yields nothing new**. Then contact
authors, and **restart if new papers appear**.

> **⚠ CAVEAT — title-only screening is dangerous here.** Wohlin found strict title screening would
> have dropped **5 of the 11 papers** his snowballing found. Relevant to Cartaxo's title-first Rapid
> Review pass, which trades exactly this.

### Snowballing for updating a review

Wohlin 2016: for a **second-generation** study — updating an existing review — **forward-only
snowballing without iteration**, starting from the earlier review(s) and their primary studies, found
**all 11 papers a database search found, plus 3 more, one of which appeared in no standard database**.
Screening cost: 1018 candidates and 16 detailed reads, against 1641 and 100 for the database search.

A striking detail: **all 16 candidates came from the two versions of the review itself, and none from
the 794 citations to its primary studies** — and citations split almost disjointly between the
conference and journal versions of the review.

> **⚙ IMPLEMENTATION.** "Update an existing review" is a distinct workflow with a distinct, cheaper
> search strategy. The platform models studies as one-shot; this is an argument for a study that
> descends from a prior study.

---

## Building and validating a search string

### The quasi-gold standard (Kitchenham 2013, amendment 2)

The endorsed technique for integrating manual and automated search **and measuring whether the
automated search worked**:

1. Run an **initial manual search** to identify a set of known papers
2. Those known papers act as a **quasi-gold standard**
3. Use it to help construct the search string, and to assess the automated search by computing
   **quasi-sensitivity** — the proportion of known papers the automated search recovers

**Practical constraints:**
- Manual searches should be based mainly on **topic-specific conferences and journals over a
  specified time period**, but it is useful to include some **general SE sources** as well
- **⚠ If the manually searched sources are not indexed by the digital libraries, they cannot act as a
  gold standard** — the automated search could never have found them
- **Split the known papers into two sets**: one to construct the string, an **independent** one to
  evaluate the search

> **⚙ IMPLEMENTATION.** The two-set split is the part the platform gets wrong today. Gap **G13a**
> records that seed papers serve only as the recall test set and never inform generation; the correct
> design uses *both*, on **disjoint** subsets. Using one set for both purposes measures memorisation,
> not recall.

### Other evaluation techniques (Petersen 2015)

- **Test set of known papers** — e.g. ask an expert for **ten papers that should be found**
- **Expert evaluates the result** after the search
- **Search key authors' web pages** when no expert is available
- **Test–retest**

### Stopping rules

Legitimate and to be defined in advance:
- **Marginal yield**: stop when a complementary strategy adds fewer than *n* new articles
- **Time budget**: fix the effort, include what was found, and **list the articles that were not
  considered**

> **⚙ IMPLEMENTATION.** The time-budget form requires recording what was left **unassessed**. An
> unassessed paper is not an excluded paper, and a PRISMA flow that conflates them is wrong.

### Database selection

Both Kitchenham 2013 and Petersen 2015 converge: **IEEE and ACM, plus at least two general indexing
systems** (SCOPUS, EI Compendex, or Web of Science).

> **⚠ CAVEATS on strings.**
> - **Do not derive the string mechanically from structured questions** — Kitchenham amendment 1
>   withdrew this. It yields very complex strings needing per-library adaptation. Use P and I only for
>   a mapping study.
> - A very specific long string still produced many false positives; **"a simpler search string might
>   have been just as effective."**
> - **Adding a domain term silently drops cross-domain work.** Removing `AND "software"` recovered two
>   relevant papers while raising results from 134 to 578.
> - **Indexing lag defeats automated search.** Re-running a search a year later found all three
>   previously missed papers. Back automated search with manual search of recent proceedings, and
>   consider re-running before publication.

---

## Selection

### The process (Ali & Petersen)

1. Specify selection criteria in the protocol
2. **Review the criteria** among the researchers → may update them
3. **"Think-aloud" application** — one reviewer narrates their reasoning on a single study, aligning
   understanding → may update criteria
4. **Pilot on a subset** → may update criteria
5. Analyse disagreements and calculate inter-rater agreement
6. **Gate: is agreement acceptable?** No → loop back. Yes → proceed
7. Perform selection with a **three-valued vote — include / exclude / uncertain** — and apply decision
   rules
8. Calculate inter-rater agreement again

### Decision rules, with measured trade-offs

|  | R2 Include | R2 Uncertain | R2 Exclude |
| --- | --- | --- | --- |
| **R1 Include** | A | B | D |
| **R1 Uncertain** | B | C | E |
| **R1 Exclude** | D | E | F |

- **A+B+C+D+E** (exclude only F) — finds **all** relevant studies, **25% more overhead**
- **A+B+C+D** — finds **94%** of them

Overhead = the percentage of irrelevant articles that had to be analysed.

> **⚙ IMPLEMENTATION.** Gap **G5** records that no decision-rule concept exists in the platform. This
> is the catalogue, with published cost/recall figures. Note the schema requirement: a **binary**
> decision cannot express cell C, so the vote must be three-valued.

### Screening in stages

- **Interpret criteria liberally at first.** Get the full text unless the paper is clearly excludable
- **⚠ Do not rely on abstracts.** "The standard of IT and software engineering abstracts is too poor
  to rely on when selecting primary studies. You should also review the conclusions." Repeated
  independently across the corpus
- A Rapid Review may use **three substeps** — title only, then abstract, then full text — accepting
  false negatives for speed
- **Exclusion can happen during extraction**, and should be recorded: papers pass full-text screening
  and then turn out to have no aggregation, or to be preliminary

### Reliability

- Two or more reviewers, agreement measured with **Cohen's Kappa**; **report the initial value**
- Every disagreement discussed and resolved; residual uncertainty feeds sensitivity analysis
- **A single reviewer must use test–retest** — re-evaluate a random sample of already-screened papers
  to check their own consistency *(gap **G4**)*
- Dybå et al. report a worked benchmark: **94% agreement, κ = 0.80**, over 2,946 hits reduced to
  1,996 unduplicated
- Staples & Niazi honestly narrate repeated inter-rater failure across rounds: 591 → 73 → 62 → 46

> **⚠ Wohlin declined to compute κ** in the two-map comparison, where the studies agreed on research
> type for only **11 of 33** shared papers. Worth knowing that a κ is not always the right summary —
> when the disagreement is about *classification* rather than *inclusion*, reporting the raw
> disagreement may be more honest.

> **⚠ Selection is harder for mapping studies, not easier.** It is harder to define criteria for broad
> topics, and genuinely difficult to decide how to treat papers that mention the topic only in
> passing.

---

## What to record

Kitchenham's search documentation requirements, which are also what SEGRESS item 7 asks for:

| Source type | Record |
| ----------- | ------ |
| Digital library | Database name; the per-database search strategy; **date of search**; years covered |
| Journal hand search | Journal name; years searched; any issues not searched |
| Conference proceedings | Proceedings title; conference name if different; translation if needed |
| Unpublished-work efforts | Groups and researchers contacted with contact details; sites searched with date and URL |
| Other | Date searched; URL; any specific conditions |

Plus a stated **rationale** for the libraries chosen, the venues chosen, and the use of electronic
versus manual search.

**And**: document the search **as it occurs**, note and justify changes, and **retain the unfiltered
results** for reanalysis.

> **⚙ IMPLEMENTATION.** "Date of search" is the field most often missing in practice — it is the
> specific omission that motivated SEGRESS's addition to item 5. It is also trivially recordable by
> software, which is a small, clean win.
