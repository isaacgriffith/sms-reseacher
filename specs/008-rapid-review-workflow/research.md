# Research: 008-Rapid-Review-Workflow

**Generated**: 2026-03-21
**Branch**: `008-rapid-review-workflow`

---

## Decision 1: Study Type Discriminator for Rapid Review

**Decision**: Use the existing `StudyType.RAPID = "Rapid"` enum value, which is already
present in `db/src/db/models.py`. No migration change to the `study` table is required.

**Rationale**: The enum was provisioned in a prior feature but never wired up. Rapid Review
phase logic is registered by adding `StudyType.RAPID` to the `_PHASE_GATE_DISPATCH` dict in
`backend/src/backend/api/v1/studies/__init__.py`, pointing to a new `get_rr_unlocked_phases`
service function — exactly the same OCP-compliant extension mechanism used for SLR.

**Alternatives considered**: New `RAPID_REVIEW` enum value — rejected because it would
require a migration to extend the PostgreSQL enum and because `RAPID` is already present.

---

## Decision 2: RapidReviewProtocol Model Design

**Decision**: Create `RapidReviewProtocol` as a separate ORM model in a new
`db/src/db/models/rapid_review.py` module. It does NOT inherit from `ReviewProtocol`;
it shares no table but mirrors the same structural conventions (one-per-study, `version_id`
optimistic locking, `DRAFT`/`VALIDATED` status lifecycle).

**Rationale**: The RR protocol adds fields (`time_budget_days`, `effort_budget_hours`,
`context_restrictions`, `single_reviewer_mode`, `quality_appraisal_mode`) that have no
counterpart in the SLR `ReviewProtocol`. Sharing a table or using single-table inheritance
would pollute the SLR model with RR-only nullable columns and violate SRP. Separate models
are DRY at the schema level (reusing only the enum pattern) without entangling concerns.

**Alternatives considered**: Extending `ReviewProtocol` with nullable columns — rejected
(SRP violation, STI coupling, migration churn). Abstract base class — deferred; only two
concrete protocol types exist so an abstraction would be YAGNI.

---

## Decision 3: Protocol Re-validation on Edit (Invalidation Cascade)

**Decision**: Any PUT to a validated `RapidReviewProtocol` resets status to `DRAFT` and
marks all `CandidatePaper` records for this study with a new `invalidation_reason =
"protocol_amended"` status (existing `CandidatePaperStatus` enum extended with
`PROTOCOL_INVALIDATED`). The API returns a 409 Conflict with the new status if the client
does not include `?acknowledge_invalidation=true` in the query string; once acknowledged,
the PUT proceeds.

**Rationale**: Forcing explicit acknowledgment prevents accidental invalidation. Storing
the invalidation on `CandidatePaper` (rather than simply deleting papers) preserves audit
history and allows a researcher to see which papers existed before the protocol change.

**Alternatives considered**: Deleting CandidatePapers on protocol edit — rejected (data
loss, no audit trail). Silent reset without warning — rejected (researcher would lose work
without realising it, violating the spec requirement for a confirmation warning).

---

## Decision 4: Evidence Briefing Versioning

**Decision**: `EvidenceBriefing` is a versioned entity. Each generation creates a new
row with an auto-incremented `version_number` scoped per `study_id`. Status is
`DRAFT | PUBLISHED`. A study may have at most one `PUBLISHED` briefing at a time;
promoting a version atomically demotes the previous published version to `DRAFT`.

**Rationale**: Explicit versioning (spec decision) gives researchers control over which
version is public-facing. Scoped `version_number` (not global) keeps numbering meaningful
per study. Atomic promotion uses a DB transaction with a prior UPDATE + subsequent INSERT
to avoid race conditions.

**Alternatives considered**: Global sequence — rejected (confusing for per-study context).
Separate `EvidenceBriefingVersion` table — rejected (YAGNI; the briefing IS the version;
no shared mutable header needed).

---

## Decision 5: Shareable Link (Share Token) Design

**Decision**: Create `EvidenceBriefingShareToken` table with a cryptographically random
`token` (32-byte URL-safe base64, generated with `secrets.token_urlsafe(32)`). The public
endpoint `GET /api/v1/public/briefings/{token}` serves only the currently `PUBLISHED`
version for the study. Tokens can be revoked (soft-delete via `revoked_at`). Tokens have
no hard expiry by default (`expires_at = NULL`), but the field exists for future use.

**Rationale**: No existing share-token pattern in the codebase — this is a net-new design.
Using the existing `cryptography` (Fernet) library for generation is unnecessary; Python's
`secrets` module is sufficient for opaque tokens. Tokens are scoped to a briefing
(not a study) to allow future per-version sharing control.

**Alternatives considered**: JWT-based share links — rejected (over-engineered for a
read-only public URL; JWT expiry management adds complexity without benefit here). Signed
URL with query param — rejected (tokens in query strings appear in server logs). Path
segment token (chosen) — clean, revocable, cache-friendly.

---

## Decision 6: Narrative Synthesis AI Drafting

**Decision**: AI-assisted narrative drafting is implemented as a new agent
(`NarrativeSynthesiserAgent`) with prompt templates in
`agents/src/agents/prompts/narrative_synthesiser/`. The draft is triggered via a new ARQ
job (`run_narrative_draft` in `narrative_synthesis_job.py`). The job writes the result to
`RRNarrativeSynthesisSection.ai_draft_text`; the researcher then accepts, edits, or
discards it from the UI. Job status is tracked via the existing `BackgroundJob` ORM model.

**Rationale**: Following the existing agent/prompt/job separation (same as
`ProtocolReviewerAgent` + `protocol_review_job.py`). The agent uses `LLMClient` (LiteLLM)
to keep provider-agnostic; prompts are Jinja2 templates that inject the study's research
question and paper abstracts.

**Alternatives considered**: Synchronous AI call in the API handler — rejected (latency
30-60 s, blocks request thread, violates async discipline). Streaming response — deferred
(complexity not warranted for a draft that the researcher edits anyway).

---

## Decision 7: Evidence Briefing PDF/HTML Generation

**Decision**: HTML generation is done server-side using Jinja2 templates stored in
`backend/src/backend/templates/rapid/evidence_briefing.html.j2`. PDF is produced from
HTML using `weasyprint` (already used for SLR report export if present; otherwise add as
a dependency). Generation is an ARQ job (`run_generate_evidence_briefing`) that stores
the output paths in `EvidenceBriefing.pdf_path` and `html_path`. Download is served via
a streaming endpoint.

**Rationale**: Jinja2 is already in the approved stack. WeasyPrint is the standard
headless HTML→PDF library for Python apps and produces high-quality one-page output
matching the spec's requirement for a practitioner-readable document.

**Alternatives considered**: Playwright headless Chrome for PDF — overly heavy for a
server-side dependency; reserved for E2E testing use. External PDF service — rejected
(external dependency, data privacy concern for research content).

---

## Decision 8: New Alembic Migration

**Decision**: Single migration `0016_rapid_review_workflow.py` creates all 6 new tables:
`rapid_review_protocol`, `practitioner_stakeholder`, `rr_threat_to_validity`,
`rr_narrative_synthesis_section`, `evidence_briefing`, `evidence_briefing_share_token`.
Also adds `PROTOCOL_INVALIDATED` to the `candidate_paper_status` PostgreSQL enum.

**Rationale**: One migration per feature is the established convention (see 0015 for SLR).
Bundling all tables in one migration ensures consistent rollback semantics.

---

## Decision 9: Frontend Page/Component Layout

**Decision**: Mirror the SLR pattern exactly:
- Pages at `frontend/src/pages/rapid/`
- Components at `frontend/src/components/rapid/`
- API services at `frontend/src/services/rapid/`
- Hooks at `frontend/src/hooks/rapid/`

The Rapid Review study phases are surfaced via the existing study phase-navigation
component (same as SLR), with RR-specific page routes registered in the router.

**Rationale**: Consistency with SLR reduces cognitive load, enables shared layout
components, and aligns with the platform's established feature-module pattern.

---

## Dependency Notes

- `weasyprint` will be added to `backend/pyproject.toml` if not already present.
- No new TypeScript packages required; PDF download uses the existing `fetch` +
  `Blob` pattern already used for other export endpoints.
- `secrets` module is Python stdlib — no new dependency.
