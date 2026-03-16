# SMS Researcher

A six-sub-project UV workspace mono-repo for systematic mapping study (SMS) research automation.

## Sub-projects

| Sub-project | Language | Purpose |
|-------------|----------|---------|
| [`backend/`](backend/README.md) | Python 3.14 / FastAPI | REST API gateway; orchestrates agents |
| [`agents/`](agents/README.md) | Python 3.14 | LLM-powered research agents (screener, extractor, synthesiser) |
| [`db/`](db/README.md) | Python 3.14 / SQLAlchemy | Shared database models + Alembic migrations |
| [`agent-eval/`](agent-eval/README.md) | Python 3.14 / Typer | CLI for evaluating agent quality with LLM-as-a-Judge |
| [`researcher-mcp/`](researcher-mcp/README.md) | Python 3.14 / FastMCP | MCP server for paper search and PDF fetching |
| [`frontend/`](frontend/) | TypeScript 5 / React 18 | Researcher-facing SPA (Vite + Vitest) |

## Quick Start

See [quickstart.md](specs/001-repo-setup/quickstart.md) for full onboarding instructions.

```bash
# Install all Python dependencies (shared UV workspace)
uv sync

# Start backend (development)
uv run --package sms-backend uvicorn backend.main:app --reload --port 8000

# Start researcher-mcp server
uv run --package sms-researcher-mcp researcher-mcp

# Start frontend (development)
cd frontend && npm install && npm run dev

# Run all Python tests
uv run pytest backend/tests/ agents/tests/ db/tests/ agent-eval/tests/ researcher-mcp/tests/
```

## Docker Compose

```bash
cp .env.example .env   # configure environment variables
docker compose up       # starts frontend + backend + db + researcher-mcp
```

See [quickstart.md](specs/001-repo-setup/quickstart.md#docker-local-deployment) for Docker details.

## Tech Stack

- **Python**: UV workspace, Ruff (lint + format), MyPy strict, pytest + pytest-asyncio, cosmic-ray (mutation)
- **TypeScript**: Vite 5, Vitest (coverage), ESLint 9, Prettier 3, Stryker (mutation)
- **Database**: SQLAlchemy 2.x async + Alembic; PostgreSQL 16 (prod) / SQLite (dev/test)
- **LLM**: LiteLLM abstraction — Anthropic Claude or local Ollama
- **MCP**: FastMCP (server) + `mcp` SDK (client)
- **Docker**: Multi-stage `python:3.14-slim` + `nginx:alpine`; images pushed to GHCR on `main`
- **CI**: GitHub Actions — lint, test (≥85% line coverage with PR comment), mutation (≥85% kill rate, manual trigger), Docker scan, GHCR push

## License

MIT — see [LICENSE](LICENSE).
