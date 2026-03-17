# Research: Database Search, Retrieval & Paper Processing

**Branch**: `006-database-search-and-retrieval`
**Date**: 2026-03-17
**Phase**: 0 — Pre-design research

---

## 1. Library Availability & Versions

### Decision: IEEE Xplore — Direct httpx REST (no PyPI client)
- **Rationale**: No stable, published PyPI package exists for the IEEE Xplore API. The official SDK is a Python 2 download from `developer.ieee.org`. Community packages (`xploreapi`, `xplore`) are either unavailable or unrelated tools. Direct `httpx` calls against the IEEE Xplore REST API (`https://ieeexploreapi.ieee.org/api/v1/search/articles`) are the pragmatic, dependency-free solution.
- **Alternatives considered**: GitHub-only forks — rejected; unmaintained and import-unstable.

### Decision: pybliometrics 4.4.1 — Scopus + ScienceDirect
- **Rationale**: Latest version (4.4.1, Jan 2026); most complete Python wrapper for both Scopus and ScienceDirect APIs. Supports Python 3.10+.
- **Limitation**: Synchronous only — must be wrapped in `asyncio.to_thread()` inside async MCP tool handlers.
- **Key classes**: `ScopusSearch`, `AbstractRetrieval` (Scopus); `ScienceDirectSearch`, `ArticleRetrieval` (ScienceDirect).
- **Config**: `pybliometrics.init()` reads from `~/.config/pybliometrics.cfg`; the integration will configure this programmatically from `ELSEVIER_API_KEY` and `ELSEVIER_INST_TOKEN` env vars at startup.

### Decision: semanticscholar 0.11.0 — AsyncSemanticScholar
- **Rationale**: The only library in this group with native async support (`AsyncSemanticScholar`). Covers paper search, citation/reference graph, and author queries. Matches existing SemanticScholarSource patterns in researcher-mcp.
- **Alternatives considered**: Direct REST calls — rejected; client handles pagination and error handling.

### Decision: Inspec/Engineering Village — Direct httpx REST
- **Rationale**: No published Python client for the Elsevier Engineering Village API. Direct REST calls to `https://api.elsevier.com/content/ev/results` with the shared `ELSEVIER_API_KEY` and `ELSEVIER_INST_TOKEN`.
- **Alternatives considered**: None viable.

### Decision: scholarly 1.7.11 — Google Scholar (with proxy warning)
- **Rationale**: The only established Python library for Google Scholar search. Synchronous — wrap in `asyncio.to_thread()`.
- **Limitation**: Requires proxy configuration (`SCHOLARLY_PROXY_URL`) to avoid CAPTCHA blocks at moderate query volumes. Without a proxy, rate-limited after ~50 queries per session.
- **Alternatives considered**: SerpAPI / Bright Data paid APIs — rejected; unnecessary dependency for an opt-in supplementary source.

### Decision: wosstarter — Direct httpx REST (not the GitHub package)
- **Rationale**: `wosstarter_python_client` is GitHub-only, auto-generated, and not published to PyPI. Installing from GitHub URLs in `pyproject.toml` creates reproducibility issues. The Web of Science Starter API is a straightforward REST interface (`https://api.clarivate.com/apis/wos-starter/v1`) accepting `q` (advanced query string), `db`, `limit`, and `page` parameters. Direct `httpx` calls are simpler and more maintainable.
- **Alternatives considered**: GitHub install — rejected (reproducibility); older SOAP `wos` package — rejected (deprecated API).

### Decision: springernature-api-client 0.0.9
- **Rationale**: Published to PyPI, Python 3.9+, covers MetaAPI, OpenAccessAPI. Synchronous — wrap in `asyncio.to_thread()`.
- **Alternatives considered**: Direct REST — acceptable fallback, but the client handles pagination.

### Decision: unpywall 0.2.3
- **Rationale**: Standard Unpaywall API client; `Unpywall.get_pdf_link(doi=...)` returns the best OA PDF URL. Synchronous — wrap in `asyncio.to_thread()`.
- **Alternatives considered**: Direct API calls — no advantage over the published client.

### Decision: markitdown[all] 0.1.5
- **Rationale**: Converts PDF bytes (`io.BytesIO`), URLs, and file paths to Markdown. `MarkItDown(llm_client=..., llm_model=...)` enables OCR via any vision LLM. Requires Python 3.10+.
- **Key API**: `MarkItDown().convert_stream(io.BytesIO(pdf_bytes))` → `.text_content`. Synchronous — wrap in `asyncio.to_thread()`.
- **Alternatives considered**: `pymupdf4llm`, `pdf2image + pytesseract` — rejected; MarkItDown is already specified and covers multi-format input.

### Decision: scidownl 1.0.2
- **Rationale**: Conditional import only when `SCIHUB_ENABLED=true`. Simple `scihub_download(doi, paper_type="doi", out=path)` API. Synchronous — wrap in `asyncio.to_thread()`.
- **Alternatives considered**: `scihub.py` — older, less maintained.

---

## 2. Async Wrapping Strategy

All synchronous third-party libraries (pybliometrics, scholarly, unpywall, markitdown, scidownl, springernature-api-client, IEEE REST, Inspec REST, WoS REST) must be wrapped using `asyncio.to_thread()` inside `async def` tool handlers to avoid blocking the event loop.

```text
Pattern:
  result = await asyncio.to_thread(sync_library_call, arg1, arg2)
```

This is consistent with Principle IX ("Async discipline") in the Constitution.

---

## 3. Fan-Out Search Architecture

The existing `search_papers` tool uses a cascade pattern (Semantic Scholar → OpenAlex). Feature 006 requires a **parallel fan-out** pattern: all enabled sources are queried concurrently and results are merged/deduplicated.

### Decision: Source Registry + asyncio.gather fan-out
- A `SourceRegistry` maps source identifiers (`DatabaseIndex` enum values) to source instances.
- `search_papers` accepts a `study_id` or a list of `indices` to query.
- `asyncio.gather(*[source.search(query) for source in enabled_sources])` executes all searches concurrently.
- Deduplication uses DOI as primary key; normalised `(title_lower, first_author_last_name)` as fallback.
- **OCP compliance**: New databases are added by registering a new source class — no changes to the fan-out logic.

---

## 4. Credential Management Architecture

### Decision: Re-use Fernet encryption pattern from Provider model
- The existing `Provider` model stores API keys as `LargeBinary` (Fernet-encrypted). A new `SearchIntegrationCredential` model follows the identical pattern.
- The `ELSEVIER_API_KEY`, `IEEE_XPLORE_API_KEY`, `WOS_API_KEY`, `SPRINGER_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY`, `SCHOLARLY_PROXY_URL`, and `UNPAYWALL_EMAIL` environment variables serve as fallbacks when no DB-stored credential exists (consistent with FR-028).
- Researcher-mcp reads credentials from the **backend API** at startup (or on-demand) rather than holding them in its own settings — this ensures the admin panel is the single source of truth. The backend exposes an internal credential-fetch endpoint (not public).

---

## 5. Study Database Selection Storage

### Decision: `StudyDatabaseSelection` join table with per-index enable flag
- One row per (study, database_index) pair with an `is_enabled` boolean.
- Stored as a proper relational table (not JSON) to allow querying "which studies use IEEExplore?" and for future analytics.
- Default selection (applied at study creation) is configurable via admin settings or hardcoded as "Semantic Scholar only" for the minimum viable search.

---

## 6. CandidatePaper Full-Text Storage

### Decision: Extend existing `Paper` model with full-text columns
- The `Paper` model (representing a deduplicated paper record) gains three nullable columns: `full_text_markdown` (Text), `full_text_source` (Enum), `full_text_converted_at` (DateTime).
- The `StudyPaper` join table retains its existing structure; full-text content belongs to the paper, not the study-paper association.
- **Alternatives considered**: Separate `PaperFullText` table — rejected for now; the single-row approach is simpler and the text column is nullable, so papers without full text incur no overhead.

---

## 7. ACM Digital Library Scraping

### Decision: httpx + BeautifulSoup with explicit rate limiting and robots.txt compliance
- ACM DL has no public API. The scraper respects `robots.txt` delays and uses conservative rate limits (10 RPM default).
- Abstract-only records are returned when institutional access is unavailable (no authentication failures raised to the user).
- The admin panel shows an explicit disclaimer: "ACM Digital Library access is provided via web scraping. Use in accordance with ACM's Terms of Service."

---

## 8. pybliometrics Configuration Approach

### Decision: Programmatic config file generation at startup
- `pybliometrics.init()` reads `~/.config/pybliometrics.cfg`. The `ScopusSource` initialiser writes this file from env vars / DB credentials before the first API call.
- This avoids requiring operators to manually configure `pybliometrics` and keeps credentials in the unified credential store.

---

## 9. FastMCP Version

- Installed version is `fastmcp 3.x` (the project has moved past 2.0 while retaining the same `@mcp.tool` decorator API). The `server.py` pattern of `mcp = FastMCP("name")` and `@mcp.tool` decorators remains unchanged. No migration required.

---

## 10. All NEEDS CLARIFICATION Markers Resolved

No open clarification markers from the spec. All decisions above resolve the technical gaps. The plan proceeds to Phase 1.
