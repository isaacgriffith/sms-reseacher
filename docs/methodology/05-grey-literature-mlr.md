# 05 — Grey Literature and Multivocal Literature Reviews

**Primary sources**: Garousi, Felderer & Mäntylä 2019 (the MLR guidelines), Garousi et al. 2016 and
2020, Adams et al. 2017 (the shades-of-grey model), Kitchenham et al. 2023 (grey material in
secondary studies), Kamei et al. 2021, Zhang et al. 2020, Schöpfel 2021, Yasin et al. 2020, Rainer &
Williams 2019 and Williams & Rainer 2017/2018/2019 (credibility), Neto et al. 2019, López et al. 2026.

---

## What grey literature is

**The field defines it by negation rather than definition, and mostly does not define it at all.**
Kamei et al. found only **34 of 446** studies used the term explicitly; Schöpfel found only **5 of
70** papers gave any definition. Two standard definitions exist and are worth naming rather than
inventing a third — the **Luxembourg** and **Prague** definitions, both reproduced in Kitchenham 2023.

Working sense for SE: material produced outside conventional academic publishing and peer review —
blog posts, white papers, technical reports, theses, videos, podcasts, forum threads, preprints,
trade journals, standards, and practitioner talks.

### The shades-of-grey model (Adams et al. 2017)

Grey literature is a **spectrum, not a category**, positioned on two axes:

- **Outlet control** — how much editorial or production control the outlet exercises
- **Source expertise** — how identifiable and credentialed the author is

High on both → close to white literature (e.g. government reports, theses). Low on both → the darkest
grey (e.g. anonymous forum posts, unattributed blogs).

> **⚠ The tiers are deliberately fuzzy and illustrative, and must be re-judged per project.** They are
> a way of reasoning about a source, not a fixed classification to apply mechanically.

**The central warning**: do not conflate grey with white literature. They warrant different appraisal,
and treating them alike is the error the model exists to prevent.

> **⚙ IMPLEMENTATION.** Two axes with a per-project judgement is a better model than the platform's
> current flat `GreyLiteratureType` enum (technical report / dissertation / rejected publication /
> work in progress), which mixes *document type* with *publication status*. Gap **G28** records that
> the enum is a manual register anyway.

---

## When to include grey literature

Garousi's **seven-question decision aid** — if the answer to any is yes, an MLR is indicated:

1. Is the subject "complex" and not solvable by considering only the formal literature?
2. Is there a lack of volume or quality of evidence, or a lack of consensus, in the formal literature?
3. Is the contextual information important to the subject under study?
4. Is it the goal to validate or corroborate scientific outcomes with practical experiences?
5. Is it the goal to challenge assumptions or falsify results from practice using academic research?
6. Would a synthesis of insights and evidence from the industrial and academic community be useful?
7. Is there a large volume of practitioner sources indicating high practitioner interest?

Neto et al. add an eighth motivation absent from Garousi's list: **an emerging research topic**, where
formal literature has not yet caught up.

**What excluding it costs**, measured: Garousi 2016 compared an SLR against an MLR on the same topic
and found **219 factor instances with grey literature against 67 without — and two whole categories
that appeared only in the grey sources.**

> **◐ DISPUTED — three positions in this corpus, and they do not reconcile.**
> - **Garousi**: include it when the decision aid says so; practitioner voice is often the point
> - **Cartaxo**: **exclude it from Rapid Reviews** — an RR already carries several limitations and
>   grey literature "could weaken the quality of the review… at least in the eyes of an unconvinced
>   researcher". Flagged by its own author as an untested hypothesis
> - **Kitchenham 2010 (tertiary)**: exclude, because good grey studies eventually appear as papers and
>   publication bias "does not appear to be a problem for systematic reviews in software engineering"
>
> These are context-specific rather than contradictory — Cartaxo is talking about practitioner-facing
> rapid work, Kitchenham about secondary studies as *subjects*. But the platform should surface the
> decision and its rationale rather than pick a default.

---

## The MLR process (Garousi 2019)

Three phases mirroring an SLR — **planning, conducting, reporting** — with five conducting sub-steps.

> **The key structural finding: only two activities genuinely differ from an SLR — the search, and
> the quality assessment.** Everything else (protocol, questions, extraction, synthesis, reporting)
> follows SLR practice. That is a small, well-defined delta.

### Search

Grey literature is found by **web search engines**, not bibliographic databases. Consequences:

- Results are **personalised and non-deterministic** — the same query returns different results for
  different users at different times
- **Coverage cannot be established** the way database coverage can
- Practical technique (López 2026): **`site:` proxy searching** of specific platforms — LinkedIn,
  Reddit, Medium — to reach communities the general web index buries

**Three stopping criteria**, because exhaustive search is impossible:
1. **Theoretical saturation** — no new concepts appear
2. **Effort bounded** — a fixed number of results or hours, e.g. the first *n* pages
3. **Evidence exhaustion** — the search space is genuinely covered

> **⚠ Yasin et al. found Google Scholar achieved 96% recall but failed precisely on the grey
> sources** — the tool most reviewers reach for is weakest exactly where grey literature lives.

### Quality assessment

Garousi's instrument is the substantive contribution: a **20-item checklist** scored **1 / 0.5 / 0**
per item, with a stated **inclusion threshold of 10 out of 20**. Categories:

| Category | Assesses |
| -------- | -------- |
| **Authority of the producer** | Is the author identifiable, credentialed, associated with a reputable organisation, cited by others? |
| **Methodology** | Is the source's method clear? Are limits stated? Is the aim clear? |
| **Objectivity** | Is the statement balanced? Is there vested interest? Are conclusions supported by data? |
| **Date** | Is a clear publication date given? |
| **Position w.r.t. related sources** | Does it corroborate or diverge from other sources? |
| **Novelty** | Does it add something? |
| **Impact** | Citations, links, shares, comments |
| **Outlet control** | Is the outlet moderated or edited? |

López 2026 adds a concrete operationalisation of "authority of the producer", and a dual-instrument
model with a **0.5 normalised cut-off**.

> **⚠ THE FIELD LARGELY DOES NOT DO THIS.** Zhang et al. examined 102 reviews: **76 merely *claim*
> grey-literature use, and 90% performed no separate grey-literature quality assessment** — while
> **79.2% of experts say one is needed**. Kamei found grey-specific appraisal in **7 of 126** studies.
> Neto's tertiary study of 12 SE MLRs found **all were run on SLR guidelines and therefore lacked
> GL-specific quality analysis and synthesis**, and names this as a validity threat.

> **⚙ IMPLEMENTATION.** This is the sharpest product opportunity in the chapter: a grey-literature
> appraisal instrument is *required by the guidelines, wanted by experts, and performed by almost
> nobody* — because doing it by hand across dozens of web sources is tedious. That is precisely the
> kind of work software should carry.

---

## Credibility of practitioner content (Rainer & Williams)

For blog-like sources specifically, a more developed apparatus exists.

**The definition**: a blog-like document is characterised by ten features (authorship, informality,
reverse-chronological presentation, and so on) rather than by its platform.

**Williams & Rainer's criteria**: 11 candidates were narrowed to 4 for operational use, and a later
study **empirically ranked 9 criteria** with practitioner respondents (n = 43). Also captured: Wohlin's
five criteria for good research evidence, and Fenton/Pfleeger/Glass's five claim questions.

**The reasoning-marker technique** (Williams & Rainer 2018): **86 linguistic markers** of reasoning —
words and phrases signalling that a claim is being argued rather than asserted. These are usable
*as search keywords*, which is the clever part: Rainer's heuristics paper splits quality criteria into
those that can be **implemented as search keywords** (reasoning indicators, author identity) and those
that can only be assessed **after retrieval** (writing quality, presence of citations).

**Rainer's evidential test per claim** (from argumentation theory): relevance · witness competence ·
tangible credibility (chain of custody, accuracy) · testimonial credibility (observational
sensitivity, objectivity, veracity) · inferential force · standpoint.

**The 2019 diagnosis**: a proper credibility framework needs **six separate objects of assessment** —
the author, the document, the content, the reader's credibility judgement, the readers, and reader
feedback. No existing instrument covers all six.

---

## Link rot — the operational problem

Grey literature disappears, and this is measured:

| Source | Finding |
| ------ | ------- |
| **Kamei et al.** | Of 1,246 grey items: **24.8% had no URL recorded, 23.7% were dead, 51.5% still live** |
| **Kitchenham 2023** | **19 of 46 URLs still live; 56% recoverable via the Wayback Machine** |

> **⚙ IMPLEMENTATION — this is gap G28 stated as a requirement.** A grey-literature record needs, at
> minimum: **URL, access date, author, title, outlet, and an archived copy or archive URL**. The
> access date is unrecoverable after the fact — it must be stamped at retrieval. The Wayback recovery
> rate says archiving at capture time is worth doing, and the 24.8% with **no URL at all** says the
> field currently does not even record the minimum.

---

## Kitchenham 2023 — the rules for including grey material

Seven numbered recommendations, of which the load-bearing ones:

- **The primary study remains the unit of analysis.** Grey material is evidence about studies, not a
  substitute for them
- **Auditability, traceability and reproducibility constrain what may be included** — a source that
  cannot be re-found cannot support a reproducible review
- **A four-way rule for comparing systematic-review findings against blog findings** — agreement,
  disagreement, and the two one-sided cases each mean something different and should be reported as
  such

---

## Preprints as a distinct stratum (López 2026, Fatima 2023)

Preprints sit awkwardly in the grey/white split: not peer reviewed, but written to academic
convention and often later published.

- López treats them as a **distinct grey class with their own search** (Scopus, arXiv), **replacement
  rules** — substitute the published version when one exists — and **white-literature-grade appraisal**
- Fatima's tool note records two practical constraints: **arXiv's 50-record copy cap**, and the
  exclusion of Google Scholar because it supplies **neither complete abstracts nor keywords**

> **⚠ Fatima 2023 reports no accuracy, precision, recall or time-saving figures for its scraper.**
> Any claim about automation accuracy must come from elsewhere; this paper does not support one.

---

## Podcasts and other emerging sources (Wyrich 2026)

A worked example of assessing a new grey source type. Corpus procedure: 4 inclusion criteria, 828
candidates → 224 → 216. The ICSE-category classification scheme was **abandoned and replaced with an
inductive one** — a useful precedent for when an existing scheme does not fit.

Survey findings: **61.2%** had ever listened; podcasts rank **last alongside social media** as a
research resource; barriers led by time cost and findability; **68% call podcasts grey literature**.

---

## Reporting an MLR

Follow SEGRESS, which covers mixed-methods reviews. The MLR-specific additions:

- **State the grey-literature inclusion decision and its rationale** (Garousi's seven questions,
  Ampatzoglou's TV6)
- **Report the grey-literature search separately** — engines used, queries, dates, stopping criterion
  reached, and how many results were examined
- **Report grey and formal literature counts separately through the funnel.** PRISMA 2020's flow
  diagram already supports this: grey records belong in the **"other methods"** column, which has no
  de-duplication box and no record-screening stage. See
  [10-reporting-and-evaluation.md](./10-reporting-and-evaluation.md)
- **Report the grey-literature quality assessment**, or state that none was performed and why

> **⚠ Schöpfel's attrition figure is worth knowing before promising much**: 52 grey items retrieved,
> **4 actually used**. Both PRISMA and Cochrane mandate a grey search; the yield is often small. That
> is not an argument against searching — it is an argument for bounding the effort with a stopping
> criterion decided in advance.
