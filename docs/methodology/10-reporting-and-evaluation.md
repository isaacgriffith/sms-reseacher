# 10 — Reporting Guidelines, Checklists and Report Evaluation

**Primary sources**: Kitchenham et al. 2023, **SEGRESS** — *Software Engineering Guidelines for
REporting Secondary Studies* (and its 2022 predecessor, whose Table 9 is byte-identical). Page et al.
2021, **PRISMA 2020**. Kitchenham et al. 2010, **DARE**.

---

## Which standard to use

**SEGRESS is the primary standard for this platform.** Two reasons:

1. **It is the only standard that marks every item required / optional / not-required *per review
   type*** — quantitative SR, mapping study, qualitative review, mixed-methods, tertiary. That maps
   directly onto the four study types the platform models.
2. PRISMA 2020's own scope is "systematic reviews of studies that evaluate the effects of health
   interventions" and explicitly **not** qualitative synthesis. SEGRESS's assessment is that PRISMA
   alone "will be of very limited value to SE researchers", because SE secondary studies are often
   mapping studies or qualitative reviews.

SEGRESS does not replace PRISMA — it is PRISMA 2020 with SE-specific extensions and per-type
applicability. Nothing is removed outright; items are marked *not required* for a type instead.

> ### ⚠ PRISMA 2020 MUST NOT BE USED AS A QUALITY INSTRUMENT
>
> PRISMA 2020 states it **"should not be used to assess the conduct or methodological quality of
> systematic reviews."** It measures *reporting completeness*, not rigour.
>
> This directly constrains gap **G10**, which proposes a PRISMA/SEGRESS report checker. The feature
> is valid, but it must be **labelled and scored as reporting completeness**. A "PRISMA score"
> presented as a quality score misuses the standard in exactly the way its authors warn against.
> For quality, use **DARE** (below) or the Petersen 2015 rubrics — instruments designed for it.

**Scale of the checklists** (reproduced in the working notes; consult the sources for exact wording):

| Standard | Items |
| -------- | ----- |
| **SEGRESS** | 27 top-level items → **44 numbered rows** with sub-items expanded, plus **9 unnumbered guidance rows** = 53 rows |
| **PRISMA 2020** | 27 top-level items → **42 numbered rows** expanded, across 7 sections |
| **PRISMA 2020 for Abstracts** | **12 items**, a separate checklist |
| **DARE** | 4 scored questions (a fifth exists in the original set — see below) |

---

## What SEGRESS adds to PRISMA 2020

The differences are the interesting part, because each encodes something SE-specific.

| Item | PRISMA 2020 | SEGRESS adds |
| ---- | ----------- | ------------ |
| **1 Title** | "Identify the report as a systematic review" | Must name the **type** (SR / mapping / tertiary / qualitative / mixed-methods) **and** the topic, so it can be found |
| **Introduction** | — | A new unnumbered **"Opening"** item: broad problem → research area → niche → focus |
| **Section purposes** | — | Each of Title / Abstract / Introduction / Methods / Results / Discussion carries a one-line statement of purpose |
| **Full Report** | — | New opening row: reference the protocol, use supplementary material, publish large model-building separately — to mitigate the report-length cost of full compliance |
| **5 Eligibility** | Inclusion/exclusion + grouping | **Search restrictions must be specified and justified** — dates, language, journal, publication type. PRISMA "assumes that there is no lower bound on the search". Plus: state how existing reviews found by the search will be used |
| **7 Search strategy** | Full strategies for databases, registers, websites, filters, limits | Adds **snowballing, manual search, finding unpublished materials, and methods used to assess achieved completeness** — SE search is not database-only |
| **8 / 16a / 18** | No mention of agreement | **Requires methods of assessing agreement rates (8) and reporting agreement statistics (16a, 18)** — SE reviews use κ; PRISMA leaves it implicit |
| **10b Data items** | Other variables, assumptions about missing information | **"For mapping studies define any classification systems used to categorize the data items"** — the defining activity of a mapping study |
| **13 heading** | "Synthesis methods" | **"Analysis and Synthesis"** — mapping studies *analyse characteristics*, they do not *synthesise outcomes* |
| **13b** | Data preparation | Adds qualitative coding: **inductive vs deductive must be stated** |
| **13e ↔ 13f** | 13e heterogeneity, 13f sensitivity | **Swapped** — sensitivity analysis first, because it "could lead to a revision of the SR analysis or synthesis before initiating any investigation of possible reasons for the heterogeneity" |
| **20c ↔ 20d** | 20c heterogeneity results, 20d sensitivity | **Swapped**, same rationale |
| **14** | "Risk of bias due to missing results… (arising from reporting biases)" | **"Risk of bias due to publication bias"** — plainer for SE readers |
| **15 / 22** | "Certainty in the body of evidence" | Names **GRADE**, and cross-references **GRADE-CERQual** for qualitative reviews |
| **21** | Assessments of reporting bias | Adds **"For meta-analysis, report the heterogeneity among studies and provide funnel plots"** |
| **23c Limitations** | "Discuss any limitations of the review processes used" | **Include only issues not previously addressed** elsewhere in the report — an explicit anti-duplication rule |
| **24a–c Registration** | Expected | 24a **optional for all**; 24b/24c optional for mapping studies — SE has no review-registry culture |
| **27 Data availability** | List of artefacts | Names repositories (Zenodo, Figshare, Dryad) and reproducible-research artefacts; **"optional but recommended"** |
| **Items 17–22** | Linear | A note permitting **iteration per subgroup or per research question** — PRISMA's linear order breaks when different findings rest on different subsets |

> **⚠ A defect in SEGRESS itself.** Its prose describes the reordering as affecting "items 13d and
> 13f", while its own table shows **13e↔13f**. The table is authoritative; the prose is a slip.

---

## Per-study-type applicability — the reason to use SEGRESS

The single most useful table for this platform. Collected from SEGRESS Table 9:

| Item | Quantitative SR | Mapping study | Qualitative review | Mixed-methods |
| ---- | --------------- | ------------- | ------------------ | ------------- |
| 1–9 | required | required | required (7, 8, 9 carry extra qualitative clauses) | required |
| 10a Outcomes | required | **not required** — mapping studies do not analyse primary outcomes | required | required |
| 10b Data items | required | required **+ define classification systems** | required | required |
| 11 Study risk of bias | required | **optional** | required | required |
| 12 Effect measures | required | **sometimes**, depending on the questions | **not required** | required |
| 13b Data preparation | required | **not required** | required **+ state inductive/deductive coding** | required |
| 13c | required | required — tables, graphs, maps | required | required |
| 13d | required | **not required** | required + constructs / comparison / validation | required |
| 13e Sensitivity | required | **not required** | required — deviant cases and exceptions | required |
| 13f Heterogeneity | required | **not required** | required | required |
| 14 Reporting bias | required | **not required** | required | required |
| 15 Certainty | essential | **not required** | essential | essential |
| 16b Near-misses | required | **optional** | required + justify synthesis exclusions | required |
| 18 Risk-of-bias results | required | **optional** | required | required |
| 19 Individual results | required | **not usually required** | required — major findings per study | required |
| 20b Statistical syntheses | required | — | **quantitative only** | required |
| 20d Heterogeneity results | required | **not required** | required | required |
| 21 Reporting biases | required | **not usually** | **not usually** | required |
| 22 Certainty of evidence | required | **not required** | required | required |
| 23b Limitations of evidence | required | **not required** | required | required |
| 23d Implications | required | **only future research is relevant** | required | required |
| 24b Protocol location | required | **optional** | required | required |
| 24c Amendments | required | **optional** | required | required |

**Tertiary studies are routed rather than given a column**: a tertiary study *about research methods*
follows the **mapping study** guidance; other tertiary studies follow the quantitative or qualitative
guidance as appropriate.

> **⚠ But with one reversal.** "Unlike most SE mapping studies, when conducting tertiary mapping
> studies that investigate SR methodology, **assessment of the quality of the primary studies is
> often required** to address the research questions." So a tertiary study takes the mapping-study
> reporting profile *except* that quality assessment comes back in — and the instrument is **DARE**,
> because its primary studies are secondary studies.

**Additional mapping-study guidance:**
- **Search**: largely the same as an SR, but **less emphasis on completeness and more on defining the
  process used**, plus specifying limitations **with a rationale**
- **Quality**: because there is no formal aggregation of primary outcomes, **risk of bias due to
  synthesis is irrelevant, as is certainty assessment**
- **Limitations**: if there were no deviations from the standards or protocol and no critical
  appraisal, **a limitations discussion is not necessary**
- **Terminology**: "Data Charting" is misleading — use PRISMA 2020's "Data Collection Process".
  "Synthesis of Results" should be **"Analysis of Study Characteristics"** for mapping studies

> **⚙ IMPLEMENTATION.** This table is the specification for a per-study-type report checker. Each row
> is (item, study type) → required | optional | not required. A mapping study penalised for omitting
> a certainty assessment would be wrong by this standard — which is exactly the failure mode of a
> one-size checklist.

---

## The PRISMA 2020 flow diagram

Required by SEGRESS item 16a ("ideally using a flow diagram"), which defers to PRISMA for the
structure.

**Two variants, and the asymmetry matters:**

| | Databases and registers | Other methods |
| --- | --- | --- |
| Identification | Records identified, per source | Records identified from websites, organisations, citation searching, etc. |
| **De-duplication** | **Records removed before screening** — duplicates, ineligible-by-automation-tool, other reasons | **No de-duplication box** |
| **Screening** | Records screened → excluded | **No record-screening stage** |
| Retrieval | Reports sought for retrieval → not retrieved | Reports sought for retrieval → not retrieved |
| Eligibility | Reports assessed for eligibility → excluded **with reasons, per reason** | Same |
| Included | Studies included; reports of included studies | Merged into the same box |

**24 counts** are demanded across the diagram.

> **⚙ IMPLEMENTATION — this bears directly on gaps G1, G14 and G28.** The "other methods" column is
> exactly where **snowballed records and grey literature** belong, and it has a *different shape*:
> no de-duplication box, no screening stage. A platform that funnels every record through one
> pipeline cannot render this diagram correctly. The provenance discriminator proposed in G14 step 2
> and the discovery edges proposed in G1 are what make the two columns separable.
>
> Note also **"excluded with reasons, per reason"**: `PaperDecision.reasons` must roll up to
> per-reason counts, which G14 step 4 records as missing.

---

## Report evaluation procedures

### DARE — for evaluating a review's quality

The instrument used across the SE tertiary studies, and the one SEGRESS says tertiary studies may use
for quality assessment. Four questions, scored **Y = 1, P = 0.5, N = 0**; full anchors are in
[04-tertiary.md](./04-tertiary.md).

1. Are the review's inclusion and exclusion criteria described and appropriate?
2. Is the literature search likely to have covered all relevant studies?
3. Did the reviewers assess the quality/validity of the included studies?
4. Were the basic data/studies adequately described?

> **⚠ The original DARE set has five criteria, and SE dropped one.** The fifth is a **mandatory
> synthesis criterion**. Its omission from the SE version is a concrete instance of SE weakening an
> inherited standard — and it is the same criterion whose absence Cruzes & Dybå found in half the
> reviews they audited. Worth restoring as an optional fifth question.

### GRADE — for certainty in the body of evidence

Named by SEGRESS at items 15 and 22. Four certainty levels across five domains. For qualitative
reviews, **GRADE-CERQual** is the counterpart. SEGRESS also cross-references **Cochrane risk-of-bias
domains**.

### The Petersen 2015 rubrics — for evaluating a mapping study's process

Five scored rubrics covering need for review, search strategy choice, search evaluation, extraction
and classification, and study validity. See [02-sms.md](./02-sms.md). These score **actions taken**,
not report prose — a complementary axis to SEGRESS's reporting completeness.

### Instruments compared

| Instrument | Measures | Applies to | Scored? |
| ---------- | -------- | ---------- | ------- |
| **SEGRESS** | Reporting completeness | All five review types, per-item | No — a checklist |
| **PRISMA 2020** | Reporting completeness | Quantitative reviews of intervention effects | No — and **must not** be used for quality |
| **DARE** | Review quality | Any secondary study | **Yes** — 0–4 in 0.5 steps |
| **GRADE / CERQual** | Certainty in the evidence body | Quantitative / qualitative | Yes — 4 levels |
| **Petersen rubrics** | Process actions taken | Mapping studies | Yes — 0–2 or 0–3 per rubric |
| **PRISMA-trAIce** | Reporting completeness of **AI *tool* use** | Reviews conducted with AI assistance | No — a checklist, and **a proposal, not a consensus standard**. See [14](./14-ai-assisted-review-reporting.md) |

---

## Reporting for a Rapid Review

None of the above applies directly. An RR reports through an **Evidence Briefing** — a one-page,
practitioner-facing document with six defined parts, described in
[03-rapid-review.md](./03-rapid-review.md). RRs are usually **internally reviewed but not peer
reviewed**, and the corresponding rigour control is Cartaxo's disclosure regime: every methodological
concession recorded in the protocol, with a limitations disclaimer in the report.

An RR *may additionally* be published as a conventional paper, in which case SEGRESS applies to that
paper.

---

## Caveats on reporting

> **⚠ Full compliance inflates report length**, and SEGRESS addresses this twice. The prescribed
> mitigations: reference the protocol rather than restating it, use supplementary material, and
> publish large model-building work separately.

> **⚠ Report deviations from the protocol.** Recurring across the corpus. The protocol is not a
> promise; the failure is not deviating but not saying you did.

> **⚠ Do not duplicate the limitations discussion.** SEGRESS item 23c requires including *only*
> issues not already addressed when specifying the review process or discussing synthesis results.
> This is a direct answer to the risk that a full threats-to-validity checklist produces a report
> that repeats itself.

> **⚠ Search dates go unreported.** This was the specific empirical finding that motivated SEGRESS's
> addition to item 5. PRISMA assumes no lower bound on the search; SE reviews routinely have one and
> routinely fail to state it.

> **⚠ ENTREQ and RAMESES have gaps.** For qualitative reviews, SEGRESS maps both onto PRISMA 2020 and
> finds ENTREQ omits title, abstract, protocol registration, data availability and financial support
> — and, most significantly, **any discussion of publication bias or confidence in the body of
> evidence**. RAMESES collapses selection and appraisal into one element. Use SEGRESS rather than
> either alone.
