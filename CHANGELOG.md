# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — feature/003-project-setup-improvements

### Added
- `cosmic-ray` configured as the standard Python mutation testing tool (replaces `mutmut`)
- `stryker` and `cosmic-ray` exposed as manually-triggered `workflow_dispatch` GitHub Actions
  workflows; both are also triggered automatically at the end of every speckit feature
  implementation
- GitHub Actions coverage gate: build fails if line coverage drops below 85% for any service;
  PR comment posted with coverage summary
- `pytest` build gate: any `@pytest.mark.skip` or `@pytest.mark.xfail` without `reason=`
  causes the test run to fail
- Frontend environment setup (Node 20 LTS, `npm install`) documented in `CLAUDE.md`
- `vitest run --coverage` command and 85% CI gate added for frontend TypeScript coverage
- Constitution v1.6.0: Principle X — Feature Completion Documentation mandates `CLAUDE.md`,
  `README.md`, and `CHANGELOG.md` updates at the end of every feature

### Changed
- `CLAUDE.md` updated to reflect `cosmic-ray` as the mutation testing tool
- `README.md` tech stack updated: `mutmut` → `cosmic-ray`, CI description expanded

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- Full six-subproject UV workspace: `backend`, `agents`, `db`, `agent-eval`,
  `researcher-mcp`, `frontend`
- **backend**: FastAPI REST gateway with endpoints for studies, papers, screening criteria,
  PICO elements, search strings, quality assessment, and results; JWT auth middleware;
  structlog request-scoped logging; ARQ background job queue
- **agents**: `ScreenerAgent`, `ExtractorAgent`, and `SynthesiserAgent` as an importable
  Python library; Jinja2 prompt templates; MCP tool integration via `MCPClient`
- **db**: SQLAlchemy 2.x async ORM with `Study`, `Paper`, and `StudyPaper` models; Alembic
  migrations; PostgreSQL 16 (production) and SQLite (development/test) support
- **agent-eval**: Typer CLI (`evaluate`, `report`, `compare`, `improve`) for LLM-as-a-Judge
  agent evaluation using DeepEval + LiteLLM
- **researcher-mcp**: FastMCP 2.0 server with five tools — `search_papers`, `get_paper`,
  `search_authors`, `get_author`, `fetch_paper_pdf`; Semantic Scholar → OpenAlex cascade;
  tenacity retry with exponential backoff; per-source token-bucket rate limiting
- **frontend**: React 18 / TypeScript 5.4 SPA; TanStack Query; React Hook Form + Zod;
  D3.js + Recharts; React Router v6; Vite 5; Vitest; Stryker mutation testing
- Docker Compose stack with multi-stage builds, health checks, and `depends_on` ordering
- GitHub Actions CI: lint, typecheck, pytest, Vitest coverage, Docker scan, GHCR push
- `ARQ`, `matplotlib`, `networkx`, `plotly + kaleido`, `rapidfuzz`, `deepeval`,
  `hypothesis` added as Python dependencies
- `D3.js`, `TanStack Query`, `React Hook Form` added as frontend dependencies

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial UV workspace mono-repo structure with root `pyproject.toml`
- Python 3.14 runtime pinned across all packages
- TypeScript 5.4 / Node 20 LTS frontend toolchain
- Ruff (lint + format), MyPy strict, pytest + pytest-asyncio baseline configuration
- Pre-commit hooks: `ruff check`, `ruff format --check`, `mypy`, `hadolint`
- Docker multi-stage build base configuration (`python:3.14-slim`, `nginx:alpine`)
- `.env.example` with required environment variable documentation
- MIT License (Copyright 2026 Isaac Griffith, PhD)
- `CLAUDE.md` with Claude Code guidance for the repository
