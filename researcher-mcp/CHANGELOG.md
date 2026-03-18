# Changelog — sms-researcher-mcp

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.6.0] — 2026-03-18 — feature/006-database-search-and-retrieval

### Added
- **Multi-database fan-out search**: `search_papers` MCP tool queries up to 9 academic databases
  in parallel; results merged and deduplicated by DOI then by normalised title + first-author
  last name (`deduplicate_paper_records` in `core/dedup.py`)
- **`DatabaseSource` typing.Protocol** (`sources/base.py`): `search()` and `get_paper()`
  signatures; `normalise_to_paper_record()` field-mapping helper; `VenueType` literal type
- **New source adapters**: `IEEESource` (REST API), `ACMSource` (scraper), `ScopusSource`
  (pybliometrics), `WoSSource` (WoS Expanded REST), `InspecSource` (pybliometrics),
  `ScienceDirectSource` (pybliometrics), `SpringerSource` (springernature-api-client),
  `GoogleScholarSource` (scholarly)
- **`SourceRegistry`** (`core/registry.py`): maps `DatabaseIndex` string values to
  `DatabaseSource` instances; `get_enabled()` for filtered fan-out; `build_default_registry()`
  factory
- **`convert_pdf_to_markdown` MCP tool**: converts PDF bytes → Markdown via MarkItDown
- **`convert_url_to_markdown` MCP tool**: fetches URL and converts to Markdown
- **`fetch_stored_markdown` MCP tool**: retrieves stored `full_text_markdown` for a paper via
  backend REST endpoint
- **`fetch_paper_pdf` update**: tries Unpaywall open-access first; falls back to Sci-Hub when
  `SCIHUB_ENABLED=true`; converts retrieved PDF to Markdown and stores via backend
- **New env vars**: `IEEE_XPLORE_API_KEY`, `ELSEVIER_API_KEY`, `ELSEVIER_INST_TOKEN`,
  `WOS_API_KEY`, `SPRINGER_API_KEY`, `SCHOLARLY_PROXY_URL` added to `ResearcherSettings`

### Changed
- `search_papers` tool extended with `indices: list[str] | None` parameter; `SearchPapersResult`
  extended with `sources_failed: list[str]` field
- `pyproject.toml`: added `pybliometrics`, `semanticscholar`, `scholarly`, `unpywall`,
  `springernature-api-client`, `markitdown[all]`, `scidownl` dependencies

---

## [0.3.0] — 2026-03-16 — feature/003-project-setup-improvements

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
