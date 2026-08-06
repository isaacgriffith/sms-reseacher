# MEMORY.md

Lessons this project learned the expensive way, and decisions whose rationale is not visible
in the code that resulted from them.

**This file answers "why is it like that, and what will bite me?"** Each entry records
something that cost real debugging time and would otherwise be rediscovered. For architecture
and layout, see [CONTEXT.md](./CONTEXT.md). For commands, see [CLAUDE.md](./CLAUDE.md). For
binding rules, see [the constitution](./.specify/memory/constitution.md).

## How to use and extend this file

- **Add an entry when a bug's root cause was surprising**, when a decision was contested, or
  when a fix's rationale would not survive a `git blame`. Do not record what the code already
  says clearly.
- **Each entry has three parts**: what is true, why it matters, and how to apply it. An entry
  without a "how to apply" is trivia.
- **Date every entry.** A lesson may expire; a dated one can be audited.
- **Promote, don't duplicate.** When a lesson becomes a rule everyone must follow, add it to
  the constitution and leave the entry here as the story behind it.
- **Delete entries that stop being true**, and say so in the commit message.

---

## Workspace package names are not directory names

_2026-08-06_

`uv run --package <name>` takes the package name from `pyproject.toml`, which does **not**
match the directory for three of the five Python packages:

| Directory         | Package name         |
| ----------------- | -------------------- |
| `backend/`        | `sms-backend`        |
| `db/`             | **`db`**             |
| `agents/`         | **`agents`**         |
| `agent-eval/`     | `sms-agent-eval`     |
| `researcher-mcp/` | `sms-researcher-mcp` |

**Why it matters.** `uv run --package sms-db …` fails with
`error: The workspace does not have a member sms-db`. CLAUDE.md carried that exact wrong
command for months, so every documented per-package test and coverage invocation for `db` and
`agents` was broken.

**How to apply.** Check `grep '^name' <dir>/pyproject.toml` before scripting anything
per-package. The `sms-` prefix is not a convention you can assume.

---

## SQLAlchemy enum columns need `values_callable`

_2026-08-05_

`Enum(MyEnum, name="my_enum")` persists enum **member names**, not their values —
`Status.IN_PROGRESS` is stored as `"IN_PROGRESS"` while every API contract and client expects
`"in_progress"`. The correct form is used in all 17 model files:

```python
Enum(CandidatePaperStatus, values_callable=enum_values, name="candidate_paper_status_enum")
```

**Why it matters.** 44 columns were affected. The failure is silent: writes succeed, and a
query filtering on the value simply matches nothing. It surfaces as "the feature does nothing"
rather than as an error.

**How to apply.** Never write a bare `Enum(SomeEnum)`. This is now Principle VIII in the
constitution, so a review that misses it is a rule violation, not an oversight.

---

## Built is not the same as delivered

_2026-08-06_

A reachability sweep found **23 frontend modules** that no user could reach — including the
entire Tertiary Studies workflow (13 modules, 7 live backend routes, a shipped migration).
Every one compiled, passed unit tests, and called a working endpoint.

**Why it matters.** No existing gate detects this. Unit tests, mypy, tsc, and coverage all
pass cleanly on an unreachable module, so the dashboard is green while the feature does not
exist for anyone. The gaps are catalogued as G16–G21 in `docs/feature-gaps.md`.

**How to apply.** Run `python3 scripts/audit_unreachable_frontend.py` — it walks the import
graph from `main.tsx` and exits non-zero on anything unreachable. A feature is done when an
e2e test drives it through the UI, not when its components exist. Now Principle X.

---

## Tests that guard on state hide missing features

_2026-08-06_

The e2e suite was full of `if (await x.isVisible()) { assert } else { test.skip() }`. Because
Playwright's `isVisible()` takes **no timeout**, it samples the DOM instantaneously and
returns `false` for anything not yet rendered — so the tests skipped rather than failed, and
a skip reads like a pass on any dashboard.

**Why it matters.** This is how every defect above stayed hidden. Removing the guards took
the suite from 67 to 82 passing and exposed seven real bugs in one afternoon.

**How to apply.** Use `expect(locator).toBeVisible({ timeout })`, which retries. When a
feature genuinely does not exist, use `test.fixme` with a comment citing the gap register —
it states "this should work and does not". Now Principle VI.

---

## TanStack Query keys collide on argument absence

_2026-08-05_

Query keys are identified by a structural **hash**. `['agents', undefined]` and
`['agents', null]` both serialise to `["agents",null]`, so a list query and a disabled detail
query shared one cache entry — and `enabled: false` only stops that observer, never the shared
query's `queryFn`.

**Why it matters.** The agent list was permanently stale and no amount of invalidation fixed
it, because the invalidation targeted a key another observer kept resurrecting.

**How to apply.** Namespace keys by role — `['agents', 'list', params]` and
`['agents', 'detail', id]` — never distinguish them by whether an argument is present.

---

## React reuses a DOM node for two elements in one position

_2026-08-05_

The study wizard rendered either a **Next** or a **Create** button in the same slot. React
reconciled them to a single DOM node and patched only the changed attributes, so clicking
Next on step 4 turned that very node into `type="submit"` — and the browser fired the submit
on the click already in flight. Step 5's input was silently discarded.

**Why it matters.** It presented as "the wizard sometimes skips the last step", which is
nearly impossible to reproduce deliberately.

**How to apply.** Give each variant a distinct stable `key` (`key="wizard-next"` /
`key="wizard-submit"`). This applies to any Edit/Save or Start/Stop pair sharing a slot.

---

## Vite proxy keys match by prefix

_2026-08-05_

`'/api'` in the Vite proxy config also captured the client-side `/api-docs` route and answered
it with the backend's JSON 404, so the API documentation page never worked in dev. Every
backend path is under `/api/v1/`, so the fix is the trailing slash: `'/api/'`.

**How to apply.** When adding a proxy entry, check that no client-side route shares its
prefix. The comment in `frontend/vite.config.ts` records this.

---

## Never point `DATABASE_URL` at the e2e database

_2026-08-06_

Running `db/tests/integration/` with `DATABASE_URL` set to the live e2e PostgreSQL corrupted
it: the tests cycle migrations up and down, leaving the database at revision `0011` with
`user.theme_preference` and the TOTP columns dropped.

**Why it matters.** Recovery is not just `alembic upgrade head` — asyncpg caches statement
plans, so the backend must also be restarted (otherwise `InvalidCachedStatementError`), and
the fixtures must be re-seeded.

**How to apply.** Integration tests default to SQLite for a reason. If you must target
PostgreSQL, use a throwaway database, never the one the e2e suite is running against.

---

## Playwright must be run from `frontend/`

_2026-08-06_

Running `npx playwright test` from the repository root picks up a different Playwright
installation and fails with a confusing `test.describe() called here` error. Root-level runs
also write `test-results/` and `playwright-report/` to the repo root, which `.gitignore` did
not originally cover — an artifact was committed by accident.

**How to apply.** `cd frontend && npx playwright test`. Both root paths are now gitignored,
but the correct working directory is still `frontend/`.

---

## Always use the mutation-testing wrapper

_2026-08-05_

`scripts/run-mutation-safe.sh <package>` runs cosmic-ray inside an isolated git worktree.

**Why it matters.** Calling `cosmic-ray run` directly mutates files in place. A crash or an
interrupted run leaves mutated source in the real working tree, where it is easy to commit
without noticing.

**How to apply.** Never call `cosmic-ray run` directly. The wrapper copies the session
database back to the package directory when it finishes.

---

## Test files are not covered by `ruff format`

_2026-08-05_

CI runs `ruff check` and `ruff format --check` against `*/src` only, so test files have never
been formatted. Running `ruff format` on one produces a large unrelated diff.

**How to apply.** When editing a test, make the edit by hand rather than reformatting the
file. Reformatting is a separate, deliberate change.

---

## Feature document numbering drifted from `specs/`

_2026-08-06_

`docs/features/` has its own sequence (`003`–`010`) that no longer lines up with the `specs/`
branch numbering — `docs/features/005` is Tertiary Studies, which is `specs/009`. From
**`012` onward the two are aligned**, and there is no `docs/features/011` because
`011-improve-testing-and-fix-ci` had no PRD.

**How to apply.** When citing a feature by number, say which sequence you mean for anything
below `012`.
