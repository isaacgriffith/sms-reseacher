# Secondary Study Methodology — Research Basis

**Compiled**: 2026-08-07
**Corpus**: `research/` — 55 PDFs, **54 unique papers** (see [Corpus manifest](#corpus-manifest))
**Purpose**: the research-backed process definitions this platform automates. Where the platform's
behaviour and this document disagree, **this document is the specification and the platform is the
defect** — unless the disagreement is recorded below as a deliberate deviation.

---

## What this supersedes

Four documents predate this one and were written without direct citation to sources:

| Document | Disposition |
| -------- | ----------- |
| `docs/systematic-literature-reviews.md` | Superseded by [01-slr.md](./01-slr.md) |
| `docs/systematic-mapping-studies.md` | Superseded by [02-sms.md](./02-sms.md) |
| `docs/rapid-reviews.md` | Superseded by [03-rapid-review.md](./03-rapid-review.md) |
| `docs/tertiary-studies.md` | **Was an empty file.** Written for the first time in [04-tertiary.md](./04-tertiary.md) |

Their content was checked against the sources rather than discarded. Where they were right, this
document says so and adds the citation they lacked. Where they were wrong or unsupported, the
correction is marked **⚠ CORRECTION** inline.

---

## Contents

| # | Document | Covers |
| - | -------- | ------ |
| 01 | [SLR](./01-slr.md) | Systematic Literature Review — the full process, as amended |
| 02 | [SMS](./02-sms.md) | Systematic Mapping Study — the full process |
| 03 | [Rapid Review](./03-rapid-review.md) | Rapid Review — the full process, Evidence Briefings |
| 04 | [Tertiary Study](./04-tertiary.md) | Tertiary Study — the full process |
| 05 | [Grey literature & MLR](./05-grey-literature-mlr.md) | What grey literature is, when to include it, how to appraise it |
| 06 | [Search & selection](./06-search-and-selection.md) | Search strategy, snowballing, selection rules, agreement |
| 07 | [Quality assessment](./07-quality-assessment.md) | Quality instruments and appraisal, per study type |
| 08 | [Extraction & synthesis](./08-extraction-and-synthesis.md) | Data extraction forms and every synthesis method |
| 09 | [Threats to validity](./09-threats-to-validity.md) | The validity frameworks and their threat catalogues |
| 10 | [Reporting & evaluation](./10-reporting-and-evaluation.md) | SEGRESS, PRISMA 2020, DARE, flow diagrams, report evaluation |
| 11 | [Caveats register](./11-caveats-register.md) | Consolidated traps, cross-referenced to the step they bite |
| 12 | [Platform implications](./12-platform-implications.md) | What this means for the codebase, mapped to `feature-gaps.md` |
| 13 | [Open science](./13-open-science.md) | Preregistration, replication packages, archival, licences, anonymisation |
| — | **[PLAYBOOK](./PLAYBOOK.md)** | **How to extend these documents when new papers arrive** — see below |
| — | [notes/](./notes/) | The per-paper extraction notes these chapters were composed from |

---

## Adding new papers — use the playbook

**[`PLAYBOOK.md`](./PLAYBOOK.md) is the maintenance document for this folder.** Read it before adding
any paper to `research/` and folding it in here.

It contains three things:

1. **The paper register** — all **54 papers already examined**, with the depth each was read to and
   which chapters each fed. Check a new paper against this first; the corpus already contains one
   duplicate pair that cost an extraction before it was caught.
2. **The pipeline, with ready-to-use prompts** — six stages from intake to verification, including a
   fill-in-the-blanks extraction prompt for subagents and a composition prompt matching this folder's
   house style. The prompts already carry fixes for every failure the original run hit.
3. **Decision rules** — when a new paper extends an existing chapter, when it warrants a
   `◐ DISPUTED` block, and when it justifies a new chapter.

**Typical use:**

| You have | Do |
| -------- | -- |
| A few papers on topics these chapters already cover | Playbook stages 1–2, then integrate directly into the affected chapter |
| Papers opening a topic no chapter covers | The full pipeline, ending in a new numbered chapter added to the Contents table above |
| A newer edition of a source already used | Rewrite the affected chapter rather than patching it |

The playbook also lists **known under-used material** — content already extracted but not yet worked
into a chapter, including Méndez's open-science and preregistration material and Stol's
method-slurring test. Those are the cheapest wins available and need no new reading.

### The extraction notes are committed too

[`notes/`](./notes/) holds the **14 structured per-paper extractions** (~203,000 words) these
chapters were composed from. They are denser than the chapters and closer to the sources, keeping
material the chapters did not need — full mitigation lists, complete rubric anchors, per-paper
empirical tables, and every uncertainty flagged during extraction.

**Consult them before re-reading a PDF.** A rewrite that starts from the notes costs a fraction of
one that starts from the corpus. The chapters remain authoritative; the notes are working material,
and where the two disagree the source PDF settles it.

---

## How to read this

Each process document follows the same shape:

- **Phases and steps**, numbered as the source numbers them
- **Per step**: what it is, what it consumes, what it produces, and how to do it
- **⚠ CAVEAT** blocks — traps the sources explicitly warn about
- **⚙ IMPLEMENTATION** blocks — what this means for the platform, and which gap it touches
- **⚠ CORRECTION** blocks — where a superseded repo document was wrong
- **◐ DISPUTED** blocks — where the sources disagree with each other, presented unresolved

Citations are `Author Year §section`. Full bibliographic detail is in the corpus manifest.

---

## Reliability of this document

**It is a synthesis, not a reproduction.** Source papers are copyrighted; this document paraphrases
them and quotes only where exact wording is load-bearing. **For any item you intend to implement
verbatim — a checklist item, a scoring anchor, a formula — consult the source PDF.** Chapter 10
lists exactly which items those are.

Known limits, recorded rather than hidden:

| Limit | Detail |
| ----- | ------ |
| **Petersen & Gencel Tables IV–V** | Check-marks displaced by one row in text extraction. The mapping in [09](./09-threats-to-validity.md) is reconstructed and **must be verified against the PDF before being quoted cell-by-cell**. |
| **Petersen 2015 Tables 5 and 7** | Tick marks and part of the column alignment did not survive extraction. Row taxonomies are sound; per-cell claims are marked unclear rather than guessed. |
| **Ampatzoglou figures** | Two defects **in the source itself**: Fig. 3a duplicates label "TV1.3" and Fig. 3b duplicates "TV15" for distinct sub-threats; the Data Validity prose says "five ungrouped" where the figure and checklist both give six. Not silently corrected. |
| **SEGRESS internal contradiction** | Its prose describes the PRISMA reordering as affecting "items 13d and 13f"; its own table shows 13e↔13f. The table is treated as authoritative. |
| **Ribeiro internal inconsistencies** | Three in its prose (a "10-factor model" vs nine groups; "four out of five studies"; "six concepts investigated more than once"). Flagged, not reconciled. |
| **Yasin, Gul, Kamei** | Yasin Table 16 and Table 9's seventh category, and Gul Figure 1 tier labels, are **images** and were not extracted. Kamei's RQ1 category counts sum to 260 against 150 reported. |
| **`basili_software_1992.pdf`** | Scanned image, no text layer, no OCR available. Read successfully as page images. |
| **Counts marked *(derived)*** | Obtained by tallying appendix study-ID lists because the source figures are images. |

---

## Corpus manifest

54 unique papers. `brereton_lessons_2007.pdf` and `kitchenham_lessons_2007.pdf` are **byte-identical
(same MD5)** — one paper filed twice; recommend deleting one.

### Process definitions and standards — the normative core

| Paper | Contributes |
| ----- | ----------- |
| `kitchenham_guidelines_2007` | The SLR process (EBSE-2007-01 v2.3). Foundational, **and amended by `kitchenham_systematic_2013`** |
| `petersen_systematic_2008` | The SMS 5-step process, keywording, bubble plot |
| `petersen_guidelines_2015` | The updated SMS guideline: 26-action checklist, 5 scoring rubrics |
| `cartaxo_rapid_2020` | The Rapid Review process and Evidence Briefings |
| `kitchenham_systematic_2010` | The tertiary study process |
| `kitchenham_systematic_2013` | **11 numbered amendments to the 2007 guidelines** |
| `garousi_guidelines_2019` | The MLR process, GL inclusion decision aid, GL quality checklist |
| `wohlin_guidelines_2014` | The snowballing procedure |
| `cruzes_recommended_2011` | Thematic synthesis, five steps |
| `ribeiro_using_2014` | Qualitative metasummary, both effect-size formulas |
| `kitchenham_segress_2023` / `_2022` | SEGRESS reporting standard |
| `page_prisma_2021` | PRISMA 2020 checklist, abstract checklist, flow diagram |
| `ampatzoglou_guidelines_2020` | Threats-to-validity framework for secondary studies |
| `petersen_worldviews_2013` | Validity classification and its paradigm justification |
| `wieringa_requirements_2006` | The research-type facet |
| `basili_goal_1994` / `basili_software_1992` | GQM |
| `petersen_identifying_2011` | Study-selection strategies |

### Evidence, lessons and critique

`brereton_lessons_2007` (= `kitchenham_lessons_2007`) · `bailey_lessons_2007` ·
`staples_experiences_2007` · `dyba_applying_2007` · `da_silva_six_2011` ·
`badampudi_experiences_2015` · `kitchenham_systematic_2009` · `babar_systematic_2009` ·
`mourao_investigating_2017` · `wohlin_reliability_2013` · `wohlin_second-generation_2016` ·
`cruzes_research_2011` · `marshall_tools_2013` · `marshall_tools_2014` · `zhang_evidence-based_2020` ·
`mendez_open_2020` · `fatima_retrieving_2023` · `stol_grounded_2016`

### Grey literature and practitioner evidence

`garousi_need_2016` · `garousi_benefitting_2020` · `adams_shades_2017` · `neto_multivocal_2019` ·
`lopez_multivocal_2026` · `kamei_grey_2021` · `gul_grey_2021` · `schopfel_how_2021` ·
`yasin_using_2020` · `rainer_using_2017` · `rainer_using_2019` · `rainer_heuristics_2019` ·
`williams_towards_2017` · `williams_using_2018` · `williams_how_2019` · `kitchenham_how_2023` ·
`wyrich_software_2026`

---

## The five headline findings

For anyone reading only one page.

**1. The 2007 SLR guidelines are amended, not current.** `kitchenham_systematic_2013` lists eleven
changes its own authors recommend — including **removing** structured questions for search-string
construction and **removing** the extractor/checker split, and **adding** quasi-gold standards,
snowballing, and duplicate-handling. A platform encoding the 2007 text unmodified encodes advice
its authors withdrew. See [01-slr.md](./01-slr.md).

**2. Database search alone is not adequate.** Badampudi et al. found snowballing retrieved 83% of
relevant papers against database search's 45.9%, and that **9 of 15 study conclusions would have
failed on database search alone, against 1 on snowballing alone**. Bailey found that of 71 papers,
Web of Science uniquely contributed 12 and Google Scholar uniquely contributed **zero**. Wohlin
found two independent maps of the same topic shared only 33 of 44 possible papers. See
[06-search-and-selection.md](./06-search-and-selection.md).

**3. PRISMA 2020 forbids being used as a quality instrument.** It states it "should not be used to
assess the conduct or methodological quality of systematic reviews". A report checker must be
framed as **reporting completeness**, never rigour. **SEGRESS is the better primary standard here**,
because it is the only one that marks each item required / optional / not-required **per review
type**. See [10-reporting-and-evaluation.md](./10-reporting-and-evaluation.md).

**4. Most SE "systematic reviews" do not synthesise.** Cruzes & Dybå's tertiary study found **49.0%
were really scoping studies**, only **20.4% cited any synthesis method**, and **4 of those 10
citations pointed at references that do not define the method claimed**. See
[08-extraction-and-synthesis.md](./08-extraction-and-synthesis.md).

**5. No tool supports the hard parts.** Marshall's mapping study found **zero tool support** for
need-identification, protocol development, and quality assessment; his feature analysis scored the
best available tool at 65.4%. That is this platform's opportunity, stated by someone else. See
[12-platform-implications.md](./12-platform-implications.md).
