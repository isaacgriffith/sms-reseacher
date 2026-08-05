# Feature Gap Analysis

**Assessed**: 2026-08-05
**Last updated**: 2026-08-05 — G13d resolved; G7 SMS-protocol claim corrected; G14 added (MLR modelled as a flag on `Study`)
**Baseline**: `docs/base-features.md` (27 features, F1-SF01 – F3-SF04)
**Evidence**: working tree of branch `011-improve-testing-and-fix-ci` (301 modified files uncommitted; base commit `32aeffb`)
**Method**: traced each feature to implementing code — ORM models, API routes, services, agents, source adapters, and UI components — not to `specs/` intent

---

## Legend

| Symbol | Meaning                                                            |
| ------ | ------------------------------------------------------------------ |
| ●      | Implemented — satisfies the requirement as written                 |
| ◐      | Partial — core exists, one or more stated sub-requirements missing |
| ✗      | Missing — no implementing code found                               |

---

## Summary

| ID       | Feature                  | Status | Headline gap                                              |
| -------- | ------------------------ | ------ | --------------------------------------------------------- |
| F1-SF01  | Simple install/setup     | ◐      | Compose path works; manual path is 5 steps across 2 stacks |
| F1-SF02  | Installation guide       | ◐      | README Quick Start only; no standalone guide               |
| F1-SF03  | Tutorial                 | ✗      | None                                                       |
| F1-SF04  | Self-contained           | ◐      | Requires 8 external API keys + an LLM provider             |
| F2-SF01  | Protocol development     | ●      | Guideline grounding is thin (see G7)                       |
| F2-SF02  | Protocol validation      | ◐      | AI review is SLR-only                                      |
| F2-SF03  | Automated searches       | ◐      | G1, G2, G3, G13 — the largest cluster                      |
| F2-SF04  | Study selection          | ◐      | G4, G5                                                     |
| F2-SF05  | Quality assessment       | ◐      | G6 — no Study entity distinct from Paper                   |
| F2-SF06  | Data extraction          | ●      | —                                                          |
| F2-SF07  | Automated analysis       | ●      | —                                                          |
| F2-SF08  | Text analysis            | ●      | —                                                          |
| F2-SF09  | Meta-analysis            | ◐      | G8 — no metasummary; thematic synthesis is not Cruzes/Dybå |
| F2-SF10  | Report write-up          | ◐      | G9 — no Typst backend; G14 — no PRISMA 2020 flow diagram   |
| F2-SF11  | Report validation        | ✗      | G10 — no PRISMA/SEGRESS/trAIce checker; G14                |
| F3-SF01  | Multiple users           | ◐      | G11 — role model mismatch, no user CRUD                    |
| F3-SF02  | Document management      | ◐      | G12 — no manual fallback, no on-disk store, no viewer      |
| F3-SF03  | Security                 | ●      | Capability matrix is coarse (see G11)                      |
| F3-SF04  | Multiple projects        | ●      | —                                                          |

---

## Gaps

### G1 — Snowball provenance DAG (F2-SF03) — **blocking, structural**

**Required.** Maintain traceability links for papers found via snowballing. If a previously included paper is later excluded, papers discovered *from* it must be excluded too — unless they were also reachable from another still-included paper. This implies a DAG.

**Current.** `run_snowball` (`backend/src/backend/jobs/search_job.py:693`) performs iterative bidirectional snowballing with a stopping threshold, dedup, and AI pre-screening against inclusion/exclusion criteria. Discovery works. But `CandidatePaper` (`db/src/db/models/candidate.py:29`) carries only `duplicate_of_id` and `source_seed_import_id` — **there is no edge recording which paper a candidate was discovered from**. `_process_snowball_batch` (`search_job.py:590`) never writes one.

**Consequence.** Retraction cascade is impossible. Excluding an included paper silently orphans its descendants, and there is no way to distinguish a descendant with a second surviving parent from one without.

**Remediation sketch.**
- New table `candidate_discovery_edge` — `(child_candidate_paper_id, parent_candidate_paper_id, direction, search_execution_id)`, self-referential many-to-many on `CandidatePaper`.
- Write an edge per accepted candidate inside `_process_snowball_batch`.
- Retraction pass on exclusion: transitive closure from the excluded node, retaining any descendant that remains reachable from an included root.
- Cycle guard — citation graphs are not acyclic in practice (preprint ↔ published pairs, errata).

**Cost.** High. Touches the screening write path and requires a migration plus a backfill decision for existing snowball results.

---

### G2 — Per-database query optimization (F2-SF03) — **high**

**Required.** Take one Boolean search string and *optimize it for each database search engine* before executing.

**Current.** `DatabaseSource.search()` accepts a single `query: str` and every adapter forwards it verbatim — e.g. `researcher-mcp/src/researcher_mcp/sources/ieee.py:144` maps it straight to `"querytext"`. No translation layer exists anywhere in `researcher-mcp/` or `backend/`. The `search_builder` agent prompt mentions truncation wildcards generically but emits one string for all engines.

**Consequence.** Field qualifiers, nesting depth limits, wildcard characters, and proximity operators differ per engine. A string tuned for one database silently under- or over-retrieves in the others, which undermines the recall claims the search-string test-retest tooling is meant to establish.

**Remediation sketch.** Parse the Boolean string into an AST once, then add a `translate(ast) -> str` method to the `DatabaseSource` protocol. Per-engine emitters: Scopus `TITLE-ABS-KEY()`, WoS `TS=`, IEEE field codes, ACM `Abstract:()`, ScienceDirect's operator subset, and a flattened form for Google Scholar (no nesting, 256-char cap).

**Cost.** Medium. Additive — the protocol gains a method with a pass-through default.

---

### G3 — Missing search modalities (F2-SF03) — **medium**

| Requirement       | State | Detail                                                                                      |
| ----------------- | ----- | ------------------------------------------------------------------------------------------- |
| Google Scholar    | ●     | `sources/google_scholar.py`                                                                  |
| arXiv             | ●     | `sources/arxiv.py`                                                                           |
| IEEE Xplore       | ●     | `sources/ieee.py`                                                                            |
| ACM DL            | ●     | `sources/acm.py`                                                                             |
| Scopus            | ●     | `sources/scopus.py`                                                                          |
| **EI Compendex**  | ✗     | No adapter                                                                                   |
| ScienceDirect     | ●     | `sources/science_direct.py`                                                                  |
| Web of Science    | ●     | `sources/wos.py`                                                                             |
| **Manual search** | ✗     | No code path for author/journal/conference-driven search and venue-site resolution           |

Beyond the required eight, adapters also exist for Inspec, Springer, Semantic Scholar, Crossref, OpenAlex, Unpaywall, and Sci-Hub.

**Remediation.** EI Compendex is a straightforward adapter (Engineering Village API). Manual search is a new subsystem: venue → website resolution, then site-specific listing traversal, feeding the same `CandidatePaper` upsert path.

---

### G4 — Intra-rater test-retest (F2-SF04) — **high**

**Required.** When a study is screened by a single human or single agent, re-evaluate a random sample of already-decided papers and compute intra-rater agreement via Cohen's κ.

**Current.** Every occurrence of "test-retest" in the codebase refers to **search-string recall validation**, a different concept — `backend/src/backend/api/v1/search_strings.py:28`, `backend/src/backend/jobs/quality_job.py:126`, `backend/src/backend/jobs/validity_job.py:128`, `frontend/src/components/phase2/TestRetest.tsx`. `AgreementRoundType` (`db/src/db/models/slr.py:73`) is `{title_abstract, intro_conclusions, full_text, quality_assessment}` — all **inter**-rater rounds, and `InterRaterAgreementRecord` requires two distinct `reviewer_a_id` / `reviewer_b_id`.

**Consequence.** Single-reviewer studies — which the Rapid Review workflow explicitly supports, warning banner and all — have no reliability evidence at all.

**Remediation sketch.** Add an intra-rater round type and allow `reviewer_a_id == reviewer_b_id` when it is set. Add a resample job: draw *n* decided candidates, blank the decision for a second pass, then score the two passes with the existing `inter_rater_service` κ computation.

**Cost.** Medium-low — the κ machinery and storage already exist; this is a sampling job plus an enum value plus relaxing one constraint.

---

### G5 — Selection decision rules (F2-SF04) — **high**

**Required.** A defined, extensible set of decision rules governing include/exclude, applied when reviewers disagree (per Petersen & Bin Ali, 2011).

**Current.** No such concept. The only "decision rules" in the tree are the **R1–R6 research-type classification** rules in `agents/src/agents/prompts/extractor/system.md:5` and `db/src/db/models/extraction.py:24` — these classify a paper's research type, they do not govern selection. Disagreement handling exists mechanically (`CandidatePaper.conflict_flag`, `PaperDecision.is_override` / `overrides_decision_id`, `frontend/src/components/slr/DiscussionFlowPanel.tsx`) but resolution is entirely manual with no encoded policy.

**Remediation sketch.** `SelectionDecisionRule` table with a seeded catalog from Petersen & Bin Ali (e.g. *inclusive-if-either*, *exclusive-if-either*, *third-reviewer-adjudicates*, *discuss-to-consensus*), bound to the protocol, plus an evaluator invoked when `conflict_flag` is set. Extensibility via user-defined rules on the same table.

---

### G6 — Study is not modeled separately from Paper (F2-SF05) — **high, structural**

**Required.** A paper may report multiple studies; a study may span multiple papers. Quality assessment applies to the *study*.

**Current.** `QualityAssessmentScore` (`db/src/db/models/slr.py:251`) is keyed to `candidate_paper_id`. There is no entity for an empirical study distinct from a bibliographic record. `DataExtraction` (`db/src/db/models/extraction.py:56`) is likewise paper-keyed.

**Consequence.** Multi-study papers cannot be scored per study; multi-paper studies are double-counted in synthesis and in every report's counts. This also biases meta-analysis, where the unit of pooling should be the study.

**Remediation sketch.** Introduce `EmpiricalStudy` with an N:M join to `CandidatePaper`, then re-key `QualityAssessmentScore` and the synthesis input set to it. Default 1:1 materialization on inclusion preserves current behaviour and keeps the migration mechanical.

**Cost.** High. Touches quality scoring, extraction, synthesis strategies, and all four report services.

---

### G7 — Guideline grounding (F2-SF01) — **medium**

The protocol subsystem itself is strong: `db/src/db/models/protocols.py` (23 task types, quality gates, typed I/O, conditional edges), `ReviewProtocol` with full PICO/S, RR and Tertiary protocols, four seeded templates, YAML round-trip. What is thin is the *citation grounding* the baseline calls for:

| Guideline set                                   | State                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------ |
| Kitchenham et al. 2007 (SLR)                    | Referenced in `agents/.../protocol_reviewer/system.md:4`            |
| PRISMA 2020                                     | Named in the same prompt line only — no structural encoding         |
| SEGRESS (Kitchenham 2023)                       | ✗ zero occurrences                                                  |
| PRISMA-trAIce (Holst 2025)                      | ✗ zero occurrences                                                  |
| Petersen 2008 / 2015 (SMS)                      | Not cited (see the SMS note below)                                  |
| Ampatzoglou 2020 / Petersen & Gencel 2013 (ToV) | Threats-to-validity model exists for **Rapid Review only**          |
| Grey literature (Garousi, Rainer, Yasin)        | `GreyLiteratureSource` model exists; heuristics not encoded         |

**SMS protocol — by design, not a gap.** SMS deliberately shares the SLR protocol model rather than having a dedicated one: an SMS protocol follows the SLR protocol, minus the quality-evaluation definition. The code supports this — `ReviewProtocol` (`db/src/db/models/slr.py:100`) is keyed only on `study_id`, and neither `slr_protocol_service` nor the `/api/v1/slr/studies/{id}/protocol` endpoints gate on `StudyType`, so an SMS study can hold a full protocol today.

What *is* missing is the deliberate omission: the quality-assessment models (`QualityAssessmentChecklist` / `Item` / `Score`) are equally ungated, so nothing marks quality evaluation as out of scope for SMS, and nothing steers an SMS author away from defining one. The gap is an absent study-type policy, not an absent model.

**SEGRESS, PRISMA 2020, and PRISMA-trAIce apply to SMS as well as SLR** — the ✗ rows above are unmet for every study type, not for SLR alone.

---

### G8 — Qualitative synthesis (F2-SF09) — **high**

**Required.** Qualitative Metasummary (Ribeiro et al. 2014) and Thematic Synthesis (Cruzes & Dybå 2011).

**Current.**
- **Statistical meta-analysis is genuinely built** — `MetaAnalysisSynthesizer` (`backend/src/backend/services/synthesis_strategies.py:93`) with pooled effects, sensitivity analysis, and Forest/Funnel SVG output.
- **Qualitative Metasummary: absent.** Zero occurrences of "metasummary". No frequency effect sizes, no intensity effect sizes.
- **Thematic Synthesis: not per the method.** `ThematicAnalysisStrategy` (`synthesis_strategies.py:472`) is a single LLM call requesting 3–7 themes as a JSON theme→index map, with a `{"raw": ...}` fallback on parse failure. That is thematic *clustering*. Cruzes & Dybå specify five steps — extract data, code data, translate codes into themes, create a model of higher-order themes, assess trustworthiness — of which only an implicit collapse of steps 2–3 is present. Nothing is auditable at the code level, and there is no trustworthiness assessment.

**Remediation sketch.** Persist codes as first-class rows (`ExtractionCode`) so step 2 is inspectable and reviewable; add a code→theme mapping table for step 3; a higher-order theme parent link for step 4; and a trustworthiness record for step 5. Metasummary is largely arithmetic once codes are persisted — frequency effect size = proportion of studies carrying a finding; intensity = proportion of findings present per study.

---

### G9 — Typst report backend (F2-SF10) — **low**

`SLRReportService` exports Markdown, LaTeX, JSON, and CSV (`backend/src/backend/services/slr_report_service.py:206`); Tertiary exports JSON/CSV/Markdown; Rapid Review produces HTML + PDF via WeasyPrint. **Typst has zero occurrences.** Additive — a new branch in `export_report` alongside the existing LaTeX emitter.

---

### G10 — Report validation (F2-SF11) — **medium, low-risk**

**Required.** Verify generated reports conform to PRISMA 2020, PRISMA-trAIce, and SEGRESS.

**Current.** Nothing. "SEGRESS" and "trAIce" do not appear in the codebase; "PRISMA" appears twice, both as prose inside the protocol-reviewer agent prompt.

**Remediation sketch.** These are checklists, and `generate_report` already returns a structured `SLRReport`. A validator is a pure function over that structure — per-item `{satisfied, evidence_section, remediation}` — with no schema change required. **This is the highest value-per-unit-risk item in this document.**

---

### G11 — Role model and user management (F3-SF01, F3-SF03) — **high**

**Required.** Three roles — superuser (adds/removes users, nothing else), project manager (creates studies, owns them, assigns members), reviewer (participates, reviews protocol and papers, sees results).

**Current.** Two orthogonal two-value enums, neither matching:
- `GroupRole = {admin, member}` (`db/src/db/models/users.py:22`)
- `StudyMemberRole = {lead, member}` (`db/src/db/models/study.py:23`)
- `ReviewerType = {human, ai_agent}` (`db/src/db/models/study.py:30`)

`User` has **no superuser flag**. More significantly, **there is no user-creation or deletion endpoint anywhere in the API**: `auth.py` exposes only `/login`, `/login/totp`, `/me`; `admin.py` exposes `/health`, `/jobs`, `/jobs/{id}/retry`; `groups.py` can add a member only by an already-existing `user_id`. There is no registration path either — users must be inserted out-of-band.

Authorization itself is coarse: `require_study_member` (`backend/src/backend/core/auth.py:227`) is the only study-scoped guard, so the PM/reviewer capability split is not enforced.

**Remediation sketch.** Add `is_superuser` to `User`; add `POST /admin/users` and `DELETE /admin/users/{id}` behind a superuser guard; introduce a capability matrix mapping (role × action) and replace bare `require_study_member` calls at endpoints that should be PM-only.

**Note.** The rest of F3-SF03 is solid — JWT with `token_version` invalidation, TOTP 2FA with bcrypt-hashed backup codes, Fernet encryption at rest, and a security audit log.

---

### G12 — Document management (F3-SF02) — **medium**

| Requirement                       | State | Detail                                                                                          |
| --------------------------------- | ----- | ----------------------------------------------------------------------------------------------- |
| Auto-retrieve correct version     | ●     | `fetch_paper_pdf` — Unpaywall OA, then gated Sci-Hub                                             |
| Flag for manual download          | ✗     | No flag, no state, no queue                                                                      |
| Manual upload path                | ✗     | None                                                                                             |
| Manage documents on disk          | ✗     | Full text is a DB text column (`Paper.full_text_markdown`); only `pdf_path` is on the RR briefing |
| Allow users to view the paper     | ◐     | `GET /papers/{id}/markdown` exists; **no frontend consumer** — backend-only                      |

**Remediation sketch.** Add a `retrieval_status` enum to `Paper` with a `manual_required` state set on retrieval failure, an upload endpoint writing to a configured object/file store, and a reader view in the frontend that consumes the existing markdown endpoint.

---

### G13 — Search-string piloting loop is open at both ends (F2-SF03, F2-SF01) — **high** *(13d resolved 2026-08-05)*

**Required.** When database search is the chosen protocol strategy, the tool must:

1. Generate a search string from the **research goal, research questions, and a set of seed papers**;
2. **Refine it iteratively** by running it — converging on a string that recovers the seed papers *and* yields a minimal set suitable for later snowball sampling;
3. **Pilot it across multiple databases and see the per-database results.**

**Current.** The data model is already the right shape and the recall check genuinely works — `SearchString` is versioned with a single `is_active` (`db/src/db/models/search.py:21`), `SearchStringIteration` records `result_set_count` / `test_set_recall` / `ai_adequacy_judgment` / `human_approved` (`search.py:51`), and `run_test_search` (`backend/src/backend/jobs/search_job.py:21`) computes `recall = |seed_dois ∩ result_dois| / |seed_dois|`. What is missing is the wiring at each end.

#### 13a — Seed papers do not inform generation

`SearchStringBuilderAgent.run()` **already declares** `seed_keywords: list[str] | None` (`agents/src/agents/services/search_builder.py:63`) and threads it into the Jinja template context. But `POST /studies/{id}/search-strings/generate` (`backend/src/backend/api/v1/search_strings.py:180`) **omits the argument entirely** and never queries `SeedPaper`. The parameter is always empty.

Seed papers therefore serve only as the recall test set — they contribute nothing to the string being tested. A wiring gap, not a missing capability.

Secondary: research goal and RQs are read from the untyped `study.metadata_` JSON blob (`meta["research_objectives"]`, `meta["research_questions"]`), while SLR/RR/Tertiary studies hold RQs in typed protocol columns (`ReviewProtocol.research_questions`). The two can silently diverge.

#### 13b — The refinement loop never closes, and minimality is unmeasured

- **No feedback-driven regeneration.** Nothing consumes iteration *N* to produce version *N+1*. Re-calling `/generate` re-runs the agent with identical inputs; it never learns which seeds were missed. Refinement is manual hand-editing in `SearchStringEditor.tsx`.
- **Minimality is never measured.** Only `result_set_count` is stored — no precision, no F-measure, no objective function trading recall against set size. The stated goal (*a minimal set adequate for later snowballing*) cannot be evaluated, let alone optimised. Recall alone is trivially maximised by an over-broad string, which is the wrong end of the tradeoff for the step that feeds G1.
- **`ai_adequacy_judgment` is never written by the test job.** It is set once at generation time to the agent's `expansion_notes` and never updated, so no AI ever judges the adequacy of an *actual* pilot run.

#### 13c — Piloting is single-aggregate, not per-database

`_fetch_test_search_results` (`search_job.py:~130`) issues one call to researcher-mcp `search_papers` and merges everything into one DOI set plus one integer.

- **No per-database breakdown** — you cannot see which database found which seeds, which contributed unique hits, or which returned nothing. This is exactly the "pilot across multiple databases and see the results" requirement, and it is not answerable from the stored data.
- **Databases are not persisted on the iteration.** `databases` is a job argument only; `SearchStringIteration` has no column for it, so pilots are neither reproducible nor comparable across runs.
- **`StudyDatabaseSelection` is ignored** — the default is hardcoded `["acm", "ieee", "scopus"]`, and the UI passes a free-text comma-separated field (`frontend/src/components/phase2/TestRetest.tsx:38`).
- **`max_results: 100`** truncates the result set, so a seed ranked 101st counts as a miss and recall is silently understated.

#### 13d — Two defects in `_fetch_test_search_results` — ✅ **RESOLVED 2026-08-05**

The original code was:

```python
if not resp.status_code > 200:      # defect 1
    ...
    return dois, len(papers)
...
return set(), 2                     # defect 2
```

1. **Inverted status guard.** `not status_code > 200` treated *only* `≤ 200` as success — a `201`/`202`/`204` fell through to the failure path.
2. **Silent failure with a magic number.** An unreachable or non-200 MCP response returned `set(), 2`, writing an iteration with `recall = 0.0` and `result_set_count = 2` — **indistinguishable from a genuinely bad search string**. A researcher would see "0% recall, 2 results" and rewrite a perfectly good query while the actual fault was a down service. The `except` branch logged a warning, which made it worse: the log said *unavailable* while the database recorded a plausible-looking result.

**Both confirmed by execution and fixed.** Verification showed a `201` response yielding an empty DOI set, and neither the exception path nor a `500` raising. Notably the defect was *enshrined in the suite* — `test_fetch_test_search_results_returns_empty_on_exception` asserted `count == 2` and passed, so the function was covered and the coverage was worthless.

Changes in `backend/src/backend/jobs/search_job.py`:

- Added `TestSearchUnavailableError(RuntimeError)` plus named constants `_HTTP_OK` / `_HTTP_MULTIPLE_CHOICES`.
- Narrowed the `try` to wrap only the HTTP call, so a malformed-but-200 payload also raises instead of being swallowed.
- Replaced the guard with an explicit `_HTTP_OK <= status < _HTTP_MULTIPLE_CHOICES` range check; all 2xx parse, all non-2xx raise with the status logged.
- Removed `return set(), 2`.

A service failure now propagates through `run_test_search`'s existing handler — the `BackgroundJob` is marked `FAILED` with an `error_message` and **no `SearchStringIteration` is written at all**. In `backend/tests/unit/test_search_job_helpers.py`, the test encoding the defect was replaced with three pinning the correct contract (raises on transport failure, raises on `500`, parses `201`).

Verified: 1096 backend tests pass (up from 1094), coverage 86.10%, `ruff check backend/src` and `mypy backend/src` both clean.

**13a–13c remain open.**

**Interaction with G2.** Because one identical string is sent to every engine, adding a per-database breakdown *before* fixing per-engine query translation would measure syntax mismatch as much as query quality — producing misleading per-database recall figures. G2 and 13c should land together.

**Remediation sketch.**

| Step | Change                                                                                                | Size               |
| ---- | ----------------------------------------------------------------------------------------------------- | ------------------ |
| ~~1~~ | ~~Fix the status guard; fail the iteration explicitly instead of `return set(), 2`~~                  | ✅ Done 2026-08-05  |
| 2    | Pass seed-derived keywords into `agent.run(seed_keywords=...)`                                          | Small              |
| 3    | Add `databases_used`, `per_database_counts` (JSON), `precision`, `missed_seed_dois` (JSON) to `SearchStringIteration` | Small + migration  |
| 4    | Return per-source results from `search_papers` rather than a merged list                                | Medium             |
| 5    | Refine endpoint feeding `missed_seed_dois` + result count back to the agent to emit version *N+1*       | Medium             |
| 6    | Define the stopping rule (recall ≥ target **and** result set ≤ ceiling) and expose it as protocol config | Medium             |
| 7    | Source the database list from `StudyDatabaseSelection` instead of the hardcoded default and free-text field | Small          |

**Cost.** Medium overall, but step 1 is a few lines and should not wait — it currently corrupts pilot data silently.

---

### G14 — PRISMA 2020 flow diagram generation (F2-SF10, F2-SF11) — **medium**

**Required.** Reports must include a **PRISMA 2020 flow diagram in SVG**, laid out as specified in the PRISMA 2020 guidance. When the review is an **MLR** (an SLR or SMS incorporating grey literature), the corresponding MLR base flow must be used instead of the standard one.

**Current.** Absent. Zero occurrences of `flow_diagram`, `flowchart`, `prisma_flow`, `MLR`, or `multivocal` across `backend/src`, `db/src`, `agents/src`, and `frontend/src`. No report service emits a flow diagram in any format.

Two supporting pieces do exist:

- **SVG generation is an established pattern.** `backend/src/backend/services/visualization.py` already emits SVG from matplotlib (`fig.savefig(buf, format="svg")` — bar chart, frequency infographic, Forest, Funnel) and from plotly (`fig.to_image(format="svg")` — bubble chart). A PRISMA renderer belongs alongside these.
- **The counts are largely derivable.** `CandidatePaper.current_status`, `duplicate_of_id`, `PaperDecision`, and `SearchExecution` between them carry identification, deduplication, screening, and inclusion tallies.

Three things block it:

1. **No MLR concept.** `StudyType` is `{SMS, SLR, TERTIARY, RAPID}` and nothing marks a review as incorporating grey literature. `GreyLiteratureSource` records *sources* but does not classify the review, so the system cannot select between the standard and MLR base flows.

   **Decision (2026-08-05): MLR is a flag on `Study`, not a fifth `StudyType`.** An MLR is an SLR or SMS that incorporates grey literature — the review type is unchanged, so grey-literature inclusion is orthogonal to it and composes with either. Modelling it as a study type would force `MLR-SMS` / `MLR-SLR` enum members (or lose the distinction), duplicate both phase gates, and split the protocol and report paths that SMS and SLR already share. A boolean keeps one code path per review type and reduces base-flow selection to a single branch at render time.
2. **Grey-literature counts are not tracked through the screening funnel.** The PRISMA 2020 MLR variant needs its grey-literature arm counted separately at each stage; `CandidatePaper` has no provenance field distinguishing a grey-literature record from a database record.
3. **"Reports excluded, with reasons" is not aggregated.** `PaperDecision.reasons` is a JSON list per decision, but nothing rolls it up into the per-reason exclusion counts the diagram's full-text box requires.

**Remediation sketch.**

| Step | Change                                                                                                     | Size              |
| ---- | ---------------------------------------------------------------------------------------------------------- | ----------------- |
| 1    | Add `Study.includes_grey_literature: bool` (default `False`); `is_mlr` is that flag AND `study_type in {SMS, SLR}`. Drives base-flow selection | Small + migration |
| 2    | Add a provenance discriminator on `CandidatePaper` so the grey-literature arm can be counted separately      | Small + migration |
| 3    | `PrismaFlowService` — assemble stage counts from `CandidatePaper` / `PaperDecision` / `SearchExecution`       | Medium            |
| 4    | Aggregate `PaperDecision.reasons` into per-reason full-text exclusion counts                                 | Small             |
| 5    | SVG renderer in `visualization.py` for both base flows, matching PRISMA 2020 box layout and arrow structure  | Medium            |
| 6    | Embed in the SLR/SMS report exporters (Markdown, LaTeX, and the eventual Typst backend of G9)                | Small             |

**Interaction.** Shares its counting layer with **G10** (a PRISMA 2020 checker needs the same stage tallies) and with **G1** — snowball-discovered records occupy their own PRISMA 2020 arm ("records identified from other methods"), which cannot be reported accurately without the provenance edges G1 introduces. Step 2 here and G1's `candidate_discovery_edge` should be designed together.

---

## Recommended sequence

| Order | Item                                   | Rationale                                                                                     |
| ----- | -------------------------------------- | --------------------------------------------------------------------------------------------- |
| ~~0~~ | ~~**G13d** two defects in `_fetch_test_search_results`~~ | ✅ **Done 2026-08-05** — was writing fabricated pilot data on service failure |
| 1     | **G10** report validation              | Greenfield, no schema change, operates on an existing structured object                        |
| 2     | **G1** + **G14** steps 1–2 provenance  | Design together — the PRISMA "other methods" arm and the snowball DAG need the same discriminator |
| 2b    | **G14** steps 3–6 flow diagram         | Follows the provenance work; reuses `visualization.py`'s existing SVG pattern                  |
| 3     | **G6** Study/Paper split               | Every downstream count and pooled estimate depends on the unit of analysis being right         |
| 4     | **G11** roles + user CRUD              | The system currently cannot onboard a user through its own API                                 |
| 5     | **G4**, **G5** reliability + rules     | Both reuse the existing κ and decision machinery                                               |
| 6     | **G2** + **G13** search fidelity + piloting | Land together — a per-database breakdown is misleading until query translation exists     |
| 7     | **G3** remaining search modalities     | EI Compendex adapter and manual search; independent of the above                               |
| 8     | **G8** qualitative synthesis           | Large, but unblocked once G6 lands                                                             |
| 9     | **G7**, **G9**, **G12**, F1 docs       | Additive, low coupling                                                                         |

---

## Observed pattern

Features that are *stateful workflow* — protocols, phase gates, screening, extraction, membership — are well built out. Features that require a **richer relational shape** — a provenance DAG (G1), a Study entity distinct from Paper (G6), an intra-rater round (G4) — are the ones that got flattened.

That is the predictable consequence of shipping ten features as sequential additive migrations `0014`–`0018`: changing the *shape* of `CandidatePaper`, or splitting `Paper` from `Study`, would have forced backfills across every previously completed workflow. The remaining structural gaps are cheap to describe and expensive to add for exactly that reason — and they get more expensive with every study the platform runs.

A second, cheaper pattern sits alongside it: **capabilities built but not connected**. G13a is the clearest case — the agent declares `seed_keywords`, the template renders it, the seed records exist, and the endpoint simply never passes the argument. G12's paper viewer is the same shape (endpoint with no frontend consumer), as is `ai_adequacy_judgment` (column written once, never updated). These cost little to close and are worth sweeping for beyond the instances catalogued here.
