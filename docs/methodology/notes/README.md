# Extraction notes

**Intermediate artefacts.** These are the structured per-paper extractions that
[`docs/methodology/`](../) was composed from — 14 files, ~203,000 words, covering all 54 papers in
`research/`.

They are **denser than the chapters and closer to the sources**, and deliberately hold material the
chapters did not need: full mitigation lists, complete rubric anchors, per-paper empirical tables,
and every `[EXTRACTION UNCLEAR]` marker raised during extraction.

## Why they are committed

A chapter rewrite that starts from these notes costs a fraction of one that starts from the PDFs.
**Consult them before re-reading a paper.**

## What is authoritative

The **chapters** are the deliverable. These notes are working material: they were written by several
different extraction agents, their style varies, and some contain flagged uncertainties that the
chapters resolved or recorded. Where a note and a chapter disagree, **check the source PDF** — do not
assume either is right.

## Which file holds which papers

See the file→papers table in [`../PLAYBOOK.md`](../PLAYBOOK.md#where-the-notes-live). The `batchN`
filenames are **historical**, recording which agent produced which file during the original run; the
numbering has gaps because failed batches were re-dispatched split in two. Use the table, not the
filenames.

Two notes on coverage:

- `batch9b-selection-classification.md` covers **one paper only** — that agent died partway, and its
  other two papers were re-extracted into `batch10-remaining.md`.
- `kitchenham_guidelines_2007.md` and the Petersen 2008 section of `corpus-notes.md` were written by
  the orchestrating agent rather than a subagent, so they are longer and quote more heavily.

## Schema

Each paper appears under a `## <author_year> — <title>` heading with these subsections, omitted where
the paper has nothing for them:

`Type` · `Role in corpus` · `Process steps or stages defined` · `Clarifications and refinements to
earlier guidance` · `Caveats, traps and pitfalls` · `Checklists, rubrics, scoring schemes,
evaluation criteria` · `Threats to validity framework` · `Data extraction and analysis techniques` ·
`Empirical findings worth citing`

New extractions should follow the same schema — the prompt that generates it is in
[`../PLAYBOOK.md`](../PLAYBOOK.md#stage-4--extraction-prompt) — and should be **named by topic**
rather than continuing the batch numbering.
