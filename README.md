# SMS Researcher

A six-sub-project `uv` workspace mono-repo that automates secondary and tertiary research
studies: Systematic Mapping Studies (SMS), Systematic Literature Reviews (SLR), Rapid
Reviews, and Tertiary Studies.

## Documentation

| Document                                        | Answers                                              |
| ----------------------------------------------- | ---------------------------------------------------- |
| [CONTEXT.md](CONTEXT.md)                        | Where am I? Architecture, repo map, request flow     |
| [MEMORY.md](MEMORY.md)                          | What will bite me? Non-obvious gotchas, with reasons |
| [CLAUDE.md](CLAUDE.md)                          | What commands do I run?                              |
| [constitution](.specify/memory/constitution.md) | What rules are binding? Principles I–X               |
| [docs/feature-gaps.md](docs/feature-gaps.md)    | What is actually built vs. only specified?           |
| [docs/features/](docs/features/README.md)       | What is planned next?                                |

## Sub-projects

| Sub-project                                   | Language                 | Purpose                                                                          |
| --------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------- |
| [`backend/`](backend/README.md)               | Python 3.14 / FastAPI    | REST API gateway; orchestrates agents                                            |
| [`agents/`](agents/README.md)                 | Python 3.14              | 12 LLM-powered research agents (screener, extractor, synthesiser, …) via LiteLLM |
| [`db/`](db/README.md)                         | Python 3.14 / SQLAlchemy | Shared database models + Alembic migrations                                      |
| [`agent-eval/`](agent-eval/README.md)         | Python 3.14 / Typer      | CLI for evaluating agent quality with LLM-as-a-Judge                             |
| [`researcher-mcp/`](researcher-mcp/README.md) | Python 3.14 / FastMCP    | MCP server for paper search and PDF fetching                                     |
| [`frontend/`](frontend/)                      | TypeScript 5 / React 18  | Researcher-facing SPA (Vite + Vitest)                                            |

## Quick Start

See [quickstart.md](specs/001-repo-setup/quickstart.md) for full onboarding instructions.

```bash
# Install all Python dependencies (shared uv workspace)
uv sync --all-packages

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

## Supported Study Types

| Study Type   | Description                                                                                                                                                         |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SMS**      | Systematic Mapping Study — scoping, search, screening, extraction, visualisation                                                                                    |
| **SLR**      | Systematic Literature Review — full PICO protocol, quality assessment, meta-analysis/synthesis, grey literature, report export                                      |
| **Rapid**    | Rapid Review — accelerated protocol with stakeholder involvement, narrative synthesis, and Evidence Briefing export                                                 |
| **Tertiary** | Tertiary Study — aggregates secondary studies (SLRs, SMSs, Rapid Reviews); seed import, structured data extraction, landscape synthesis, and tertiary report export |

All study types share the **Protocol** tab (Phase 0) — a reusable, versioned research protocol graph visualised with D3.js. Researchers can view the default template, copy and customise it in the dual-pane editor (visual graph + YAML), assign it to a study, and track task execution state in real time.

## Frontend Routes

| Route                                   | Description                                                  | Auth required |
| --------------------------------------- | ------------------------------------------------------------ | ------------- |
| `/login`                                | Sign in (password + optional TOTP second step)               | No            |
| `/public/briefings/:token`              | Public Evidence Briefing view (unauthenticated, share token) | No            |
| `/groups`                               | Research groups list                                         | Yes           |
| `/groups/:groupId/studies`              | Studies for a group                                          | Yes           |
| `/studies/:studyId`                     | Study workspace — phase tabs, dispatched by study type       | Yes           |
| `/studies/:studyId/results`             | Results dashboard — charts, domain model, export             | Yes           |
| `/protocols`                            | Protocol Library — browse, copy, import, assign, export      | Yes           |
| `/protocols/:id`, `/protocols/:id/edit` | Protocol editor — dual-pane D3 graph + YAML                  | Yes           |
| `/admin`                                | Admin panel — providers, models, agents, search integrations | Yes           |
| `/preferences`                          | Password change, theme selector, 2FA management              | Yes           |
| `/api-docs`                             | Interactive Swagger UI (auto-generated from backend)         | Yes           |

**The SLR and Rapid Review workflows have no routes of their own.** Their editors, quality
configuration, synthesis, report, and briefing pages are phase panels rendered inside
`/studies/:studyId`, dispatched on the study's type. The Tertiary Studies UI is built but not
yet dispatched, so it is currently unreachable — see G19 in
[docs/feature-gaps.md](docs/feature-gaps.md).

> MUI v5 migration complete — all components use `@mui/material`.

## Admin Panel

The admin panel (`/admin`) provides management tabs for:

| Tab                     | Description                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Providers**           | Add/edit/delete LLM provider credentials (Anthropic, OpenAI, Ollama)                                         |
| **Models**              | View and enable/disable individual models fetched from each provider                                         |
| **Agents**              | Create, edit, and manage AI agent definitions via a multi-step wizard                                        |
| **Search Integrations** | Configure and test API credentials for academic database sources (IEEE Xplore, Scopus, Web of Science, etc.) |

### Supported LLM Provider Types

| Type        | Auth          | Model source                              |
| ----------- | ------------- | ----------------------------------------- |
| `anthropic` | API key       | `GET https://api.anthropic.com/v1/models` |
| `openai`    | API key       | `GET https://api.openai.com/v1/models`    |
| `ollama`    | Base URL only | `GET {base_url}/api/tags`                 |

Agent system messages are Jinja2 templates rendered at invocation time with `{{ domain }}` and `{{ study_type }}` variables injected from the active study context.

## Database Search & Full-Text Retrieval

The `researcher-mcp` server provides MCP tools for multi-database academic paper search:

| MCP Tool                  | Description                                                            |
| ------------------------- | ---------------------------------------------------------------------- |
| `search_papers`           | Fan-out search across up to 9 databases; merged + deduplicated results |
| `fetch_paper_pdf`         | Retrieve full-text PDF via Unpaywall (OA) or Sci-Hub (opt-in)          |
| `convert_pdf_to_markdown` | Convert PDF bytes to Markdown via MarkItDown                           |
| `convert_url_to_markdown` | Fetch a URL and convert content to Markdown                            |
| `fetch_stored_markdown`   | Retrieve previously stored full-text Markdown for a paper              |

### Supported Database Sources

| Source              | Credential env var                        |
| ------------------- | ----------------------------------------- |
| IEEE Xplore         | `IEEE_XPLORE_API_KEY`                     |
| ACM Digital Library | _(no key required)_                       |
| Scopus              | `ELSEVIER_API_KEY`, `ELSEVIER_INST_TOKEN` |
| Web of Science      | `WOS_API_KEY`                             |
| Inspec              | `ELSEVIER_API_KEY`, `ELSEVIER_INST_TOKEN` |
| ScienceDirect       | `ELSEVIER_API_KEY`, `ELSEVIER_INST_TOKEN` |
| SpringerNature      | `SPRINGER_API_KEY`                        |
| Google Scholar      | `SCHOLARLY_PROXY_URL` (optional)          |
| Semantic Scholar    | `SEMANTIC_SCHOLAR_API_KEY` (optional)     |

Full-text retrieval also uses `UNPAYWALL_EMAIL` and `SCIHUB_ENABLED` env vars.

## Tech Stack

- **Python**: UV workspace, Ruff (lint + format), MyPy strict, pytest + pytest-asyncio, cosmic-ray (mutation)
- **TypeScript**: Vite 5, Vitest (coverage), ESLint 9, Prettier 3, Stryker (mutation)
- **Database**: SQLAlchemy 2.x async + Alembic; PostgreSQL 16 (prod) / SQLite (dev/test)
- **LLM**: LiteLLM abstraction — Anthropic Claude, OpenAI, or local Ollama; per-agent `ProviderConfig` override
- **MCP**: FastMCP (server) + `mcp` SDK (client)
- **Security**: TOTP 2FA (`pyotp`), encrypted secrets (Fernet), bcrypt backup codes, JWT `token_version` session invalidation
- **UI**: MUI v5 (`@mui/material`), TanStack Query v5, React Hook Form + Zod, `swagger-ui-react`
- **Docker**: Multi-stage `python:3.14-slim` + `nginx:alpine`; images pushed to GHCR on `main`
- **CI**: GitHub Actions — lint, test (≥85% line coverage with PR comment), mutation (≥85% kill rate, manual trigger), Docker scan, GHCR push

## License

MIT — see [LICENSE](LICENSE).
