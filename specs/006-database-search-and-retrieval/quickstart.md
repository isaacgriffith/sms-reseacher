# Quickstart: Database Search, Retrieval & Paper Processing

**Branch**: `006-database-search-and-retrieval`
**Date**: 2026-03-17

---

## New Environment Variables

Add the following to `.env` (and `.env.example` with placeholder values):

```env
# IEEE Xplore
IEEE_XPLORE_API_KEY=your_ieee_key_here

# Elsevier (Scopus, ScienceDirect, Inspec) — shared
ELSEVIER_API_KEY=your_elsevier_key_here
ELSEVIER_INST_TOKEN=your_institutional_token_here   # optional

# Web of Science
WOS_API_KEY=your_wos_key_here

# Springer Nature
SPRINGER_API_KEY=your_springer_key_here

# Semantic Scholar (optional; increases rate limit)
SEMANTIC_SCHOLAR_API_KEY=your_s2_key_here

# Unpaywall (required for open-access PDF retrieval)
UNPAYWALL_EMAIL=researcher@yourinstitution.edu

# Google Scholar proxy (optional; recommended for production)
SCHOLARLY_PROXY_URL=http://user:pass@proxy.example.com:8080

# SciHub (operator opt-in; false by default)
SCIHUB_ENABLED=false
```

---

## Install New Dependencies

```bash
# From repo root — adds packages to researcher-mcp
uv add --package sms-researcher-mcp \
    pybliometrics>=4.4.0 \
    semanticscholar>=0.11.0 \
    scholarly>=1.7.11 \
    unpywall>=0.2.3 \
    "springernature-api-client>=0.0.9" \
    "markitdown[all]>=0.1.5" \
    scidownl>=1.0.2
```

Note: `scidownl` is conditionally imported; the package must be installed for the import to succeed when `SCIHUB_ENABLED=true`.

---

## Run Database Migration

```bash
uv run alembic upgrade head
```

This applies migration `0013_database_search_and_retrieval.py`, which adds the `study_database_selection` and `search_integration_credential` tables and extends the `paper` table with full-text columns.

---

## Configure Search Integrations (Admin Panel)

1. Log in as an administrator.
2. Navigate to **Administration → Search Integrations**.
3. For each subscription-gated integration (IEEE Xplore, Elsevier, Web of Science, Springer Nature), enter the API key and click **Save**.
4. Click **Test Now** to verify connectivity. The panel reports success, rate-limit warning, or auth failure.

Alternatively, set environment variables as listed above — the admin panel displays "Configured via environment" for keys found in env vars.

---

## Configure Database Selection for a Study

1. Open a study's **Settings** tab (or use the New Study Wizard, Phase 2).
2. In the **Search Databases** section, toggle the desired indices on/off.
3. Indices with missing credentials show a warning badge.
4. Optionally enable **Snowball Sampling** for backward/forward citation tracing.
5. To enable SciHub: ensure `SCIHUB_ENABLED=true` is set on the server, then check **Enable SciHub** and acknowledge the legal disclaimer.

---

## Run a Search

Via MCP (for AI agents):

```python
# Fan-out search across all study-selected indices
result = await search_papers(
    query="systematic mapping study software engineering",
    indices=["ieee_xplore", "scopus", "semantic_scholar"],
    max_results=200,
    year_from=2015,
    year_to=2025,
)
print(result.papers)
print(result.sources_failed)   # check for any failed sources
```

---

## Retrieve Full Text

```python
# 1. Get PDF (Unpaywall → direct → SciHub opt-in)
pdf_result = await fetch_paper_pdf(doi="10.1109/TSE.2023.12345", allow_scihub=False)

# 2. Convert to Markdown
if pdf_result.available:
    md_result = await convert_paper_to_markdown(
        pdf_bytes_b64=pdf_result.pdf_bytes_b64
    )
    print(md_result.markdown[:500])

# 3. Or convert directly by DOI (pipeline in one call)
md_result = await convert_paper_to_markdown(doi="10.1109/TSE.2023.12345")
```

---

## Run Tests

```bash
# researcher-mcp unit + integration tests
uv run --package sms-researcher-mcp pytest researcher-mcp/tests/ \
    --cov=src/researcher_mcp --cov-report=term-missing

# db tests (includes migration tests)
uv run --package sms-db pytest db/tests/

# backend tests (includes new admin API)
uv run --package sms-backend pytest backend/tests/

# frontend tests
cd frontend && npm test
```

---

## New Source Structure (researcher-mcp)

```text
researcher-mcp/src/researcher_mcp/
├── sources/
│   ├── base.py               # DatabaseSource Protocol + PaperRecord normalisation helpers
│   ├── ieee.py               # IEEESource (httpx REST)
│   ├── acm.py                # ACMSource (httpx + BeautifulSoup scraper)
│   ├── google_scholar.py     # GoogleScholarSource (scholarly + asyncio.to_thread)
│   ├── inspec.py             # InspecSource (httpx REST, Elsevier Engineering Village)
│   ├── scopus.py             # ScopusSource (pybliometrics + asyncio.to_thread)
│   ├── wos.py                # WoSSource (httpx REST, Clarivate Starter API)
│   ├── science_direct.py     # ScienceDirectSource (pybliometrics + asyncio.to_thread)
│   ├── springer.py           # SpringerSource (springernature-api-client + asyncio.to_thread)
│   ├── semantic_scholar.py   # SemanticScholarSource (AsyncSemanticScholar — upgraded)
│   ├── unpaywall.py          # UnpaywallSource (unpywall + asyncio.to_thread — upgraded)
│   ├── arxiv.py              # ArxivSource (unchanged)
│   └── scihub.py             # SciHubSource (scidownl + asyncio.to_thread — upgraded)
├── tools/
│   ├── search.py             # search_papers (fan-out), source-specific tools
│   ├── snowball.py           # get_references, get_citations (upgraded)
│   ├── pdf.py                # fetch_paper_pdf (upgraded waterfall)
│   ├── convert.py            # convert_paper_to_markdown, get_paper_markdown (new)
│   └── authors.py            # search/get author tools (upgraded for Semantic Scholar)
└── core/
    ├── config.py             # ResearcherSettings (new credential env vars added)
    ├── http_client.py        # TokenBucket, retry (unchanged)
    ├── registry.py           # SourceRegistry — maps DatabaseIndex → source instance
    └── dedup.py              # Deduplication logic (DOI + title/author fallback)
```
