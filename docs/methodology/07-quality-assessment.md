# 07 — Quality Assessment

**Primary sources**: Kitchenham & Charters 2007 §6.3 (the framework and both checklists), Dybå &
Dingsøyr 2007 (the 11-item instrument), Kitchenham et al. 2010 (DARE), Kitchenham et al. 2013 (the
withdrawal), Garousi et al. 2019 (grey literature), Ivarsson & Gorschek (rigour–relevance), Petersen
et al. 2015 (mapping studies).

---

## Start here: the guidance was withdrawn

Kitchenham et al. 2013 assessed their own 2007 guidance and concluded that **the discussion of quality
checklists "is not useful"**, that **"the current unhelpful guidelines should be removed"** — and,
candidly, **"it is not clear what should replace them."**

So this chapter does not present a single authoritative instrument, because the corpus does not
contain one. It presents the framework, the instruments that exist, and the constraints on using any
of them.

---

## What quality means, and why you are assessing it

**Quality = the extent to which a study minimises bias and maximises internal and external validity.**
Internal validity is a **prerequisite** for external validity.

| Term | Definition |
| ---- | ---------- |
| **Bias** (systematic error) | A tendency to produce results departing systematically from the true results. Unbiased results are internally valid |
| **Internal validity** | The extent to which design and conduct prevent systematic error |
| **External validity** | The extent to which observed effects apply outside the study |

**Five purposes** — decide which apply before choosing an instrument:
1. Finer inclusion/exclusion criteria
2. Investigating whether quality differences explain differing results
3. Weighting studies during synthesis
4. Guiding interpretation and the strength of inference
5. Guiding recommendations for further research

### The four types of bias, with SE-adapted protection

| Type | Definition | Protection |
| ---- | ---------- | ---------- |
| **Selection** (allocation) | Systematic difference between comparison groups with respect to treatment | Randomisation of many subjects **with concealment of the allocation method** — allocation by program, not experimenter choice |
| **Performance** | Systematic difference in how comparison groups are conducted, apart from the treatment | Replication with different experimenters; experimenters with **no personal interest** in either treatment |
| **Measurement** (detection) | Systematic difference in how outcomes are ascertained | Blinding outcome assessors — sometimes possible |
| **Attrition** (exclusion) | Systematic differences in withdrawals or exclusions | Report reasons for all withdrawals; sensitivity analysis including excluded participants |

> Medicine relies on blinding subjects and experimenters. **That is usually impossible in SE**, which
> is why the protections above are weaker than their medical counterparts.

---

## Two uses, two data flows — the distinction that must be modelled

| Use | When the data is collected | On what form |
| --- | -------------------------- | ------------ |
| **To select studies** — quality becomes an inclusion/exclusion criterion | **Before** the main extraction | **Separate** forms |
| **To analyse** — quality identifies subsets to test against outcomes | **With** the main extraction | **Joint** form |

Both may coexist in one review.

> **⚙ IMPLEMENTATION.** This is a real modelling requirement, not a nicety. If quality gates
> inclusion, the scores must exist before extraction runs; if quality feeds analysis, they can be
> captured alongside. The platform's `QualityScore` should record **which purpose it served**,
> because that determines whether a study missing a score is an error or is simply not yet assessed.

---

## The instruments

### The hierarchy of evidence — and why not to use it naively

The traditional hierarchy puts systematic reviews and randomised trials at the top, quasi-experiments
and expert opinion at the bottom.

> **⚠ Petticrew & Roberts: this is too simplistic.** Different designs are better for different
> *question types* — qualitative studies beat randomised experiments for "do practitioners find this
> technology appropriate for the systems they build". **Restrict to designs best suited to your
> specific question, not to a fixed ranking.**

> **⚠ And a warning about observational studies.** Large observational findings have been overturned
> by trials — the vitamin C case, where vitamin C use turned out to be a *surrogate* for lifestyle.
> This matters in SE because much cost-estimation and success-factor research is correlational. Good
> observational studies must consider confounders, measure them, adjust the analysis, and run
> sensitivity analysis for **measured and unmeasured** confounders.

### Kitchenham's checklists (2007)

Two, organised by **study stage — design · conduct · analysis · conclusions**:

- **Quantitative**: a large item pool with columns for {quantitative empirical, correlational,
  surveys, experiments}. Representative items — design: are the aims clearly stated; what population;
  who was included and excluded; is the sample representative; were treatments randomly allocated; is
  the sample size justified; are variables adequately measured. Analysis: are confounders adequately
  controlled; is statistical significance assessed; is the actual p value given; are confidence
  limits given; is there evidence of multiple testing or many post-hoc analyses. Conclusions: **are
  negative findings presented**; is practical significance discussed; how are null findings
  interpreted; are important effects overlooked.
- **Qualitative — 18 items**: credibility and importance of findings; how understanding was extended;
  how well the evaluation addresses its aims; scope for wider inference; defensibility of the design;
  sample design and coverage; data collection; how analysis was conveyed; retention of context;
  diversity of perspective; richness; **clarity of the links between data, interpretation and
  conclusions**; coherence of reporting; assumptions and theoretical perspectives; ethics; how
  adequately the research process was documented.

**Do not use all the items.** Select those appropriate to your questions. You may need a
**measurement scale per item**, because Yes/No can mislead. **The instrument must be assessed for
reliability and usability during protocol piloting** before being applied to the full set.

### Dybå & Dingsøyr (2007) — 11 items, the most-reused SE instrument

Derived from CASP, covering **rigour, credibility and relevance**, scored **yes/no with no overall
grade**. Widely reused in SE and referenced by Ampatzoglou as a mitigation for TV11 and TV12.

### Ivarsson & Gorschek — rigour and relevance

An alternative axis: **rigour** assessed from the description of context, empirical design and
validity discussion; **relevance** from subjects, context, scale and research method used.

### DARE — for secondary studies

Four questions, scored **Y = 1 / P = 0.5 / N = 0**. The instrument for **tertiary studies**, because
their primary studies are secondary studies. Full anchors in [04-tertiary.md](./04-tertiary.md).

### Garousi — for grey literature

**20 items, scored 1 / 0.5 / 0, inclusion threshold 10 of 20**, across authority of the producer,
methodology, objectivity, date, position with respect to related sources, novelty, impact and outlet
control. See [05-grey-literature-mlr.md](./05-grey-literature-mlr.md).

### GRADE / GRADE-CERQual — for certainty in the body of evidence

Not a per-study instrument. Four certainty levels across five domains, assessing the **body** of
evidence. Named by SEGRESS items 15 and 22.

---

## Per study type

| Study type | Quality assessment |
| ---------- | ------------------ |
| **SLR** | Expected. Choose an instrument per study type present; qualitative and quantitative studies need **different checklists** |
| **SMS** | **Papers are not evaluated for quality** (Petersen 2008). Where used at all, it must **not impose high requirements** — e.g. only to confirm enough information exists to extract. SEGRESS marks risk-of-bias items *optional* for mapping studies |
| **Rapid Review** | Three options: **skip entirely** (with the threat reported), **venue proxy**, or **reduced-staffing appraisal**. See [03](./03-rapid-review.md) |
| **Tertiary** | **DARE.** And note the reversal: tertiary studies about SR methodology **do** require primary-study quality assessment, unlike most mapping studies |
| **MLR** | A **separate** grey-literature instrument in addition to the formal-literature one |

> **⚠ If you omit quality assessment, give a rationale.** Kitchenham 2010 makes this explicit —
> omission is reasonable for a large mapping study where follow-on reviews would assess quality, but
> it must be stated, not silent. DARE Q3 scores **N** for "quality data extracted but not used", so
> collecting scores and ignoring them is worse than not collecting them.

---

## Caveats — most of this chapter is caveats, and that is the honest picture

> **⚠ Do not infer that unreported means not done.** "It is tempting to assume that because something
> wasn't reported, it wasn't done. This assumption may be incorrect." Ask the authors.

> **⚠ Assess methodological quality, not reporting quality.** Where you score both, keep them as
> **separate metrics**. Kitchenham's worked example weighted reporting quality *lower*, and states
> plainly that combining them into a single number is bad practice.

> **⚠ Do not weight meta-analysis by quality score.** Not recommended by any medical guideline,
> despite being an intuitive move.

> **⚠ Scores are only comparable between studies of the same type and size.** Small studies can score
> well while providing limited evidence — "the quality score should only be used to differentiate
> between studies of the same type and size."

> **⚠ A checklist will not catch what it does not ask about.** Applying a generic checklist "will not
> identify invalid empirical practices" such as using an inappropriate accuracy metric to compare
> models. Quality instruments are necessary and not sufficient.

> **⚠ Generic checklist items misfire in context.** Kitchenham's own team found some questions
> inappropriate to the study context, and **their assessment of validation-method type frequently
> differed from that of the papers' own authors**.

> **⚠ Inter-rater reliability on quality scoring is poor even among experts.** In the tertiary study,
> the correlation between two authors was **0.67** on the number of applicable questions and **0.54**
> on the average quality score — "statistically significant but still disappointingly low."

> **⚠ Mapping studies score lower on DARE for structural reasons** — they seldom assess primary-study
> quality and often lack per-study traceability. Do not compare scores across review types without
> saying so.

> **⚠ Large primary-study counts correlate with lower quality scores**, because traceability and
> repeatability degrade at volume.

> **⚠ The field mostly does not do this.** Only **six SLRs performed a full quality evaluation** in
> Kitchenham's tertiary study; da Silva found full explicit quality assessment in **21%** of 120
> reviews; **quality assessment of papers using different research methods** is one of the three most
> reported problems in the whole corpus.

---

## What this means for the platform

> **⚙ IMPLEMENTATION.**
> - **Do not ship a single default checklist.** The guidance for one was explicitly withdrawn, and
>   the corpus supports per-study-type and per-design instruments instead. The existing
>   `QualityChecklist` / `QualityChecklistItem` model is the right shape — a *template* mechanism, not
>   a fixed list.
> - **Per-item scales, not booleans.** Yes/No misleads; the real instruments use 0/0.5/1 or ordinal
>   anchors.
> - **Keep methodological and reporting quality as separate scores.** Never sum them.
> - **Record the purpose** — selection or analysis — because it determines the data flow and whether a
>   missing score is a defect.
> - **Expect low inter-rater agreement and surface it** rather than hiding it behind a consensus
>   value. 0.54 correlation between experts is the benchmark to beat, and it is a low one.
> - **The strongest opportunity is grey-literature appraisal**, which is required, wanted, and almost
>   never performed — see [05](./05-grey-literature-mlr.md).
