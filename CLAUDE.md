# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

This is a research project by Isaac Griffith, PhD, licensed under the MIT License. The repository is in early stages with no source code yet committed.

Update this file as the project's structure, language, build system, and workflow are established.

## Active Technologies

### Runtime & Language
- Python 3.14 (backend, agents, db, agent-eval, researcher-mcp); TypeScript 5.4 / Node 20 LTS (frontend)
- PostgreSQL 16 (production/Docker Compose); SQLite + `aiosqlite` (unit/integration tests)

### Python Libraries (002-sms-workflow)
- **Job queue**: ARQ (async Redis-based background task queue)
- **Charting / visualisation**: matplotlib, networkx, plotly + kaleido (PDF/PNG export)
- **String matching / deduplication**: rapidfuzz
- **LLM evals**: deepeval + hypothesis (metamorphic tests)
- **FastMCP**: FastMCP 2.0+ (`@mcp.tool` decorator pattern)

### Frontend Libraries (002-sms-workflow)
- **Data visualisation**: D3.js (network graphs, result charts)
- **State / data fetching**: TanStack Query (React Query) with `refetchInterval` polling
- **Forms**: React Hook Form with `useWatch` (not `watch()`)

## Recent Changes
- 001-repo-setup: Added Python 3.12 (backend, agents, db); TypeScript 5.4 / Node 20 LTS (frontend)
- 002-sms-workflow: Finalised library choices — ARQ, matplotlib, networkx, plotly/kaleido, rapidfuzz, D3.js
