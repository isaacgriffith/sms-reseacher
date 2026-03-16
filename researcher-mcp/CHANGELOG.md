# Changelog — sms-researcher-mcp

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — feature/003-project-setup-improvements

### Changed
- Coverage command documented in `CLAUDE.md`:
  `uv run pytest researcher-mcp/tests/ --cov=researcher_mcp`
- Mutation testing tool updated to `cosmic-ray` (was `mutmut`); run via manual GitHub
  Actions `workflow_dispatch` workflow
- `pytest` build gate enforced: skip/xfail markers without `reason=` cause the run to fail

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- FastMCP 2.0 server serving five MCP tools over HTTP/SSE on port 8002
- `search_papers` — Semantic Scholar → OpenAlex cascade search
- `get_paper` — retrieve full paper metadata by ID or DOI with CrossRef enrichment
- `search_authors` — search authors by name via Semantic Scholar
- `get_author` — retrieve author profile and publication list
- `fetch_paper_pdf` — download open-access PDFs via Unpaywall → arXiv → SciHub (opt-in)
- `ResearcherSettings` — Pydantic Settings with `lru_cache` for configuration
- `httpx` client factory with `tenacity` retry (3 attempts, exponential backoff + jitter)
- Per-source token-bucket rate limiting (`SEMANTIC_SCHOLAR_RPM`, `OPEN_ALEX_RPM`)
- SciHub access disabled by default; opt-in via `SCIHUB_ENABLED=true`
- Multi-stage `Dockerfile` (`python:3.14-slim`)
- Unit tests: cascade logic, retry behaviour, SciHub disabled-by-default enforcement

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial `pyproject.toml` (`sms-researcher-mcp`) as UV workspace member
- FastMCP 2.0 dependency baseline
- Ruff, MyPy strict, pytest + pytest-asyncio configuration
