# Quickstart: Wire Up Unreachable Workflows

**Feature**: `012-wire-up-unreachable-workflows`
**Branch**: `012-wire-up-unreachable-workflows`

How to set up, verify the starting state, and confirm the feature is done. Read
[plan.md](./plan.md) for what to build and [research.md](./research.md) for why.

---

## Setup

```bash
uv sync --all-packages
cd frontend && npm install && cd ..

cp .env.example .env         # DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY
docker compose up -d
uv run alembic upgrade head
uv run python scripts/seed_e2e_user.py
```

> Package names are not directory names — `agents` and `db`, not `sms-agents` / `sms-db`.
> See [MEMORY.md](../../MEMORY.md).

---

## Confirm the starting state

Everything below **should fail or report a problem right now**. If any already passes, the
baseline has moved and the plan needs revisiting before you start.

```bash
# 1. 23 modules unreachable — the defect this feature closes
python3 scripts/audit_unreachable_frontend.py

# 2. Two placeholders standing over finished components
grep -rn "future sprint" frontend/src

# 3. Three screening tests marked test.fixme because the capability is unreachable
grep -c "test.fixme" frontend/e2e/screen-paper.spec.ts

# 4. A Tertiary study renders the mapping-study workspace — verify by opening one in the UI
```

Baseline as of 2026-08-06: 23 unreachable modules, 2 placeholders, 8 `test.fixme` across the
suite (3 in `screen-paper.spec.ts`).

### Re-verified 2026-08-08, after TREF1–TREF9 landed (T001)

Nothing has started passing, so the plan stands. One count moved, and it is worth knowing why
before T032 is written:

| Check                                           | 2026-08-06 | 2026-08-08 | Reading                                     |
| ----------------------------------------------- | ---------- | ---------- | ------------------------------------------- |
| `audit_unreachable_frontend.py`                 | 23, exit 1 | 23, exit 1 | Unchanged — the refactors moved no boundary |
| `grep -rn "future sprint" frontend/src`         | 2          | **4**      | See below                                   |
| `grep -c "test.fixme" e2e/screen-paper.spec.ts` | 3          | 3          | Unchanged                                   |
| `test.fixme` suite-wide                         | 8          | 8          | 4 database-selection · 3 screen-paper · 1 admin/test_agent_wizard |
| `uv run pre-commit run --all-files` (T002)      | —          | 9/9 pass   | Later gate failures are attributable here   |

**The placeholder grep went up while the defect went down.** TREF2 replaced the two literal
`<Typography>` lines in `StudyPage.tsx` with a single `futureSprintPlaceholder(phase)` factory in
`frontend/src/components/studies/studyTypeDispatch.tsx`, and TREF1's characterisation test names
the string three times to prove the extraction preserved behaviour. One production occurrence,
three assertions about it.

Consequences for later tasks:

- **T032 is a replacement, not a removal.** Nothing here is deleted to make a grep pass. The
  placeholder goes away because T029–T031 register real renderers for phases 4 and 5 —
  `ExtractionPage`, `ValidityForm`, `QualityReport` — and `futureSprintPlaceholder` is then
  referenced by nothing. `StudyPage.tsx` itself stays; it already delegates to the dispatch map,
  and after TREF2 no longer contains the placeholder string at all. If the placeholder were
  stripped before its replacement were wired, phases 4 and 5 would render blank — a worse state
  than an honest "not yet available", and one the reachability audit would not catch, because the
  audit answers *is this module imported*, not *does this phase show anything*.
- **T028** and the definition-of-done grep below must exclude test files, or they will fail on the
  very assertions that prove the placeholder is gone. A grep count is a poor oracle: it cannot
  tell an assertion about a defect from the defect.

---

## Build order

The order matters — two items are refactors that must land **before** the work they enable, per
Principle IV.

| Step | Work                                                                | Why here                                                                                      |
| ---- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 1    | **C1** — cover, then extract `StudyPage`'s study-type dispatch      | Behaviour-preserving. Adding Tertiary to a boolean chain deepens a violation                  |
| 2    | **C2** — extract the screening helpers into `screening_pipeline`    | The re-screen job is its second consumer; extracting first avoids duplication                 |
| 3    | **C3** — make the screening pass propagate provider errors          | FR-024 is unsatisfiable while a fault is persisted as a rejection                             |
| 4    | Journey 1 — screening decisions (shared view, panel, funnel)        | P1; unblocks agreement measurement                                                            |
| 4a   | **C5** — required observed state + migrate existing decision tests  | Same change as journey 1. ~10 existing calls stop working; migrating them is part of the task |
| 5    | Journey 2 — `research_group_id`, then Tertiary via the dispatch map | P2; one edge makes 13 modules reachable                                                       |
| 6    | Journey 3 — phases 4 and 5 over the existing components             | P3                                                                                            |
| 7    | Journey 4 — migration `0019`, endpoint, ARQ job                     | P4; the only genuinely new capability                                                         |
| 8    | Wire the reachability audit into CI                                 | Turns the oracle into a regression gate                                                       |

Steps 1–3 are `refactor:` / `fix:` commits and must not carry feature changes (Principle IV).

---

## Verify each journey

```bash
cd frontend && npx playwright test screen-paper.spec.ts        # journey 1
cd frontend && npx playwright test tertiary-workflow.spec.ts   # journey 2
cd frontend && npx playwright test extraction-phases.spec.ts   # journey 3
cd frontend && npx playwright test rescreen.spec.ts            # journey 4
```

> Run Playwright from `frontend/`. From the repository root it picks up a different installation
> and fails with `test.describe() called here`.

---

## Definition of done

```bash
# Reachability — the acceptance oracle. Must exit 0
python3 scripts/audit_unreachable_frontend.py

# No placeholder survives its implementation
grep -rn "future sprint" frontend/src && echo "FAIL: placeholder still present"

# No conditional skips or isVisible() guards introduced (Principle VI)
grep -rn "isVisible()" frontend/e2e/ | grep -v "^\s*//"
grep -rn "test.skip(" frontend/e2e/

# Full suites
uv run pytest backend/tests/ db/tests/
cd frontend && npm run test:coverage && npx playwright test

# Quality gates
uv run ruff check backend/src db/src && uv run ruff format --check backend/src db/src
uv run mypy backend/src db/src
uv run pre-commit run --all-files

# Mutation, per modified subproject (≥85% killed)
./scripts/run-mutation-safe.sh backend
./scripts/run-mutation-safe.sh db
cd frontend && npx stryker run
```

Also required before merge:

- `docs/feature-gaps.md` — mark **G18, G19, G20** closed; the audit count drops to the two G21
  modules.
- Root `README.md` — the route-table note saying Tertiary is unreachable is no longer true.
- `CLAUDE.md`, `CHANGELOG.md`, and the `backend/`, `db/`, `frontend/` subproject READMEs and
  CHANGELOGs, per Development Workflow step 9.

---

## Traps specific to this feature

| Trap                                                                                    | Guard                                                         |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Components unreachable for months were unit-tested against mocks, never a live server   | Exercise each through e2e before calling its part done        |
| `JobType.RESCREEN` needs a migration — a Python enum member alone fails on insert       | Migration `0019` with a working `downgrade()`                 |
| The enum column persists values, not names, via `values_callable`                       | Stored value is `"rescreen"`. See MEMORY.md                   |
| Reusing the shared AI reviewer makes two rounds indistinguishable                       | One reviewer per round, recorded in `agent_config` (R2)       |
| `_run_screening_pass` currently turns a provider fault into a rejection                 | Fix in step 3, with its own test, before journey 4            |
| Adding `isTertiary` beside `isSLR` / `isRapid` is the cheapest change and the wrong one | Step 1 first — this is how the Tertiary UI became unreachable |
