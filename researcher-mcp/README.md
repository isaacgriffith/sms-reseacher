# sms-researcher-mcp

FastMCP server providing academic paper search and PDF fetching tools via the Model Context Protocol (MCP) over HTTP/SSE on port 8002.

> **Legal notice**: SciHub access is **opt-in only** (`SCIHUB_ENABLED=true`). It is **disabled by default**. Users are solely responsible for compliance with applicable copyright law in their jurisdiction. The authors of this software do not condone copyright infringement.

## Setup

```bash
# From repo root
uv sync

# Start the server (development)
uv run --package sms-researcher-mcp researcher-mcp
# → Listening on http://0.0.0.0:8002

# Verify SSE endpoint
curl http://localhost:8002/sse

# Run tests
uv run --package sms-researcher-mcp pytest researcher-mcp/tests/

# Run tests with coverage (minimum 85% line coverage required)
uv run --package sms-researcher-mcp pytest researcher-mcp/tests/ --cov=researcher_mcp --cov-report=term-missing

# Mutation testing (run via GitHub Actions workflow_dispatch, or locally)
uv run cosmic-ray run researcher-mcp/cosmic-ray.toml

# Lint and type-check
uv run ruff check researcher-mcp/src
uv run ruff format --check researcher-mcp/src
uv run mypy researcher-mcp/src
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_papers` | Fan-out search across up to 9 academic databases; merged + deduplicated |
| `get_paper` | Retrieve full metadata by DOI or source ID from a specific database |
| `search_authors` | Search authors by name (Semantic Scholar) |
| `get_author` | Retrieve author profile and publication list |
| `fetch_paper_pdf` | Download full-text PDF via Unpaywall (OA) or Sci-Hub (opt-in) and convert to Markdown |
| `convert_pdf_to_markdown` | Convert PDF bytes to Markdown via MarkItDown |
| `convert_url_to_markdown` | Fetch a URL and convert its content to Markdown |
| `fetch_stored_markdown` | Retrieve previously stored full-text Markdown for a paper |
| `snowball_references` | Backward snowballing: find papers cited by a given paper |
| `snowball_citations` | Forward snowballing: find papers that cite a given paper |

### `search_papers`

```json
{
  "query": "systematic mapping studies software engineering",
  "limit": 10,
  "year_from": 2015,
  "year_to": 2024,
  "fields": ["title", "doi", "year", "authors"]
}
```

### `fetch_paper_pdf`

```json
{
  "doi": "10.1145/3597503.3608138",
  "output_path": "/tmp/paper.pdf"
}
```

Cascade order: **Unpaywall** (open access) → **arXiv** (preprint) → **SciHub** (opt-in only).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEMANTIC_SCHOLAR_RPM` | `100` | Semantic Scholar requests/minute |
| `OPEN_ALEX_RPM` | `300` | OpenAlex requests/minute |
| `SCIHUB_ENABLED` | `false` | Enable SciHub PDF fetching (read legal notice above) |
| `SCIHUB_URL` | `https://sci-hub.se` | SciHub mirror URL |
| `UNPAYWALL_EMAIL` | `researcher@example.com` | Required by Unpaywall API |
| `IEEE_XPLORE_API_KEY` | — | IEEE Xplore REST API key |
| `ELSEVIER_API_KEY` | — | Elsevier API key (Scopus, Inspec, ScienceDirect) |
| `ELSEVIER_INST_TOKEN` | — | Elsevier institutional token (optional) |
| `WOS_API_KEY` | — | Web of Science Expanded API key |
| `SPRINGER_API_KEY` | — | SpringerNature API key |
| `SCHOLARLY_PROXY_URL` | — | Proxy URL for scholarly (Google Scholar; optional) |

## Supported Database Sources

| Source | Adapter | Credential |
|--------|---------|------------|
| IEEE Xplore | `IEEESource` | `IEEE_XPLORE_API_KEY` |
| ACM Digital Library | `ACMSource` | *(none required)* |
| Scopus | `ScopusSource` | `ELSEVIER_API_KEY` |
| Web of Science | `WoSSource` | `WOS_API_KEY` |
| Inspec | `InspecSource` | `ELSEVIER_API_KEY` |
| ScienceDirect | `ScienceDirectSource` | `ELSEVIER_API_KEY` |
| SpringerNature | `SpringerSource` | `SPRINGER_API_KEY` |
| Google Scholar | `GoogleScholarSource` | `SCHOLARLY_PROXY_URL` (optional) |
| Semantic Scholar | `SemanticScholarSource` | `SEMANTIC_SCHOLAR_API_KEY` (optional) |

## Project Structure

```
researcher-mcp/
├── pyproject.toml
├── Dockerfile
├── src/researcher_mcp/
│   ├── server.py           # FastMCP app + main() entrypoint
│   ├── core/
│   │   ├── config.py       # ResearcherSettings (pydantic-settings)
│   │   └── http_client.py  # httpx client factory + tenacity retry
│   ├── sources/
│   │   ├── semantic_scholar.py
│   │   ├── open_alex.py
│   │   ├── crossref.py
│   │   ├── unpaywall.py
│   │   ├── arxiv.py
│   │   └── scihub.py       # Opt-in; disabled by default
│   └── tools/
│       ├── search.py       # search_papers, get_paper
│       ├── authors.py      # search_authors, get_author
│       └── pdf.py          # fetch_paper_pdf
└── tests/unit/
    ├── test_cascade.py
    ├── test_retry.py
    └── test_scihub_disabled.py
```

## Retry & Rate Limiting

All outbound HTTP calls use tenacity (max 3 attempts, exponential backoff + full jitter) and per-source token-bucket rate limiting. Retry exhaustion on a primary source triggers cascade to the next source automatically.
