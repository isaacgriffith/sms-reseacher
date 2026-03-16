# Quickstart: Project Setup & Quality Toolchain

This guide documents every command a contributor needs to run tests, check coverage,
lint, and execute mutation testing across the SMS Researcher mono-repo.

## Prerequisites (clean checkout)

```bash
# 1. Python 3.14
uv python install 3.14   # if using uv's managed Python
# or install system Python 3.14 and ensure it is on PATH

# 2. Install all Python workspace dependencies
uv sync --all-packages

# 3. Node 20 LTS + frontend dependencies
# Install Node 20 LTS from https://nodejs.org or via nvm:
nvm install 20 && nvm use 20
cd frontend && npm install && cd ..

# 4. Playwright browsers (for e2e tests)
cd frontend && npx playwright install --with-deps chromium && cd ..

# 5. (Optional) pre-commit hooks
uv run pre-commit install
```

---

## Python Services

### Run all Python tests

```bash
# All packages together
uv run pytest backend/tests/ agents/tests/ db/tests/ agent-eval/tests/ researcher-mcp/tests/

# Single package
uv run --package sms-backend pytest backend/tests/
uv run --package sms-agents pytest agents/tests/
uv run --package sms-db pytest db/tests/
uv run --package sms-agent-eval pytest agent-eval/tests/
uv run --package sms-researcher-mcp pytest researcher-mcp/tests/
```

### Run with coverage (minimum 85% enforced)

Coverage thresholds are configured in each `pyproject.toml` (`--cov-fail-under=85`).

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
```

### Python lint and type check

```bash
# Lint + format check (all packages)
uv run ruff check backend/src agents/src db/src agent-eval/src researcher-mcp/src
uv run ruff format --check backend/src agents/src db/src agent-eval/src researcher-mcp/src

# Type check (all packages)
uv run mypy backend/src agents/src db/src agent-eval/src researcher-mcp/src
```

### Python mutation testing (cosmic-ray)

Mutation testing is slow. Run per package when needed.

```bash
# Run mutation session (creates/updates a .sqlite results database)
uv run cosmic-ray run backend/cosmic-ray.toml
uv run cosmic-ray run agents/cosmic-ray.toml
uv run cosmic-ray run db/cosmic-ray.toml
uv run cosmic-ray run agent-eval/cosmic-ray.toml
uv run cosmic-ray run researcher-mcp/cosmic-ray.toml

# View results (kill rate)
uv run cosmic-ray results backend/cosmic-ray.toml

# Generate HTML report
uv run cosmic-ray html-report backend/cosmic-ray.toml > /tmp/backend-mutation-report.html
```

---

## Frontend

### Run unit/component tests

```bash
cd frontend
npm test                      # run once
npm run test:watch            # watch mode
npm run test:coverage         # with coverage (min 85% enforced via vite.config.ts)
```

### Frontend lint and format check

```bash
cd frontend
npm run lint                  # ESLint
npm run format:check          # Prettier
```

### Frontend mutation testing (Stryker)

```bash
cd frontend
npx stryker run               # runs against src/**; fails if kill rate < 85%
```

---

## End-to-End Tests (Playwright)

E2e tests require the backend and a database to be running. Playwright's `webServer`
config starts the Vite dev server automatically.

### Using Docker Compose (recommended for local e2e)

```bash
# Start the full stack
cp .env.example .env   # configure DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY
docker compose up -d

# Run e2e tests (Playwright connects to running stack)
cd frontend
PLAYWRIGHT_BASE_URL=http://localhost:5173 npx playwright test

# View HTML report (after test run)
npx playwright show-report
```

### Without Docker (manual stack start)

```bash
# Terminal 1 — database migrations
uv run alembic upgrade head

# Terminal 2 — backend
DATABASE_URL=sqlite+aiosqlite:///./dev.db \
SECRET_KEY=dev-secret \
uv run uvicorn backend.main:app --reload --port 8000

# Terminal 3 — frontend dev server (Playwright webServer starts this automatically)

# Terminal 4 — run e2e tests
cd frontend && npx playwright test
```

---

## Database Migrations

```bash
uv run alembic upgrade head              # apply all migrations
uv run alembic revision --autogenerate -m "describe_change"   # new migration
uv run alembic downgrade -1              # roll back one step
```

---

## CI Mutation Workflows (GitHub Actions)

Mutation tests do not run on every PR. Trigger manually:

1. Go to **Actions** → **Python Mutation Tests** → **Run workflow**
2. Go to **Actions** → **Frontend Mutation Tests (Stryker)** → **Run workflow**

Or trigger from another workflow (speckit end-of-feature):

```yaml
- uses: ./.github/workflows/mutation-python.yml
- uses: ./.github/workflows/mutation-frontend.yml
```
