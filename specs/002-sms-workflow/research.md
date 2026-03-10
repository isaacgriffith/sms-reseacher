# Research: SMS Workflow System

**Branch**: `002-sms-workflow` | **Date**: 2026-03-10

---

## 1. Async Background Jobs for Long-Running Tasks

**Decision**: **ARQ** (Async Redis Queue) as the background job backend.

**Rationale**:
- FastAPI `BackgroundTasks` runs in the same process and is not suitable for multi-minute tasks — if the HTTP worker restarts, the job is lost.
- ARQ is a pure-Python async job queue that integrates naturally with asyncio, uses Redis as the broker, and supports job cancellation, progress updates stored in Redis, and a worker process separate from the API server. It's the lightest durable option for a small team with asyncio-native code.
- Celery is more feature-rich but carries significant operational overhead (separate broker config, beat scheduler, complex serialization) and its async support in Python 3.14 requires a more complex setup.
- In-process `asyncio.create_task()` with SSE is viable for very small scale (1–2 concurrent users) but loses jobs on restart and offers no persistence or retry semantics.

**Architecture**:
- Job functions defined in `backend/src/backend/jobs/` as async functions decorated with `@arq_job`.
- Worker started via `uv run python -m backend.jobs.worker` — connects to Redis, polls for jobs.
- Job progress written to Redis (`arq:job:{job_id}:progress`) as JSON. The API SSE endpoint reads from Redis to stream progress to frontend clients.
- Job records persisted to PostgreSQL `BackgroundJob` table for durable history (job IDs, status, completion time).

**Alternatives considered**:
- Celery + Redis: rejected — heavier, more config, Celery's Python 3.13+ support has historically lagged.
- Dramatiq: considered — good async support but less community momentum than ARQ for FastAPI projects.
- Taskiq: considered — native asyncio, FastAPI integration, Redis broker. Valid alternative if ARQ's minimalism becomes limiting.

---

## 2. Real-Time Progress: SSE vs WebSocket

**Decision**: **Server-Sent Events (SSE)** via FastAPI `StreamingResponse`.

**Rationale**:
- Progress streaming is unidirectional (server → client only). SSE is purpose-built for this pattern and requires no protocol upgrade.
- SSE uses standard HTTP/1.1 or HTTP/2, works through proxies and firewalls without special configuration.
- Browser support is universal for modern browsers.
- Client reconnection is built into the `EventSource` API — if a connection drops, the browser automatically reconnects and the server can resume from the last event ID.
- WebSockets are appropriate for bidirectional communication (e.g., live collaborative editing). For job progress streaming, WebSocket adds unnecessary complexity.
- Long polling would add latency and is inferior to SSE for continuous streaming.

**Implementation pattern**:
- `GET /jobs/{job_id}/progress` returns `text/event-stream`.
- FastAPI `StreamingResponse` with an async generator that polls Redis every 0.5s for `arq:job:{job_id}:progress`, emitting `event: progress` and `event: complete` messages.
- Frontend uses a typed `useJobProgress(jobId)` React hook that wraps `EventSource`, handles reconnection, and exposes `{ status, progressPct, detail }` state.

**Alternatives considered**:
- WebSocket: rejected — bidirectional complexity not needed for progress-only updates.
- Long polling: rejected — higher latency and more HTTP overhead.

---

## 3. Optimistic Locking with SQLAlchemy 2.0 Async

**Decision**: SQLAlchemy's built-in **`version_id_col`** with custom conflict response.

**Rationale**:
- SQLAlchemy 2.0 supports `__mapper_args__ = {"version_id_col": version_id}` on any mapped class. On each `UPDATE`, SQLAlchemy adds `WHERE version_id = <expected>` to the query. If the row has been updated concurrently, the affected row count is 0, SQLAlchemy raises `StaleDataError`.
- This works correctly with async sessions (`AsyncSession`) — the exception is raised at `await session.commit()` time.
- On `StaleDataError`, the API endpoint catches the exception, fetches the current server state, and returns `HTTP 409 Conflict` with both the client's submitted payload and the current DB state in the response body.
- The frontend `DiffViewer` component presents both versions side-by-side and the researcher selects which fields to keep, then resubmits with the updated `version_id`.

**Tables using version_id_col**:
- `CandidatePaper.version_id`
- `DataExtraction.version_id`

**Critical implementation notes** (confirmed by research):
- `version_id_col` is configured via `__mapper_args__`, **not** via `mapped_column()` directly:
  ```python
  class CandidatePaper(Base):
      version_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
      __mapper_args__ = {"version_id_col": version_id}
  ```
- After catching `StaleDataError`, **must `rollback()` before re-querying** — the failed UPDATE leaves the session dirty.
- `StaleDataError` does NOT include the conflicting DB values — requires a fresh SELECT after rollback.
- The project's existing `expire_on_commit=False` setting in `session_factory` must be preserved — it ensures the in-memory state (the "your changes" side of the conflict diff) is still available after the flush fails.
- Alembic migration: add column with `server_default="0"` to initialize existing rows, then remove the server default so subsequent UPDATEs increment properly via SQLAlchemy.

**Alternatives considered**:
- Pessimistic locking (`SELECT FOR UPDATE`): rejected — locks rows for entire edit session duration, unsuitable for long-form review workflows.
- Application-level timestamp comparison: rejected — SQLAlchemy's built-in is more reliable and less code.

---

## 4. SVG Visualization Generation

**Decision**: **matplotlib + networkx** as primary; **D3.js** in the frontend for the interactive domain model only.

**Rationale** (revised based on research agent findings):
- **matplotlib** (with `backend_svg`) is the industry standard for scientific publication — trusted by academic reviewers, reproducible from Python code, compatible with LaTeX pipelines. Produces valid SVG/1.1 files. This is the safest choice for charts submitted to IEEE, ACM, Elsevier, etc.
- **networkx + matplotlib** is the established combination for concept/graph diagrams in CS research papers — native graph layout algorithms, publication-grade output, cited in 1000s of CS papers.
- **Plotly** (via `kaleido`) is used for bubble charts only, where it handles bubble sizing and labeling better than matplotlib. Plotly bubble chart SVG output is acceptable for publication.
- **D3.js** is used in the frontend for the domain model diagram — provides interactive force-directed exploration of concepts and relationships, with SVG export for static publication use. This avoids requiring a headless browser on the backend for complex graph layouts.

**Chart types and libraries summary**:

| Chart | Library | Location |
|-------|---------|----------|
| Publications per year (bar) | matplotlib | Backend → SVG |
| Keyword bubble map | Plotly + kaleido | Backend → SVG |
| Research classification bubbles | Plotly + kaleido | Backend → SVG |
| Venue / author / locale / institution / year / research type / method charts | matplotlib | Backend → SVG |
| Publication frequency infographic | matplotlib (custom styling) | Backend → SVG |
| Domain model (UML concept diagram) | D3.js (force-directed) | Frontend → SVG export |
| Author/locale network | networkx + matplotlib | Backend → SVG |

**Alternatives considered**:
- Altair/Vega-Lite: valid choice, but requires `vl-convert` (Rust binary dependency) for server-side rendering, adds DevOps complexity. Less universally accepted than matplotlib in traditional STEM publication.
- All matplotlib: viable but bubble charts have inferior sizing/labeling vs Plotly.
- All D3.js: rejected — makes server-side batch generation and export archive impossible without a headless browser.

---

## 5. Agent Architecture

**Decision**: All new agents follow the existing LiteLLM + Jinja2 prompt template pattern in `sms-agents`.

Existing agents (`ScreenerAgent`, `ExtractorAgent`, `SynthesiserAgent`) are extended rather than replaced. New agents:

| Agent | Package | Purpose |
|-------|---------|---------|
| `LibrarianAgent` | `agents` | Suggests seed papers and key authors for a study topic |
| `ExpertAgent` | `agents` | Identifies 10–20 high-confidence relevant papers without hallucination |
| `SearchStringBuilderAgent` | `agents` | Generates and refines PICO/C-based search strings with synonym expansion |
| `QualityJudgeAgent` | `agents` | Evaluates study against 5-rubric quality framework, produces scores + recommendations |
| `DomainModelAgent` | `agents` | Extracts concepts and relationships from open codings to produce domain model JSON |

Each new agent:
1. Has a directory under `agents/src/agents/prompts/<agent_name>/` with `system.jinja2` and `user.jinja2` templates.
2. Has a corresponding eval in `agent-eval/src/agent_eval/evals/` using deepeval.
3. Returns structured Pydantic models (validated via LiteLLM structured output or post-parsing).

---

## 6. Paper Deduplication

**Decision**: Two-stage deduplication: exact DOI match first, then fuzzy title + author similarity.

**Implementation** (`backend/src/backend/services/dedup.py`):
1. **Stage 1 — DOI exact match**: Query `Paper` table by DOI. O(1) with index. Definite duplicate.
2. **Stage 2 — Fuzzy match**: Use `rapidfuzz` (Python, C extension) for title similarity. Score ≥ 0.90 with at least one matching author → probable duplicate, flagged for human review. Score < 0.90 → new paper.
3. **Performance**: For 2000 candidate papers, batch fuzzy matching using the existing paper title index. Acceptable at scale for SMS-sized studies.

**Alternatives considered**:
- Semantic embedding similarity: more accurate but requires an LLM call per paper — prohibitively slow for initial dedup pass. Reserved for borderline human-review cases.

---

## 7. New Frontend Dependencies

The existing React 18 + Vite + Vitest scaffold needs these additions:

| Dependency | Purpose |
|-----------|---------|
| `@tanstack/react-query` | Server state management, SSE integration via query invalidation |
| `react-hook-form` + `zod` | Form handling for wizard, PICO/C form, criteria forms |
| `recharts` | Bar/line charts for phase 2 test-retest result display (frontend-only; publication SVGs generated by backend) |
| `d3` + `@types/d3` | Domain model UML force-directed graph |
| `react-router-dom` | Client-side routing (login, groups, studies, phases, results) |
| `diff` | Text diff library for the `DiffViewer` conflict resolution component |

All additions are lightweight and well-maintained. No UI component library chosen — components are built from scratch per UX spec to avoid opinionated styling constraints.
