# Quickstart: Improve Testing and Fix CI

## Verify CI Fixes

After applying changes, verify all CI jobs would pass locally:

```bash
# Python lint (all subprojects)
uv run ruff check backend/src agents/src db/src agent-eval/src researcher-mcp/src
uv run ruff format --check backend/src agents/src db/src agent-eval/src researcher-mcp/src
uv run mypy backend/src agents/src db/src agent-eval/src researcher-mcp/src

# Python tests with coverage (each subproject)
uv run --package backend pytest backend/tests/ --cov=src/backend --cov-fail-under=85
uv run --package agents pytest agents/tests/ --cov=src/agents --cov-fail-under=85
uv run --package db pytest db/tests/ --cov=src/db --cov-fail-under=85
uv run --package agent-eval pytest agent-eval/tests/ --cov=src/agent_eval --cov-fail-under=85
uv run --package researcher-mcp pytest researcher-mcp/tests/ --cov=src/researcher_mcp --cov-fail-under=85

# Frontend lint
cd frontend && npm run lint && npm run format:check && cd ..

# Frontend tests with coverage
cd frontend && npm run test:coverage && cd ..

# Docker builds
docker build -f backend/Dockerfile -t backend:ci .
docker build -f researcher-mcp/Dockerfile -t researcher-mcp:ci .
docker build -f frontend/Dockerfile -t frontend:ci .
```

## Verify Pre-Commit Hooks

```bash
# Install hooks
uv run pre-commit install

# Run all hooks against entire codebase
uv run pre-commit run --all-files
```

## Verify Rename

```bash
# Check no sms- prefixed package names remain
grep -r "sms-backend\|sms-agent-eval\|sms-researcher-mcp\|sms-frontend" \
  --include="*.toml" --include="*.yml" --include="*.yaml" \
  --include="*.json" --include="*.md" --include="Dockerfile" \
  --exclude-dir=.venv --exclude-dir=specs --exclude-dir=node_modules .

# Verify workspace resolves
uv sync --all-packages

# Regenerate lockfile
cd frontend && npm install && cd ..
```

## Key Files Modified

| Area            | Files                                                                                                            |
| --------------- | ---------------------------------------------------------------------------------------------------------------- |
| CI workflow     | `.github/workflows/ci.yml`, `.github/workflows/mutation-python.yml`                                              |
| Pre-commit      | `.pre-commit-config.yaml`                                                                                        |
| Package names   | `backend/pyproject.toml`, `agent-eval/pyproject.toml`, `researcher-mcp/pyproject.toml`, `frontend/package.json`  |
| Docker          | `backend/Dockerfile`, `researcher-mcp/Dockerfile`                                                                |
| Cosmic-ray      | `backend/cosmic-ray.toml`, `agent-eval/cosmic-ray.toml`, `researcher-mcp/cosmic-ray.toml`                        |
| Coverage config | `frontend/vite.config.ts`                                                                                        |
| Documentation   | `README.md`, `CLAUDE.md`, `*/README.md`, `*/CHANGELOG.md`                                                        |
| Governance      | `.specify/memory/constitution.md`, `.specify/templates/plan-template.md`, `.specify/templates/tasks-template.md` |
