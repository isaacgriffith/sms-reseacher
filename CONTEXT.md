# CONTEXT.md

Durable orientation for this repository: what the system **is**, how its parts fit together,
and the invariants that are not obvious from any single file.

**This file answers "where am I, and where does X live?"** It changes only when the
architecture changes. For commands and toolchain, see [CLAUDE.md](./CLAUDE.md). For hard-won
lessons and gotchas, see [MEMORY.md](./MEMORY.md). For binding rules, see
[the constitution](./.specify/memory/constitution.md).

---

## What this system is

A platform for automating **secondary and tertiary research studies** in software
engineering. A researcher defines a protocol, searches academic databases, screens the
results, extracts data, synthesises findings, and generates a publishable report — with AI
agents assisting at each step and a human retaining the decision.

Four study types are supported. They share the same spine and diverge in rigour and output:

| Type         | What it reviews                          | Distinguishing machinery                                                    |
| ------------ | ---------------------------------------- | --------------------------------------------------------------------------- |
| **SMS**      | Primary studies, breadth-first           | The baseline workflow; classification and mapping over depth                |
| **SLR**      | Primary studies, depth-first             | PICO/S protocol, quality checklists, Cohen's κ, meta-analysis, Forest plots |
| **Rapid**    | Primary studies, time-boxed for practice | Practitioner stakeholders, narrative synthesis, Evidence Briefing PDF       |
| **Tertiary** | _Secondary_ studies (SLRs, SMSs, RRs)    | Seed import from existing platform studies, landscape-of-reviews report     |

### The phase model

Every study progresses through numbered phases, and **phases unlock progressively** — a study
cannot reach screening before its search is configured. Each study type has its own gate
function, dispatched by type:

```text
backend/services/phase_gate.py            → SMS (and the default for unknown types)
backend/services/slr_phase_gate.py        → SLR
backend/services/rr_phase_gate.py         → Rapid
backend/services/tertiary_phase_gate.py   → Tertiary
```

`GET /api/v1/studies/{id}/phases` and `StudyDetail.unlocked_phases` both route through
`_PHASE_GATE_DISPATCH` in `backend/api/v1/studies/__init__.py`. **Adding a study type means
adding an entry there** — the fallback silently applies the SMS gate.

### Protocols (the newer, more general model)

Feature `010` generalised the fixed phase pipeline into a **research protocol graph**: nodes
are tasks (23 task types), edges carry typed outputs into typed inputs with optional
conditions, and quality gates block progression until a metric threshold or human sign-off is
met. Studies are auto-assigned their type's default protocol at creation.

Protocols and phase gates currently **coexist**: phases drive the study UI, protocols drive
task execution state. Treat that as a known transitional seam, not a design.

---

## Repository map

A `uv` workspace of five Python packages plus a Vite/React frontend.

> **Package names differ from directory names.** Use the name, not the folder, with
> `uv run --package`. See [MEMORY.md](./MEMORY.md#workspace-package-names-are-not-directory-names).

| Directory         | Package name         | Owns                                                                       |
| ----------------- | -------------------- | -------------------------------------------------------------------------- |
| `backend/`        | `sms-backend`        | FastAPI app, REST API, services, ARQ jobs, Jinja2 report templates         |
| `db/`             | `db`                 | SQLAlchemy 2.0 async models, Alembic migrations — the single schema source |
| `agents/`         | `agents`             | LLM agents, prompt templates, LiteLLM client                               |
| `researcher-mcp/` | `sms-researcher-mcp` | FastMCP server: academic database adapters, PDF fetch, Markdown conversion |
| `agent-eval/`     | `sms-agent-eval`     | deepeval pipelines scoring agent quality                                   |
| `frontend/`       | (npm)                | React 18 + MUI v5 SPA, TanStack Query, Playwright e2e                      |
| `scripts/`        | —                    | Operational tooling (see below)                                            |
| `docs/`           | —                    | Feature PRDs, gap register, methodology notes                              |
| `specs/`          | —                    | Per-feature speckit specs, plans, and task lists                           |

### Scripts

| Script                                  | Purpose                                                                       |
| --------------------------------------- | ----------------------------------------------------------------------------- |
| `scripts/audit_unreachable_frontend.py` | Reachability audit — fails if any module is unreachable from `main.tsx`       |
| `scripts/run-mutation-safe.sh`          | Runs cosmic-ray inside an isolated git worktree (never mutates the real tree) |
| `scripts/seed_e2e_user.py`              | Seeds users, studies, and fixtures the e2e suite depends on                   |

---

## How a request flows

```text
React component
  └─ TanStack Query hook  (frontend/src/hooks/…)
       └─ service module  (frontend/src/services/…)  →  /api/v1/…
            └─ FastAPI router     (backend/api/v1/…)      auth + validation
                 └─ service class (backend/services/…)    business logic
                      └─ SQLAlchemy async session         (db/models/…)

Long-running work never blocks the request:
  router → enqueue ARQ job → returns {job_id}
             worker (backend/jobs/…) → agents/ → LiteLLM → provider
                                     → researcher-mcp → academic databases
  frontend polls the job endpoint (JobProgressPanel)
```

**Layering rule**: routers validate and delegate; services hold logic and own their
transactions; models hold no behaviour. A service that calls `db.commit()` cannot be composed
inside another service's transaction — extract a commit-free helper when you need both.

---

## Cross-cutting mechanisms

- **Background jobs** — ARQ on Redis. Job functions are `async def`, take a `ctx`, and record
  progress on `BackgroundJob` so the frontend can poll. All of `backend/jobs/`.
- **AI agents** — every LLM call goes through `agents/core/llm_client.py` (LiteLLM). Prompts
  are Jinja2 templates under `agents/src/agents/prompts/<agent>/`, never inline strings.
  Providers (Anthropic / OpenAI / Ollama) are configured per-agent in the admin panel, with
  API keys Fernet-encrypted at rest.
- **External search** — nine academic database adapters behind the `DatabaseSource` protocol
  in `researcher-mcp`. Results merge and deduplicate by DOI, then by normalised
  title + first author.
- **Authorisation** — JWT auth; a user's capability on a study comes from `StudyMember.role`
  (`lead` or `member`), surfaced to the frontend as `StudyDetail.viewer_role`. **A UI control
  gated on a permission needs that permission in the response body** — see Principle X.
- **Encrypted secrets** — provider API keys and TOTP secrets are Fernet-encrypted columns.
  They are never returned by an API; responses expose `has_api_key: bool` instead.

---

## Where authority lives

Prefer these over inference when they disagree with code comments or with each other:

| Question                                | Authority                                            |
| --------------------------------------- | ---------------------------------------------------- |
| What are the binding engineering rules? | `.specify/memory/constitution.md`                    |
| What is built vs. merely specified?     | `docs/feature-gaps.md` (21 catalogued gaps)          |
| What is planned next?                   | `docs/features/` (PRDs) and `specs/` (specs + tasks) |
| What is the database schema?            | `db/src/db/models/` + `db/alembic/versions/`         |
| What commands do I run?                 | `CLAUDE.md`                                          |
| What has burned us before?              | `MEMORY.md`                                          |

---

## Invariants worth knowing before you edit

1. **`db/` is the only place schema is defined.** Every schema change needs an Alembic
   migration with a working `downgrade()`. Migrations apply on service startup.
2. **Enum columns need `values_callable`.** Without it SQLAlchemy persists member _names_
   instead of values. See [MEMORY.md](./MEMORY.md#sqlalchemy-enum-columns-need-values_callable).
3. **A component that nothing imports is dead**, however complete it is. A new page must be
   routed or dispatched to, and the reachability audit must stay clean.
4. **Study type dispatch is not exhaustive by the compiler.** Adding a type means touching
   the phase gate dispatch, `StudyPage`'s branches, and the protocol templates — a missing
   branch renders another type's UI over your data rather than failing.
5. **Tests run against SQLite; production is PostgreSQL.** Anything relying on PostgreSQL
   semantics (native enums, JSONB operators, concurrent index creation) needs a test that
   actually targets PostgreSQL.
