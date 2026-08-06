# Feature Gap Analysis

**Assessed**: 2026-08-05
**Last updated**: 2026-08-06 — G16–G21 added. A systematic reachability sweep found **23 frontend modules unreachable from `main.tsx`**, including the entire Tertiary Studies frontend. See [Built-but-never-wired audit](#built-but-never-wired-audit).
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

| ID      | Feature              | Status | Headline gap                                                                |
| ------- | -------------------- | ------ | --------------------------------------------------------------------------- |
| F1-SF01 | Simple install/setup | ◐      | Compose path works; manual path is 5 steps across 2 stacks                  |
| F1-SF02 | Installation guide   | ◐      | README Quick Start only; no standalone guide                                |
| F1-SF03 | Tutorial             | ✗      | None                                                                        |
| F1-SF04 | Self-contained       | ◐      | 8 external API keys + an LLM provider; G15 — only Ollama self-hostable; G17 |
| F2-SF01 | Protocol development | ●      | Guideline grounding is thin (see G7)                                        |
| F2-SF02 | Protocol validation  | ◐      | AI review is SLR-only                                                       |
| F2-SF03 | Automated searches   | ◐      | G1, G2, G3, G13 — the largest cluster                                       |
| F2-SF04 | Study selection      | ◐      | G4, G5; G18 — no UI to record a screening decision at all                   |
| F2-SF05 | Quality assessment   | ◐      | G6 — no Study entity distinct from Paper; G21 — QualityScoreForm orphaned   |
| F2-SF06 | Data extraction      | ◐      | G20 — extraction UI exists but phase 4 shows a placeholder                  |
| F2-SF07 | Automated analysis   | ●      | —                                                                           |
| F2-SF08 | Text analysis        | ●      | —                                                                           |
| F2-SF09 | Meta-analysis        | ◐      | G8 — no metasummary; thematic synthesis is not Cruzes/Dybå                  |
| F2-SF10 | Report write-up      | ◐      | G9 — no Typst backend; G14 — no PRISMA 2020 flow diagram                    |
| F2-SF11 | Report validation    | ✗      | G10 — no PRISMA/SEGRESS/trAIce checker; G14                                 |
| F3-SF01 | Multiple users       | ◐      | G11 — role model mismatch, no user CRUD                                     |
| F3-SF02 | Document management  | ◐      | G12 — no manual fallback/store/viewer; G16 — SciHub toggle unreachable      |
| F3-SF03 | Security             | ●      | Capability matrix is coarse (see G11)                                       |
| F3-SF04 | Multiple projects    | ◐      | G19 — the entire Tertiary Studies frontend is unreachable                   |

---

## Gaps

### G1 — Snowball provenance DAG (F2-SF03) — **blocking, structural**

**Required.** Maintain traceability links for papers found via snowballing. If a previously included paper is later excluded, papers discovered _from_ it must be excluded too — unless they were also reachable from another still-included paper. This implies a DAG.

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

**Required.** Take one Boolean search string and _optimize it for each database search engine_ before executing.

**Current.** `DatabaseSource.search()` accepts a single `query: str` and every adapter forwards it verbatim — e.g. `researcher-mcp/src/researcher_mcp/sources/ieee.py:144` maps it straight to `"querytext"`. No translation layer exists anywhere in `researcher-mcp/` or `backend/`. The `search_builder` agent prompt mentions truncation wildcards generically but emits one string for all engines.

**Consequence.** Field qualifiers, nesting depth limits, wildcard characters, and proximity operators differ per engine. A string tuned for one database silently under- or over-retrieves in the others, which undermines the recall claims the search-string test-retest tooling is meant to establish.

**Remediation sketch.** Parse the Boolean string into an AST once, then add a `translate(ast) -> str` method to the `DatabaseSource` protocol. Per-engine emitters: Scopus `TITLE-ABS-KEY()`, WoS `TS=`, IEEE field codes, ACM `Abstract:()`, ScienceDirect's operator subset, and a flattened form for Google Scholar (no nesting, 256-char cap).

**Cost.** Medium. Additive — the protocol gains a method with a pass-through default.

---

### G3 — Missing search modalities (F2-SF03) — **medium**

| Requirement       | State | Detail                                                                             |
| ----------------- | ----- | ---------------------------------------------------------------------------------- |
| Google Scholar    | ●     | `sources/google_scholar.py`                                                        |
| arXiv             | ●     | `sources/arxiv.py`                                                                 |
| IEEE Xplore       | ●     | `sources/ieee.py`                                                                  |
| ACM DL            | ●     | `sources/acm.py`                                                                   |
| Scopus            | ●     | `sources/scopus.py`                                                                |
| **EI Compendex**  | ✗     | No adapter                                                                         |
| ScienceDirect     | ●     | `sources/science_direct.py`                                                        |
| Web of Science    | ●     | `sources/wos.py`                                                                   |
| **Manual search** | ✗     | No code path for author/journal/conference-driven search and venue-site resolution |

Beyond the required eight, adapters also exist for Inspec, Springer, Semantic Scholar, Crossref, OpenAlex, Unpaywall, and Sci-Hub.

**Remediation.** EI Compendex is a straightforward adapter (Engineering Village API). Manual search is a new subsystem: venue → website resolution, then site-specific listing traversal, feeding the same `CandidatePaper` upsert path.

---

### G4 — Intra-rater test-retest (F2-SF04) — **high**

**Required.** When a study is screened by a single human or single agent, re-evaluate a random sample of already-decided papers and compute intra-rater agreement via Cohen's κ.

**Current.** Every occurrence of "test-retest" in the codebase refers to **search-string recall validation**, a different concept — `backend/src/backend/api/v1/search_strings.py:28`, `backend/src/backend/jobs/quality_job.py:126`, `backend/src/backend/jobs/validity_job.py:128`, `frontend/src/components/phase2/TestRetest.tsx`. `AgreementRoundType` (`db/src/db/models/slr.py:73`) is `{title_abstract, intro_conclusions, full_text, quality_assessment}` — all **inter**-rater rounds, and `InterRaterAgreementRecord` requires two distinct `reviewer_a_id` / `reviewer_b_id`.

**Consequence.** Single-reviewer studies — which the Rapid Review workflow explicitly supports, warning banner and all — have no reliability evidence at all.

**Remediation sketch.** Add an intra-rater round type and allow `reviewer_a_id == reviewer_b_id` when it is set. Add a resample job: draw _n_ decided candidates, blank the decision for a second pass, then score the two passes with the existing `inter_rater_service` κ computation.

**Cost.** Medium-low — the κ machinery and storage already exist; this is a sampling job plus an enum value plus relaxing one constraint.

---

### G5 — Selection decision rules (F2-SF04) — **high**

**Required.** A defined, extensible set of decision rules governing include/exclude, applied when reviewers disagree (per Petersen & Bin Ali, 2011).

**Current.** No such concept. The only "decision rules" in the tree are the **R1–R6 research-type classification** rules in `agents/src/agents/prompts/extractor/system.md:5` and `db/src/db/models/extraction.py:24` — these classify a paper's research type, they do not govern selection. Disagreement handling exists mechanically (`CandidatePaper.conflict_flag`, `PaperDecision.is_override` / `overrides_decision_id`, `frontend/src/components/slr/DiscussionFlowPanel.tsx`) but resolution is entirely manual with no encoded policy.

**Remediation sketch.** `SelectionDecisionRule` table with a seeded catalog from Petersen & Bin Ali (e.g. _inclusive-if-either_, _exclusive-if-either_, _third-reviewer-adjudicates_, _discuss-to-consensus_), bound to the protocol, plus an evaluator invoked when `conflict_flag` is set. Extensibility via user-defined rules on the same table.

---

### G6 — Study is not modeled separately from Paper (F2-SF05) — **high, structural**

**Required.** A paper may report multiple studies; a study may span multiple papers. Quality assessment applies to the _study_.

**Current.** `QualityAssessmentScore` (`db/src/db/models/slr.py:251`) is keyed to `candidate_paper_id`. There is no entity for an empirical study distinct from a bibliographic record. `DataExtraction` (`db/src/db/models/extraction.py:56`) is likewise paper-keyed.

**Consequence.** Multi-study papers cannot be scored per study; multi-paper studies are double-counted in synthesis and in every report's counts. This also biases meta-analysis, where the unit of pooling should be the study.

**Remediation sketch.** Introduce `EmpiricalStudy` with an N:M join to `CandidatePaper`, then re-key `QualityAssessmentScore` and the synthesis input set to it. Default 1:1 materialization on inclusion preserves current behaviour and keeps the migration mechanical.

**Cost.** High. Touches quality scoring, extraction, synthesis strategies, and all four report services.

---

### G7 — Guideline grounding (F2-SF01) — **medium**

The protocol subsystem itself is strong: `db/src/db/models/protocols.py` (23 task types, quality gates, typed I/O, conditional edges), `ReviewProtocol` with full PICO/S, RR and Tertiary protocols, four seeded templates, YAML round-trip. What is thin is the _citation grounding_ the baseline calls for:

| Guideline set                                   | State                                                       |
| ----------------------------------------------- | ----------------------------------------------------------- |
| Kitchenham et al. 2007 (SLR)                    | Referenced in `agents/.../protocol_reviewer/system.md:4`    |
| PRISMA 2020                                     | Named in the same prompt line only — no structural encoding |
| SEGRESS (Kitchenham 2023)                       | ✗ zero occurrences                                          |
| PRISMA-trAIce (Holst 2025)                      | ✗ zero occurrences                                          |
| Petersen 2008 / 2015 (SMS)                      | Not cited (see the SMS note below)                          |
| Ampatzoglou 2020 / Petersen & Gencel 2013 (ToV) | Threats-to-validity model exists for **Rapid Review only**  |
| Grey literature (Garousi, Rainer, Yasin)        | `GreyLiteratureSource` model exists; heuristics not encoded |

**SMS protocol — by design, not a gap.** SMS deliberately shares the SLR protocol model rather than having a dedicated one: an SMS protocol follows the SLR protocol, minus the quality-evaluation definition. The code supports this — `ReviewProtocol` (`db/src/db/models/slr.py:100`) is keyed only on `study_id`, and neither `slr_protocol_service` nor the `/api/v1/slr/studies/{id}/protocol` endpoints gate on `StudyType`, so an SMS study can hold a full protocol today.

What _is_ missing is the deliberate omission: the quality-assessment models (`QualityAssessmentChecklist` / `Item` / `Score`) are equally ungated, so nothing marks quality evaluation as out of scope for SMS, and nothing steers an SMS author away from defining one. The gap is an absent study-type policy, not an absent model.

**SEGRESS, PRISMA 2020, and PRISMA-trAIce apply to SMS as well as SLR** — the ✗ rows above are unmet for every study type, not for SLR alone.

---

### G8 — Qualitative synthesis (F2-SF09) — **high**

**Required.** Qualitative Metasummary (Ribeiro et al. 2014) and Thematic Synthesis (Cruzes & Dybå 2011).

**Current.**

- **Statistical meta-analysis is genuinely built** — `MetaAnalysisSynthesizer` (`backend/src/backend/services/synthesis_strategies.py:93`) with pooled effects, sensitivity analysis, and Forest/Funnel SVG output.
- **Qualitative Metasummary: absent.** Zero occurrences of "metasummary". No frequency effect sizes, no intensity effect sizes.
- **Thematic Synthesis: not per the method.** `ThematicAnalysisStrategy` (`synthesis_strategies.py:472`) is a single LLM call requesting 3–7 themes as a JSON theme→index map, with a `{"raw": ...}` fallback on parse failure. That is thematic _clustering_. Cruzes & Dybå specify five steps — extract data, code data, translate codes into themes, create a model of higher-order themes, assess trustworthiness — of which only an implicit collapse of steps 2–3 is present. Nothing is auditable at the code level, and there is no trustworthiness assessment.

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

| Requirement                   | State | Detail                                                                                            |
| ----------------------------- | ----- | ------------------------------------------------------------------------------------------------- |
| Auto-retrieve correct version | ●     | `fetch_paper_pdf` — Unpaywall OA, then gated Sci-Hub                                              |
| Flag for manual download      | ✗     | No flag, no state, no queue                                                                       |
| Manual upload path            | ✗     | None                                                                                              |
| Manage documents on disk      | ✗     | Full text is a DB text column (`Paper.full_text_markdown`); only `pdf_path` is on the RR briefing |
| Allow users to view the paper | ◐     | `GET /papers/{id}/markdown` exists; **no frontend consumer** — backend-only                       |

**Remediation sketch.** Add a `retrieval_status` enum to `Paper` with a `manual_required` state set on retrieval failure, an upload endpoint writing to a configured object/file store, and a reader view in the frontend that consumes the existing markdown endpoint.

---

### G13 — Search-string piloting loop is open at both ends (F2-SF03, F2-SF01) — **high** _(13d resolved 2026-08-05)_

**Required.** When database search is the chosen protocol strategy, the tool must:

1. Generate a search string from the **research goal, research questions, and a set of seed papers**;
2. **Refine it iteratively** by running it — converging on a string that recovers the seed papers _and_ yields a minimal set suitable for later snowball sampling;
3. **Pilot it across multiple databases and see the per-database results.**

**Current.** The data model is already the right shape and the recall check genuinely works — `SearchString` is versioned with a single `is_active` (`db/src/db/models/search.py:21`), `SearchStringIteration` records `result_set_count` / `test_set_recall` / `ai_adequacy_judgment` / `human_approved` (`search.py:51`), and `run_test_search` (`backend/src/backend/jobs/search_job.py:21`) computes `recall = |seed_dois ∩ result_dois| / |seed_dois|`. What is missing is the wiring at each end.

#### 13a — Seed papers do not inform generation

`SearchStringBuilderAgent.run()` **already declares** `seed_keywords: list[str] | None` (`agents/src/agents/services/search_builder.py:63`) and threads it into the Jinja template context. But `POST /studies/{id}/search-strings/generate` (`backend/src/backend/api/v1/search_strings.py:180`) **omits the argument entirely** and never queries `SeedPaper`. The parameter is always empty.

Seed papers therefore serve only as the recall test set — they contribute nothing to the string being tested. A wiring gap, not a missing capability.

Secondary: research goal and RQs are read from the untyped `study.metadata_` JSON blob (`meta["research_objectives"]`, `meta["research_questions"]`), while SLR/RR/Tertiary studies hold RQs in typed protocol columns (`ReviewProtocol.research_questions`). The two can silently diverge.

#### 13b — The refinement loop never closes, and minimality is unmeasured

- **No feedback-driven regeneration.** Nothing consumes iteration _N_ to produce version _N+1_. Re-calling `/generate` re-runs the agent with identical inputs; it never learns which seeds were missed. Refinement is manual hand-editing in `SearchStringEditor.tsx`.
- **Minimality is never measured.** Only `result_set_count` is stored — no precision, no F-measure, no objective function trading recall against set size. The stated goal (_a minimal set adequate for later snowballing_) cannot be evaluated, let alone optimised. Recall alone is trivially maximised by an over-broad string, which is the wrong end of the tradeoff for the step that feeds G1.
- **`ai_adequacy_judgment` is never written by the test job.** It is set once at generation time to the agent's `expansion_notes` and never updated, so no AI ever judges the adequacy of an _actual_ pilot run.

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

1. **Inverted status guard.** `not status_code > 200` treated _only_ `≤ 200` as success — a `201`/`202`/`204` fell through to the failure path.
2. **Silent failure with a magic number.** An unreachable or non-200 MCP response returned `set(), 2`, writing an iteration with `recall = 0.0` and `result_set_count = 2` — **indistinguishable from a genuinely bad search string**. A researcher would see "0% recall, 2 results" and rewrite a perfectly good query while the actual fault was a down service. The `except` branch logged a warning, which made it worse: the log said _unavailable_ while the database recorded a plausible-looking result.

**Both confirmed by execution and fixed.** Verification showed a `201` response yielding an empty DOI set, and neither the exception path nor a `500` raising. Notably the defect was _enshrined in the suite_ — `test_fetch_test_search_results_returns_empty_on_exception` asserted `count == 2` and passed, so the function was covered and the coverage was worthless.

Changes in `backend/src/backend/jobs/search_job.py`:

- Added `TestSearchUnavailableError(RuntimeError)` plus named constants `_HTTP_OK` / `_HTTP_MULTIPLE_CHOICES`.
- Narrowed the `try` to wrap only the HTTP call, so a malformed-but-200 payload also raises instead of being swallowed.
- Replaced the guard with an explicit `_HTTP_OK <= status < _HTTP_MULTIPLE_CHOICES` range check; all 2xx parse, all non-2xx raise with the status logged.
- Removed `return set(), 2`.

A service failure now propagates through `run_test_search`'s existing handler — the `BackgroundJob` is marked `FAILED` with an `error_message` and **no `SearchStringIteration` is written at all**. In `backend/tests/unit/test_search_job_helpers.py`, the test encoding the defect was replaced with three pinning the correct contract (raises on transport failure, raises on `500`, parses `201`).

Verified: 1096 backend tests pass (up from 1094), coverage 86.10%, `ruff check backend/src` and `mypy backend/src` both clean.

**13a–13c remain open.**

**Interaction with G2.** Because one identical string is sent to every engine, adding a per-database breakdown _before_ fixing per-engine query translation would measure syntax mismatch as much as query quality — producing misleading per-database recall figures. G2 and 13c should land together.

**Remediation sketch.**

| Step  | Change                                                                                                                | Size               |
| ----- | --------------------------------------------------------------------------------------------------------------------- | ------------------ |
| ~~1~~ | ~~Fix the status guard; fail the iteration explicitly instead of `return set(), 2`~~                                  | ✅ Done 2026-08-05 |
| 2     | Pass seed-derived keywords into `agent.run(seed_keywords=...)`                                                        | Small              |
| 3     | Add `databases_used`, `per_database_counts` (JSON), `precision`, `missed_seed_dois` (JSON) to `SearchStringIteration` | Small + migration  |
| 4     | Return per-source results from `search_papers` rather than a merged list                                              | Medium             |
| 5     | Refine endpoint feeding `missed_seed_dois` + result count back to the agent to emit version _N+1_                     | Medium             |
| 6     | Define the stopping rule (recall ≥ target **and** result set ≤ ceiling) and expose it as protocol config              | Medium             |
| 7     | Source the database list from `StudyDatabaseSelection` instead of the hardcoded default and free-text field           | Small              |

**Cost.** Medium overall, but step 1 is a few lines and should not wait — it currently corrupts pilot data silently.

---

### G14 — PRISMA 2020 flow diagram generation (F2-SF10, F2-SF11) — **medium**

**Required.** Reports must include a **PRISMA 2020 flow diagram in SVG**, laid out as specified in the PRISMA 2020 guidance. When the review is an **MLR** (an SLR or SMS incorporating grey literature), the corresponding MLR base flow must be used instead of the standard one.

**Current.** Absent. Zero occurrences of `flow_diagram`, `flowchart`, `prisma_flow`, `MLR`, or `multivocal` across `backend/src`, `db/src`, `agents/src`, and `frontend/src`. No report service emits a flow diagram in any format.

Two supporting pieces do exist:

- **SVG generation is an established pattern.** `backend/src/backend/services/visualization.py` already emits SVG from matplotlib (`fig.savefig(buf, format="svg")` — bar chart, frequency infographic, Forest, Funnel) and from plotly (`fig.to_image(format="svg")` — bubble chart). A PRISMA renderer belongs alongside these.
- **The counts are largely derivable.** `CandidatePaper.current_status`, `duplicate_of_id`, `PaperDecision`, and `SearchExecution` between them carry identification, deduplication, screening, and inclusion tallies.

Three things block it:

1. **No MLR concept.** `StudyType` is `{SMS, SLR, TERTIARY, RAPID}` and nothing marks a review as incorporating grey literature. `GreyLiteratureSource` records _sources_ but does not classify the review, so the system cannot select between the standard and MLR base flows.

   **Decision (2026-08-05): MLR is a flag on `Study`, not a fifth `StudyType`.** An MLR is an SLR or SMS that incorporates grey literature — the review type is unchanged, so grey-literature inclusion is orthogonal to it and composes with either. Modelling it as a study type would force `MLR-SMS` / `MLR-SLR` enum members (or lose the distinction), duplicate both phase gates, and split the protocol and report paths that SMS and SLR already share. A boolean keeps one code path per review type and reduces base-flow selection to a single branch at render time.

2. **Grey-literature counts are not tracked through the screening funnel.** The PRISMA 2020 MLR variant needs its grey-literature arm counted separately at each stage; `CandidatePaper` has no provenance field distinguishing a grey-literature record from a database record.
3. **"Reports excluded, with reasons" is not aggregated.** `PaperDecision.reasons` is a JSON list per decision, but nothing rolls it up into the per-reason exclusion counts the diagram's full-text box requires.

**Remediation sketch.**

| Step | Change                                                                                                                                         | Size              |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| 1    | Add `Study.includes_grey_literature: bool` (default `False`); `is_mlr` is that flag AND `study_type in {SMS, SLR}`. Drives base-flow selection | Small + migration |
| 2    | Add a provenance discriminator on `CandidatePaper` so the grey-literature arm can be counted separately                                        | Small + migration |
| 3    | `PrismaFlowService` — assemble stage counts from `CandidatePaper` / `PaperDecision` / `SearchExecution`                                        | Medium            |
| 4    | Aggregate `PaperDecision.reasons` into per-reason full-text exclusion counts                                                                   | Small             |
| 5    | SVG renderer in `visualization.py` for both base flows, matching PRISMA 2020 box layout and arrow structure                                    | Medium            |
| 6    | Embed in the SLR/SMS report exporters (Markdown, LaTeX, and the eventual Typst backend of G9)                                                  | Small             |

**Interaction.** Shares its counting layer with **G10** (a PRISMA 2020 checker needs the same stage tallies) and with **G1** — snowball-discovered records occupy their own PRISMA 2020 arm ("records identified from other methods"), which cannot be reported accurately without the provenance edges G1 introduces. Step 2 here and G1's `candidate_discovery_edge` should be designed together.

---

### G15 — vLLM and LM Studio providers (F1-SF04) — **low, additive**

**Required.** The platform must support two additional LLM providers beyond the current three: **vLLM** and **LM Studio**.

**Current.** `ProviderType` (`db/src/db/models/agents.py:42`) has exactly three members — `ANTHROPIC`, `OPENAI`, `OLLAMA`. Ollama is the only self-hostable option, which is why F1-SF04 ("self-contained") is still `◐`: a user who wants local inference has exactly one engine available, and it is the weakest of the three for serving throughput.

Both requested providers are **OpenAI-API-compatible**, which is what makes this cheap rather than structural:

- **vLLM** serves an OpenAI-compatible endpoint (`/v1/models`, `/v1/chat/completions`). LiteLLM addresses it as `hosted_vllm/<model>` with an `api_base`. Usually keyless, but can be started with `--api-key`, so the key must be _optional_, not absent.
- **LM Studio** serves the same OpenAI-compatible surface, by default on `http://localhost:1234/v1`. LiteLLM addresses it as `lm_studio/<model>`. Keyless.

The existing abstractions already fit. `ProviderConfig` (`agents/src/agents/core/provider_config.py`) is a `Protocol` of exactly `model_string`, `api_base`, and `api_key` — precisely the three fields both engines need, and `api_base` was already introduced for Ollama. No new interface is required.

Three places hard-code the three-way enum:

1. **Model fetch dispatch** — `backend/src/backend/services/provider_service.py:491` branches Anthropic / OpenAI / `else: OLLAMA`. Note the `else` is a silent catch-all: a new enum member added without touching this function would be routed to `fetch_models_ollama` rather than failing loudly.
2. **LiteLLM prefix map** — `backend/src/backend/services/agent_service.py:885` maps each `ProviderType` to its prefix string.
3. **Frontend union** — `frontend/src/types/provider.ts:12` and `ProviderForm.tsx:25` both declare the literal union, and `ProviderForm.tsx:88` decides key-required via `providerType === 'anthropic' || providerType === 'openai'`.

**Remediation sketch.**

| Step | Change                                                                                                                                                                                                                                            | Size              |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| 1    | Add `VLLM = "vllm"` and `LM_STUDIO = "lm_studio"` to `ProviderType`; Alembic `ALTER TYPE ... ADD VALUE` (not reversible in a single migration — the downgrade needs a type rebuild)                                                               | Small + migration |
| 2    | Give `fetch_models_openai` a `base_url` parameter and reuse it for both — both expose OpenAI's `/v1/models`. Replace the `else: OLLAMA` catch-all with explicit branches so an unhandled provider raises instead of silently fetching from Ollama | Small             |
| 3    | Extend the LiteLLM prefix map with `hosted_vllm` and `lm_studio`                                                                                                                                                                                  | Trivial           |
| 4    | Widen both frontend unions; make `base_url` required and `api_key` optional for both; add them to the form's select                                                                                                                               | Small             |
| 5    | Document default endpoints (`:8000/v1` vLLM, `:1234/v1` LM Studio) in the install guide (F1-SF02)                                                                                                                                                 | Trivial           |

**Cost.** Low — this is the cheapest open gap. Steps 2–4 are mechanical because the OpenAI-compatible surface is already implemented; the only real work is the enum migration.

**Interaction.** Directly improves **F1-SF04** — with vLLM available, the platform can run fully locally with a serving engine suitable for batch agent workloads, which matters for the high-volume screening and extraction phases. Also worth pairing with the connectivity-test pattern already built for search integrations (`CredentialService.run_connectivity_test`), since a mistyped `base_url` is the most likely failure mode for both.

---

### G16 — SciHub toggle is unreachable (F3-SF02) — **low, mechanical**

**Claim.** The SciHub acknowledgment flow specified in feature 006 cannot be reached from the UI.

**Evidence.** `frontend/src/components/studies/DatabaseSelectionPanel/index.tsx` declares the action (`:90`), handles it in the reducer (`:109`) and renders the full "Enable SciHub Access?" dialog (`:273`) — but `TOGGLE_SCIHUB` is **never dispatched**. There is no toggle control, so the dialog is dead code.

The backend half is complete: `backend/src/backend/api/v1/studies/database_selection.py:165` gates on the server-level `SCIHUB_ENABLED` env var and rejects `scihub_enabled=True` when it is off.

**Remediation.** Render a `Switch` in the panel that dispatches `TOGGLE_SCIHUB`, driven by `state.scihub_enabled`. Un-`fixme` the four tests in `frontend/e2e/database-selection.spec.ts`.

**Cost.** Low — one control; the reducer, dialog, and API are already written.

---

### G17 — Agents list has no task-type filter (F1-SF04) — **low, mechanical**

**Claim.** The admin Agents tab cannot be filtered by task type, though every layer beneath it supports the filter.

**Evidence.** `useAgents()` accepts `{ task_type }` and forwards it as a query param (`frontend/src/services/agentsApi.ts:33`), and the API honours it — but `AdminPage`'s `AgentsTab` calls `useAgents()` with no arguments (`frontend/src/pages/AdminPage.tsx:216`) and renders no filter control.

**Remediation.** Add a task-type `TextField select` to the tab, hold the value in `AdminState`, and pass it to `useAgents`. Un-`fixme` the test in `frontend/e2e/admin/test_agent_wizard.spec.ts`.

**Cost.** Low.

---

### G18 — Phase 3 screening decisions cannot be recorded (F2-SF04) — **medium**

**Claim.** A human reviewer has no way to accept, reject, or mark a paper as a duplicate. This is the most consequential of the three, because manual screening is a core SMS/SLR activity and the backend for it is finished.

**Evidence.** Two complete components are orphaned — **imported by nothing**:

- `frontend/src/components/phase2/ReviewerPanel.tsx` renders accepted/rejected/duplicate buttons and POSTs to `/api/v1/studies/{id}/papers/{candidate}/decisions` (`:58`).
- `frontend/src/components/shared/PaperCard.tsx` queries a paper's decisions and offers conflict resolution.

What Phase 3 actually renders is `frontend/src/components/phase2/PaperQueue.tsx`, a **read-only** listing: its only controls are Refresh, Run Full Search, and pagination. There is likewise no control anywhere that starts a screening run, so the job-progress panel can never appear.

The backend is complete: `backend/src/backend/api/v1/papers.py:157` onward implements the decisions endpoints, including conflict detection (`_detect_conflict`, `:223`), and is covered by `backend/tests/integration/test_papers_decisions.py`.

**Remediation.**

| #   | Step                                                                                                          |
| --- | ------------------------------------------------------------------------------------------------------------- |
| 1   | Mount `ReviewerPanel` in the Phase 3 view, wired to the selected candidate paper.                             |
| 2   | Make `PaperQueue` rows selectable so a paper can be sent to the panel.                                        |
| 3   | Mount `PaperCard` (or fold its decision history into the panel) so prior decisions and conflicts are visible. |
| 4   | Add a control that enqueues a screening job, so the existing progress panel has a trigger.                    |
| 5   | Un-`fixme` the three tests in `frontend/e2e/screen-paper.spec.ts`.                                            |

**Cost.** Medium — the components and API exist, so this is wiring plus selection state, not new feature work. Step 4 is the only part that may need new backend surface.

**Interaction.** Blocks meaningful end-to-end coverage of **F2-SF04**, and by extension the inter-rater reliability work in **G4/G5** — κ cannot be exercised through the UI if decisions cannot be recorded through it.

---

### G19 — The Tertiary Studies frontend is unreachable (F3-SF04) — **high**

**Claim.** Feature 009 is complete on both sides and connected on neither. Thirteen frontend modules — the entire Tertiary Studies UI — cannot be reached from the application entry point.

**Evidence.** Unreachable from `main.tsx`:

| Layer      | Modules                                                                                                                   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------- |
| Pages      | `TertiaryStudyPage.tsx`, `TertiaryReportPage.tsx`                                                                         |
| Components | `TertiaryProtocolForm`, `SeedImportPanel`, `TertiaryExtractionForm`, `TertiaryQAGuidancePanel`, `LandscapeSummarySection` |
| Hooks      | `hooks/tertiary/useProtocol.ts`, `useSeedImports.ts`, `useExtractions.ts`                                                 |
| Services   | `services/tertiary/protocolApi.ts`, `seedImportApi.ts`, `extractionApi.ts`                                                |

Two independent causes:

1. `App.tsx` registers no route for `TertiaryStudyPage` — the router knows nothing about it.
2. `StudyPage` branches on `isSLR` and `isRapid` only. There is no `isTertiary`, so a study whose `study_type` is `Tertiary` falls through to the SMS path and renders SMS phase panels.

The backend is live: all **7** `/api/v1/tertiary/*` routes are registered and answer, migration `0017` is applied, and `TertiaryReportService` / `TertiaryExtractionService` are implemented and tested.

**Remediation.**

| #   | Step                                                                                                                                                                                    |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Add `const isTertiary = study?.study_type === 'Tertiary'` to `StudyPage` and dispatch its five phases to the tertiary panels, matching the `isSLR` / `isRapid` pattern already there.   |
| 2   | Decide whether `TertiaryStudyPage` is the host (add a route) or whether its panels fold into `StudyPage` as the SLR and Rapid pages do. The latter is more consistent with what exists. |
| 3   | Wire `TertiaryReportPage` to the phase-5 slot.                                                                                                                                          |
| 4   | Add an e2e spec — the workflow currently has no end-to-end coverage, because there is no way to reach it.                                                                               |

**Cost.** Medium — no new components, no API work, no migration. This is dispatch wiring over finished parts.

**Interaction.** Until this lands, feature 009 delivers nothing to a user, and its 13 modules cannot be exercised by any test that drives the UI.

---

### G20 — Phases 4 and 5 show a placeholder over finished components (F2-SF06, F2-SF10) — **medium**

**Claim.** For SMS and Tertiary studies, `StudyPage` renders _"Phase 4 content will be available in a future sprint."_ and the same for phase 5, while the components those phases need are written and their endpoints answer.

**Evidence.** `StudyPage.tsx` phase 4 and 5 fall through to placeholder text for `!isSLR && !isRapid`. Unreachable but complete:

| Module                                   | Purpose                                                                    | Backend                                   |
| ---------------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------- |
| `pages/ExtractionPage.tsx`               | Lists accepted papers, hosts `ExtractionView`, opens `DiffViewer` on a 409 | `GET /studies/{id}/extractions` → **200** |
| `components/phase3/ExtractionView.tsx`   | Per-paper extraction form                                                  | as above                                  |
| `components/shared/DiffViewer.tsx`       | Conflict resolution on concurrent edits                                    | PATCH 409 path                            |
| `components/phase4/ValidityForm.tsx`     | Six validity dimensions, autosave, "Generate with AI" ARQ job              | `GET/PUT /studies/{id}/validity`          |
| `components/phase5/QualityReport.tsx`    | Rubric score cards and prioritised recommendations                         | `GET /studies/{id}/quality-reports`       |
| `components/phase2/MetricsDashboard.tsx` | identified → accepted → rejected → duplicates funnel                       | `GET /studies/{id}/metrics` → **200**     |

**Remediation.** Mount `ExtractionPage` at phase 4 and `QualityReport` at phase 5 for the non-SLR/non-Rapid branch; add `ValidityForm` to the phase-4 view; place `MetricsDashboard` in the phase-2 view. Replace the placeholders.

**Cost.** Medium — wiring plus deciding the phase-4 layout (paper list beside extraction form).

---

### G21 — Two orphaned controls in otherwise-wired features (F2-SF05) — **low**

**Claim.** Two components are complete and unused inside features that are themselves reachable.

- `components/slr/QualityScoreForm.tsx` — per-reviewer scoring with a live aggregate. `QualityAssessmentPage` imports `QualityChecklistEditor` but not this, so a reviewer can define a checklist and never score against it.
- `components/protocols/EdgeConditionBuilder.tsx` — builds the conditional triple on a protocol edge. Nothing imports it, so conditional edges cannot be authored in the visual editor (the YAML pane remains the only route).

**Remediation.** Mount `QualityScoreForm` in `QualityAssessmentPage` beneath the checklist; surface `EdgeConditionBuilder` from the protocol editor when an edge is selected.

**Cost.** Low.

---

## Built-but-never-wired audit

Five defects of the same shape were found on 2026-08-06, so the codebase was swept systematically rather than incident by incident.

**Method.** Build the import graph of `frontend/src` and compute what is reachable from `main.tsx`. Anything else is dead, however complete it is. Re-runnable:

```bash
# modules unreachable from the entry point
python3 scripts/audit_unreachable_frontend.py
```

**Result.** 142 modules scanned, **23 unreachable** (excluding `test-setup.ts`, a Vitest entry point):

| Cluster                           | Modules | Gap |
| --------------------------------- | ------: | --- |
| Tertiary Studies frontend         |      13 | G19 |
| Extraction / phases 4–5 / metrics |       6 | G20 |
| Screening decisions               |       2 | G18 |
| Orphaned controls                 |       2 | G21 |

The backend has no equivalent problem: all **56** `APIRouter` modules are registered.

**Already fixed, same pattern.** Recorded because they show the failure mode is not confined to whole components:

| Defect                                                                                                                                                                         | Fix                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| `StudyPage` passed `isAdmin={false}` as a literal, so protocol task **Mark Complete** and **Approve** were rendered for nobody, though both endpoints exist and are LEAD-gated | `342fc4b` — added `viewer_role` to `StudyDetail` and gated on it |
| `NewStudyWizard` reused one DOM node across the Next/Create swap, so clicking Next on step 4 submitted the form and **discarded step 5's input**                               | `513d973` — distinct React keys                                  |

**Why it stayed hidden.** In every case the e2e tests that should have caught it were guarding on `isVisible()` — which takes no timeout — and silently skipping, or asserting against a placeholder. The lesson is recorded under [Observed pattern](#observed-pattern): a component compiling, passing unit tests, and having a working endpoint says nothing about whether a user can reach it.

---

## Recommended sequence

| Order | Item                                                     | Rationale                                                                                                           |
| ----- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| ~~0~~ | ~~**G13d** two defects in `_fetch_test_search_results`~~ | ✅ **Done 2026-08-05** — was writing fabricated pilot data on service failure                                       |
| 1     | **G10** report validation                                | Greenfield, no schema change, operates on an existing structured object                                             |
| 2     | **G1** + **G14** steps 1–2 provenance                    | Design together — the PRISMA "other methods" arm and the snowball DAG need the same discriminator                   |
| 2b    | **G14** steps 3–6 flow diagram                           | Follows the provenance work; reuses `visualization.py`'s existing SVG pattern                                       |
| 3     | **G6** Study/Paper split                                 | Every downstream count and pooled estimate depends on the unit of analysis being right                              |
| 4     | **G11** roles + user CRUD                                | The system currently cannot onboard a user through its own API                                                      |
| 5     | **G4**, **G5** reliability + rules                       | Both reuse the existing κ and decision machinery                                                                    |
| 6     | **G2** + **G13** search fidelity + piloting              | Land together — a per-database breakdown is misleading until query translation exists                               |
| 7     | **G3** remaining search modalities                       | EI Compendex adapter and manual search; independent of the above                                                    |
| 8     | **G8** qualitative synthesis                             | Large, but unblocked once G6 lands                                                                                  |
| 9     | **G7**, **G9**, **G12**, F1 docs                         | Additive, low coupling                                                                                              |
| —     | **G15** vLLM + LM Studio providers                       | Unordered — cheapest item on the list and independent of everything else; land whenever local inference is wanted   |
| 1b    | **G18** wire up screening decisions                      | Promote near the top: the components and API already exist, and until it lands F2-SF04 has no exercisable path      |
| 1c    | **G19** wire up Tertiary Studies                         | Highest ratio of delivered value to work on the list — 13 finished modules and 7 live routes, needing only dispatch |
| 1d    | **G20** phases 4–5 over finished parts                   | Same shape as G18/G19; removes two "future sprint" placeholders                                                     |
| —     | **G16**, **G17**, **G21** unreachable UI controls        | Unordered — each is a single control over machinery that is already written                                         |

---

## Observed pattern

Features that are _stateful workflow_ — protocols, phase gates, screening, extraction, membership — are well built out. Features that require a **richer relational shape** — a provenance DAG (G1), a Study entity distinct from Paper (G6), an intra-rater round (G4) — are the ones that got flattened.

That is the predictable consequence of shipping ten features as sequential additive migrations `0014`–`0018`: changing the _shape_ of `CandidatePaper`, or splitting `Paper` from `Study`, would have forced backfills across every previously completed workflow. The remaining structural gaps are cheap to describe and expensive to add for exactly that reason — and they get more expensive with every study the platform runs.

A second, cheaper pattern sits alongside it: **capabilities built but not connected**. G13a is the clearest case — the agent declares `seed_keywords`, the template renders it, the seed records exist, and the endpoint simply never passes the argument. G12's paper viewer is the same shape (endpoint with no frontend consumer), as is `ai_adequacy_judgment` (column written once, never updated). These cost little to close and are worth sweeping for beyond the instances catalogued here.
