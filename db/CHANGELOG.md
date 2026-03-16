# Changelog — sms-db

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — feature/003-project-setup-improvements

### Changed
- Coverage command documented in `CLAUDE.md`: `uv run pytest db/tests/ --cov=db`
- Mutation testing tool updated to `cosmic-ray` (was `mutmut`); run via manual GitHub
  Actions `workflow_dispatch` workflow
- `pytest` build gate enforced: skip/xfail markers without `reason=` cause the run to fail

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- `Study` model: `id`, `name`, `study_type` (SMS/SLR/Tertiary/Rapid), `status`
  (draft/active/completed/archived), `created_at`, `updated_at`
- `Paper` model: `id`, `title`, `abstract`, `doi` (unique), `metadata` (JSON),
  `created_at`
- `StudyPaper` join table: composite PK (`study_id`, `paper_id`),
  `inclusion_status` (pending/included/excluded), CASCADE deletes
- Alembic migration `0001_initial_schema.py` creating all three tables
- `engine_factory()` — async SQLAlchemy engine factory supporting PostgreSQL and SQLite
- `get_session()` — async context manager for session lifecycle management
- Async-compatible `alembic/env.py` for programmatic migration application
- Integration tests using `aiosqlite` (SQLite in-memory)

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial `pyproject.toml` (`sms-db`) as UV workspace member
- SQLAlchemy 2.x async + Alembic dependency baseline
- Ruff, MyPy strict, pytest + pytest-asyncio configuration
