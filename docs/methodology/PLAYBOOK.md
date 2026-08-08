# Playbook — Extending and Updating the Methodology Documents

**Purpose**: reproduce the process that produced `docs/methodology/` when new papers are added to
`research/`, without re-reading what has already been read.

**Read [The paper register](#the-paper-register) first.** It lists all 55 papers already examined and
which chapters each fed. Anything already there does not need re-extraction unless a chapter is being
rewritten.

---

## When to run this

| Trigger | Run |
| ------- | --- |
| A handful of new papers on covered topics | [Stages 1–2](#stage-1--intake), then [Stage 5](#stage-5--integrate) integration only |
| New papers opening a topic no chapter covers | Full pipeline, ending in a **new chapter** |
| A new edition or amendment of a source already covered (e.g. a SEGRESS revision) | Stages 1–2, then rewrite the affected chapter rather than patching it |
| A claim in a chapter is disputed | Stage 6 verification only — go back to the PDF |

---

## Prerequisites

```bash
# Text extraction — the whole pipeline depends on this
which pdftotext pdfinfo || sudo apt-get install poppler-utils

export RESEARCH=/home/isaacg/git/sms-reseacher/research
export NOTES=/home/isaacg/git/sms-reseacher/docs/methodology/notes   # committed — see below
export SCRATCH=/tmp/methodology-update                               # text dumps only, disposable
mkdir -p "$SCRATCH/txt"
```

---

## Where the notes live

**[`docs/methodology/notes/`](./notes/) — committed to the repository.** 15 files, ~207,000 words.

These are the structured extractions the chapters were composed from. They are **denser than the
chapters and closer to the sources**, holding material that did not make the cut — full mitigation
lists, complete rubric anchors, per-paper empirical tables, and every `[EXTRACTION UNCLEAR]` marker.

**Consult them before re-reading a PDF.** A chapter rewrite that starts from the notes costs a
fraction of one that starts from the corpus.

**New extractions go here too** — write directly into `$NOTES/`, not into a scratch directory. Only
the `pdftotext` dumps are disposable.

| Notes file | Papers |
| ---------- | ------ |
| `kitchenham_guidelines_2007.md` | Kitchenham & Charters 2007 — its own file, being the longest source |
| `corpus-notes.md` | Petersen et al. 2008; plus the reconciliation of the four pre-existing repo docs |
| `batch1-slr-lessons.md` | brereton · bailey · staples · dyba · badampudi · da_silva |
| `batch2-sms-tertiary.md` | petersen_guidelines_2015 · kitchenham_systematic_2010 · _2009 · _2013 · babar · mourao |
| `batch3a-snowballing.md` | wohlin_guidelines_2014 · wohlin_second-generation_2016 · wohlin_reliability_2013 |
| `batch4-rapid-reviews-tools.md` | cartaxo · kitchenham_how_2023 · wyrich · marshall_2013 · marshall_2014 |
| `batch5-mlr-grey-guidelines.md` | garousi ×3 · adams · neto · lopez |
| `batch6a-rainer-credibility.md` | rainer_using_2019 · rainer_heuristics_2019 · rainer_using_2017 |
| `batch6b-grey-empirical.md` | kamei · yasin · gul · schopfel |
| `batch7-reporting-standards.md` | segress_2023 · segress_2022 · prisma_2021 · williams ×3 |
| `batch8-validity-gqm.md` | ampatzoglou · petersen_worldviews · basili_1994 · basili_1992 |
| `batch9a-synthesis.md` | cruzes_recommended · ribeiro · cruzes_research |
| `batch9b-selection-classification.md` | petersen_identifying **only** — this batch died partway; its other two papers were re-extracted into `batch10` |
| `batch10-remaining.md` | wieringa · mendez · zhang · stol · fatima |
| `ai-assisted-review-reporting.md` | holst_transparent_2025 — added 2026-08-07; **the first topic-named notes file**, per the naming rule below |

> **⚠ Naming is historical, not semantic.** The `batchN` names record which agent produced which file
> during the original run, and the numbering has gaps (`3a`, `6a`/`6b`, `9a`/`9b`) because failed
> batches were re-dispatched split in two. **Use the table above, not the filenames, to find a
> paper.** New extractions should be named by topic rather than continuing the batch numbering.

---

## The pipeline

```
1. Intake        → identify new papers, dedupe against the register
2. Extract       → pdftotext, size the corpus, spot scanned PDFs
3. Batch         → group thematically, 3–6 papers per agent
4. Note          → subagents write structured notes to disk
5. Integrate     → compose or revise chapters from the notes
6. Verify        → links, counts, and anything flagged unclear
```

---

## Stage 1 — Intake

```bash
cd "$RESEARCH"
# Page counts and sizes
for f in *; do printf "%5s  %s\n" "$(pdfinfo "$f" 2>/dev/null | awk '/^Pages:/{print $2}')" "$f"; done | sort -rn

# Detect duplicates. NOT on PDF bytes — that check missed this corpus's only real duplicate for
# months, because two downloads of one paper differ in metadata while their text is identical.
# Dedupe on extracted text instead (run after Stage 2), then eyeball title + page count.
md5sum "$SCRATCH"/txt/*.txt | sort | awk '{print $1}' | uniq -d

# Note `ls -A`, not `*.pdf`: at least one corpus file has no extension.
ls -A
```

Cross off anything already in [the register](#the-paper-register). For each genuinely new paper,
record what you expect it to contribute — that drives batching.

---

## Stage 2 — Extract text

```bash
cd "$RESEARCH"
for f in *; do pdftotext -layout "$f" "$SCRATCH/txt/${f%.pdf}.txt" 2>/dev/null; done

# Any file with ~0 words is a scanned image with no text layer
wc -w "$SCRATCH"/txt/*.txt | sort -n | head
```

**Scanned PDFs**: `pdftotext` yields nothing and no OCR is installed. They are still readable — the
Read tool handles page images directly, up to 20 pages per request. One paper in the original corpus
(`basili_software_1992.pdf`, 24 pages) was read this way in two requests and lost nothing.

---

## Stage 3 — Batch

**Rules learned from the original run:**

- **3–6 papers per agent.** Larger batches failed at the write step.
- **Group thematically**, so one agent produces coherent cross-paper notes.
- **Put the highest-priority paper first** in the prompt and say so — if an agent dies partway, you
  keep the most important extraction.
- **Give each batch its own output file.** A failed batch then costs only itself.

---

## Stage 4 — Extraction prompt

Copy this, fill the four `«slots»`, and dispatch one agent per batch. This is the corrected version —
it already carries the fixes for every failure observed in the original run.

````text
Extract methodology content from software-engineering research papers to inform a reference
document on conducting systematic reviews.

Plain-text extractions are at:
«$SCRATCH»/txt/

READ IN FULL, in this priority order:
1. «highest_priority_paper».txt — «one line on why it matters»
2. «paper_2».txt
3. «paper_3».txt

Focus: «the theme this batch covers».

## WRITING STYLE — important
These are copyrighted papers. Write **your own synthesis in your own words**. Do NOT reproduce
long passages of source text.
- Paraphrase every rule, step, definition and warning into your own prose.
- Quote directly ONLY where the exact phrasing is load-bearing, and keep each quotation **under
  about 20 words**, in quotation marks, attributed.
- For enumerated criteria and checklists: give a **condensed paraphrase of each item** plus its
  number/label, so a reader knows what it covers and can look up the official wording.
- Formulas, counts, percentages and numeric results are facts — state those precisely and fully.
- Cite paper and section throughout.

## WRITE INCREMENTALLY
Write the file containing the first paper only, then use Edit to append each further paper.
Never attempt one large write.

## SCHEMA — for each paper
## <author_year> — <full title>
**Type:** (guideline / standard / experience report / empirical study / tertiary study / tool paper)
**Role in corpus:** one sentence on what only this paper contributes.
### Process steps or stages defined
Any named/numbered process, in your own words, preserving structure, order, and stated
inputs/outputs.
### Clarifications and refinements to earlier guidance
Where this paper CHANGES or refines earlier guidance, state the old position and the new one
explicitly.
### Caveats, traps and pitfalls
Every warning, trap, difficulty, or thing that went wrong — with the process step each attaches to.
### Checklists, rubrics, scoring schemes, evaluation criteria
Condensed paraphrase of each item with its number/label, plus any scoring anchors.
### Threats to validity framework
Named validity/threat categories and what each means.
### Data extraction and analysis techniques
Techniques for extracting, coding, aggregating, or analysing data; forms, fields, tools.
### Empirical findings worth citing
Numbers, rates, agreement statistics, effort figures — be precise and complete here.

## RULES
- Accuracy over brevity. A wrong attribution is worse than an omission.
- Distinguish each paper's OWN contribution from guidance it merely cites.
- If a paper contradicts another source, say so explicitly and summarise both positions.
- **Never invent.** If extraction is garbled or a table did not survive PDF conversion, write
  `[EXTRACTION UNCLEAR: <what>]`. If a figure is an image, say so. Do not reconstruct from memory.
- Label any count you derived yourself (e.g. by tallying an appendix) as *(derived)*.

OUTPUT: write to «docs/methodology/notes»/«topic-name».md
(Name the file by topic. Do not continue the historical `batchN` numbering.)

A PreToolUse "Fact-Forcing Gate" hook may block your Write. If so, reply with these four facts in
a message on their own, then retry the identical Write in the next message:
1. Nothing calls this file programmatically — it is a scratchpad notes artefact read back by the
   orchestrating agent when composing `docs/methodology/`.
2. No existing file serves this purpose (run `ls` on the notes directory to confirm).
3. It reads `txt/*.txt` and writes Markdown only; no structured data records; dates appear only as
   bibliographic years.
4. User instruction: "deeply review each document and construct a document with full step-by-step
   breakdowns for SLR, SMS, RR and Tertiary Studies, caveats and traps to avoid, reporting
   guidelines and checklists, threats to validity frameworks, and techniques for data extraction
   and analysis."

Your final message should be ONLY: the output file path and a one-line summary per paper. Do not
paste the notes.
````

### Failure modes seen in the original run, and what fixes them

| Symptom | Cause | Fix (already in the prompt above) |
| ------- | ----- | --------------------------------- |
| `Output blocked by content filtering policy` at the write step | Instructions demanded verbatim reproduction of long copyrighted passages | The **writing-style** block: synthesise, quote under ~20 words |
| Same error on large batches | Single oversized write | **Write incrementally**, 3–6 papers per batch |
| Agent completed but file has only the first paper | Died on an append | Priority-ordered reading, so the loss is the least important paper |
| `Fact-Forcing Gate` denial | Hook requires facts before first touch of a file | Facts in a message **on their own**, then the write in the *next* message. Facts and the write in the same message are denied |

Six of the original fifteen agents failed. **Check `ls $NOTES/` and count `^## ` headings
per file before assuming a batch succeeded** — a "completed" agent may still have written only part.

```bash
for f in "$NOTES"/*.md; do
  echo "$(basename "$f"): $(grep -c '^## ' "$f") papers, $(wc -l < "$f") lines"
done
```

---

## Stage 5 — Integrate

### Decide: extend a chapter, or create one?

| Situation | Action |
| --------- | ------ |
| The paper refines a process already documented | **Extend** the chapter. Add a `⚠ CAVEAT`, `⚙ IMPLEMENTATION`, or `◐ DISPUTED` block, or a row to an existing table |
| The paper *contradicts* a documented claim | **Add a `◐ DISPUTED` block** presenting both positions unresolved. Do not silently pick a winner |
| The paper supersedes a source (new edition, published amendment) | **Rewrite** the affected sections and add a note saying what changed |
| The paper opens a topic no chapter covers | **New chapter**, numbered after the current highest, and add it to the README Contents table |
| The paper is a worked example of a documented method | Extend with the example; worked numbers are the most reusable content |

### Composition prompt

````text
Compose/revise «docs/methodology/NN-name.md» from the extraction notes in
docs/methodology/notes/.

Read only the sections of the notes relevant to this chapter — grep the headings first rather than
reading whole files, which are large (the largest is ~150 KB). The notes/ README maps each file to
the papers it covers.

House style, matching the existing chapters:
- Header block naming the primary sources and what this supersedes
- Phases and steps numbered as the source numbers them
- Per step: what it is, what it consumes, what it produces, and how to do it
- `> **⚠ CAVEAT**` blocks for traps the sources explicitly warn about
- `> **⚙ IMPLEMENTATION**` blocks for what it means for the platform, naming the `feature-gaps.md`
  gap ID where one applies
- `> **◐ DISPUTED**` blocks where sources disagree — present both, resolve neither
- `> **⚠ CORRECTION**` blocks where a superseded repo document was wrong
- Tables for anything enumerable; bold the load-bearing clause in each row
- Cite `Author Year §section`

Rules:
- Synthesis, not reproduction. Short quotations only, where wording carries the point.
- Carry forward every `[EXTRACTION UNCLEAR: …]` marker as an explicit caveat in the chapter, and
  add it to the README's Reliability table. Never quietly drop one.
- Preserve numeric findings exactly.
- If this chapter contradicts another chapter, fix both or record the disagreement.
````

### After composing

1. **Update `README.md`** — Contents table, the Reliability table if new extraction limits appeared,
   the corpus manifest, and the headline findings if something displaces one.
2. **Update [the paper register](#the-paper-register)** in this file.
3. **Update `docs/feature-gaps.md`** if the research confirms, refutes or reframes a gap. The original
   run did exactly this for **G10** — PRISMA 2020 forbids its use as a quality instrument, so the
   planned checker had to be reframed as reporting completeness.

---

## Stage 6 — Verify

```bash
cd docs/methodology
# Every relative link resolves
for f in *.md; do
  grep -oE '\]\(\./[A-Za-z0-9._-]+\)' "$f" | sed 's/](\.\///; s/)//' | sort -u | while read -r t; do
    [ -f "$t" ] || echo "MISSING: $f -> $t"
  done
done

# Nothing was dropped
grep -rn "EXTRACTION UNCLEAR" . || echo "none carried forward — confirm that is correct"
```

**Completion checklist:**

- [ ] Every new paper appears in the register with the chapters it fed
- [ ] Every `[EXTRACTION UNCLEAR]` from the notes is either resolved against the PDF or recorded in
      the README Reliability table
- [ ] All relative links resolve
- [ ] README Contents table matches the files on disk
- [ ] Contradictions between chapters are resolved or recorded as `◐ DISPUTED`
- [ ] `feature-gaps.md` updated if a gap's premise changed
- [ ] **New notes committed to `docs/methodology/notes/`** and added to the file→papers table above

---

## Principles that made the original output trustworthy

These are the parts worth keeping even if the mechanics change.

1. **Never invent to fill a gap.** Every agent was told to write `[EXTRACTION UNCLEAR: …]` instead of
   guessing, and several did — including one that flagged its own reconstruction of a table as
   needing verification against the PDF before being quoted cell-by-cell.
2. **Record defects in the sources themselves.** Ampatzoglou duplicates two sub-threat labels;
   SEGRESS's prose contradicts its own table; Ribeiro has three internal inconsistencies. All are
   noted, none silently corrected.
3. **Preserve disagreement.** Snowballing noise, whether citing guidelines predicts quality, and
   whether grey literature belongs in a Rapid Review are all unresolved in the corpus and unresolved
   in the documents.
4. **Cross-check arithmetic where you can.** Ribeiro's effect-size formulas were verified by checking
   that the intensity numerators summed to the reported total.
5. **Distinguish a paper's own contribution from what it cites.** Much of this corpus quotes other
   guidelines; conflating the two produces false attributions.
6. **State what a source refuses to support.** One tool paper reports no accuracy figures at all, so
   no automation-accuracy claim may rest on it.

---

## The paper register

**55 unique papers, 55 files — one file per paper.**

> **⚠ CORRECTION, 2026-08-08 — the duplicate is gone, and the intake check that missed it is
> wrong.** This register previously recorded `brereton_lessons_2007.pdf` and
> `kitchenham_lessons_2007.pdf` as **byte-identical**. **The PDFs never were**: different MD5s
> (`5942133…` / `7f7a5e6…`), 302,812 vs 303,196 bytes, first difference at byte 38,887 — two
> downloads of one 13-page paper. What was genuinely byte-identical was their **`pdftotext` output**
> (`02de16e2…`), a true fact about the *text* recorded in `notes/batch1-slr-lessons.md` and
> transposed into a false one about the *PDFs*.
>
> **So the `md5sum * | uniq -d` step in [Stage 1](#stage-1--intake) cannot catch a duplicate like
> this, and did not.** Fixed there: dedupe on extracted text, then on title and page count.
>
> `kitchenham_lessons_2007.pdf` was **deleted 2026-08-08**; Brereton is first author and Kitchenham
> second, so the surviving filename is the correct one. `research/` is gitignored, so the deletion is
> not in version control.
>
> Second intake trap, still live: **`kitchenham_systematic_2010` has no `.pdf` extension**, so every
> `*.pdf` glob in this playbook silently skips it. Use `ls -A` or `find`, not `*.pdf`.

Legend for *Depth*: **F** = read in full · **T** = targeted sections · **V** = read as page images
(no text layer).

### Process definitions and standards

| Paper | Depth | Contributes | Chapters fed |
| ----- | :---: | ----------- | ------------ |
| `kitchenham_guidelines_2007` | F | The SLR process, EBSE-2007-01 v2.3 | 01, 06, 07, 08, 10, 11 |
| `kitchenham_systematic_2013` | F | **11 amendments to the 2007 guidelines**; quasi-gold standard | 01, 04, 06, 07, 11 |
| `petersen_systematic_2008` | F | SMS 5-step process, keywording, bubble plot, research-type facet | 02, 11 |
| `petersen_guidelines_2015` | F | Updated SMS guideline: 26-action checklist, 5 rubrics, decision rules | 02, 06, 07, 11 |
| `cartaxo_rapid_2020` | F | The Rapid Review process; Evidence Briefings | 03, 05, 08, 10, 11 |
| `kitchenham_systematic_2010` | F | The tertiary-study process; DARE anchors; consensus/minority-report protocol | 04, 06, 07, 10, 11 |
| `kitchenham_systematic_2009` | F | The first SE tertiary study; the template | 04 |
| `garousi_guidelines_2019` | F | MLR process; GL inclusion decision aid; 20-item GL quality checklist | 05, 09, 11 |
| `wohlin_guidelines_2014` | F | The snowballing procedure; start-set criteria; stopping rule | 06, 11 |
| `cruzes_recommended_2011` | F | Thematic synthesis, five steps; the code/theme funnel | 08, 11 |
| `ribeiro_using_2014` | F | Qualitative metasummary; both effect-size formulas | 08, 11 |
| `kitchenham_segress_2023` | F | **SEGRESS** reporting standard; per-review-type applicability | 10, 11 |
| `kitchenham_segress_2022` | F | Earlier SEGRESS; Table 9 identical to 2023 | 10 |
| `page_prisma_2021` | F | PRISMA 2020 checklist, abstract checklist, flow diagram | 10, 11 |
| `ampatzoglou_guidelines_2020` | F | Threats-to-validity framework: 22/34 threats, 60 mitigations | 09, 11 |
| `petersen_worldviews_2013` | F | Validity classification and its paradigm justification | 09 |
| `wieringa_requirements_2006` | F | The research-type facet, at source | 02 |
| `basili_goal_1994` | F | GQM, three-level model | 09 |
| `basili_software_1992` | **V** | GQM goal template (scanned; no text layer) | 09 |
| `petersen_identifying_2011` | F | Study-selection strategies and decision rules | 06 |
| `holst_transparent_2025` | F | **PRISMA-trAIce** — 17-item checklist for reporting AI used *as a tool* in a review; adapted flow diagram. **Proposal, not consensus** | 14, 10, 11, 12 |

### Evidence, lessons and critique

| Paper | Depth | Contributes | Chapters fed |
| ----- | :---: | ----------- | ------------ |
| `brereton_lessons_2007` | F | 10-stage/3-phase model; lessons L1–L19; transferability table. *(Was also filed as `kitchenham_lessons_2007`; that copy was deleted 2026-08-08)* | 01, 11 |
| `bailey_lessons_2007` | F | Search-engine non-overlap, quantified | 06, 11 |
| `staples_experiences_2007` | F | Complementary research questions; unit of analysis | 01, 11 |
| `dyba_applying_2007` | F | 11-item rigour/credibility/relevance checklist; κ = 0.80 | 06, 07 |
| `da_silva_six_2011` | F | Tertiary study over 120 SLRs; DARE trends | 04, 07, 12 |
| `badampudi_experiences_2015` | F | Snowballing 83% vs database 45.9%; 9 of 15 conclusions | 06, 11, 12 |
| `babar_systematic_2009` | F | Practitioner-sourced best practices; requested guideline improvements | 02 |
| `mourao_investigating_2017` | F | Hybrid search strategy; 100% / 81% recall bounds | 06 |
| `wohlin_reliability_2013` | F | Two maps sharing 33 of 44 papers; classification disagreement | 06, 11 |
| `wohlin_second-generation_2016` | F | Forward-only snowballing for review updates | 06, 12 |
| `cruzes_research_2011` | F | 13-method synthesis catalogue; the 49% / 20.4% audit | 08, 11, 12 |
| `marshall_tools_2013` | F | **Zero tool support** for need-identification, protocol, quality | 12 |
| `marshall_tools_2014` | F | DESMET feature analysis; best tool at 65.4% | 12 |
| `mendez_open_2020` | F | Open-science disclosure; preregistration; licence traps; DOI archival | 13 |
| `zhang_evidence-based_2020` | F | **Grey-literature use**, not general EBSE: 102 reviews, 90% no GL appraisal | 05, 12 |
| `fatima_retrieving_2023` | F | Preprint scraping; **reports no accuracy figures** | 05 |
| `stol_grounded_2016` | F | Grounded-theory variants; **method slurring** and its disqualifying test | 08, 11 |

### Grey literature and practitioner evidence

| Paper | Depth | Contributes | Chapters fed |
| ----- | :---: | ----------- | ------------ |
| `garousi_need_2016` | F | Cost of excluding GL: 219 vs 67 factor instances | 05 |
| `garousi_benefitting_2020` | F | GL as a research data source; five usage modes | 05 |
| `adams_shades_2017` | F | Outlet-control × source-expertise tier model | 05, 11 |
| `neto_multivocal_2019` | F | Tertiary study of 12 MLRs; all lacked GL-specific appraisal | 05 |
| `lopez_multivocal_2026` | F | Preprints as a distinct GL class; `site:` proxy search | 05 |
| `kamei_grey_2021` | F | Link rot: 24.8% no URL, 23.7% dead | 05, 11, 12 |
| `gul_grey_2021` | F | GL definitions and classification | 05 |
| `schopfel_how_2021` | F | GL defined by negation; 52 retrieved → 4 used | 05 |
| `yasin_using_2020` | F | Three GL indicators; Google Scholar's 96% recall failing on GL | 05, 11 |
| `rainer_using_2017` | F | Schum's evidential test per claim; argumentation schemes | 05 |
| `rainer_using_2019` | F | 10-feature blog definition; six objects of assessment | 05 |
| `rainer_heuristics_2019` | F | Quality criteria as search keywords | 05 |
| `williams_towards_2017` | F | 11 candidate blog-credibility criteria → 4 operational | 05, 10 |
| `williams_using_2018` | F | **86 reasoning markers**; GL URL coding frame | 05, 10 |
| `williams_how_2019` | F | 9 credibility criteria empirically ranked (n = 43) | 05, 10 |
| `kitchenham_how_2023` | F | Luxembourg/Prague definitions; 7 recommendations; link rot | 05, 11 |
| `wyrich_software_2026` | F | Podcasts as a research resource; inductive scheme replacement | 05 |

### Known under-used material

Extracted but not yet fully worked into a chapter. Cheap wins for the next pass:

| Paper | What is unused | Suggested home |
| ----- | -------------- | -------------- |
| ~~`mendez_open_2020`~~ | ~~Six openness facets; preregistration; licence traps; DOI archival~~ | ✅ **Worked into [13 — Open science](./13-open-science.md)** 2026-08-07 |
| ~~`stol_grounded_2016`~~ | ~~Method slurring and its disqualifying test~~ | ✅ **Worked into [08 Part 4b](./08-extraction-and-synthesis.md) and [11](./11-caveats-register.md)** 2026-08-07. *Still unused: the three GT variants' coding procedures and the eleven core practices, which would only matter if the platform ever supports grounded theory as a primary method* |
| `basili_software_1992` | QIP and the Experience Factory; defect-slippage interpretation | 09, if GQM is expanded |
| `garousi_benefitting_2020` | The process model of *how GL is authored*, locating validity threats in the author's invisible internal processes | 05 |
