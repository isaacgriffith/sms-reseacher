# 12 — Implications for This Platform

What the corpus means for the codebase. Cross-referenced to `docs/feature-gaps.md` gap IDs.

This chapter makes claims about the platform from the *methodology* side only. Where it says a gap is
confirmed, that means the research supports the gap's premise — not that the code has been re-checked
here.

---

## The market, stated by other people

Three findings from the corpus that together describe why this platform should exist:

| Finding | Source |
| ------- | ------ |
| **Zero tool support** for need-identification, protocol development, and quality assessment across the SLR stages | Marshall 2013 |
| The best available SLR tool scored **65.4%** on a DESMET feature analysis; the rest 45–53% | Marshall 2014 |
| **54 literature reviews used no defined search strategy at all**, against 53 genuine SLRs in the same period | Kitchenham 2010 |
| Only **six SLRs performed a full quality evaluation**; da Silva found 21% across 120 reviews | Kitchenham 2010, da Silva 2011 |
| **49%** of SE "systematic reviews" were really scoping studies; **20.4%** cited any synthesis method | Cruzes & Dybå 2011b |
| **90%** of reviews using grey literature performed no grey-specific quality assessment, though **79.2%** of experts say one is needed | Zhang 2020 |

The pattern: the expensive, judgement-heavy steps are the ones that get skipped, and they are the ones
no tool supports. That is the opportunity, and it is also the risk — see the closing caution.

---

## Gaps the research confirms

| Gap | What the research adds |
| --- | ---------------------- |
| **G1** — snowball provenance DAG | Wohlin's **include-before-snowballing rollback rule** is precisely why the edge is needed: excluding a paper requires reconsidering everything found from it. Without the edge you cannot distinguish a descendant with a second surviving parent. Also required by the PRISMA "other methods" arm |
| **G2** — per-database query optimisation | Kitchenham amendment 1 withdrew mechanical string construction *because* strings "need to be adapted for each digital library". Bailey's non-overlap data (12 unique from WoS, 0 from Google Scholar) is the evidence that per-engine behaviour differs materially |
| **G3** — missing search modalities | **Manual search is not optional** — Petersen 2015 says it "may be more effective"; Kitchenham 2013 requires manual search of recent proceedings to cover indexing lag. arXiv is confirmed absent, and preprints are a distinct stratum (López 2026) |
| **G4** — intra-rater test–retest | Explicitly required for the single-reviewer case by Kitchenham & Charters, and listed by Petersen 2015 as a search-evaluation technique. The platform's Rapid Review explicitly supports single reviewers |
| **G5** — selection decision rules | Petersen 2015 supplies the full catalogue with **measured trade-offs** (A+B+C+D+E finds all, 25% overhead; A+B+C+D finds 94%). Confirms the gap and supplies the content |
| **G6** — Study distinct from Paper | Confirmed from three directions: Cruzes' `Publication → Context → Finding` extraction template; Petersen 2008's screening rule that studies in one paper are treated separately; Staples' *unit of analysis* concept |
| **G8** — qualitative synthesis | Confirmed and sharpened. Cruzes' five steps, the 30–40 → 15–20 → 5–7 funnel, and four trustworthiness criteria are the specification. Ribeiro's two metasummary formulas are recovered and arithmetically verified |
| **G10** — report validation | Confirmed, **but reframed** — see the constraint below |
| **G12** — document management | Kamei's link-rot data (23.7% dead, 24.8% no URL) and Kitchenham 2023's (19/46 live, 56% Wayback-recoverable) make archival a requirement, not a nicety |
| **G13a/b/c** — search-string piloting | The quasi-gold-standard method requires **two disjoint sets** — one to build the string, one to evaluate it. The platform uses one set for both, which measures memorisation rather than recall |
| **G14** — PRISMA flow diagram | Fully specified: two column variants, 24 counts, and the asymmetry (no de-duplication or screening box in the "other methods" arm). Per-reason exclusion counts are explicitly required |
| **G24** — DOI-less snowballing | Confirmed as consequential: grey literature, theses and reports are exactly what lacks a DOI, and they are what the excluded population consists of |
| **G28** — grey literature | Confirmed and greatly expanded. Garousi's 20-item instrument, the seven-question decision aid, three stopping criteria, and the metadata minimum |

---

## The constraint that changes a planned feature

> ### G10 must be reframed
>
> **PRISMA 2020 states it "should not be used to assess the conduct or methodological quality of
> systematic reviews."**
>
> A PRISMA/SEGRESS checker is still the right feature, but it measures **reporting completeness**. It
> must never be labelled or scored as quality or rigour.
>
> For quality, the corpus supplies instruments designed for it: **DARE** (4 questions, 0/0.5/1, over
> data the platform already holds) and the **Petersen 2015 rubrics** (5 scored rubrics over process
> actions). Both are more implementable than a PRISMA score and neither misuses its source.
>
> **`docs/feature-gaps.md` G10 should be amended accordingly.**

---

## New requirements the corpus implies

Things not currently in the gap catalogue.

| # | Requirement | Source |
| - | ----------- | ------ |
| N1 | **SEGRESS per-study-type applicability.** Every checklist item is required / optional / not-required *per review type*. A one-size checker would wrongly penalise a mapping study for omitting a certainty assessment | [10](./10-reporting-and-evaluation.md) |
| N2 | **Three-valued screening vote.** Include / exclude / **uncertain**. A binary decision cannot express the decision-rule table's cell C | [06](./06-search-and-selection.md) |
| N3 | **Stopping rules as first-class protocol fields** — marginal-yield or time-budget, with a record of what was left **unassessed**. An unassessed paper is not an excluded paper | [02](./02-sms.md), [06](./06-search-and-selection.md) |
| N4 | **Escalatable reading depth per paper.** Abstract → introduction/conclusion → full text, escalating when classification is uncertain. Not a global setting | [02](./02-sms.md) |
| N5 | **Rationale per classification.** Petersen 2008 recorded a short rationale for every category assignment; the consensus-and-minority-report protocol requires a justification per quality answer | [02](./02-sms.md), [04](./04-tertiary.md) |
| N6 | **Protocol versioning with justification**, required by the Rapid Review method and by "report deviations from the protocol" everywhere else | [03](./03-rapid-review.md) |
| N7 | **Concession → threat auto-derivation**, generalised from the Rapid Review case to all study types using Ampatzoglou's 22/34 threats and 60 mitigations — including the exclusivity rules and the one concession that must *not* generate a threat | [09](./09-threats-to-validity.md) |
| N8 | **GQM traceability**: goal → question → extraction field. Makes "will the extracted data answer the questions?" checkable rather than a matter of opinion | [09](./09-threats-to-validity.md) |
| N9 | **A "review update" workflow.** Forward-only snowballing from a prior review found all database-search papers plus three more, at a fraction of the screening cost. Studies currently have no ancestry | [06](./06-search-and-selection.md) |
| N10 | **Terminology-variant search** — one concept, many strings — needed for tertiary studies, where 15 simple strings outperformed one complex one | [04](./04-tertiary.md) |
| N11 | **Exclusion after inclusion**, with a reason, reflected in the flow diagram. Papers pass full-text screening and still fail during extraction | [04](./04-tertiary.md) |
| N12 | **Grey-source metadata minimum**: URL, **access date stamped at retrieval**, author, title, outlet, archived copy | [05](./05-grey-literature-mlr.md) |
| N13 | **Quality-instrument purpose flag** — selection or analysis — because it determines whether scores must precede extraction | [07](./07-quality-assessment.md) |
| N14 | **Per-item ordinal scales**, not booleans. Every real instrument uses 0/0.5/1 or ordinal anchors | [07](./07-quality-assessment.md) |
| N15 | **Separate methodological and reporting quality scores.** Never summed | [07](./07-quality-assessment.md) |

---

## Where the platform's current framing is wrong

| Claim in the repo | Correction |
| ----------------- | ---------- |
| `all-together.md`: Rapid Reviews are "the least rigorous of the three" | An RR is defined by being **bound to a practitioner's problem and conducted with that practitioner**. A review without those is a *deviation to be avoided*, not a lightweight review. See [03](./03-rapid-review.md) |
| `systematic-mapping-studies.md`: rubrics presented without source | They are Petersen 2015's; the validity classes are Petersen & Gencel's. Now attributed, with the malformed search-evaluation table repaired. See [02](./02-sms.md) |
| `tertiary-studies.md`: empty | Written from Kitchenham 2010/2009/2013. See [04](./04-tertiary.md) |
| Implicit: SMS assessment omits quality "because it is lighter" | Petersen's reason is different and better — quality restriction **biases the map**, because some sub-areas are easier to study empirically than others |
| Implicit: one synthesis strategy per study type | The catalogue has **13 methods**, chosen by research question and primary-study design — not by study type |

---

## The caution to carry into every design decision

Three findings that constrain how far automation should go:

> **1. Extraction decoupled from appraisal produces confident wrong answers.** Kitchenham et al.
> distrust automated extraction "unless our ability to evaluate the quality of different studies
> improves" — extracting from a study without checking whether it used an invalid metric yields
> results "very quickly but will be wrong". This is the sharpest warning in the corpus for a platform
> like this one. It does not forbid automation; it forbids extraction that skips appraisal.

> **2. Outcome quality tracks reviewer experience.** Expert pairs converged on 9 of 10 studies and the
> same conclusions; research associates produced different studies from each other and from a prior
> expert review. Reliable results are "only likely when SRs are undertaken by experienced researchers
> with domain knowledge."

> **3. Threat TV21 — unfamiliarity with the research field — is mitigated by *becoming familiar*.**
> The recommended actions are exhaustive related-work reading and involving senior researchers in
> analysis and interpretation.

Taken together: **encoded guidance and enforced gates are worth most to inexperienced reviewers, who
currently do worst — and automation that removes the need to engage with the literature conceals
TV21 rather than mitigating it.** The design principle that follows is that the platform should make
the *process* rigorous and visible, not make the *judgement* disappear. Immersion, rationale capture,
and disagreement surfacing all serve that; a pipeline that silently produces a finished review does
not.

---

## Suggested reading order for implementation work

1. **[11 — Caveats register](./11-caveats-register.md)** — the checklist; skim before designing anything
2. **[10 — Reporting](./10-reporting-and-evaluation.md)** and **[09 — Validity](./09-threats-to-validity.md)** — the two most directly implementable catalogues
3. The process chapter for whichever study type you are working on
4. **[06 — Search](./06-search-and-selection.md)** and **[08 — Extraction & synthesis](./08-extraction-and-synthesis.md)** — where most of the open gaps live
