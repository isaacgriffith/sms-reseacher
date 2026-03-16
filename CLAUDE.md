# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

This is a research project by Isaac Griffith, PhD, licensed under the MIT License. A six-subproject UV workspace mono-repo for systematic mapping study (SMS) research automation.

## Active Technologies
- Python 3.14 (backend, db); TypeScript 5.4 / Node 20 LTS (frontend) + FastAPI + Pydantic v2, SQLAlchemy 2.0+ async, Alembic, React 18, MUI v5, react-hook-form + Zod, TanStack Query v5, pyotp, qrcode[pil], cryptography (Fernet), swagger-ui-react (004-frontend-improvements)
- PostgreSQL 16 (production/Docker Compose); SQLite + aiosqlite (unit/integration tests) (004-frontend-improvements)

### Runtime & Language
- Python 3.14 (backend, agents, db, agent-eval, researcher-mcp); TypeScript 5.4 / Node 20 LTS (frontend)
- PostgreSQL 16 (production/Docker Compose); SQLite + `aiosqlite` (unit/integration tests)

### Python Libraries (002-sms-workflow)
- **Job queue**: ARQ (async Redis-based background task queue)
- **Charting / visualisation**: matplotlib, networkx, plotly + kaleido (PDF/PNG export)
- **String matching / deduplication**: rapidfuzz
- **LLM evals**: deepeval + hypothesis (metamorphic tests)
- **FastMCP**: FastMCP 2.0+ (`@mcp.tool` decorator pattern)

### Frontend Libraries (002-sms-workflow)
- **Data visualisation**: D3.js (network graphs, result charts)
- **State / data fetching**: TanStack Query (React Query) with `refetchInterval` polling
- **Forms**: React Hook Form with `useWatch` (not `watch()`)

### User-Facing Features (004-frontend-improvements)
- **Authentication**: Password change with `token_version` session invalidation; partial JWT for 2FA second step
- **2FA / TOTP**: `pyotp` (secret generation, code verification); `qrcode[pil]` (QR base64 PNG); `cryptography` Fernet for TOTP secret encryption at rest; `bcrypt` for backup code hashing
- **Frontend UI**: MUI v5 (`@mui/material` + `@emotion/react`) — full migration of all components; `ThemeProvider` with Light/Dark/System palette modes
- **API Documentation**: `swagger-ui-react` — authenticated Swagger UI at `/api-docs`; backend `GET /api/v1/openapi.json` requires full JWT

### Quality Toolchain (003-project-setup-improvements)
- **Python mutation testing**: `cosmic-ray` (replaces `mutmut`) — run per package via `cosmic-ray.toml`
- **TypeScript mutation testing**: Stryker (`@stryker-mutator/vitest-runner`) — `npx stryker run` in `frontend/`
- **Python coverage**: `pytest-cov` with `--cov-fail-under=85`; Cobertura XML for CI PR comments
- **TypeScript coverage**: `@vitest/coverage-v8`; threshold 85% in `vite.config.ts`
- **E2e testing**: Playwright (TypeScript) in `frontend/e2e/`; `npx playwright test`
- **Skip enforcement**: Root `conftest.py` fails the run if any `@pytest.mark.skip` / `@pytest.mark.xfail` lacks `reason=`
- **Mutation CI**: Separate `workflow_dispatch` workflows (`mutation-python.yml`, `mutation-frontend.yml`) — NOT run per PR

## Recent Changes
- 001-repo-setup: Added Python 3.12 (backend, agents, db); TypeScript 5.4 / Node 20 LTS (frontend)
- 002-sms-workflow: Finalised library choices — ARQ, matplotlib, networkx, plotly/kaleido, rapidfuzz, D3.js
- 003-project-setup-improvements: cosmic-ray, Playwright, vitest coverage-v8, skip enforcement, mutation workflow_dispatch
- 004-frontend-improvements: password change + session invalidation, TOTP 2FA with QR/backup codes, theme preference (Light/Dark/System), full MUI v5 migration, authenticated API docs page

---

## Developer Workflow

### Environment Setup

```bash
# 1. Python 3.14
uv python install 3.14   # if using uv's managed Python

# 2. Install all Python workspace dependencies
uv sync --all-packages

# 3. Node 20 LTS + frontend dependencies
# Install Node 20 LTS via nvm or https://nodejs.org:
nvm install 20 && nvm use 20
cd frontend && npm install && cd ..

# 4. Playwright browsers (for e2e tests)
cd frontend && npx playwright install --with-deps chromium && cd ..

# 5. (Optional) pre-commit hooks
uv run pre-commit install
```

### Test Commands

```bash
# All Python packages together
uv run pytest backend/tests/ agents/tests/ db/tests/ agent-eval/tests/ researcher-mcp/tests/

# Single package
uv run --package sms-backend pytest backend/tests/
uv run --package sms-agents pytest agents/tests/
uv run --package sms-db pytest db/tests/
uv run --package sms-agent-eval pytest agent-eval/tests/
uv run --package sms-researcher-mcp pytest researcher-mcp/tests/

# Frontend
cd frontend && npm test             # run once
cd frontend && npm run test:watch   # watch mode
```

### Coverage Commands (minimum 85% line coverage enforced)

```bash
uv run --package sms-backend pytest backend/tests/ \
  --cov=src/backend --cov-report=term-missing --cov-report=xml:backend/coverage.xml

uv run --package sms-agents pytest agents/tests/ \
  --cov=src/agents --cov-report=term-missing --cov-report=xml:agents/coverage.xml

uv run --package sms-db pytest db/tests/ \
  --cov=src/db --cov-report=term-missing --cov-report=xml:db/coverage.xml

uv run --package sms-agent-eval pytest agent-eval/tests/ \
  --cov=src/agent_eval --cov-report=term-missing --cov-report=xml:agent-eval/coverage.xml

uv run --package sms-researcher-mcp pytest researcher-mcp/tests/ \
  --cov=src/researcher_mcp --cov-report=term-missing \
  --cov-report=xml:researcher-mcp/coverage.xml

# Frontend (85% threshold enforced via vite.config.ts)
cd frontend && npm run test:coverage
```

### Lint and Type-Check

```bash
# Python: lint + format check (all packages)
uv run ruff check backend/src agents/src db/src agent-eval/src researcher-mcp/src
uv run ruff format --check backend/src agents/src db/src agent-eval/src researcher-mcp/src

# Python: type check (all packages)
uv run mypy backend/src agents/src db/src agent-eval/src researcher-mcp/src

# Frontend
cd frontend && npm run lint
cd frontend && npm run format:check
```

### Mutation Testing

Mutation testing is slow and NOT run on every PR. Use `workflow_dispatch` in GitHub Actions
or run locally when needed.

```bash
# Python mutation testing (cosmic-ray) — run per package
uv run cosmic-ray run backend/cosmic-ray.toml
uv run cosmic-ray run agents/cosmic-ray.toml
uv run cosmic-ray run db/cosmic-ray.toml
uv run cosmic-ray run agent-eval/cosmic-ray.toml
uv run cosmic-ray run researcher-mcp/cosmic-ray.toml

# View kill rate
uv run cosmic-ray results backend/cosmic-ray.toml

# Generate HTML report
uv run cosmic-ray html-report backend/cosmic-ray.toml > /tmp/backend-mutation-report.html

# Frontend mutation testing (Stryker)
cd frontend && npx stryker run
```

### End-to-End Tests (Playwright)

E2e tests require the backend and a database to be running.

```bash
# Using Docker Compose (recommended for local e2e)
cp .env.example .env   # configure DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY
docker compose up -d

cd frontend
PLAYWRIGHT_BASE_URL=http://localhost:5173 npx playwright test
npx playwright show-report
```

Alternative — manual stack startup:

```bash
# Terminal 1: database migrations
uv run alembic upgrade head

# Terminal 2: backend
DATABASE_URL=sqlite+aiosqlite:///./dev.db \
SECRET_KEY=dev-secret \
uv run uvicorn backend.main:app --reload --port 8000

# Terminal 3: e2e tests (Playwright starts the Vite dev server automatically)
cd frontend && npx playwright test
```

### Database Migrations

```bash
uv run alembic upgrade head                                        # apply all migrations
uv run alembic revision --autogenerate -m "describe_change"        # new migration
uv run alembic downgrade -1                                        # roll back one step
```

### CI Mutation Workflows (GitHub Actions)

Mutation tests do not run on every PR. Trigger manually:

1. Go to **Actions** → **Python Mutation Tests** → **Run workflow**
2. Go to **Actions** → **Frontend Mutation Tests (Stryker)** → **Run workflow**

Or trigger via `workflow_call` from another workflow (e.g. speckit end-of-feature):

```yaml
- uses: ./.github/workflows/mutation-python.yml
- uses: ./.github/workflows/mutation-frontend.yml
```
