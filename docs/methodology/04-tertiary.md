# 04 — Tertiary Study

**Primary sources**: Kitchenham et al. 2010, *Systematic literature reviews in software engineering
— A tertiary study* (the fullest worked method). Kitchenham et al. 2009, *…— A systematic literature
review* (the original, "T1"). Kitchenham et al. 2013 and da Silva et al. 2011 as further worked
examples.
**Supersedes**: `docs/tertiary-studies.md` — **which was an empty file.** This is the first written
description of the process in this repository.

---

## What a tertiary study is

A secondary study whose primary studies are themselves secondary studies. **Method: "the basic SLR
method as described by Kitchenham and Charters."** There is no separate tertiary methodology — the
SLR process is applied with secondary studies as the unit of analysis.

That single fact carries most of the design consequences: **everything in [01-slr.md](./01-slr.md)
applies**, and what follows records only where a tertiary study differs in practice.

**When to conduct one.** The project's own framing — when a significant number of secondary studies
turn up during a mapping study — is consistent with practice, though the published examples were
motivated by a different question: *is the method itself being adopted, and is its quality
improving?* Both motivations are legitimate and they imply different research questions.

**Worked research questions** (Kitchenham 2010), useful as templates:
- How many SLRs were published in period X?
- What research topics are being addressed?
- Which individuals and organisations are most active in SLR-based research?
- Are the limitations observed in earlier work still an issue?
- Is the quality of SLRs improving?

> Note the authors' own correction between studies: "Who is leading the research effort?" was revised
> to "Which individuals and organizations are most active?" — **because they measured activity, not
> leadership.** A small but exemplary instance of aligning a question with what the data can support.

---

## Phase 1 — Planning

Identical to an SLR, with two tertiary-specific decisions.

### The unit of analysis is a secondary study — and the boundary is fuzzy

Two things must be distinguished during selection, and the source concedes the line "can be somewhat
fuzzy":

| | Conventional SLR | Mapping study |
| --- | --- | --- |
| Aggregates | Results for a specific research question | Classification of primary studies in a topic area |
| Question form | Specific | Coarse — "what do we know about X?" |
| Method | **Same search and extraction methods** | **Same search and extraction methods**, but relies more on tabulating studies into categories |

**Both are in scope for a tertiary study**, and the type must be recorded per included study, because
it affects the quality scores (see the caveat on mapping-study DARE scores below).

### Deciding on grey literature

Kitchenham excludes it, on an explicit argument worth reproducing because it is contestable: good
grey-literature studies will eventually appear as journal or conference papers, and the main reason
for grey literature not being formally published is publication bias — which "does not appear to be a
problem for systematic reviews in software engineering."

> **◐ DISPUTED.** That argument is specific to *secondary studies as subjects*, and does not
> generalise to tertiary studies over practitioner-facing topics. See
> [05-grey-literature-mlr.md](./05-grey-literature-mlr.md). Record the decision and its rationale
> either way.

---

## Phase 2 — Conducting

### 2.1 Search — the terminology problem dominates

**This is the defining difficulty of a tertiary study.** You are searching for a *method*, and
authors describe that method inconsistently.

**Use many simple strings rather than one complex string.** Kitchenham used **15 simple strings**,
each `"software engineering" AND <term>`, where the term varied across: *review of studies ·
structured review · systematic review · literature review · literature analysis · in-depth survey ·
literature survey · meta-analysis · past studies · subject matter expert · analysis of research ·
empirical body of knowledge · overview of existing research · body of published research* — plus
`"evidence-based software engineering"` in both spellings. Searches were on **title, keywords and
abstract**.

Sources: IEEE, ACM, Citeseer, SpringerLink, Web of Science, plus **SCOPUS**. For SCOPUS two complex
strings were used instead, run once per period — the stated rationale being that **reducing the
number of searches reduces the problem of integrating results**.

**Validate the automated search against a manual one.** The automated search found **15 of 18**
studies a prior manual search had found. Two misses were borderline; one used "review" without
"literature review". Conclusion: the automated search was **almost as good** as manual for the most
important SE sources — a calibrated claim, not a blanket endorsement.

> **⚠ CAVEAT — indexing lag defeats automated search.** Re-running the same search a year later found
> **all three previously missed papers**, confirming they simply were not indexed yet. There can be
> considerable delay between a conference paper appearing and its appearing in an index. **This
> affects every SLR, not only tertiary studies.**
>
> Mitigation the authors recommend: back up automated searches with **manual searches of the most
> recent relevant conference proceedings**, and consider **re-running an indexing-system search
> immediately before publication**.

> **⚠ CAVEAT — adding "software" to the string silently drops cross-domain papers.** Removing
> `AND TITLE-ABS-KEY("software")` recovered two relevant papers but raised the result count from
> **134 to 578**. A precision/recall trade-off with a measured cost.

> **⚠ CAVEAT — the SE / IS / CS border is leaky.** Studies on the boundary between software
> engineering, information systems and computer science are likely to be missed.

**Advice to authors, which the platform can act on directly**: use the terms "systematic review" or
"systematic literature review" **in the title or keywords** if you want the study to be found.

> **⚙ IMPLEMENTATION.** A tertiary study is the strongest case for the platform's multi-database
> fan-out plus a *terminology-variant* search: one concept, many strings. It is also the case where
> re-running a search before publication should be a prompted workflow step, not a manual habit.

### 2.2 Study selection — two-step screening with random reviewer allocation

A concrete, encodable allocation protocol:

**Step 1 — title and abstract.** Three researchers screen each paper independently: **two drawn at
random from a pool of five**, plus one reviewer (Kitchenham) who reviews **every** paper.
Disagreements are discussed, **with the emphasis on not rejecting disputed papers.**

**Step 2 — full text.** Obtain full copies. Apply:
- There is a full paper — not a PowerPoint presentation or extended abstract
- The paper includes a literature review whose papers were **included based on a defined search
  process**
- The paper is about software engineering rather than IS or computer science

Same allocation: two of five at random, plus the constant reviewer; disagreements discussed and
resolved; **emphasis on not rejecting possibly relevant papers.**

**Worked attrition**, useful for calibrating expectations: 1757 papers → 161 after initial screening
→ 119 after step 1 → 40 after step 2 (54 rejected for having *no defined search process*, 25 for
being related-work-only, duplicate, or not SE) → adjustments for time frame, duplicate reports and
papers known to the researchers → **4 further rejected during data extraction** → 19 in the final
set of the newer period.

> **⚠ CAVEAT — rejection can happen during extraction, and the reasons are instructive.** Two papers
> were excluded because "apart from the search there was nothing systematic about their literature
> review"; two because of incompleteness — one reporting preliminary results only, one a short paper
> reporting **no aggregation** of the papers it identified. A study can pass full-text screening and
> still fail once you try to extract from it.
>
> **⚙ IMPLEMENTATION.** The platform must permit exclusion *after* inclusion, with a reason, and
> reflect it in the PRISMA flow. A screening decision is not final.

### 2.3 Quality assessment — DARE, with full anchors

The instrument for tertiary studies. Four questions, scored **Y = 1, P = 0.5, N = 0**, total out of 4.

| # | Question | Y (1) | P (0.5) | N (0) |
| - | -------- | ----- | ------- | ----- |
| **Q1** | Are the review's inclusion and exclusion criteria described and appropriate? | Inclusion criteria explicitly defined in the paper | Inclusion criteria implicit | Not defined and not readily inferable |
| **Q2** | Is the literature search likely to have covered all relevant studies? | Searched **four or more** digital libraries **and** used additional search strategies, **or** identified and referenced all journals addressing the topic | Searched **3 or 4** libraries with no extra strategies, **or** a defined but restricted set of journals and proceedings | Searched **up to 2** libraries, or an extremely restricted set of journals |
| **Q3** | Did the reviewers assess the quality/validity of the included studies? | Explicitly defined quality criteria, extracted from each primary study | The research question itself involves quality issues addressed by the study | No explicit quality assessment attempted — **or quality data extracted but not used** |
| **Q4** | Were the basic data/studies adequately described? | Information presented per paper such that data summaries can be **traced to relevant papers** | Only summary information — papers grouped into categories, but individual studies cannot be linked to a category | Results of individual studies not specified; primary studies not cited |

**Two qualifications that matter for automation:**
- Scoring Q2 **also requires judging whether the digital libraries were appropriate for that specific
  SLR** — a count alone is insufficient.
- The anchors "provide support for the assessment; **it is not a strict mutually exclusive
  classification process.**"

> **⚠ NOTE on Q3.** The "extracted but not used" clause is a **tightening introduced in 2010** and
> applied only to papers published after a cutoff date. If comparing scores across studies, know
> which version of Q3 was applied.

**New advice arising from the scoring**: authors **should give a rationale if they do not evaluate
primary-study quality** — which is reasonable for a large-scale mapping study where follow-on SLRs
would assess quality instead.

> **⚙ IMPLEMENTATION.** DARE is the single most implementable evaluator in this corpus: four
> questions, three anchors each, over data the platform already holds. Note that Q4 is a
> **traceability** check — can a summary be traced to the papers behind it — which the platform can
> answer structurally rather than by asking a model.

### 2.4 Data extraction — the consensus and minority report protocol

The only fully specified multi-rater extraction protocol in the corpus:

1. **Two researchers from a pool of five** (excluding two designated people) are **randomly
   allocated** to each study
2. Both **independently** answer the quality questions, **providing a justification for each answer**
3. The two compare results and reach a **consensus**
4. A **third reviewer independently** answers the quality questions for **all** studies, also with
   justifications
5. The consensus is compared against that third extraction, and **the two original extractors discuss
   disagreements until final consensus** — with the third reviewer **deliberately excluded from the
   final discussion, so that one person does not have too much influence on the results**

A simpler variant for the other subset: three researchers extract, **median value taken as
consensus**. Non-subjective data — publication source, type, authors, affiliations — extracted by
**one** person.

> **⚙ IMPLEMENTATION.** Step 5's exclusion rule is the subtle part and the part most likely to be
> lost in an implementation: the arbitrator supplies an independent reading but **must not adjudicate**.
> That is a different role from the "third reviewer resolves ties" pattern the platform currently
> implies, and it is deliberately different — it exists to prevent a senior reviewer dominating.
> Note also that **justification per answer is mandatory**, not optional metadata.

**Data extracted per included secondary study:**
- Type of study — SLR or mapping study
- Review focus — SE-oriented or research-methods-oriented
- **Number of primary studies included** — to judge whether SE has enough primary studies for reviews
  to be useful
- Whether it posed detailed technical questions (**RQ**), addressed trends in an SE topic area
  (**SERT**), or addressed how software engineers do research (**RT**)
- Quality score; year; publication source and type
- Whether it **positioned itself as an EBSE study** by citing EBSE papers or the SLR guidelines
- Whether it included **practitioner guidelines**; the topic

### 2.5 Analysis

Descriptive aggregation — counts per year, medians of primary-study counts, means of quality scores
by publication source and by guideline-citation status.

**Regression analysis** is used, with total quality score as the dependent variable and year, review
type, guideline citation, EBSE citation and publication type as factors.

> **◐ DISPUTED — does citing the guidelines predict quality?** Kitchenham found guideline citation
> significant (parameter estimate 0.55) and mapping-study type significantly negative (−0.48). But
> the guideline effect **loses significance (p = 0.06) if Springer book chapters are treated as a
> separate publication category** — the authors report this themselves. **da Silva et al. found the
> guideline effect non-significant.** Do not present "citing the guidelines improves quality" as
> settled.

**Secondary framing used**: map each study's topic onto the *SE 2004 Curriculum Guidelines* and onto
**SWEBOK** chapters, then record a per-study judgement of "useful for education / useful for
practitioners / why". A reusable pattern for tertiary studies aiming at practical impact.

---

## Phase 3 — Reporting

As for an SLR. See [10-reporting-and-evaluation.md](./10-reporting-and-evaluation.md) — **SEGRESS
explicitly marks which of its items apply to tertiary studies**, and is the right standard here.

---

## Caveats specific to tertiary studies

> **⚠ Mapping studies score lower on DARE than SLRs, for structural reasons — not because they are
> worse.** They seldom assess primary-study quality (costing Q3) and often lack clear traceability
> from individual studies to their characteristics (costing Q4). **Do not compare DARE scores across
> review types without saying so.**

> **⚠ Large primary-study counts correlate with lower quality.** With many papers, traceability from
> primary studies to conclusions (Q4) and repeatability (Q1) tend to be compromised, and individual
> papers are unlikely to be quality-assessed (Q3).

> **⚠ Blinding was not achieved, and the authors say so.** Quality assessment may have been
> influenced by knowing whether a study cited the guidelines; there was no formal blinding. Partial
> mitigations used: ordering the form so quality came first, and collecting citation data only after
> quality data. **The mitigation is worth copying; so is the disclosure.**

> **⚠ One person seeing every paper is a known bias, accepted deliberately.** Kitchenham reviewed and
> extracted from all papers, judging an overview more valuable than the bias it introduced. Record
> the trade-off rather than pretending it does not exist.

> **⚠ Mixed extraction methods across sub-sets limit comparison.** Where different subsets used
> different extraction protocols, only **within-subset** comparisons are valid.

---

## Findings worth citing

- **54 literature reviews used no defined search strategy at all**, against 53 genuine SLRs in the
  same period — "many literature reviews are not performed in accordance with any methodology."
- **Only six SLRs performed a full quality evaluation**, and two more a partial one.
- Median primary studies: **~20–26 for SLRs, ~92–133 for mapping studies** — an order-of-magnitude
  difference that should inform default expectations in the platform.
- Of reviews apparently targeted at practitioners, **only four explicitly provided
  practitioner-oriented advice.**
- 29 SLRs mapped onto only **17 of 233** curriculum sub-topics — coverage of core SE topics is
  extremely sparse.
- Adoption: SLRs had "gone past the stage of being used solely by innovators but cannot yet be
  considered a main stream software engineering research methodology."

> **⚙ IMPLEMENTATION.** The first two findings are the platform's market in one line: most reviews
> calling themselves systematic have no defined search process and no quality evaluation. Both are
> things software can require rather than merely permit.
