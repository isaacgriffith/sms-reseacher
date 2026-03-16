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

## Frontend Routes

| Route | Description | Auth required |
|-------|-------------|---------------|
| `/login` | Sign in (password + optional TOTP second step) | No |
| `/groups` | Research groups list | Yes |
| `/groups/:id/studies` | Studies for a group | Yes |
| `/studies/:id` | Study workspace | Yes |
| `/preferences` | Password change, theme selector, 2FA management | Yes |
| `/api-docs` | Interactive Swagger UI (auto-generated from backend) | Yes |

> MUI v5 migration complete — all components use `@mui/material`.

## Tech Stack

- **Python**: UV workspace, Ruff (lint + format), MyPy strict, pytest + pytest-asyncio, cosmic-ray (mutation)
- **TypeScript**: Vite 5, Vitest (coverage), ESLint 9, Prettier 3, Stryker (mutation)
- **Database**: SQLAlchemy 2.x async + Alembic; PostgreSQL 16 (prod) / SQLite (dev/test)
- **LLM**: LiteLLM abstraction — Anthropic Claude or local Ollama
- **MCP**: FastMCP (server) + `mcp` SDK (client)
- **Security**: TOTP 2FA (`pyotp`), encrypted secrets (Fernet), bcrypt backup codes, JWT `token_version` session invalidation
- **UI**: MUI v5 (`@mui/material`), TanStack Query v5, React Hook Form + Zod, `swagger-ui-react`
- **Docker**: Multi-stage `python:3.14-slim` + `nginx:alpine`; images pushed to GHCR on `main`
- **CI**: GitHub Actions — lint, test (≥85% line coverage with PR comment), mutation (≥85% kill rate, manual trigger), Docker scan, GHCR push

## License

MIT — see [LICENSE](LICENSE).
