# Feature Gap Analysis

**Assessed**: 2026-08-05
**Last updated**: 2026-08-07
**Baseline**: `docs/base-features.md` (27 features, F1-SF01 – F3-SF04), plus `docs/todo.md` and `docs/todo2.md`
**Evidence**: branch `012-wire-up-unreachable-workflows` at `dd1fe20`, working tree clean but for `docs/`
**Scope**: 43 gaps catalogued (G1–G43), 2 resolved; 23 frontend modules still unreachable, pending feature 012

**Method**: each feature traced to implementing code — ORM models, API routes, services, agents, source adapters, UI components — rather than to `specs/` intent.

> **This document is now the single backlog.** `docs/todo.md` and `docs/todo2.md` were separate wish-lists whose items overlapped this catalogue, each other, and work already shipped. Every line of both was checked against the tree on 2026-08-07 and folded in here — see [Unified intake from todo.md and todo2.md](#unified-intake-from-todomd-and-todo2md), which maps each original line to a verdict and a gap. The two source files are left in place unedited as a provenance record; they are no longer the place to look for what is outstanding.

> **Known limit of that method.** Tracing to code answers _does an implementation exist_, not _does it work_. Two features marked ● survived a trace while being inert: `_generate_all_charts` looped over an empty list, and the group study listing leaked across research groups. Both had a function that existed, was called, and was covered by passing tests. Claims about behaviour now need the feature exercised — which is what [feature 012](./features/012-wire-up-unreachable-workflows.md) makes a standing requirement. See [Re-check of affected gap claims](#re-check-of-affected-gap-claims-2026-08-06).

### Revision history

| Date       | Change                                                                                                                                                                                                                                                |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-08-05 | Initial assessment, G1–G15. G13d resolved                                                                                                                                                                                                             |
| 2026-08-06 | **G16–G21 added.** A systematic reachability sweep found 23 frontend modules unreachable from `main.tsx`, including the entire Tertiary Studies frontend — see [Built-but-never-wired audit](#built-but-never-wired-audit)                            |
| 2026-08-06 | **G18–G20 designed together** as feature 012; that pass corrected several claims in G18 and G19 (see the `Correction` notes in each)                                                                                                                  |
| 2026-08-06 | **60+ committed mutation artifacts found** in `backend/src`, invisible to a fully green suite. Reverted in `e47abd9`, contained in `0303a3c` — see [Committed mutation artifacts](#committed-mutation-artifacts-resolved-2026-08-06)                  |
| 2026-08-06 | **Every gap claim resting on repaired source re-checked.** No verdict changed; four claims corrected, including G13d's root cause — see [Re-check of affected gap claims](#re-check-of-affected-gap-claims-2026-08-06)                                |
| 2026-08-06 | **G21 broadened** to cover two package-shadowed backend modules, both since deleted (`fdd5220`). This document's claim that the backend had no reachability problem was withdrawn, and `scripts/check_shadowed_modules.py` now guards the class in CI |
| 2026-08-07 | **G22–G23 added**, both found while fixing the screening pipeline (`d8f6dcf`, `1e01097`). Snowballing is a registered job with no enqueue site, and admin job retry enqueues function names that are not registered, with arguments matching no job's signature — while reporting `200`. Neither is visible to the reachability oracles, which model imports rather than HTTP routes; see [Neither oracle sees a backend route](#neither-oracle-sees-a-backend-route) |
| 2026-08-07 | **G22 resolved.** `POST /studies/{id}/snowball` plus a `SnowballControls` mount, with seeds defaulting to the study's accepted papers, a `409` naming any in-flight pass (FR-026), and a `422` rather than an empty run. 16 integration tests, 10 component tests. G23 remains open |
| 2026-08-07 | **In-flight guard made bidirectional**, and **G24 added**: snowballing is DOI-keyed, so grey literature, reports, theses and older proceedings — the papers most likely to lack a DOI — are silently excluded from the walk. Both directions are recoverable, backward from stored full text and forward by resolving to a non-DOI identifier, but which citation index to prefer needs a research spike |
| 2026-08-07 | **G35–G43 added from the methodology corpus.** Requirements the 54-paper research pass established that were not in this catalogue: protocol-as-preregistration with a validation snapshot; stopping rules and the *assessed vs never-assessed* distinction; escalatable reading depth and per-classification rationale; the quality-instrument shape (purpose flag, ordinal scales, separated scores); threat derivation from protocol configuration; GQM goal→question→field traceability; review-update as a workflow; terminology-variant search; and replication-package export with archival and licence discipline. Seven further requirements were folded into existing gaps rather than given IDs — see the table at the end of that section |
| 2026-08-07 | **G10 amended** after the research pass behind [`docs/methodology/`](./methodology/). PRISMA 2020 states it "should not be used to assess the conduct or methodological quality of systematic reviews", so the planned checker measures **reporting completeness**, not rigour. SEGRESS replaces PRISMA as the primary standard, being the only one that marks each item required/optional/not-required **per review type**; quality scoring moves to DARE and the Petersen 2015 rubrics. The gap becomes two features rather than one |
| 2026-08-07 | **`docs/todo.md` and `docs/todo2.md` folded in — G25–G34 added.** Every line of both was executed against the tree rather than read. Nine of 26 assessable items were already delivered and seven partial; the rest became gaps. The largest is **G25**: the backend addresses researcher-mcp over a REST API that server does not serve — `mcp.http_app()` exposes exactly one route, `/mcp`, so all five `POST /tools/…` and `GET /health` call sites fail, four of them silently. Every database search, PDF fetch and snowball walk in the platform runs through those calls. See [Unified intake](#unified-intake-from-todomd-and-todo2md) |

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
| F1-SF01 | Simple install/setup | ◐      | Compose path works; manual path is 5 steps across 2 stacks; G34 — the documented coverage command fails from the repo root |
| F1-SF02 | Installation guide   | ◐      | README Quick Start only; no standalone guide                                |
| F1-SF03 | Tutorial             | ✗      | None                                                                        |
| F1-SF04 | Self-contained       | ◐      | 8 external API keys + an LLM provider; G15 — only Ollama self-hostable; G17 |
| F2-SF01 | Protocol development | ◐      | G7 — thin guideline grounding; G35 — the protocol is a preregistration but is not committed as one; G40 — no goal→question→field traceability |
| F2-SF02 | Protocol validation  | ◐      | AI review is SLR-only                                                       |
| F2-SF03 | Automated searches   | ✗      | **G25 — the MCP call surface does not exist, so no search returns papers.** Then G1, G2, G3, G13, G24, G26, G28, G36, G41, G42 — largest cluster by far. G22 resolved: snowballing is startable |
| F2-SF04 | Study selection      | ◐      | G4, G5; G18 — no UI to record a screening decision at all                   |
| F2-SF05 | Quality assessment   | ◐      | G6 — no Study entity distinct from Paper; G21 — orphaned + shadowed modules; G38 — instrument model is the wrong shape |
| F2-SF06 | Data extraction      | ◐      | G20 — extraction UI exists but phase 4 shows a placeholder; G25 — full text never retrieved, so extraction runs on abstracts; G37 — no reading depth or rationale capture |
| F2-SF07 | Automated analysis   | ●      | Re-verified 2026-08-06 — the ● was unearned when written (see below)        |
| F2-SF08 | Text analysis        | ●      | —                                                                           |
| F2-SF09 | Meta-analysis        | ◐      | G8 — no metasummary; thematic synthesis is not Cruzes/Dybå; G27 — SMS has no synthesis at all |
| F2-SF10 | Report write-up      | ◐      | G9 — no Typst backend; G14 — no PRISMA 2020 flow diagram; G27 — SMS produces a data archive, not a report; G43 — no replication package or archival |
| F2-SF11 | Report validation    | ✗      | G10 — no checker. **Amended**: SEGRESS is the standard, per review type; PRISMA may not score quality; G14; G35 — no protocol snapshot to detect deviation against; G39 — threats not derived from configuration |
| F3-SF01 | Multiple users       | ◐      | G11 — role model mismatch, no user CRUD; G23 — job retry silently no-ops; G31 — no user avatar |
| F3-SF02 | Document management  | ◐      | G12 — no manual fallback/store/viewer; G16 — SciHub toggle unreachable; G28 — grey literature is a register, not a source |
| F3-SF03 | Security             | ●      | Capability matrix is coarse (G11); a live access-control defect was missed  |
| F3-SF04 | Multiple projects    | ◐      | G19 — the entire Tertiary Studies frontend is unreachable; G27 — the four study types are parallel implementations |

---

## Unified intake from `todo.md` and `todo2.md`

The two files hold 27 bullets between them; several bundle two or three separable asks, so they resolve to **26 assessable items**, each executed against the tree on 2026-08-07 rather than read. **Nine are delivered, seven are partial, ten are not started.** Everything in `todo.md` is done or partial — nothing there is untouched — while ten of `todo2.md`'s thirteen have no implementation at all. The verdict column cites the command or file that decides it; anything not marked ● became a gap in the catalogue that follows.

### `docs/todo.md`

| # | Item | Verdict | Evidence | Gap |
| - | ---- | ------- | -------- | --- |
| 1a | CLAUDE.md + constitution explain how to run tests, linters, static analysis correctly first time | ◐ | Both document the toolchain in detail, and `ruff` / `ruff format` / `mypy` all pass clean across the five `src` roots plus `scripts`. But the coverage command CLAUDE.md gives reports **0.00%** and fails the 85% gate when run from the repo root, where every other command in that file is run | **G34** |
| 1b | All tests pass; coverage ≥ 85% | ● | `1946 passed, 16 skipped` across the five Python packages; the 16 skips all carry a `reason=` naming a live PostgreSQL requirement. Frontend `1349 passed` in 126 files. **Every package clears the gate**: backend 86.23%, agents 87.42%, db 96.23%, agent-eval 86.34%, researcher-mcp 87.90%, frontend 91.06% lines / 85.42% branches | — |
| 1c | Fix mutmut or move to another mutation tool; ≥ 85% mutants killed | ◐ | The **tooling** is done and hardened past what was asked: cosmic-ray replaces mutmut, `scripts/run-mutation-safe.sh` isolates runs in a worktree, and three independent guards prevent a repeat of the committed-mutant incident. The **score** is not established — all five `cosmic-ray-survivors.md` files open by disclaiming themselves | **G34** |
| 2a | Swagger/OpenAPI documentation endpoint in the frontend | ● | `swagger-ui-react@^5.17.14`; `/api-docs` route in `App.tsx:43`; backend `GET /api/v1/openapi.json` | — |
| 2b | Frontend uses Material UI | ● | `@mui/material@^5.16.7` + `@emotion`; 92 files use the `sx` prop. Residual inline `style={{…}}` remains, tracked separately | **G33** (residue) |
| 2c | User preferences: password change, 2FA, display preference | ● | `components/preferences/` — `PasswordChangeForm`, `TwoFactorSettings`, `TwoFactorSetupDialog`, `ThemeSelector`; `/preferences` route; `hooks/useTotp.ts` | — |
| 3a | Agent prompt templates cover SE **and AI**; make the field a variable | ◐ | The variable mechanism is real and broad: `build_study_context` → `{{ domain }}` / `{{ study_type }}` → `render_system_message` → `system_message_override`, honoured by 9 of 10 agent classes and wired from 5 jobs. But it only fires when an `Agent` **row** is linked, no rows are seeded, and **9 of the 12 shipped `prompts/*/system.md` name software engineering directly**, while exactly one contains `{{ domain }}` — and only as documentation of a variable it writes for others | **G29** |
| 3b | Templates for any study type, not just SMS _(author-deferred)_ | ◐ | Same mechanism — `_STUDY_TYPE_LABELS` maps the enum to a label for `{{ study_type }}`. Same limitation | **G29** |
| 3c | Admin panel: providers section + available-models section | ● | Feature 005 — `Provider` / `AvailableModel` tables, Providers and Models tabs, Anthropic / OpenAI / Ollama. (vLLM and LM Studio are a separate ask, already **G15**) | — |
| 3d | `Agent` abstraction storing nine named fields | ● | `db/src/db/models/agents.py:169` carries all nine: `id`, `role_name`, `role_description`, `persona_name`, `persona_description`, `persona_svg`, `system_message_template`, `model_id`, `provider_id` | — |
| 3e | Admin agents tab: syntax-highlighted system message, Generate/Update button, guided Create Agent | ◐ | `AgentList` / `AgentForm` / `AgentWizard` / `SystemMessageEditor` all exist and are reachable; `POST /admin/agents/{id}/generate-system-message` is live and the wizard restricts to `AgentTaskType`. **Not syntax-highlighted** — `SystemMessageEditor` is a plain MUI multiline `TextField` and `package.json` carries no highlighting library | **G30** |
| 4a | Graph-based, editable research protocol definition | ● | Feature 010 — `ResearchProtocol` / `ProtocolNode` (23 task types) / typed I/O / `QualityGate` / `NodeAssignee` / `ProtocolEdge`, migration `0018`, four seeded templates | — |
| 4b | Protocols editable textually **and** visually | ● | Dual-pane `ProtocolEditorPage`: `ProtocolGraph` (D3, drag-to-reposition) beside `ProtocolTextEditor` (YAML). Caveat: `EdgeConditionBuilder` is unreachable, so conditional edges are YAML-only — already **G21** | — |

### `docs/todo2.md`

| # | Item | Verdict | Evidence | Gap |
| - | ---- | ------- | -------- | --- |
| 1 | Constitution: file-level doc comments; mutation gate; all tests/lint/static analysis pass including pre-existing | ● | Constitution v1.7.0 added all three (§ Documentation, § Mutation Testing, Development Workflow step 6) and v1.8.0 layered Principle X on top. Enforced, not merely stated: `ruff --select D100` passes across all five `src` roots and `scripts` | — |
| 2a | All workflows based on the SLR workflow, aspects relaxed per type | ✗ | Four independent phase gates, four protocol models, and four hand-written phase maps in `studyTypeDispatch.tsx`. Nothing derives from an SLR base | **G27** |
| 2b | All workflows handle validity / threats to validity | ✗ | Only Rapid has a threats model (`RRThreatToValidity`) and UI. SMS's `ValidityForm.tsx` is unreachable; SLR and Tertiary have neither model nor view | **G27** |
| 2c | All workflows handle data synthesis | ✗ | SLR ●, Rapid ●, Tertiary ● but unreachable, **SMS renders `futureSprintPlaceholder(5)`** | **G27** |
| 2d | All workflows produce a report | ✗ | SLR ●, Tertiary ●, Rapid ● (Evidence Briefing). SMS has only `POST /studies/{id}/export` emitting `svg_only \| json_only \| csv_json \| full_archive` — a data archive, not a report | **G27** |
| 3a | Hunt blog posts via web search; scrape to Markdown with access metadata | ✗ | No web-search capability of any kind in the tree. `scrape_journal` / `scrape_author_page` traverse journal TOCs and author pages, not blogs, and capture no access date or `@online` fields | **G28** |
| 3b | Search Master's theses and doctoral dissertations; download PDF; convert; capture metadata | ✗ | `GreyLiteratureType.DISSERTATION` is a label on a manually-typed row. No ProQuest / EThOS / DART-Europe / NDLTD adapter, no search path | **G28** |
| 3c | Extract from arXiv — download, convert, capture metadata | ✗ | `ArxivSource` exists but is referenced **only by its own unit tests**: absent from `SourceRegistry`, from `sources/__init__.py`, and from `fetch_paper_pdf`'s waterfall. There is no arXiv *search* at all, and `DatabaseIndex` has no arXiv member. **This corrects G3, which marked arXiv ●** | **G28** |
| 3d | UI to select grey literature and its types during search setup | ✗ | `DatabaseSelectionPanel` offers exactly the nine `DatabaseIndex` members and nothing else | **G28** |
| 4 | User avatar, settable in user settings | ✗ | `User` has no avatar column. `SideNav` renders an MUI `Avatar` showing initials. The only avatar code in the tree generates persona SVGs for *agents* | **G31** |
| 5 | Automate agent improvement with DSPy alongside DeepEval | ✗ | DeepEval is present (`agent-eval`, `deepeval>=1.0`). "dspy" appears exactly once in the repository — in `todo2.md` itself | **G32** |
| 6 | Replace inline styles with consolidated per-component styles | ◐ | 80 `style={{` props across 26 files against 92 files using `sx`. Concentrated: `NewStudyWizard` (15), `DiffViewer` (7), `TestRetest` (7) | **G33** |
| 7 | Extract paper metadata and abstract from the index during search | ◐ | `PaperRecord` carries eleven fields including `abstract`, and `_upsert_paper` persists seven. Three are dropped, `Paper.metadata_` is never written, and `source_url` is read under a key the record does not use — so it is **always** `None`. All of it is moot until G25 | **G26** |

### What the intake changed about existing entries

| Entry | Change |
| ----- | ------ |
| **G3** | arXiv row corrected from ● to ✗ — see the entry |
| **G13c** | Broadened: `StudyDatabaseSelection` is ignored on the **full-search** path too, not only the pilot, and the UI hardcodes index names that do not exist |
| **G19**, **G20** | Evidence re-anchored. `StudyPage` no longer branches on `isSLR` / `isRapid`; `17aaab1` moved dispatch into `components/studies/studyTypeDispatch.tsx`. Both verdicts stand unchanged |
| **F2-SF03** | ◐ → ✗. It cannot be partial when no search can return a paper |

---

## Gaps

### G1 — Snowball provenance DAG (F2-SF03) — **blocking, structural**

**Required.** Maintain traceability links for papers found via snowballing. If a previously included paper is later excluded, papers discovered _from_ it must be excluded too — unless they were also reachable from another still-included paper. This implies a DAG.

**Current.** `run_snowball` (`backend/src/backend/jobs/search_job.py:693`) performs iterative bidirectional snowballing with a stopping threshold, dedup, and AI pre-screening against inclusion/exclusion criteria. Discovery works. But `CandidatePaper` (`db/src/db/models/candidate.py:29`) carries only `duplicate_of_id` and `source_seed_import_id` — **there is no edge recording which paper a candidate was discovered from**. `_process_snowball_batch` (`search_job.py:590`) never writes one.

**Consequence.** Retraction cascade is impossible. Excluding an included paper silently orphans its descendants, and there is no way to distinguish a descendant with a second surviving parent from one without.

> **Correction — 2026-08-06.** "Discovery works" was true of the design and false of the code when this was written: `_process_snowball_batch` deduplicated with `Paper.doi > ep.doi` instead of `==`, and its counters ran `added = -1` / `added += 2`. Both were cosmic-ray mutants, repaired in `e47abd9`; the premise now holds. The gap itself is unchanged — the missing discovery edge is structural and has nothing to do with the mutants.

> **Correction — 2026-08-07.** "Discovery works" was still too generous, twice over, and the paths above are stale. Both functions now live in `backend/src/backend/jobs/snowball_job.py` (`1e01097`). More importantly: **`run_snowball` had no enqueue site**, so none of this code had ever run for a user — see [G22](#g22--snowball-sampling-has-no-enqueue-site-f2-sf03--medium-resolved-2026-08-07), closed the same day. And until `d8f6dcf` the screening pass inside it rejected every paper by crashing, because it was handed a `CandidatePaper` that could not produce a title. The structural gap this entry describes is unaffected — but it was never observable before, and only becomes so now that a user can start a snowball run at all.

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
| **arXiv**         | ✗     | See the correction below — `sources/arxiv.py` is neither a search adapter nor reachable |
| IEEE Xplore       | ●     | `sources/ieee.py`                                                                  |
| ACM DL            | ●     | `sources/acm.py`                                                                   |
| Scopus            | ●     | `sources/scopus.py`                                                                |
| **EI Compendex**  | ✗     | No adapter                                                                         |
| ScienceDirect     | ●     | `sources/science_direct.py`                                                        |
| Web of Science    | ●     | `sources/wos.py`                                                                   |
| **Manual search** | ✗     | No code path for author/journal/conference-driven search and venue-site resolution |

Beyond the required eight, adapters also exist for Inspec, Springer, Semantic Scholar, Crossref, OpenAlex, Unpaywall, and Sci-Hub.

> **Correction — 2026-08-07 (arXiv).** The ● above was assigned from the existence of `sources/arxiv.py`, which is exactly the failure mode this document's header warns about. Three checks say otherwise:
>
> - **It is not a search adapter.** `ArxivSource` exposes one method, `fetch_pdf(doi, output_path)`. It has no `search()`, so it cannot satisfy the `DatabaseSource` protocol, and its own docstring says "arXiv source for preprint PDF fetching".
> - **Nothing constructs it.** `grep -rn "ArxivSource" --include=*.py .` returns thirteen hits, **all thirteen in `researcher-mcp/tests/unit/test_sources.py`**. It is absent from `core/registry.py`, from `sources/__init__.py` (which is empty), and from the `fetch_paper_pdf` waterfall, which runs Unpaywall → direct → optional Sci-Hub and never consults it.
> - **A user could not select it if it worked.** `DatabaseIndex` has nine members and arXiv is not among them, so no `StudyDatabaseSelection` row can name it.
>
> This is the same orphan shape as G21, in a third package. The audit that would catch it does not exist: `audit_unreachable_frontend.py` reads only `frontend/src`, and `check_shadowed_modules.py` looks for a different defect. See [Neither oracle sees a backend route](#neither-oracle-sees-a-backend-route) — a class-covered, lint-clean, type-clean module that nothing constructs passes every gate in the repository.
>
> arXiv is now tracked under **[G28](#g28--grey-literature-is-a-manual-register-not-a-discovery-capability-f2-sf03-f3-sf02--high)**, where the todo's arXiv, thesis, and blog requirements sit together.

**Remediation.** EI Compendex is a straightforward adapter (Engineering Village API). arXiv needs a real `search()` against `export.arxiv.org/api/query`, a `DatabaseIndex` member, and registry registration — the PDF half is written. Manual search is a new subsystem: venue → website resolution, then site-specific listing traversal, feeding the same `CandidatePaper` upsert path.

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

> **⚠ Amended 2026-08-07 — what this checker may and may not claim.** The research pass behind
> [`docs/methodology/`](./methodology/) turned up a constraint that changes the feature's framing,
> though not its value.
>
> **PRISMA 2020 states it "should not be used to assess the conduct or methodological quality of
> systematic reviews."** It measures *reporting completeness*. A "PRISMA score" presented as a
> quality or rigour score misuses the standard in precisely the way its authors warn against, so the
> checker must be labelled and surfaced as completeness — "your report does not state X", never "your
> review is weak".
>
> **SEGRESS should be the primary standard here, not PRISMA.** Two reasons. PRISMA 2020's own scope
> is reviews of health-intervention effects and explicitly excludes qualitative synthesis; SEGRESS's
> assessment is that PRISMA alone "will be of very limited value to SE researchers". And SEGRESS is
> **the only standard that marks every item required / optional / not-required per review type** —
> quantitative SR, mapping study, qualitative review, mixed-methods, tertiary. That maps directly onto
> the four study types already modelled, and it matters: a one-size checker would penalise a mapping
> study for omitting a certainty assessment that SEGRESS marks *not required* for it. The full
> per-type applicability table is in
> [`10-reporting-and-evaluation.md`](./methodology/10-reporting-and-evaluation.md).
>
> **For quality, use instruments designed for it.** The corpus supplies two, both cheaper to build
> than a PRISMA checker and neither misusing its source:
> - **DARE** — 4 questions scored Y=1 / P=0.5 / N=0, with full anchors, over data the platform
>   already holds. Note Q4 is a *traceability* check (can a summary be traced to the papers behind
>   it), which is answerable structurally rather than by asking a model. See
>   [`04-tertiary.md`](./methodology/04-tertiary.md).
> - **The Petersen 2015 rubrics** — five scored rubrics for mapping studies. These score **process
>   actions taken**, not report prose, so they need access to recorded execution state rather than the
>   generated report. See [`02-sms.md`](./methodology/02-sms.md).
>
> **Scope note.** "PRISMA-trAIce" remains absent from the corpus reviewed here, so the requirement to
> validate against it is neither confirmed nor costed by this pass.
>
> Net effect on this gap: **unchanged in priority, changed in shape.** It is two features, not one —
> a per-study-type *reporting completeness* checker (SEGRESS), and a *quality* scorer (DARE and the
> Petersen rubrics). Conflating them is the error to avoid.

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

> **Correction — 2026-08-06.** That note was too confident when written. `GET /groups/{group_id}/studies` was gating on `GroupMembership.group_id >= group_id` and `StudyMember.user_id >= current_user.user_id`, so membership in any higher-id group passed the check and the listing returned other members' studies — broken access control, live, while the feature was marked ●. Both are equality again as of `e47abd9`; the note is accurate now. The mechanisms it praises were never the problem, which is the point: sound primitives do not make a system secure if a predicate is wrong.
>
> Separately, the `admin.py` named above is `backend/src/backend/api/v1/admin.py`, which the `admin/` package shadows (G21) — it is never imported. Its three routes match the live package exactly, so the conclusion drawn here is unaffected, but the file to read is `api/v1/admin/__init__.py`.

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

> **Broadened — 2026-08-07.** "`StudyDatabaseSelection` is ignored" was scoped to the pilot. It is ignored **everywhere**. `grep -rn "StudyDatabaseSelection" backend/src/` returns hits in exactly two files, `services/database_selection.py` and the router that mounts it — the table is read only by its own CRUD endpoint. The full-search path takes `search_exec.databases_queried or ["acm", "ieee", "scopus"]` (`search_job.py:453`), and that column is filled straight from the request body (`searches.py:84`), whose default is the same three strings (`searches.py:35`), which `FullSearchControl.tsx:22` also hardcodes as `DEFAULT_DATABASES`. **Feature 006's database-selection panel therefore changes nothing about any search the platform runs.**
>
> Worse, the three strings are not valid index names. `SourceRegistry` registers `ieee_xplore`, `acm_dl`, `scopus`, `web_of_science`, `inspec`, `science_direct`, `springer_link`, `google_scholar`, `semantic_scholar`; `DatabaseIndex` declares the same nine. Of the hardcoded `acm` / `ieee` / `scopus`, **two match nothing**. So even after G25 restores the transport, two thirds of the default fan-out would address databases that do not exist — and `search_papers` records unknown indices in `sources_failed` rather than raising, so the search would still report success.

#### 13d — Two defects in `_fetch_test_search_results` — ✅ **RESOLVED 2026-08-05**

> **Correction — 2026-08-06 (root cause).** Neither "defect" below was written by hand. Both are
> cosmic-ray mutants committed by `ecc32de`, confirmed against that commit's diff:
>
> ```text
> -            if resp.status_code == 200:        →  +            if not resp.status_code > 200:
> -    return set(), 0                            →  +    return set(), 2
> ```
>
> The `2` in `return set(), 2` was never a "magic number" chosen by a developer — it is the
> `NumberReplacer` mutator incrementing a `0`. The reasoning below about intent is therefore
> wrong, though every observation about _behaviour_ is right and the fix stands (it improved on
> the original by adding `TestSearchUnavailableError` and an explicit 2xx range check, which the
> pre-mutation code lacked).
>
> Two consequences worth keeping. First, `test_fetch_test_search_results_returns_empty_on_exception`
> did not "enshrine a defect" — it was written at `a05d09b` on 2026-03-17, two days _after_ the
> corruption, against mutated behaviour. That is the same pattern as
> `test_process_single_candidate_returns_none_when_existing_cp`, corrected in `e47abd9`. When a
> mutant is committed, tests written afterwards calcify it.
>
> Second, and more costly: this was the corruption's **first encounter**, on 2026-08-05. Diagnosed
> as two ordinary defects in one function, it prompted no search for siblings — so the other 60+
> mutants survived another day, until an unrelated read of `search_job.py` on 2026-08-06 turned up
> `Paper.doi > doi` two lines away. See [Committed mutation artifacts](#committed-mutation-artifacts-resolved-2026-08-06).
> The lesson is to ask where a defect came from, not only what it does.

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

What Phase 3 actually renders is `frontend/src/components/phase2/PaperQueue.tsx`, a **read-only** listing: its only controls are Refresh, a filter reset, and pagination.

The backend is complete: `backend/src/backend/api/v1/papers.py:157` onward implements the decisions endpoints, including conflict detection (`_detect_conflict`, `:223`), and is covered by `backend/tests/integration/test_papers_decisions.py`.

**Correction — 2026-08-06.** This entry originally claimed that "there is no control anywhere that starts a screening run, so the job-progress panel can never appear", and attributed a **Run Full Search** control to `PaperQueue`. Both were wrong, and the design pass for [feature 012](./features/012-wire-up-unreachable-workflows.md) found it by reading the code rather than the entry:

- **Run Full Search** exists, but lives in `StudyPage.tsx:436`, not in `PaperQueue`. It POSTs to `/studies/{id}/searches` and feeds the returned `job_id` to `JobProgressPanel`.
- `backend/src/backend/jobs/search_job.py` runs `ScreenerAgent` over every candidate as part of that job. **AI screening is therefore both reachable and observable today.**

What genuinely does not exist is a way to **re-screen an existing candidate set** against revised criteria without re-running the database search — no endpoint, no ARQ job. That is worth having on its own merits (criteria change after a search; re-running the full fan-out is expensive and pollutes provenance), so step 4 below is restated in those terms.

The e2e test named `job progress panel is visible during a screening run` fails only because it looks for a button matching `/run screening/i`; the machinery it is testing is present.

**Remediation.**

| #   | Step                                                                                                                                                                                             |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Mount `ReviewerPanel` in the Phase 3 view, wired to the selected candidate paper.                                                                                                                |
| 2   | Make `PaperQueue` rows selectable so a paper can be sent to the panel.                                                                                                                           |
| 3   | Mount `PaperCard` (or fold its decision history into the panel) so prior decisions and conflicts are visible.                                                                                    |
| 4   | Add `POST /studies/{id}/screening-runs` + an ARQ job to re-screen existing candidates against current criteria, recording a **new** `Reviewer` round rather than overwriting prior AI decisions. |
| 5   | Un-`fixme` the three tests in `frontend/e2e/screen-paper.spec.ts`.                                                                                                                               |

**Cost.** Medium — steps 1–3 are wiring plus selection state over components and endpoints that already exist. Step 4 is the only genuinely new work, and is smaller than first described: the trigger, the progress panel, and the screening agent all exist; what is new is invoking the agent over a candidate set that is already in the database.

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

The cause: `StudyPage` branches on `isSLR` and `isRapid` only. There is no `isTertiary`, so a study whose `study_type` is `Tertiary` falls through to the SMS path and renders SMS phase panels. (`App.tsx` also registers no route for `TertiaryStudyPage`, but per the correction below, a route is not the right fix.)

> **Evidence re-anchored — 2026-08-07.** The boolean branching described above is gone. `17aaab1` replaced it with a dispatch table in `frontend/src/components/studies/studyTypeDispatch.tsx`: `STUDY_TYPE_PHASES` maps `"SMS"`, `"SLR"` and `"Rapid"` to a `PhaseMap`, and `renderStudyPhase` resolves `STUDY_TYPE_PHASES[studyType] ?? DEFAULT_PHASE_MAP`. **The gap is unchanged, only relocated**: there is still no `"Tertiary"` key, and `DEFAULT_PHASE_MAP` is `MAPPING_STUDY_PHASES`, so a Tertiary study still silently renders the mapping-study workspace. The audit still reports the same 13 modules. What did change is the shape of the fix — step 1 below is now a map entry rather than a boolean, and that file's own header comment already names the omission and points at task T024.

The backend is live: all **7** `/api/v1/tertiary/*` routes are registered and answer, migration `0017` is applied, and `TertiaryReportService` / `TertiaryExtractionService` are implemented and tested.

**Correction — 2026-08-06.** The design pass for [feature 012](./features/012-wire-up-unreachable-workflows.md) found that two of the four remediation steps below were already done inside the unreachable subtree, that the recommendation in step 2 was backwards, and that the cost line was wrong:

- **Step 3 is already done.** `TertiaryReportPage` is mounted by `Phase5Panel` (`TertiaryStudyPage.tsx:428`), gated on synthesis completion. It is unreachable only because everything above it is.
- **The phase gate already dispatches on study type.** `_PHASE_GATE_DISPATCH[StudyType.TERTIARY] = get_tertiary_unlocked_phases` (`backend/src/backend/api/v1/studies/__init__.py:118`), so `study.unlocked_phases` is already correct for a Tertiary study — no SLR-style extra `usePhases` query is needed.
- **Step 2's recommendation is backwards.** Folding the panels into `StudyPage` is _not_ more consistent with what exists: `TertiaryStudyPage` owns its own `PhaseTabs` and its `Phase1Panel`…`Phase5Panel` are module-private. Folding them in means exporting five internals and rendering two tab bars. The page was written as a host; `StudyPage` should hand off to it wholesale.
- **"No API work" is wrong.** `TertiaryStudyPage` requires a `groupId` prop, which it passes to `SeedImportPanel` → `useGroupStudies` → `GET /api/v1/groups/{groupId}/studies`. **`StudyDetail` does not return `research_group_id`**, and the route is `/studies/:studyId`, so there is no group in the URL to fall back on. Seed import is the substance of Tertiary Phase 2, so this gap cannot be closed by frontend wiring alone.

Net effect: the work is **smaller than described in every respect but one**. There is exactly one missing edge, and adding it makes all thirteen modules reachable at once — but it must be accompanied by a backend field, in the same shape as the `viewer_role` addition in `342fc4b`.

**Remediation.**

| #   | Step                                                                                                                                                                                                                             |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Add `const isTertiary = study?.study_type === 'Tertiary'` to `StudyPage`, render the study header, then hand off wholesale to `<TertiaryStudyPage>` — skipping `StudyPage`'s own tab bar, since the tertiary page owns its tabs. |
| 2   | Add `research_group_id: int` to `StudyDetail` and pass it through as `groupId`, without which seed import cannot function.                                                                                                       |
| 3   | ~~Wire `TertiaryReportPage` to the phase-5 slot.~~ Already done — `Phase5Panel` mounts it.                                                                                                                                       |
| 4   | Add an e2e spec — the workflow currently has no end-to-end coverage, because there is no way to reach it.                                                                                                                        |

**Cost.** Medium — no new components and no migration, but **one backend field is required** (see the correction above). Otherwise this is dispatch wiring over finished parts.

**Interaction.** Until this lands, feature 009 delivers nothing to a user, and its 13 modules cannot be exercised by any test that drives the UI.

---

### G20 — Phases 4 and 5 show a placeholder over finished components (F2-SF06, F2-SF10) — **medium**

**Claim.** For SMS and Tertiary studies, `StudyPage` renders _"Phase 4 content will be available in a future sprint."_ and the same for phase 5, while the components those phases need are written and their endpoints answer.

**Evidence.** `StudyPage.tsx` phase 4 and 5 fall through to placeholder text for `!isSLR && !isRapid`. Unreachable but complete:

> **Evidence re-anchored — 2026-08-07.** As with G19, `17aaab1` moved this. The placeholder is now `futureSprintPlaceholder(phase)` in `components/studies/studyTypeDispatch.tsx`, bound at `MAPPING_STUDY_PHASES[4]` and `[5]`. Because Tertiary falls back to that same map, **the placeholder is what a Tertiary study shows at phases 4 and 5 as well**. Verdict and module list unchanged.

| Module                                   | Purpose                                                                    | Backend                                   |
| ---------------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------- |
| `pages/ExtractionPage.tsx`               | Lists accepted papers, hosts `ExtractionView`, opens `DiffViewer` on a 409 | `GET /studies/{id}/extractions` → **200** |
| `components/phase3/ExtractionView.tsx`   | Per-paper extraction form                                                  | as above                                  |
| `components/shared/DiffViewer.tsx`       | Conflict resolution on concurrent edits                                    | PATCH 409 path                            |
| `components/phase4/ValidityForm.tsx`     | Six validity dimensions, autosave, "Generate with AI" ARQ job              | `GET/PUT /studies/{id}/validity`          |
| `components/phase5/QualityReport.tsx`    | Rubric score cards and prioritised recommendations                         | `GET /studies/{id}/quality-reports`       |
| `components/phase2/MetricsDashboard.tsx` | identified → accepted → rejected → duplicates funnel                       | `GET /studies/{id}/metrics` → **200**     |

**Remediation.** Mount `ExtractionPage` at phase 4 and `QualityReport` at phase 5 for the non-SLR/non-Rapid branch; add `ValidityForm` to the phase-4 view; place `MetricsDashboard` in the phase-2 view. Replace the placeholders.

**Note — 2026-08-06.** `ExtractionPage` takes no props; it reads `useParams<{ studyId: string }>()`. The `StudyPage` route is `studies/:studyId`, so mounting it as a child happens to work — by coincidence of a matching param name, not by design. Give it an optional `studyId` prop that takes precedence over the route param, as `TertiaryReportPage` and the SLR pages already do. Found during the [feature 012](./features/012-wire-up-unreachable-workflows.md) design pass.

**Cost.** Medium — wiring plus deciding the phase-4 layout (paper list beside extraction form).

---

### G21 — Orphaned controls and shadowed modules (F2-SF05) — **low**

**Claim.** Four modules are complete and unreachable inside features that are themselves reachable. Two are frontend controls nothing imports; two are Python files the interpreter never loads.

_Frontend — imported by nothing:_

- `components/slr/QualityScoreForm.tsx` — per-reviewer scoring with a live aggregate. `QualityAssessmentPage` imports `QualityChecklistEditor` but not this, so a reviewer can define a checklist and never score against it.
- `components/protocols/EdgeConditionBuilder.tsx` — builds the conditional triple on a protocol edge. Nothing imports it, so conditional edges cannot be authored in the visual editor (the YAML pane remains the only route).

_Backend — shadowed by a same-named package_ (added 2026-08-06):

A module `X.py` sitting beside a package `X/` in the same directory is dead: Python resolves `import X` to the package every time. Two exist, both stale duplicates of the package that displaced them.

| Dead file                             |   Size | Shadowed by                | Verified                                                |
| ------------------------------------- | -----: | -------------------------- | ------------------------------------------------------- |
| `backend/src/backend/api/v1/admin.py` | 14.5 K | `api/v1/admin/__init__.py` | `backend.api.v1.admin.__file__` resolves to the package |
| `db/src/db/models.py`                 |  5.4 K | `db/models/__init__.py`    | `db.models.__file__` resolves to the package            |

`admin.py` declares its own `APIRouter(prefix="/admin")` carrying the same three routes as the live package, and `models.py` redefines `StudyType`, `StudyStatus`, `InclusionStatus`, `Study`, `Paper` and `StudyPaper` — every one of which also exists in the package. Editing either file has no effect on the running system, which is the trap: they look exactly like the code you are changing.

`admin.py` is also where a copy-pasted `GroupMembership.role <= GroupRole.ADMIN` mutant was found (see [Committed mutation artifacts](#committed-mutation-artifacts-resolved-2026-08-06)). It was repaired in `e47abd9` alongside the live copies rather than left to mislead the next reader.

**Origin — corrected 2026-08-06.** This section first called both files "genuine forks rather than leftovers of a half-finished move". The git history says the opposite, and each arrived a different way:

- `admin.py` was created at `f812348` (2026-03-08) as an ordinary module. Feature 005 (`a05d09b`, 2026-03-17) converted it into a package and **left the original in place** — a half-finished move, precisely what the earlier wording denied.
- `db/models.py` was created at `f812348` in the **same commit** as the package that shadows it. It was never imported, not once, in its entire existence.

The distinction matters for the fix: neither file holds newer work, so both are safe to delete outright rather than merge.

**Remediation — ✅ done 2026-08-06.**

- Both files deleted. Verified safe first: identical top-level symbol sets, and the live package a strict superset on columns (`Study` 18 vs 13, `Paper` 16 vs 13, `StudyPaper` 7 vs 7, nothing unique to the dead copies). No `pyproject.toml`, coverage, mypy or cosmic-ray config referenced either by path. After deletion `backend.api.v1.admin` and `db.models` still resolve, the app serves its routes, and 1253 backend + db tests pass.
- `scripts/check_shadowed_modules.py` added — the Python counterpart to `audit_unreachable_frontend.py`, run in pre-commit and CI, with 9 tests in `scripts/tests/`. It scans the whole tree rather than staged files, because the defect is a _relationship between two paths_: staging only one of them still creates it.

Frontend items remain open: mount `QualityScoreForm` in `QualityAssessmentPage` beneath the checklist, and surface `EdgeConditionBuilder` from the protocol editor when an edge is selected.

**Cost.** Low. The backend half is complete; the two frontend mounts remain.

---

### G22 — Snowball sampling has no enqueue site (F2-SF03) — **medium** _(resolved 2026-08-07)_

**Claim.** `run_snowball` was a complete, registered ARQ job that nothing could start. It appears in `WorkerSettings.functions` (`backend/src/backend/jobs/worker.py:49`) and nowhere else: no endpoint enqueues it, no service calls it, no frontend control reaches it.

```bash
grep -rn "run_snowball" --include=*.py backend/src/
# jobs/worker.py:23  — the import
# jobs/worker.py:49  — the registration
```

This is the same defect class as G18–G20 — finished code no user can reach — on the side of the codebase where `scripts/audit_unreachable_frontend.py` cannot see it. That script walks the frontend import graph from `main.tsx`; a backend job is reachable only via an HTTP route, which no import graph models. `scripts/check_shadowed_modules.py` does not catch it either: `snowball_job.py` is imported, just never invoked.

**Why it matters.** Backward and forward snowballing is a named requirement of the search phase, and the implementation is real — iterative citation walking, a stopping threshold, dedup, and AI pre-screening. `Study.snowball_threshold` is a column users can set, so the platform asks for a parameter governing a capability it never runs.

**G1** (no discovery edge recorded per snowballed candidate) was written against this job as though it ran. It does not. G1 remains correct as a structural gap, but its symptom cannot be observed until this one is closed — and its opening line, "Discovery works", is true only of code that is never executed.

**Remediation — ✅ done 2026-08-07.**

- `POST /studies/{id}/snowball` in `backend/src/backend/api/v1/searches.py`, on the router that already carries `start_full_search`. Creates the `SearchExecution` and `BackgroundJob`, then enqueues `run_snowball` with the five arguments its signature needs. `202 {job_id, search_execution_id, seed_count}`.
- **Seeds default to the study's accepted papers.** That is what snowballing means in a mapping study — walk citations from the set that survived screening — and it is the only default a reviewer cannot get wrong. Explicit `paper_dois` override it; papers without a DOI are skipped, since neither `get_references` nor `get_citations` can resolve one.
- **`409` naming the blocking run** while any `FULL_SEARCH` or `SNOWBALL_SEARCH` job is non-terminal, per FR-026. The payload carries `blocking_job_id` and `blocking_job_type`, so the UI can say which run is in the way rather than only that something is.
- **`422` rather than an empty run** when there is nothing to snowball from. A run over zero seeds would complete instantly reporting zero new papers, which reads exactly like a search that found nothing.
- `phase_tag` follows the direction (`backward-search` / `forward-search`). One tag for both would merge them in the PRISMA funnel.
- `components/phase2/SnowballControls.tsx`, mounted in `renderSearchAndScreen` beside "Run Full Search". Both refusals are surfaced in an alert rather than swallowed — a `409` and a `422` are ordinary outcomes here, and hiding them leaves a button that appears to do nothing. Reachable from `main.tsx`; the audit count is unchanged at 23.
- `_resolve_search_string` extracted, since `start_full_search` held the same fallback inline (Principle II).
- 16 integration tests over the endpoint, 10 component tests over the control.

**Guard made bidirectional — 2026-08-07.** It first landed one-directional: a snowball was refused while a full search ran, but not the reverse. `start_full_search` now calls the same `_reject_if_screening_in_flight`, so either order is refused with the same `409` payload. That made a second defect load-bearing — the full-search button's `catch { /* error handled by user */ }` discarded every failure, and a `409` is now an ordinary answer there — so the button moved into `FullSearchControl.tsx`, which surfaces refusals the way `SnowballControls` does. 8 further integration tests, 7 component tests.

**Follow-on.** DOI-less papers are excluded from snowballing entirely; see [G24](#g24--snowballing-skips-papers-without-a-doi-f2-sf03--medium).

---

### G23 — Admin job retry enqueues jobs that cannot run (F3-SF01) — **medium**

**Claim.** `POST /admin/jobs/{id}/retry` returns `200` with a new job id for jobs that will never execute. `_arq_function_for_type` (`backend/src/backend/api/v1/admin/__init__.py:428`) maps a `JobType` to an ARQ function name, and the endpoint enqueues it as `redis.enqueue_job(arq_function, job.study_id, new_job_id)`. Three things are wrong, independently.

_1. Two names are not registered functions._

| `JobType`         | Mapped name           | Registered in `WorkerSettings.functions` |
| ----------------- | --------------------- | ---------------------------------------- |
| `SNOWBALL_SEARCH` | `run_snowball_search` | ✗ — the function is `run_snowball`       |
| `TEST_SEARCH`     | absent → fallback     | ✗ — the fallback is `run_generic_job`    |

`TEST_SEARCH` is missing from the map entirely, so it takes the `run_generic_job` default, and no such function exists anywhere in the repository.

_2. The argument list matches no job's signature._ Every registered job takes `(ctx, study_id, …)` with a job-specific tail: `run_full_search(ctx, study_id, search_execution_id: int)`, `run_snowball(ctx, study_id, phase_tag, paper_dois, direction, search_execution_id)`. Retry passes `(study_id, new_job_id)` for all of them, so even the six correctly-named entries either receive a UUID string where an integer `search_execution_id` is expected, or too few arguments outright.

_3. The endpoint reports success regardless._ `enqueue_job` accepts an arbitrary function name, so the call returns and the endpoint responds `200 {new_job_id}`. The failure surfaces later in the worker, against a different job row than the one the operator was looking at — or not at all.

**Why it matters.** The user-visible behaviour is worse than a broken button: an administrator retries a failed job, is told it succeeded, and nothing happens. This is a silent failure of the same shape as the screening swallow — an operation reporting a result it did not achieve.

It also means job retry has no test that runs a retried job. The existing tests assert the endpoint's response, which is precisely the part that is right.

**Fix.** Derive the function name from the registration rather than restating it — a `JobType` → callable map keyed on the imported functions, so a rename breaks at import time instead of at retry time, and a missing entry raises `KeyError` rather than yielding a plausible-looking string. Reconstruct each job's real arguments from the original `BackgroundJob` row, which is the only place a retry can learn what the first attempt was called with; `run_snowball` needs four values the row does not currently carry, so retry for that type stays unsupported until they are recorded. Cover it with a test that retries a failed job and asserts the worker dispatches it.

**Cost.** Medium. The dispatch map is small; reconstructing arguments needs the job rows to record what each job was invoked with.

---

### G24 — Snowballing skips papers without a DOI (F2-SF03) — **medium**

**Claim.** Both snowball directions are DOI-keyed, so a paper without one is silently excluded from the walk. `_accepted_paper_dois` filters on `Paper.doi IS NOT NULL` (`api/v1/searches.py`), and it has to: `get_references` requests `/paper/DOI:{doi}/references` from Semantic Scholar and falls back to CrossRef `works/{doi}`, while `get_citations` is the same shape (`researcher-mcp/src/researcher_mcp/tools/snowball.py`). Neither accepts a title.

**Why it matters.** The excluded papers are not a random sample. Grey literature, technical reports, theses, workshop proceedings and older conference papers are exactly what lacks a registered DOI — and grey literature is a named requirement (G7, and the Rapid Review workflow's whole premise). A snowball that quietly walks only the DOI-bearing subset reports a citation neighbourhood narrower than the study's own accepted set, with nothing in the UI saying so. The seed count now returned by `POST /studies/{id}/snowball` makes the shortfall visible for the first time, but does not explain it.

**Both directions are recoverable without a DOI, by different routes.**

_Backward (references) — from a stored copy._ If the paper's full text was retrieved, its reference list can be extracted directly rather than asked for. The columns already exist: `Paper.full_text_markdown`, `full_text_source`, and `full_text_converted_at` were added by feature 006, populated via `fetch_paper_pdf` (Unpaywall, then optionally Sci-Hub) and `convert_pdf_to_markdown` (`markitdown`). A reference-section parser over that Markdown yields titles, and each title resolves to a `PaperRecord` through the existing `search_papers` fan-out. This is strictly better than the DOI path for the papers it covers, because it reports what the authors actually cited rather than what an index recorded.

_Forward (citations) — resolve to some other identifier first._ **A DOI is not the only key a citation index accepts**, and the general shape of the fix is: match the paper by title and authors, obtain whatever identifier that index uses, then ask for citations by that identifier. Which index to prefer is an open question and **needs a research spike before implementation** — the candidates below differ in coverage, licensing, and rate limits, and no one of them dominates.

| Route                | Identifier reached                                             | Already in the repo                                   | Notes                                                                                          |
| -------------------- | -------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Semantic Scholar** | `paperId` (an S2 hash, **not** a DOI) via `/paper/search`      | `SemanticScholarSource.search_papers`, `get_paper`    | Likely the strongest first candidate: already the primary source for DOI-keyed snowballing, so the citation shape is known. `/paper/{id}/citations` accessor is what is missing. Also accepts `CorpusId:`, `arXiv:`, `PMID:`, `ACL:`, `MAG:` prefixes |
| **OpenAlex**         | Work ID via title search                                       | `sources/open_alex.py`                                | `referenced_works` and `cited_by_api_url` are on the record itself. CC0, generous limits, strong coverage of non-DOI grey literature |
| **Crossref**         | DOI recovered by bibliographic query                            | `sources/crossref.py`                                 | Not a citation index, but can *recover* a DOI from title plus authors, after which the existing DOI path applies unchanged. Cheapest to try |
| **arXiv**            | arXiv ID                                                        | `sources/arxiv.py`                                    | Narrow but exact for preprints, which are a large slice of what lacks a DOI |
| **Google Scholar**   | Scholar cluster id, then `citedby`                              | `GoogleScholarSource` (`scholarly`, `SCHOLARLY_PROXY_URL`) | Broadest coverage and the worst citizen: aggressive rate limiting, datacentre-IP blocking, and terms that discourage automation. Treat as a last resort, not the design centre |

Crossref deserves separating from the rest: recovering a DOI turns the problem back into the one already solved, so it should be attempted before any citation index is chosen. Only papers that genuinely have no DOI anywhere need the alternative-identifier path.

**Research needed.** Measure, on a sample of this project's own accepted-but-DOI-less papers: how many each route resolves, how the returned citation sets overlap, and how they compare against a DOI-bearing control walked both ways. The answer decides whether one source suffices, several are merged the way `search_papers` already fans out across nine databases, or the route is chosen per paper by what identifiers it has.

**Sketch.**

- Add a `get_references_from_full_text` MCP tool reading `Paper.full_text_markdown`, and a `get_citations_by_title` tool whose backing source is chosen by the spike above rather than fixed in advance.
- Widen `_accepted_paper_dois` into a seed resolver returning a discriminated seed — DOI, stored full text, or title-and-authors — and let `run_snowball` dispatch per seed rather than requiring one identifier for all of them.
- Report coverage on the response: how many accepted papers were reachable, by which route, and how many by none. FR-024's distinction between *assessed* and *never assessed* applies here too — a paper skipped for want of an identifier is not a paper with no references.

**Risks.** Every candidate source rate-limits, and Scholar also blocks datacentre IPs — which is why `SCHOLARLY_PROXY_URL` exists. Whichever is chosen, **treat a block or a throttle as an unavailability error rather than an empty citation list**, exactly as `TestSearchUnavailableError` and `ScreeningUnavailableError` do elsewhere; a paper reported as uncited because the index refused the request is the same defect class as a paper rejected because the screener timed out. Title matching is also fuzzy in a way DOI lookup is not, so a match threshold and a record of which route produced each edge both belong in the design. Reference-list extraction from converted Markdown is lossy and needs its accuracy measured against a DOI-bearing sample before it is trusted — the same paper walked both ways is the natural check.

**Cost.** Medium. Two MCP tools and a seed resolver; the storage, the converter, and the Scholar client are all in place.

---

### G25 — The backend addresses researcher-mcp over an HTTP API that server does not serve (F2-SF03, F2-SF06, F3-SF02) — **critical, blocking**

**Claim.** Every call the backend makes to researcher-mcp targets a URL that returns 404. The search subsystem, full-text retrieval, and both snowball directions all run through those calls. Four of the five call sites swallow the failure and report success.

**Evidence — the server's entire route table is one path.** `researcher-mcp/src/researcher_mcp/server.py:85` runs `uvicorn.run(mcp.http_app(), host="0.0.0.0", port=8002)`. `mcp.http_app()` is FastMCP's MCP transport, not a REST façade. Enumerated rather than assumed:

```text
$ uv run --package sms-researcher-mcp python -c \
    "from researcher_mcp.server import mcp; print([r.path for r in mcp.http_app().routes])"
['/mcp']
```

FastMCP 3.4.5. There is no `/tools/<name>`, and no `/health`. `grep -rn "custom_route\|FastAPI\|APIRouter" researcher-mcp/src/` returns nothing, so no shim adds them.

**Evidence — what the backend asks for.** Five call sites, all built from `settings.researcher_mcp_url`:

| # | Call site | URL | On failure |
| - | --------- | --- | ---------- |
| 1 | `jobs/search_job.py:169` — pilot search | `POST {base}/tools/search_papers` | Raises `TestSearchUnavailableError` → job `FAILED`. **The only loud one**, and it landed by accident: G13d added it to fix a different defect |
| 2 | `jobs/search_job.py:232` — full search | `POST {base}/tools/search_papers` | `if resp.status_code == 200` is false → `return []`. The sweep completes over zero papers and the run is marked successful |
| 3 | `jobs/extraction_job.py:154` — full text | `POST {base}/tools/fetch_paper_pdf` | Same guard → falls through to `paper.abstract or paper.title`. Extraction runs on the abstract and `full_text_available` stays `False` |
| 4 | `jobs/snowball_job.py:48` — citation walk | `POST {base}/tools/{get_references\|get_citations}` | Same guard → `return []`. The walk reports zero new papers for every seed |
| 5 | `api/v1/admin/__init__.py:205` — health probe | `GET {base}/health` | 404 ≠ 200 → the service is permanently reported `degraded` |

`docker-compose.yml:89` compounds it: `curl -f http://localhost:8002/health` can never pass, so the container never reaches `healthy`. Nothing declares `depends_on: researcher-mcp`, so this mislabels rather than blocks — but it means the one signal an operator would check has been red since the service was written.

**Two further mismatches sit behind the first**, so fixing the transport alone is not sufficient:

- **Wrong parameter name.** All three `search_papers` calls send `{"query", "databases", "max_results"}`. The tool's signature is `search_papers(query, indices, max_results, year_from, year_to)` (`tools/search.py:177`). There is no `databases` parameter.
- **Wrong index names.** The defaults are `["acm", "ieee", "scopus"]`; the registry keys are `acm_dl`, `ieee_xplore`, `scopus`. Two of three name nothing. See the broadened note on [G13c](#13c--piloting-is-single-aggregate-not-per-database).

**Why nothing caught it.** `grep -rl "tools/search_papers" backend/tests/ researcher-mcp/tests/` returns **no files**. Every backend test that exercises these jobs mocks `httpx` at the client boundary, so the tests assert the shape of a response the server has never produced. The two packages are tested thoroughly and independently, and nothing tests the seam between them — which is exactly where the contract lives. Both sides also pass `ruff` and `mypy` cleanly, because a URL string is opaque to both.

**Consequence.** This subsumes several existing entries. G13's piloting loop cannot be evaluated because pilots cannot run. G22 delivered a snowball trigger that reaches a walk returning nothing. G24's DOI-less exclusion is invisible beneath a walk that excludes everything. And F2-SF03 is not partially met — **no database search in this platform has ever returned a paper through this path.**

**Fix.**

| Step | Change | Size |
| ---- | ------ | ---- |
| 1 | Decide the seam deliberately: either speak MCP from the backend (an MCP client against `/mcp`, which is what `core/mcp_client.py` in `agents` already implies) or give researcher-mcp explicit `@mcp.custom_route` REST endpoints beside the MCP app. The second is smaller and keeps the five call sites; the first is the contract the server was built to expose | Medium |
| 2 | Add `/health` on whichever surface is chosen, and point the compose healthcheck at it | Trivial |
| 3 | Rename `databases` → `indices` at all three call sites | Trivial |
| 4 | Replace the `["acm", "ieee", "scopus"]` defaults — in `search_job.py`, `searches.py`, and `FullSearchControl.tsx` — with `DatabaseIndex` values sourced from `StudyDatabaseSelection` (G13c step 7) | Small |
| 5 | **One contract test that starts the real researcher-mcp app and calls it from the backend's client code.** Everything above is a symptom of its absence; without it the next rename reintroduces the same class | Medium |
| 6 | Replace the four `if resp.status_code == 200: … return []` guards with explicit unavailability errors, as `TestSearchUnavailableError` and `ScreeningUnavailableError` already do | Small |

**Cost.** Medium, and it is the highest-priority item in this document — every other search gap is unobservable until it lands.

---

### G26 — Search result metadata is lost at ingest (F2-SF03) — **low, mechanical**

**Required** (`todo2.md`, "Paper Metadata"). During search, extract the paper metadata and the abstract, where the index supplies them.

**Current.** The retrieval half is right and the persistence half leaks. `PaperRecord` (`researcher-mcp/src/researcher_mcp/sources/base.py:36`) normalises eleven fields across every adapter — `doi`, `title`, `abstract`, `authors`, `year`, `venue`, `venue_type`, `url`, `open_access`, `source_database`, `raw_id`. `_upsert_paper` (`backend/src/backend/jobs/screening_pipeline.py:87`) persists seven of them.

| Field | Fate |
| ----- | ---- |
| `title`, `abstract`, `doi`, `authors`, `year`, `venue` | ● Persisted. **The abstract is captured** — the todo's main ask is met |
| `url` | ✗ **Silently dropped.** The code reads `paper_data.get("source_url")`, but the record's field is `url`. `Paper.source_url` is therefore always `None` |
| `venue_type`, `open_access`, `raw_id` | ✗ Dropped — no column, and none is added |
| `Paper.metadata_` | ✗ Never written, though its column comment is "Flexible bibliographic fields" — the obvious home for the three above |

The `source_url` line is the instructive one: a `.get()` against a key that is never present cannot fail, cannot warn, and cannot be caught by a type checker, because both sides are `dict[str, Any]` across a JSON boundary. It reads as deliberate.

**Consequence.** Beyond the empty column, the dropped fields are ones later phases want: `venue_type` is the natural discriminator for the PRISMA grey-literature arm (G14 step 2), `open_access` predicts whether `fetch_paper_pdf` will succeed, and `raw_id` is precisely the non-DOI identifier G24 needs for forward snowballing. Three gaps are each proposing to recover a value the search already had and threw away.

**Fix.** Correct the key to `url`; add `venue_type` and `open_access` as columns (both are small and queried) and put `raw_id` alongside `source_database` in `metadata_`; parse the MCP response into `PaperRecord` on the backend side rather than passing a raw `dict`, so the next field mismatch is a validation error instead of a `None`.

**Cost.** Low — one migration and one function. Blocked behind **G25**: until the transport works there is no `paper_data` to persist.

---

### G27 — The four workflows are parallel implementations, not one relaxed base (F3-SF04, F2-SF09, F2-SF10) — **high, structural**

**Required** (`todo2.md`, "Unify the Workflows"). All workflows derive from the SLR workflow with aspects turned off or relaxed for SMS, Rapid Review, and Tertiary. All four handle validity and threats to validity, all four handle data synthesis, and all four produce a report.

**Current.** Four independent implementations that share a `Study` row and little else.

| Layer | SMS | SLR | Rapid | Tertiary |
| ----- | --- | --- | ----- | -------- |
| Phase gate | `phase_gate.py` | `slr_phase_gate.py` | `rr_phase_gate.py` | `tertiary_phase_gate.py` |
| Protocol model | reuses `ReviewProtocol` | `ReviewProtocol` | `RapidReviewProtocol` | `TertiaryStudyProtocol` |
| Frontend phases | `MAPPING_STUDY_PHASES` | `SLR_PHASES` | `RAPID_PHASES` | none — falls back to SMS (G19) |
| API prefix | `/studies/…` | `/slr/…` | `/rapid/…` | `/tertiary/…` |

Nothing is derived from anything. `studyTypeDispatch.tsx` is an honest map of four hand-written column definitions, and its header comment says so.

**Against the three specific requirements:**

| Requirement | SMS | SLR | Rapid | Tertiary |
| ----------- | --- | --- | ----- | -------- |
| Validity / threats to validity | ◐ `PUT /studies/{id}/validity` writes six Petersen dimensions to `Study.validity`, but `phase4/ValidityForm.tsx` is **unreachable** (G20) | ✗ no model, no view | ● `RRThreatToValidity`, auto-created from QA mode, with a UI | ✗ none |
| Data synthesis | ✗ phase 5 renders `futureSprintPlaceholder(5)` | ● `SynthesisPage`, three strategies | ● `RRNarrativeSynthesisSection` | ● reuses `slr/synthesisApi` — but unreachable |
| A report | ✗ only `POST /studies/{id}/export` → `svg_only \| json_only \| csv_json \| full_archive`, a data archive | ● `GET /slr/studies/{id}/export/slr-report` in Markdown / LaTeX / JSON / CSV | ● Evidence Briefing, HTML + PDF, with share tokens | ● `GET /tertiary/studies/{id}/report` — but unreachable |

**SMS is the outlier on all three**, which is worth stating plainly given the repository is named for it: the mapping-study workflow — the platform's original and default study type — ends at screening. Phases 4 and 5 are placeholders, and what it can emit is a chart bundle.

**Note the ordering with feature 012.** Two of the ✗ cells above are *reachability*, not absence: SMS validity and the entire Tertiary column are written and answer. Feature 012 converts those to ● without any new synthesis or report work. The genuinely missing pieces after 012 lands are SMS synthesis, an SMS report, SLR validity, and Tertiary validity.

**Fix.** Two orders are possible and they differ in cost.

- **Bottom-up (cheaper, recommended).** Land feature 012; then add SMS synthesis and an `SMSReportService` modelled on `slr_report_service.py`; then generalise validity into one study-type-agnostic `ThreatToValidity` model, migrating `RRThreatToValidity` into it. Each step delivers on its own.
- **Top-down (what the todo literally asks).** Define an SLR-shaped base workflow with per-type capability flags — `requires_quality_assessment`, `requires_dual_screening`, `synthesis_approaches`, `report_template` — and re-express all four gates and phase maps against it. Structurally right, and it touches every phase gate, every protocol model, and all four frontend phase maps at once.

The bottom-up route reaches the same feature matrix; only the top-down route makes a fifth study type cheap. That is the actual decision, and it is worth taking explicitly rather than by default.

**Cost.** High for the top-down form. Medium for the bottom-up form, and much of it is already paid by feature 012.

---

### G28 — Grey literature is a manual register, not a discovery capability (F2-SF03, F3-SF02) — **high**

**Required** (`todo2.md`, "Grey Literature"). Find relevant blog posts by web search and scrape them to Markdown with access metadata; search Master's theses and doctoral dissertations, download and convert the PDFs; extract from arXiv likewise; and let a user choose grey-literature types when setting up the search.

**Current.** `GreyLiteratureSource` (`db/src/db/models/slr.py:446`) is a hand-typed row: `source_type`, `title`, `authors`, `year`, `url`, `description`, with `GreyLiteratureType = {technical_report, dissertation, rejected_publication, work_in_progress}`. CRUD endpoints and a `GreyLiteraturePanel` exist. **It records what a researcher found elsewhere. It finds nothing.**

| Requirement | State | Detail |
| ----------- | ----- | ------ |
| Blog discovery by web search | ✗ | No web-search capability anywhere: `grep -rniE "\b(web_search\|duckduckgo\|serpapi\|tavily\|brave.search\|bing)\b"` over all five packages returns nothing |
| Blog scraping to Markdown | ◐ | The parts exist and are not connected. `tools/scraper.py` fetches HTML with BeautifulSoup, but targets journal TOCs and author pages; `convert_paper_to_markdown` (`markitdown`) and `convert_url_to_markdown` handle the conversion |
| Web-citation metadata (access date, post author, title) | ✗ | Nothing captures BibTeX `@online` fields. `Paper` has no access-date column, and `urldate` is the one field a web citation cannot be reconstructed without after the fact |
| Thesis / dissertation search | ✗ | No ProQuest, EThOS, DART-Europe, NDLTD, or OpenAIRE adapter. `DISSERTATION` is a label on a manual row |
| arXiv | ✗ | `ArxivSource` fetches PDFs by DOI and is constructed only by its own tests — see the correction under [G3](#g3--missing-search-modalities-f2-sf03--medium). No arXiv search; not a `DatabaseIndex` member |
| UI to select grey-literature types during search setup | ✗ | `DatabaseSelectionPanel` renders exactly the nine `DatabaseIndex` members |

**Why it matters beyond the todo.** Grey literature is load-bearing in three places already catalogued. G7 names Garousi/Rainer/Yasin as unencoded guidelines. G14 needs a grey-literature arm counted separately to select the PRISMA MLR base flow, and `Study.includes_grey_literature` is proposed there. G24 identifies exactly this population — grey literature, reports, theses, older proceedings — as what snowballing silently skips for want of a DOI. **The same set of documents is missing from search, from the PRISMA diagram, and from the citation walk**, and each entry proposes to solve it locally. They should be designed as one provenance model.

**Fix sketch.**

| Step | Change | Size |
| ---- | ------ | ---- |
| 1 | Extend `DatabaseIndex` with `arxiv`, and give `ArxivSource` a real `search()` against `export.arxiv.org/api/query` — its PDF half is written and its metadata is rich (authors, categories, versions) | Small |
| 2 | Add a thesis source. OpenAIRE and DART-Europe are open APIs; NDLTD aggregates broadly; ProQuest needs a licence, so it should not be the first choice | Medium |
| 3 | Add a `venue_type`-style provenance discriminator on `CandidatePaper` — the same field G14 step 2 needs — so grey records are countable through the funnel | Small + migration |
| 4 | Add `@online` metadata columns (`accessed_at`, `site_name`, `post_author`) for web sources, populated at fetch time. **Access date must be stamped on retrieval**; it is unrecoverable later | Small + migration |
| 5 | Add a web-search source behind the `DatabaseSource` protocol, then reuse `scrape_journal`'s fetch-and-parse path for the discovered pages | Medium |
| 6 | Group the grey-literature indices in `DatabaseSelectionPanel` under their own heading, so the type selection the todo asks for is the index selection that already exists | Small |

Steps 1 and 6 alone satisfy the arXiv requirement and give the UI something to select, and neither depends on the rest.

**Cost.** High in aggregate, but it decomposes cleanly and step 1 is a day.

---

### G29 — Shipped agent prompts hardcode SMS and Software Engineering (F2-SF01) — **medium**

**Required** (`todo.md`, "Models and Agents"). Agent prompt templates should express expertise in systematic mapping studies for **Software Engineering and Artificial Intelligence** — with the field ideally a variable — and later generalise to any study type.

**Current.** The parameterisation exists and the defaults do not use it.

*What works.* `build_study_context` (`services/agent_service.py:279`) derives `domain` from `Study.topic` and `study_type` from a label map; `render_system_message` renders an `Agent.system_message_template` with `role_name`, `role_description`, `persona_name`, `persona_description`, `domain`, `study_type`; the result is passed as `system_message_override`, honoured by **9 of 10** agent classes and wired from five jobs (screening, extraction, validity, quality, results). `SystemMessageEditor` lists all six variables. This is a real answer to "make the field a variable".

*What does not.* The override fires only when a `Reviewer` row carries an `agent_id`. `Agent` rows are created **only** through `POST /admin/agents` — nothing seeds them, and neither `scripts/seed_e2e_user.py` nor any migration creates one. On a fresh install every agent therefore runs its file-backed prompt. There are 12 such files, and **9 of them name software engineering directly**:

| Prompt | Line |
| ------ | ---- |
| `librarian/system.md:3` | "specialising in systematic mapping studies in software engineering" |
| `domain_modeler/system.md:3` | "specialising in systematic mapping studies in software engineering" |
| `expert/system.md:3` | "a domain expert in software engineering research … for a systematic mapping study" |
| `quality_judge/system.md:3` | "for systematic mapping studies (SMS) in software engineering research" |
| `validity/system.md:3` | "specialising in systematic mapping studies (SMS) in software engineering" |
| `extractor`, `synthesiser`, `screener`, `agent_generator` | also name software engineering |
| `protocol_reviewer`, `narrative_synthesiser`, `search_builder` | the remaining three — no domain named, but no variable either |

Counted exactly:

```text
$ ls agents/src/agents/prompts/*/system.md | wc -l                       # 12
$ grep -ril "software engineering" agents/src/agents/prompts/*/system.md # 9
$ grep -rl  "{{ domain"            agents/src/agents/prompts/*/system.md # 1
```

That single file is `agent_generator/system.md`, and it does not consume `{{ domain }}` — it *documents* the variable for the templates it writes, naming "Software Engineering and Artificial Intelligence" as an example value. **No prompt the platform actually runs is domain-parameterised, and Artificial Intelligence appears in no other prompt at all.** `SearchStringBuilderAgent` is additionally the one class with no `system_message_override` parameter, so its prompt cannot be overridden even with an `Agent` row.

**Consequence.** A user running the platform over an AI, HCI, or security corpus gets agents that tell the model they are software-engineering specialists. The system prompt is where domain framing does the most work, so this biases screening, extraction, and quality judgement — quietly, and in a way no test detects, because every test asserts structure rather than framing.

**Fix.**

1. Parameterise the twelve prompt files on `{{ domain }}` and `{{ study_type }}`, with `PromptLoader` supplying defaults when no study context is present. This alone closes the todo, because the file-backed path becomes domain-aware without needing an `Agent` row.
2. Seed one `Agent` row per `AgentTaskType` at first run, the way feature 010 seeds four protocol templates — so the DB-backed path is populated rather than empty by default.
3. Add `system_message_override` to `SearchStringBuilderAgent` for parity.
4. Add a test asserting the rendered system message contains the study's topic, for every agent that takes an override.

**Cost.** Low-medium — mostly prompt editing over an existing mechanism.

---

### G30 — The system message editor is not syntax-highlighted (F1-SF04) — **low, mechanical**

**Claim.** `todo.md` asks for "a syntax-highlighted section which allows for the modification of the Agent's System message". `SystemMessageEditor.tsx` is a plain MUI `TextField multiline`; `frontend/package.json` contains no `prism`, `highlight.js`, `codemirror`, or `monaco` dependency.

Everything around it is built: the variable list is rendered as helper text, an undo buffer is wired to `system_message_undo_buffer`, and `POST /admin/agents/{id}/generate-system-message` regenerates the template through `AgentGeneratorAgent`.

**Remediation.** These templates are Jinja2 over Markdown. A dependency-free option is an overlay — a `<pre>` behind a transparent `<textarea>`, highlighting only `{{ … }}` and `{% … %}` — which costs no bundle weight and covers the case that matters, spotting a mistyped variable. If a full editor is wanted, CodeMirror 6 with the Jinja mode is the smaller of the two libraries and lazy-loads cleanly.

Pairs naturally with **G17** (no task-type filter on the agents list): both are single controls in the same admin tab.

**Cost.** Low.

---

### G31 — No user avatar (F3-SF01) — **low, additive**

**Claim.** `todo2.md` asks for a user avatar settable in user settings. `User` (`db/src/db/models/users.py`) has no avatar column, and `GET /me` returns none. `SideNav.tsx:49` renders an MUI `Avatar` containing the user's initials.

The only avatar machinery in the tree belongs to *agents*: `generate_persona_svg` (`services/agent_service.py:798`) asks an LLM for a persona SVG, validates it, and stores it in `Agent.persona_svg`.

**Remediation.** Two shapes, and the choice is about deployment rather than UI. An uploaded image needs the object store G12 already wants for manual PDF upload — worth doing once, for both. A generated identicon or an SVG reusing the `persona_svg` validation path needs no storage at all and is a column plus a form field. Given F1-SF04's self-contained goal, the second is the better default with upload added alongside G12's store.

**Cost.** Low.

---

### G32 — Agent improvement is manual (F1-SF04) — **medium, research-shaped**

**Claim.** `todo2.md` asks for DSPy-based tooling to automate agent improvement alongside the existing DeepEval evaluation. **"dspy" occurs exactly once in the repository — in `todo2.md`.**

The evaluation half is real: `agent-eval` depends on `deepeval>=1.0` and holds `evals/`, `judge/`, `pipelines/`, `commands/`, and a CLI. So the platform can score an agent and cannot act on the score — every prompt improvement is a human editing `system_message_template`.

**What makes this a good fit here, and what does not.** The pieces DSPy needs are unusually well placed. `Agent.system_message_template` is already a first-class, versioned, database-stored artefact with an undo buffer — the optimisation target — and `agent-eval`'s DeepEval metrics are the objective function. `AgentGeneratorAgent` already occupies the "rewrite this prompt" slot that DSPy would take over, with a better search procedure behind it.

What is missing is the training signal. DSPy optimisers need labelled examples — screening decisions with known-correct outcomes, extractions with a gold standard. The platform generates screening decisions constantly, but nothing marks a set as ground truth, and `PaperDecision.is_override` is the closest thing: a human overriding an AI decision is a labelled correction. **Harvesting overrides into an evaluation set is the prerequisite**, and it is worth doing whether or not DSPy follows, because it also gives G4's intra-rater work a corpus.

**Fix sketch.** Build the override-derived gold set first; express one agent — the screener, which has the crispest objective — as a DSPy module over its existing prompt; wire a DeepEval metric as the optimiser's metric; run `BootstrapFewShot` or `MIPROv2` offline and write the winning template back through the existing undo-buffer path so a human approves before it takes effect. Never auto-promote: a prompt regression here silently changes every screening decision that follows.

**Cost.** Medium-high, and genuinely research-shaped — the gold-set question is harder than the DSPy integration.

---

### G33 — Residual inline styles (F1-SF04) — **low**

**Claim.** `todo2.md` asks to move from inline styles to consolidated per-component styles. The MUI migration (feature 004) is done — 92 files use the `sx` prop — but **80 `style={{…}}` props remain across 26 files**.

| File | Count |
| ---- | ----: |
| `components/studies/NewStudyWizard.tsx` | 15 |
| `components/shared/DiffViewer.tsx` | 7 |
| `components/phase2/TestRetest.tsx` | 7 |
| `components/phase1/SeedPapers.tsx` | 6 |
| `phase2/{SearchStringEditor, PaperQueue, CriteriaForm}`, `phase1/PICOForm` | 5 each |
| 18 further files | 1–4 each |

`studyTypeDispatch.tsx` shows the mixed state within a single file: `sx` on the `Box` wrappers, raw `style` on the `<ul>` and `<li>` inside them.

**Why it is not merely cosmetic.** Inline `style` cannot read theme tokens, so hardcoded literals like `background: '#f8fafc'` and `color: '#374151'` do not respond to the Light/Dark/System preference feature 004 shipped. The residue is therefore a live theming defect in the dark palette, not just an inconsistency — which makes the two worst offenders, `NewStudyWizard` and `DiffViewer`, the ones to convert first.

**Remediation.** Convert `style` to `sx` and replace colour literals with `theme.palette` references. An ESLint rule (`react/forbid-dom-props` with `forbid: ['style']`) prevents regression; add it after the conversion, not before, or it fails the build on 80 sites.

**Cost.** Low, and mechanical.

---

### G34 — Verification debt: unestablished mutation scores and a documented command that fails (F1-SF01) — **medium**

Two findings from executing `todo.md`'s first item and `todo2.md`'s constitution item. Both concern the checks the project relies on to know its own state.

**1 — No trustworthy mutation score exists.** `todo.md` asks for ≥ 85% mutants killed, and the constitution now requires it before any feature is marked complete (§ Mutation Testing). The tooling is done and hardened well past the original ask — cosmic-ray replaces mutmut, `run-mutation-safe.sh` isolates each run in a git worktree, and three independent guards prevent a repeat of the committed-mutant incident. But **every score on record disclaims itself**:

| Report | Score | Status |
| ------ | ----- | ------ |
| `backend/cosmic-ray-survivors.md` | — | "⚠ This report is unreliable. Do not cite the score below." |
| `agents`, `db`, `agent-eval`, `researcher-mcp` | 100% each | All four carry: "Re-run via the wrapper before relying on it" |
| `frontend/stryker-survivors.md` | 94.96% | Scope is `src/services/**/*.ts` only — **no component is mutated** |

So the gate is codified, the safety rails are built, and no package has a citable number. Closing this is a matter of running the wrapper five times and recording the results; the guards that make that safe are the part that was hard, and it is finished.

**2 — The documented coverage command reports 0.00% and fails.** ✅ **RESOLVED 2026-08-07.** CLAUDE.md gave:

```bash
uv run --package sms-backend pytest backend/tests/ --cov=src/backend …
```

Every other command in that document runs from the repository root, where `src/backend` does not exist — so `--cov` matches nothing. Reproduced side by side:

```text
# from repo root, exactly as documented
FAIL Required test coverage of 85% not reached. Total coverage: 0.00%
95 passed

# same package, cwd inside it
Required test coverage of 85% reached. Total coverage: 86.34%
95 passed
```

This bears directly on `todo.md`'s first item — "explain how to correctly run all types of tests, linters, and static analysis tools for the project correctly on the first try" — which is otherwise met: `ruff`, `ruff format`, and `mypy` all run clean from the root as documented. Coverage is the one command that does not, and it fails in the worst way: a red gate rather than an error, which reads as *your tests do not cover the code* rather than *you ran this from the wrong directory*. The real figures, measured correctly, are backend 86.23%, agents 87.42%, db 96.23%, agent-eval 86.34%, researcher-mcp 87.90%, frontend 91.06%.

**3 — One oracle is not actually enforced.** CLAUDE.md states "Both oracles run in pre-commit and CI." `check_mutation_artifacts.py` and `check_shadowed_modules.py` do (`.pre-commit-config.yaml:9,19`; `ci.yml:35,40`). **`audit_unreachable_frontend.py` appears in neither** — the constitution's own v1.8.0 sync-impact report records this as a known outstanding violation of Principle X, and CLAUDE.md has not caught up.

> **⚠ The obvious alternative fix is wrong, and was nearly shipped.** Keeping the command at the
> root and passing the module name (`--cov=agent_eval`) appears to work — but each package's
> `branch = true` lives in **its own** `pyproject.toml` and there is no coverage config at the root,
> so that form **silently disables branch coverage**. It reported 87.05% against the correct 86.34%.
> The commands are now `cd`-prefixed subshells, which preserve the configured measurement, write
> `<package>/coverage.xml` to the same path, and leave the caller's working directory unchanged.
> Verified against agent-eval and db before committing.

**Fix.** ~~Make the coverage commands `cd`-prefixed and verify each before committing the doc~~ ✅ done 2026-08-07; wire `audit_unreachable_frontend.py` into pre-commit and CI — with feature 012 landed it should report zero, making it a genuine gate; run `run-mutation-safe.sh` across all five packages plus Stryker and replace the six disclaimed reports; widen Stryker's scope beyond `src/services`.

**Cost.** Low in effort, mostly machine time. The point is that a documented command that fails and an unenforced oracle both erode the evidence base every other entry in this document rests on.

---

## G35–G43 — requirements from the methodology corpus

Added 2026-08-07 from [`docs/methodology/`](./methodology/), chapters 12 and 13. These are
requirements the research establishes that **were not previously in this catalogue**. Requirements
that merely confirm an existing gap are recorded as notes on that gap instead, and listed at the end
of this section.

Each cites the chapter carrying the full treatment.

---

### G35 — The protocol is a preregistration, and is not committed as one (F2-SF01, F2-SF11) — **medium**

**Required.** A review protocol specifies the questions, the rationale, and exactly how the questions
will be answered — which is what preregistration registers. Its value depends on a **commitment
property**: timestamped, immutable, and fixed *before* the data exist. Preregistration is credited
with avoiding three named pathologies — publication bias, p-hacking, and HARKing (hypothesising after
the results are known).

**Current.** `ReviewProtocol`, `RapidReviewProtocol` and `TertiaryStudyProtocol` all carry a status
lifecycle (`draft` → `validated`) and optimistic locking via `version_id`. What does not exist is a
**snapshot**: an immutable, citable record of what the protocol said at the moment it was validated,
against which later divergence can be measured.

**Why it matters.** "Report deviations from the protocol" recurs independently across the corpus —
Kitchenham & Charters, Cartaxo, and SEGRESS all require it. Without a snapshot, a deviation is
something a researcher must remember to disclose. With one, it is **detectable**. That is the
difference between an honour system and a control.

Two ordering constraints follow, and both are enforceable by software in a way a spreadsheet cannot
be:
- **The analysis plan is fixed before the data are analysed.** For a secondary study, the synthesis
  strategy should be committed before extraction completes.
- **Some methods cannot be selected retrospectively at all.** "Research cannot be reconstructed as
  [grounded theory] at write-up", because the method dictates the order of collection and analysis. A
  UI offering synthesis-strategy selection after extraction has finished offers an invalid choice for
  those methods.

**Remediation sketch.** Persist a protocol snapshot when status moves to `validated`; render
deviations as a diff against it; optionally export to the Open Science Framework so the snapshot is
externally verifiable. Gate synthesis-strategy selection on extraction not having completed, for the
strategies where order is constitutive.

**Cost.** Medium. The protocol model and its versioning exist; the snapshot, the diff, and the gate
are new. **See [13 — Open science](./methodology/13-open-science.md) and
[08 Part 4b](./methodology/08-extraction-and-synthesis.md).**

---

### G36 — Stopping rules are not modelled, and unassessed papers are indistinguishable from excluded ones (F2-SF03) — **medium**

**Required.** Exhaustive search is not always the goal — Petersen 2015 reverses the position for
mapping studies, and grey-literature search cannot be exhaustive in principle. A **stopping rule**
must therefore be defined in advance, in one of two forms: **marginal yield** (stop when a
complementary strategy adds fewer than *n* new articles) or **time budget** (fix the effort, include
what was found, **and list the articles that were not considered**). Grey literature adds a third:
**theoretical saturation**.

**Current.** `Study.snowball_threshold` is one instance of a marginal-yield rule, hardcoded to that
one use. There is no general stopping-rule concept, and no way to record papers that were retrieved
but never assessed.

**Why it matters.** **An unassessed paper is not an excluded paper.** Conflating them corrupts the
PRISMA flow (G14) and misrepresents the search: a reader cannot tell whether a paper was judged
irrelevant or simply never reached. FR-024's distinction between *assessed* and *never assessed* — 
already noted under G24 — is the same requirement arriving from a different direction.

**Remediation sketch.** A protocol-level stopping rule with a type, a threshold, and a
saturation option; a `not_assessed` terminal state on `CandidatePaper` distinct from `rejected`; and
both surfaced in the flow diagram and the report.

**Cost.** Small–medium. **See [02](./methodology/02-sms.md), [05](./methodology/05-grey-literature-mlr.md)
and [06](./methodology/06-search-and-selection.md).**

---

### G37 — Reading depth is global, and classification rationale is not captured (F2-SF04, F2-SF06) — **medium**

**Required.** Two related properties of screening and classification:

1. **Reading depth must escalate per paper.** Petersen 2015 is explicit: do not pre-specify that only
   certain parts of a paper may be read; allow more detailed study of papers whose classification is
   unclear. Abstracts are "often misleading and lack important information", so the fallback to
   introduction and conclusion is part of the method, not a workaround.
2. **A rationale must be recorded per classification.** Petersen 2008 recorded a short rationale for
   every category assignment; Kitchenham's consensus-and-minority-report protocol requires a
   justification for every quality answer.

**Current.** Screening and classification produce a decision; `PaperDecision.reasons` holds a JSON
list against a *decision*, not against a *classification*, and there is no notion of how much of a
paper was read.

**Why it matters.** Reading depth is the difference between a mapping study and a review — the two
"can be considered as different points on a continuum". Recording it makes that position explicit
rather than implied. And rationale capture is what makes a classification auditable: the corpus
records **73% of papers designated incorrectly by their own authors**, so a classifier's reasoning is
the only way a reader can check the call.

**Remediation sketch.** A `reading_depth` enum on the per-paper decision (`abstract` ·
`intro_conclusion` · `full_text`), set by whoever made the call and escalatable; a required
`rationale` field on classification records.

**Cost.** Small. **See [02](./methodology/02-sms.md).**

---

### G38 — The quality-instrument model is the wrong shape (F2-SF05) — **medium**

**Required.** Three properties the corpus establishes, none currently modelled:

1. **A purpose flag — selection or analysis.** The distinction is load-bearing and changes the data
   flow. Quality data used to *select* studies becomes inclusion/exclusion criteria and **must be
   collected before the main extraction, on separate forms**. Quality data used to *analyse* may be
   collected alongside extraction on a joint form. Both may coexist in one review.
2. **Per-item ordinal scales, not booleans.** Every real instrument uses ordinal anchors — DARE is
   Y=1 / P=0.5 / N=0; Garousi's grey-literature checklist is 1 / 0.5 / 0 with a 10-of-20 threshold.
   Kitchenham warns that a simple Yes/No "may be misleading".
3. **Methodological and reporting quality kept as separate scores.** "It is good practice not to
   include quality of study and quality of reporting scores in a single metric." Kitchenham's own
   worked example weighted reporting quality *lower* rather than merging it.

**Current.** `QualityChecklist` / `QualityChecklistItem` / `QualityScore` exist and are the right
overall shape — a template mechanism rather than a fixed list, which is correct, because the 2007
quality guidance was **explicitly withdrawn** by its own authors with no replacement named. What is
missing is the purpose flag, the ordinal scales, and the separation.

**Why it matters.** Without the purpose flag, a study missing a quality score is ambiguous — an error,
or simply not yet assessed. Without ordinal scales the instruments cannot be represented faithfully.
And a merged score is one the sources say should not exist.

**Cost.** Small. **See [07](./methodology/07-quality-assessment.md).**

---

### G39 — Threats are not derived from the protocol configuration (F2-SF11) — **medium**

**Required.** Ampatzoglou supplies **22 top-level threats expanding to 34**, with **60 mitigation
actions**, organised by review phase, plus exclusivity rules — e.g. if digital-library selection is
used, the venue-selection threat does not apply, *except* when a quasi-gold standard from specific
venues is also used. The author-side procedure requires that **every threat be checked for
applicability**, and that each applicable one carry either a mitigation or an explicit
acknowledgement that it is not mitigated.

**Current.** `RRThreatToValidity` auto-creates threats from the Rapid Review QA mode — the right
pattern, scoped to one study type and one configuration switch.

**Why it matters.** The generalisation is mechanical: threats follow from what the protocol says the
study will do. A study that searches one database, screens with one reviewer, and skips appraisal has
a determinable threat set. Presenting a flat 34-item checklist instead would be noise; deriving the
applicable subset is the feature. Note also the trap the corpus records: **a mitigation for one threat
can create another** — snowballing and grey literature mitigate publication bias while introducing
their own risks.

**Remediation sketch.** Generalise `RRThreatToValidity` to all study types; encode the threat
catalogue with its phase mapping, its exclusivity rules, and the one Rapid Review concession that must
**not** generate a threat (narrowing criteria to the practitioner's context is good practice, not a
threat); enforce mitigation-or-acknowledgement as a completion gate.

**Cost.** Medium — the catalogue is large but flat, and the platform already has the pattern. **See
[09](./methodology/09-threats-to-validity.md) and [03](./methodology/03-rapid-review.md).**

---

### G40 — No traceability from goal to research question to extracted field (F2-SF01, F2-SF06) — **medium**

**Required.** Kitchenham's protocol evaluation asks whether "the data to be extracted will properly
address the research question(s)". **GQM** is the structure that makes this checkable rather than a
matter of opinion — goal → question → metric, where the goal has an object, purpose, quality focus,
viewpoint and environment. Ampatzoglou names GQM as the best practice for mitigating **TV19,
coverage of research questions**.

**Current.** Research questions and extraction fields both exist, with no link between them.

**Why it matters.** It answers a question the platform otherwise cannot: *which extraction fields
belong on this form?* Those, and only those, that answer a question derived from the goal. It also
makes protocol review mechanical — an unlinked question is one nothing will answer; an unlinked field
is data nobody asked for.

**Cost.** Small — a join table and two validations. **See [09](./methodology/09-threats-to-validity.md).**

---

### G41 — Updating an existing review is not a supported workflow (F2-SF03) — **medium**

**Required.** A "second-generation" study updates a prior review, and it has a **different and much
cheaper search strategy**: forward-only snowballing, without iteration, from the earlier review and
its primary studies.

**Evidence.** That strategy found **all 11 papers a database search found, plus 3 more — one of which
appeared in no standard database** — while screening 1,018 candidates and reading 16 in detail,
against 1,641 and 100 for the database search. A striking detail: **all 16 candidates came from the
two versions of the review itself, and none from the 794 citations to its primary studies.**

**Current.** Studies are one-shot. There is no ancestry relation between a study and the study it
updates.

**Why it matters.** Reviews go out of date — Petersen warns that mapping studies "may quickly become
out of date" — and updating one is a common, well-defined task with an evidenced cheaper method. The
platform currently offers no path other than starting again.

**Remediation sketch.** A `supersedes` / `updates` relation on `Study`; a search mode that seeds
forward snowballing from the prior study's report and included set; a report section stating what
changed.

**Cost.** Medium. **See [06](./methodology/06-search-and-selection.md).**

---

### G42 — No terminology-variant search (F2-SF03) — **low**

**Required.** Where the target is described inconsistently across the literature, **many simple search
strings outperform one complex string**. Kitchenham's tertiary study used **15 simple strings** — one
per terminological variant of "systematic review" — plus a separate pair of complex strings for one
database, on the stated rationale that "reducing the number of searches reduces the problem of
integrating search results".

**Current.** One search string per `SearchString` record, with versioning. The model supports several
strings only as successive *versions*, not as a simultaneous set.

**Why it matters.** This is the defining difficulty of a **tertiary study**, where you are searching
for a *method* and authors call it "literature survey", "assembly of studies", or just "review". It
also bears on G2: variant strings and per-engine translation are different problems and should not be
conflated.

**Cost.** Small. **See [04](./methodology/04-tertiary.md).**

---

### G43 — No replication package, and no archival discipline (F1-SF04, F2-SF10) — **medium**

**Required.** An open-science-conforming study discloses three things: a **preregistered protocol**
(G35), a **replication package** — all analysed data plus all files, scripts and codebooks needed to
comprehend the study — and a **preprint**.

**Archival is constrained, not free-form.** Replication packages must go to a repository providing a
**DOI and permanent archival** — Zenodo or figshare — and **never** to a personal or institutional
URL. Web pages disappear continuously, empirically demonstrated over a four-year longitudinal study.
This is the same link-rot problem G28 records for grey-literature *sources*, arriving from the other
direction: **our own outputs rot too.**

**Current.** `POST /studies/{id}/export` produces `svg_only | json_only | csv_json | full_archive`
locally. There is no DOI, no external archival, no licence handling, and no anonymisation step.

**Why it matters.** Three concrete consequences:
- **Licence selection is a real trap.** Never offer `-NC`: the legal meaning of "commercial" is far
  broader than it looks, and it would bar open infrastructure born from commercial entities —
  figshare and PeerJ are the named examples — from using the material at all. `-SA` and `-NC` are
  usually incompatible with traditional publishing. The positive guidance is arXiv's default
  non-exclusive licence when a traditional publisher is intended, **CC BY** when a gold open access
  venue is.
- **Where consent for underlying data is refused** — which the source expects to be common for
  qualitative data — the fallback is publishing **the protocol, the coding schema and the coding
  rules**, so the trustworthiness of the analysis can be checked. That is the same persistence change
  **G8** already proposes on methodological grounds.
- **Anonymisation** is needed before exporting anything participant-derived — relevant if the platform
  ever holds interview data from Rapid Review stakeholder work.

**Evidence it is worth building.** Under **voluntary, non-mandatory** open science policies at recent
SE venues, **more than 50% of authors disclosed their data.**

**Cost.** Medium. Zenodo and figshare both have APIs. **See
[13 — Open science](./methodology/13-open-science.md).**

---

### Requirements folded into existing gaps rather than given new IDs

| Requirement | Gap it belongs to | Note |
| ----------- | ----------------- | ---- |
| **SEGRESS per-study-type applicability** | **G10** | Already added in the G10 amendment above — it is the reason SEGRESS replaces PRISMA as the primary standard |
| **Three-valued screening vote (include / exclude / uncertain)** | **G5** | A schema prerequisite: a binary decision cannot express the "both uncertain" cell of the decision-rule table, and Petersen 2015's measured trade-offs are stated over that table |
| **Publishable coding schema and coding rules** | **G8** | Persisting codes as first-class rows serves both the synthesis method and the open-science fallback when data cannot be released — one change, two justifications |
| **Exclusion after inclusion, with a reason** | **G14** | Papers pass full-text screening and still fail during extraction; the flow diagram must show it, and "excluded with reasons, per reason" is a PRISMA requirement |
| **Grey-source metadata minimum** — URL, access date stamped at retrieval, author, title, outlet, archived copy | **G28** | The access date is unrecoverable after the fact. 24.8% of grey items in one study had **no URL recorded at all** |
| **Manual search is not optional** | **G3** | Petersen 2015 says it "may be more effective"; Kitchenham 2013 requires manual search of recent proceedings to cover indexing lag |
| **Two disjoint seed sets** — one to build the string, one to evaluate it | **G13a** | Using one set for both measures memorisation, not recall |

---

### Neither oracle sees a backend route

G22 and G23 are the built-but-never-wired defect on the backend, and both passed every gate in the repository. It is worth being explicit about why, because the two oracles added on 2026-08-06 can read as covering more than they do.

| Oracle                              | What it proves                                   | What it cannot see                                            |
| ----------------------------------- | ------------------------------------------------ | ------------------------------------------------------------- |
| `audit_unreachable_frontend.py`     | Every module is reachable from `main.tsx`        | Anything not in `frontend/src` — no backend job or route      |
| `check_shadowed_modules.py`         | No `X.py` is displaced by a package `X/`         | A module that is imported and never called                    |

Both reason about **imports**. A backend capability is reachable only through an HTTP route and, for a job, an enqueue call — neither of which an import graph models. `snowball_job.py` is imported by `worker.py` and registered with ARQ, so it looks alive to every static check while being unreachable to every user. The `run_snowball_search` string in G23 is worse still: it is not an import at all, so no tool in the repository can tell it apart from a correct name.

**Extended — 2026-08-07.** G25 and the orphaned `ArxivSource` are the same blindness in two more organs, and they are worse than G22 because neither involves a name a tool could even in principle resolve.

| Defect | Why every gate passed it |
| ------ | ------------------------- |
| **G25** — the backend posts to `/tools/search_papers`, a path researcher-mcp does not serve | A URL is a string. `ruff` and `mypy` see `str`; the tests mock `httpx` below the seam, so both sides are green while the contract between them is fiction |
| **G25** — `{"databases": …}` against a parameter named `indices` | Crosses a JSON boundary as `dict[str, Any]`. Nothing types the wire format, on either side |
| **G25** — `["acm", "ieee", "scopus"]` against registry keys `acm_dl`, `ieee_xplore`, `scopus` | Free strings, never validated against `DatabaseIndex`, and unknown indices are recorded in `sources_failed` rather than raised |
| **`ArxivSource`** — constructed only by its own unit tests | Imported, so `check_shadowed_modules.py` is satisfied; outside `frontend/src`, so the reachability audit never looks; covered by tests, so coverage rises because of it |

That last row is the sharpest form of the pattern this document keeps returning to: **its unit tests are the only thing keeping it alive, and they are also the only reason it looks healthy.** Test coverage measures whether code is executed, not whether anything but a test executes it.

**What would catch these.** Four checks, all cheap and none yet written:

1. Assert that every name `_arq_function_for_type` can return is the `__name__` of a function in `WorkerSettings.functions`. A plain unit test over both collections; it fails today.
2. Assert that every `JobType` member has a route that enqueues it. This is the backend analogue of the frontend reachability audit and would have caught G22 on the day snowballing was written.
3. **One contract test per cross-service seam** — start the real researcher-mcp ASGI app in-process and drive it with the backend's own client code. This is the only check that catches G25, and it catches all three of its layers at once, because a wrong path, a wrong parameter name, and a wrong index name all produce a failing call.
4. **Assert every `DatabaseSource` implementation is reachable from `build_default_registry()`.** A source that no registry constructs is dead however well it is tested; this is `audit_unreachable_frontend.py`'s question asked of the source adapters, and it fails today on `ArxivSource`.

Principle X requires an e2e test driving each user-facing feature through the UI, which subsumes both — but only for features someone remembered to route. A capability nobody exposed has no journey to write a test against, which is precisely how it stays hidden.

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

**Correction — 2026-08-06.** This section previously read "The backend has no equivalent problem: all **56** `APIRouter` modules are registered." Every registered router does resolve, but the statement was drawn from the registration list rather than from the import graph, and it misses the opposite failure: a module that is never loaded at all. `backend/src/backend/api/v1/admin.py` declared an `APIRouter` that nothing could reach, because the `admin/` package beside it shadows the name — as did `db/src/db/models.py`. Both are recorded under G21, and both were deleted the same day.

The backend had the same disease in a different organ, and what it lacked was an audit that would find it. It now has one: `scripts/check_shadowed_modules.py` runs in pre-commit and CI beside the mutation scanner. Two oracles now guard reachability, one per language:

| Oracle                                  | Language   | Failure it detects                                         |
| --------------------------------------- | ---------- | ---------------------------------------------------------- |
| `scripts/audit_unreachable_frontend.py` | TypeScript | Module not reachable from `main.tsx` in the import graph   |
| `scripts/check_shadowed_modules.py`     | Python     | Module shadowed by a same-named package, so never imported |

**Already fixed, same pattern.** Recorded because they show the failure mode is not confined to whole components:

| Defect                                                                                                                                                                         | Fix                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| `StudyPage` passed `isAdmin={false}` as a literal, so protocol task **Mark Complete** and **Approve** were rendered for nobody, though both endpoints exist and are LEAD-gated | `342fc4b` — added `viewer_role` to `StudyDetail` and gated on it |
| `NewStudyWizard` reused one DOM node across the Next/Create swap, so clicking Next on step 4 submitted the form and **discarded step 5's input**                               | `513d973` — distinct React keys                                  |

**Why it stayed hidden.** In every case the e2e tests that should have caught it were guarding on `isVisible()` — which takes no timeout — and silently skipping, or asserting against a placeholder. The lesson is recorded under [Observed pattern](#observed-pattern): a component compiling, passing unit tests, and having a working endpoint says nothing about whether a user can reach it.

---

## Committed mutation artifacts (resolved 2026-08-06)

Not a feature gap: a correctness incident in code the catalogue above assumes is sound. Recorded here because several gaps were assessed against source that turned out to be wrong, and because the detection method generalises.

**What happened.** Commit `ecc32de` — "feat: complete 003-project-setup-improvements", the commit that _introduced_ cosmic-ray — ran mutation testing against the real working tree and committed the mutants it left behind. `scripts/run-mutation-safe.sh`, which isolates runs in a git worktree, was not written until `64c99c0` two weeks later; the wrapper was added, but the damage already committed was never reverted. **60+ artifacts survived five feature releases**, and the corruption spread: features 005 and 006 copy-pasted a mutated admin guard into five further files.

**Why nothing caught it.** This is the part worth internalising. A _surviving_ mutant is by definition one the test suite cannot detect — that is what "survived" means. Committing survivors therefore yields a codebase that is green and broken simultaneously. Throughout, **1104 backend tests passed**, coverage held above its gate, and CI was green. Two artifacts were even reported by the linters and then _suppressed_ rather than recognised: `# noqa: F821` silenced "undefined name" on `except CosmicRayTestingException`, and `# type: ignore` silenced the empty-iterable warning on `for chart_type in []`. Neither test results nor static analysis can find this class; only reading the source diff can.

**Representative defects** (full list in the root `CHANGELOG.md`):

| Defect                                                                     | Effect                                                               |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `GroupMembership.group_id >= group_id`, `StudyMember.user_id >= …`         | Membership in any higher-id group passed the gate — cross-group leak |
| `if decision != "accepted"`                                                | Accepted and rejected counters swapped on **every** search           |
| `InclusionCriterion.study_id != study_id`, `Reviewer.study_id != study_id` | Screening and validity loaded every **other** study's rows           |
| `for chart_type in []`                                                     | Results charts never generated                                       |
| `except CosmicRayTestingException` ×3                                      | Undefined name — handler raised `NameError`, masking the real error  |
| `_process_single_candidate` returning `(None, False)`                      | `None` candidate entered the screening pass                          |

**Interaction with an existing gap.** The last row compounded a separate defect. A `None` candidate reaching `_run_screening_pass` raises `AttributeError`, which that function's bare `except Exception` swallowed and returned as `("rejected", [])` — so an already-seen paper was silently _rejected_ on a crash. The mutation and the silent-failure defect concealed each other. That bare `except` is tracked as **C3** in [feature 012's plan](./features/012-wire-up-unreachable-workflows.md) and is fixed by tasks TREF5–TREF6.

**Detection method**, re-runnable and now enforced in pre-commit and CI:

```bash
# cosmic-ray signatures in tracked source
python3 scripts/check_mutation_artifacts.py
```

It tokenizes each file and matches executable code only — docstring prose such as "`WorkerSettings.functions` is a non-empty list" reads exactly like an identity comparison, and flagging it produced four false positives on a clean tree. A commit gate that cries wolf gets disabled, so precision is treated as load-bearing; 16 tests in `scripts/tests/` cover both directions. Deliberate exceptions are justified inline with `# cosmic-ray-ok: <reason>`.

**Resolution.** `e47abd9` reverted 63 sites across 17 files and corrected one unit test that had been written against a mutant two days after the corruption landed. `0303a3c` added three independent guards: a structural refusal that stops any cosmic-ray test run outside a linked worktree (`git rev-parse` can prove that; an environment variable cannot), a before/after fingerprint of the tracked tree in the wrapper, and the commit-time scanner above. The five `cosmic-ray-survivors.md` reports are annotated — their "100% killed" scores came from the unsafe session and should not be cited until re-run.

### Re-check of affected gap claims (2026-08-06)

Every gap assessed before 2026-08-06 was read against corrupted source, so each claim resting on a repaired file was re-verified against the repaired tree. **No gap's verdict changed** — the structural absences the catalogue records are real and independent of the mutants. Four claims did need correcting, and one of them is the most instructive item in this document.

| Claim                                                    | Verdict                                                                                                                                                                                  |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **G13d** — "two defects in `_fetch_test_search_results`" | ⚠ **Root cause wrong.** Both were cosmic-ray mutants, not design defects. Fix stands. See the correction on that gap — this was the corruption's first, misdiagnosed encounter           |
| **F2-SF07** Automated analysis — marked ●                | ⚠ **Unearned when written.** `_generate_all_charts` looped over `[]`, so zero charts were ever produced. Now genuinely correct — verified below                                          |
| **F3-SF03** Security — marked ●, "the rest is solid"     | ⚠ **Overstated when written.** A broken-access-control defect was live in `GET /groups/{id}/studies`. Now correct — verified below                                                       |
| **G1** — "Discovery works"                               | ⚠ **Premise was false, verdict unaffected.** Snowball dedup (`Paper.doi > ep.doi`) and its counters (`added = -1`, `added += 2`) were broken. Repaired; the missing DAG is still missing |
| **G11** — cites `admin.py` route list                    | ✓ Names the package-shadowed dead file (G21), but its three routes are identical to the live package, so the conclusion holds                                                            |
| **G4, G15, G18, G19** — reference repaired files         | ✓ Unaffected. Each rests on a structural absence, not on mutated behaviour                                                                                                               |

**F2-SF07 re-verified.** `ChartType` has 8 members; `_generate_all_charts` is called from `run_generate_results` (`results_job.py:77`), persists a `ClassificationScheme` per type, is served by `results.py`, and is rendered by `components/results/ChartGallery.tsx` on `ResultsPage`. The path is complete end to end. It was not before: for five releases the feature marked "fully implemented" generated nothing.

**F3-SF03 re-verified.** Both predicates in the group study listing are equality again, so membership in one group no longer grants visibility of another's studies. The rest of the F3-SF03 note remains accurate — JWT with `token_version` invalidation, TOTP 2FA with bcrypt-hashed backup codes, Fernet at rest, and both audit modules (`services/audit.py` for data changes, imported by six routers; `services/audit_service.py` for security events) are intact and distinct.

**What this says about the assessment method.** The header of this document states the method: "traced each feature to implementing code — not to `specs/` intent". That is the right instinct, and it still failed here, because tracing to code answers _does an implementation exist_ and not _does it work_. Both ● marks above survived a trace: the function existed, was called, was covered by passing tests. What would have caught them is the question feature 012 was written to institutionalise — can a user reach this, and does exercising it produce the claimed effect? An e2e test opening the results page and asserting eight charts would have failed for five releases.

---

## Recommended sequence

> **Reordered — 2026-08-07.** The intake put one item ahead of everything previously listed. **G25** is not a gap in the ordinary sense — it is a broken seam beneath the whole search subsystem, and while it stands, G1, G2, G13, G22, G24, G26 and G28 are all unobservable: their symptoms cannot be reproduced because the code path they describe returns nothing. Anything measured against search before it lands measures the outage.

| Order | Item                                                                                           | Rationale                                                                                                                                                                                                                         |
| ----- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ~~0~~ | ~~**G13d** two defects in `_fetch_test_search_results`~~                                       | ✅ **Done 2026-08-05** — was writing fabricated pilot data on service failure                                                                                                                                                     |
| **0** | **G25** researcher-mcp call surface, plus the contract test that pins it                       | **Ahead of everything.** No search in the platform returns a paper today. Every other search gap is unobservable until this lands, and four of the five call sites report success while failing                                   |
| 0b    | **G34** part 2 — fix the coverage command; wire `audit_unreachable_frontend.py` into CI       | Minutes of work on the evidence base every other item is judged against                                                                                                                                                           |
| 1     | **G10** report validation — **as two features**: a SEGRESS per-study-type completeness checker, and a DARE quality scorer | Greenfield, no schema change, operates on an existing structured object. See the amendment on G10 — PRISMA may not be used to score quality, and SEGRESS is the only standard with per-review-type applicability |
| 2     | **G1** + **G14** steps 1–2 provenance                                                          | Design together — the PRISMA "other methods" arm and the snowball DAG need the same discriminator                                                                                                                                 |
| 2b    | **G14** steps 3–6 flow diagram                                                                 | Follows the provenance work; reuses `visualization.py`'s existing SVG pattern                                                                                                                                                     |
| 3     | **G6** Study/Paper split                                                                       | Every downstream count and pooled estimate depends on the unit of analysis being right                                                                                                                                            |
| 4     | **G11** roles + user CRUD                                                                      | The system currently cannot onboard a user through its own API                                                                                                                                                                    |
| 5     | **G4**, **G5** reliability + rules                                                             | Both reuse the existing κ and decision machinery                                                                                                                                                                                  |
| 6     | **G2** + **G13** search fidelity + piloting                                                    | Land together — a per-database breakdown is misleading until query translation exists                                                                                                                                             |
| 7     | **G3** remaining search modalities                                                             | EI Compendex adapter and manual search; independent of the above                                                                                                                                                                  |
| 8     | **G8** qualitative synthesis                                                                   | Large, but unblocked once G6 lands                                                                                                                                                                                                |
| 9     | **G7**, **G9**, **G12**, F1 docs                                                               | Additive, low coupling                                                                                                                                                                                                            |
| —     | **G15** vLLM + LM Studio providers                                                             | Unordered — cheapest item on the list and independent of everything else; land whenever local inference is wanted                                                                                                                 |
| 1b    | **G18**, **G19**, **G20** — see [feature 012](./features/012-wire-up-unreachable-workflows.md) | Designed together, since they are one defect shape and all three land in `StudyPage`. Promote near the top: G19 has the highest ratio of delivered value to work on the list, and until G18 lands F2-SF04 has no exercisable path |
| 6b    | **G26** search metadata at ingest                                                              | Lands with G2/G13 — three later gaps each propose to recover a field the search already had and dropped                                                                                                                            |
| 7b    | **G28** grey literature as a real source                                                       | Follows G3; steps 1 and 6 (arXiv search + a UI grouping) are a day and close the arXiv ask on their own                                                                                                                            |
| 8b    | **G27** workflow unification                                                                   | Take the bottom-up route unless a fifth study type is planned; feature 012 already pays for two of its ✗ cells. The SMS report and SMS synthesis are the substance                                                                |
| 9b    | **G29** de-hardcode the agent prompts                                                          | Cheap, and it silently biases every screening and extraction decision until done                                                                                                                                                  |
| 1c    | **G40** GQM traceability · **G38** quality-instrument shape · **G37** reading depth and rationale | Three small schema changes that turn later gates from advisory into checkable. All are additive columns and join tables                                                                                                            |
| 2c    | **G35** protocol snapshot and deviation diff                                                    | Turns "report deviations from the protocol" from an honour system into a control, and is a prerequisite for report validation meaning anything. Also fixes the ordering problem: some synthesis methods cannot be chosen after extraction |
| 5b    | **G36** stopping rules; *assessed* vs *never assessed*                                          | Land with **G14** — the PRISMA flow cannot be correct while an unassessed paper is indistinguishable from an excluded one                                                                                                          |
| 6c    | **G42** terminology-variant search                                                              | Small, and it is the defining search difficulty for tertiary studies. Keep separate from G2 — variant strings and per-engine translation are different problems                                                                    |
| 8c    | **G39** threat derivation from protocol configuration                                           | Generalises the pattern `RRThreatToValidity` already implements, to all study types and the full 34-threat catalogue                                                                                                              |
| 9c    | **G43** replication package, archival and licence discipline                                    | Follows **G8**'s code persistence, which supplies the qualitative fallback artefact                                                                                                                                                |
| —     | **G41** review-update workflow                                                                  | Unordered — self-contained, and the evidenced cheaper search strategy makes it a good standalone feature                                                                                                                          |
| —     | **G34** part 1 — run the mutation wrapper and record real scores                                | Unordered but overdue: the gate is codified, the rails are built, and no package has a citable number                                                                                                                              |
| —     | **G16**, **G17**, **G21**, **G30** unreachable or absent UI controls                           | Unordered — each is a single control over machinery that is already written. G17 and G30 sit in the same admin tab                                                                                                                 |
| —     | **G31** user avatar, **G33** inline-style residue                                              | Unordered and independent. G33 is a live dark-theme defect, not only a tidiness item                                                                                                                                               |
| —     | **G32** DSPy-driven agent improvement                                                          | Last. Its prerequisite is a gold-standard evaluation set derived from human overrides, which is worth building on its own and also feeds G4                                                                                        |

---

## Observed pattern

Features that are _stateful workflow_ — protocols, phase gates, screening, extraction, membership — are well built out. Features that require a **richer relational shape** — a provenance DAG (G1), a Study entity distinct from Paper (G6), an intra-rater round (G4) — are the ones that got flattened.

That is the predictable consequence of shipping ten features as sequential additive migrations `0014`–`0018`: changing the _shape_ of `CandidatePaper`, or splitting `Paper` from `Study`, would have forced backfills across every previously completed workflow. The remaining structural gaps are cheap to describe and expensive to add for exactly that reason — and they get more expensive with every study the platform runs.

A second, cheaper pattern sits alongside it: **capabilities built but not connected**. G13a is the clearest case — the agent declares `seed_keywords`, the template renders it, the seed records exist, and the endpoint simply never passes the argument. G12's paper viewer is the same shape (endpoint with no frontend consumer), as is `ai_adequacy_judgment` (column written once, never updated). These cost little to close and are worth sweeping for beyond the instances catalogued here.

**Updated 2026-08-07 — the second pattern is the dominant one, and it has a third form.** Folding in `todo.md` and `todo2.md` added ten gaps, and six are disconnection rather than absence:

| Gap | Both halves exist | The missing edge |
| --- | ----------------- | ---------------- |
| **G25** | Nine working source adapters; a backend that wants to search | The URL between them names a route that does not exist |
| **G26** | `PaperRecord.url` populated by every adapter | The reader asks for `source_url` |
| **G13c** | `StudyDatabaseSelection`, a UI to set it, a `databases_queried` column | No search path reads the table, and the hardcoded default names two indices that do not exist |
| **G28** | `ArxivSource`, `convert_url_to_markdown`, `scrape_journal` | Nothing constructs `ArxivSource`; nothing points the scraper at a blog |
| **G29** | `{{ domain }}` plumbing through 9 agents and 5 jobs | No `Agent` row is ever seeded, so the plumbing never carries anything |
| **G27** | Validity, synthesis and report machinery, three or four times over | No study type has all three, and SMS has none |

So the codebase's characteristic defect is not missing capability. **It is a missing edge between two capabilities that are each finished, each tested, and each green.** The first pattern — flattened relational shape — is expensive and rare. This one is cheap and everywhere, and it is invisible to the whole toolchain: a linter sees valid syntax, a type checker sees compatible types, a unit test sees its own mock, and coverage rises when a test is the only caller.

Which sharpens what the two oracles are for. `audit_unreachable_frontend.py` did not find a category of bug; it found *one instance* of the category, in the one language where an import graph happens to model reachability. The same question — **what constructs this, and what calls that** — is unasked of ARQ job registrations (G22, G23), of HTTP seams between services (G25), and of source-adapter registries (`ArxivSource`). Each needs its own oracle, and each is a short script. The four listed under [Neither oracle sees a backend route](#neither-oracle-sees-a-backend-route) are the ones this pass would have wanted.
