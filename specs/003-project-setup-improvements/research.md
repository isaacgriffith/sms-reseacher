# Research: Project Setup & Quality Improvements

**Feature**: 003-project-setup-improvements
**Date**: 2026-03-15

---

## 1. cosmic-ray Configuration for Python 3.14 + pytest + uv

**Decision**: Use `cosmic-ray.toml` per Python package, invoking pytest via `uv run`.

**Rationale**: cosmic-ray operates at the AST level and is independent of the async runtime,
making it compatible with `asyncio_mode = "auto"`. Each package requires its own config
because cosmic-ray has no workspace-level inheritance. The `uv run` prefix ensures the
correct virtual environment is activated.

**Canonical `cosmic-ray.toml` structure** (per package, e.g. `backend/cosmic-ray.toml`):

```toml
[cosmic-ray]
module-path = "src/backend"
timeout = 30.0
excluded-modules = []

[cosmic-ray.executor]
# Use the default local executor (single process)

[cosmic-ray.test-command]
command = "uv run --package sms-backend pytest backend/tests/unit -x -q"
```

**Run command**:
```bash
uv run cosmic-ray run backend/cosmic-ray.toml
uv run cosmic-ray results backend/cosmic-ray.toml  # show kill rate
uv run cosmic-ray html-report backend/cosmic-ray.toml > /tmp/mutation-report.html
```

**Kill-rate check** (for CI):
```bash
SCORE=$(uv run cosmic-ray results backend/cosmic-ray.toml \
  | grep -oP 'score: \K[\d.]+')
```

**Python 3.14 compatibility**: cosmic-ray targets the standard CPython AST; no known
incompatibilities with 3.14. The `timeout` field guards against infinite loops caused by
async mutations.

**Alternatives considered**:
- `mutmut`: Incompatible approach (per-file rather than per-operator); harder to parallelise;
  already present but being superseded per spec clarification.

---

## 2. pytest-cov Coverage PR Comments in GitHub Actions

**Decision**: Generate Cobertura XML with `pytest-cov`; post PR comment using
`MishaKav/pytest-coverage-comment@main`.

**Rationale**: `pytest-cov` already configured in every `pyproject.toml` with
`--cov-fail-under=85`. Adding `--cov-report=xml:coverage.xml` generates Cobertura format,
which `MishaKav/pytest-coverage-comment` consumes directly. This action posts a
collapsible coverage table on the PR with line/branch percentages.

**Required CI step additions** (in `python-test` matrix job):

```yaml
- name: Run pytest with coverage
  run: |
    uv run --package ${{ matrix.package }} pytest ${{ matrix.testdir }} \
      --cov-report=xml:${{ matrix.testdir }}/../coverage.xml \
      --cov-fail-under=85

- name: Post coverage comment
  uses: MishaKav/pytest-coverage-comment@main
  if: github.event_name == 'pull_request'
  with:
    pytest-xml-coverage-path: ${{ matrix.srcdir }}/../coverage.xml
    title: "Coverage — ${{ matrix.package }}"
  permissions:
    pull-requests: write
```

**Fail behaviour**: `--cov-fail-under=85` already causes `pytest` to exit non-zero; the
comment is informational even when the build fails.

**Alternatives considered**:
- `codecov/codecov-action`: Requires a Codecov account; adds external dependency.
- `actions/github-script` custom comment: More code to maintain.

---

## 3. vitest Coverage Configuration and PR Comments

**Decision**: Use `@vitest/coverage-v8` as the coverage provider; add `json-summary`
reporter; post PR comment via `davelosert/vitest-coverage-report-action`.

**Rationale**: The `v8` provider is the recommended native coverage provider for Vitest
(no Istanbul instrumentation overhead). `json-summary` generates
`coverage/coverage-summary.json` which the report action reads.

**`vite.config.ts` additions**:

```typescript
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: ['./src/test-setup.ts'],
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'json-summary', 'lcov'],
    thresholds: {
      lines: 85,
      branches: 85,
    },
    include: ['src/**/*.{ts,tsx}'],
    exclude: ['src/**/*.test.{ts,tsx}', 'src/test-setup.ts'],
  },
},
```

**New dev dependency**: `@vitest/coverage-v8`

**CI step additions** (in `frontend-test` job):

```yaml
- name: Run Vitest with coverage
  run: npm run test:coverage
  working-directory: frontend

- name: Post coverage comment
  uses: davelosert/vitest-coverage-report-action@v2
  if: github.event_name == 'pull_request'
  with:
    working-directory: frontend
  permissions:
    pull-requests: write
    contents: read
```

**Fail behaviour**: `thresholds` in `vite.config.ts` cause vitest to exit non-zero when
coverage is below 85% — CI fails before the comment step.

**Alternatives considered**:
- Istanbul provider: More complex setup; v8 is simpler and sufficient.
- Manual `node -e` threshold check: Already in `ci.yml` but fragile; replaced by vitest
  native thresholds.

---

## 4. pytest Skip/xfail Enforcement

**Decision**: Root `conftest.py` with a `pytest_collection_finish` hook that fails the
session if any collected item has a skip or xfail marker without a non-empty `reason=`.

**Rationale**: A conftest.py hook at the repo root applies to all packages in the uv
workspace when running `pytest` from the root. No third-party plugin is needed; the hook
is ~15 lines and trivially testable.

**Implementation** (`/conftest.py` at repo root):

```python
"""Root conftest: enforce reason= on all skip/xfail markers."""
import pytest


def pytest_collection_finish(session: pytest.Session) -> None:
    """Fail the session if any skip or xfail marker lacks a non-empty reason."""
    violations: list[str] = []
    for item in session.items:
        for marker_name in ("skip", "xfail"):
            marker = item.get_closest_marker(marker_name)
            if marker is None:
                continue
            reason = marker.kwargs.get("reason", "") or (
                marker.args[0] if marker.args else ""
            )
            if not str(reason).strip():
                violations.append(
                    f"{item.nodeid}: @pytest.mark.{marker_name} missing reason="
                )
    if violations:
        pytest.fail(
            "The following markers are missing a reason=:\n"
            + "\n".join(f"  {v}" for v in violations),
            pytrace=False,
        )
```

**Alternatives considered**:
- `pytest-enforce-skip-reason` PyPI plugin: Does the same thing; prefer zero extra deps.
- Ruff rule: No standard ruff rule exists for this today; a custom plugin would be needed.
- `pytest --strict-markers` + CI check: Catches undefined markers, not missing `reason=`.

---

## 5. Playwright E2e Tests with FastAPI + React in GitHub Actions

**Decision**: Use Playwright `webServer` to start the Vite dev server automatically;
start the FastAPI backend as a background process; provision PostgreSQL via GitHub Actions
`services:` container.

**Rationale**: Playwright's `webServer` config handles dev server lifecycle and base URL
injection automatically. The backend is a standard Python process that can be backgrounded
with `&` and waited for with a simple health-check poll. This requires no external
orchestration tools.

**`playwright.config.ts`**:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: [
    {
      // Vite dev server (frontend)
      command: 'npm run dev',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
      cwd: '.',
    },
    {
      // FastAPI backend
      command: 'uv run uvicorn backend.main:app --port 8000',
      url: 'http://localhost:8000/api/v1/health',
      reuseExistingServer: !process.env.CI,
      cwd: '..',
    },
  ],
});
```

**GitHub Actions e2e job** (added to `ci.yml`):

```yaml
e2e-tests:
  name: E2e Tests (Playwright)
  runs-on: ubuntu-latest
  needs: [python-test, frontend-test]
  services:
    postgres:
      image: postgres:16
      env:
        POSTGRES_USER: sms
        POSTGRES_PASSWORD: sms
        POSTGRES_DB: sms_test
      ports:
        - 5432:5432
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5
  env:
    DATABASE_URL: postgresql+asyncpg://sms:sms@localhost:5432/sms_test
    SECRET_KEY: test-secret-key
    LLM_PROVIDER: anthropic
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v4
      with: { version: "latest" }
    - run: uv python install 3.14
    - run: uv sync --all-packages
    - uses: actions/setup-node@v4
      with: { node-version: "20", cache: "npm",
              cache-dependency-path: "frontend/package-lock.json" }
    - run: npm ci
      working-directory: frontend
    - run: npx playwright install --with-deps chromium
      working-directory: frontend
    - run: uv run alembic upgrade head
    - run: npx playwright test
      working-directory: frontend
    - uses: actions/upload-artifact@v4
      if: failure()
      with:
        name: playwright-report
        path: frontend/playwright-report/
```

**E2e test scope** (primary user journeys per service):
- Create a study (backend → db)
- Search for papers (backend → researcher-mcp → Semantic Scholar mock)
- Screen a paper (backend → agents → LLM stub)
- View results dashboard (frontend → backend)

**Note on LLM calls in e2e**: Agent-triggered LLM calls should be stubbed/mocked at the
`LLMClient` level via environment variable (`LLM_PROVIDER=mock`) or fixture injection to
avoid real API costs in CI.

**Alternatives considered**:
- Full Docker Compose in CI: More faithful to production but ~3× slower to build.
- API-only e2e with `pytest + httpx`: Excluded per spec clarification (Playwright chosen).

---

## 6. Mutation Workflow Separation (workflow_dispatch)

**Decision**: Extract mutation testing jobs into two separate workflow files:
`mutation-python.yml` and `mutation-frontend.yml`, each with
`on: [workflow_dispatch, workflow_call]`. Remove mutation jobs from `ci.yml`.

**Rationale**: Mutation testing is slow (minutes to hours per service). Running it on
every PR would block contributor feedback loops. `workflow_dispatch` enables manual
triggering; `workflow_call` enables the speckit end-of-feature trigger mechanism.

**`mutation-python.yml` trigger block**:
```yaml
on:
  workflow_dispatch:
    inputs:
      packages:
        description: "Comma-separated package names to test (default: all)"
        required: false
        default: "all"
  workflow_call:
    inputs:
      packages:
        type: string
        required: false
        default: "all"
```

**Alternatives considered**:
- Scheduled nightly workflow: Would run even when no code changed; `workflow_dispatch` is
  more intentional.
- Keep in `ci.yml` with `if: github.event_name == 'workflow_dispatch'`: Clutters the
  primary CI file; separate files are cleaner.
