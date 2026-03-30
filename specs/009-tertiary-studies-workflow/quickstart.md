# Quickstart: Tertiary Studies Workflow

**Feature**: 009-tertiary-studies-workflow
**Date**: 2026-03-29

---

## Prerequisites

```bash
# Start the full stack
cp .env.example .env   # ensure DATABASE_URL, SECRET_KEY are set
docker compose up -d

# Apply migrations (including new 0017_tertiary_studies_workflow)
uv run alembic upgrade head
```

---

## Run Tests

```bash
# All Python packages
uv run pytest backend/tests/ agents/tests/ db/tests/

# Backend only (tertiary-specific tests)
uv run --package sms-backend pytest backend/tests/ -k "tertiary"

# DB models only
uv run --package sms-db pytest db/tests/ -k "tertiary"

# With coverage
uv run --package sms-backend pytest backend/tests/ \
  --cov=src/backend --cov-report=term-missing --cov-fail-under=85

# Frontend
cd frontend && npm test
cd frontend && npm run test:coverage
```

---

## Lint & Type Check

```bash
# Ruff lint + format
uv run ruff check backend/src agents/src db/src
uv run ruff format --check backend/src agents/src db/src

# Mypy (strict)
uv run mypy backend/src/backend/api/v1/tertiary/
uv run mypy backend/src/backend/services/tertiary_phase_gate.py
uv run mypy backend/src/backend/services/tertiary_report_service.py
uv run mypy db/src/db/models/tertiary.py

# Frontend
cd frontend && npm run lint
cd frontend && npm run format:check
```

---

## Exercise the Feature Manually

### 1. Create a Tertiary Study

```bash
# Create study of type TERTIARY
curl -X POST http://localhost:8000/api/v1/studies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Tertiary Review of SE Secondary Studies", "study_type": "Tertiary"}'
```

### 2. Set Up Protocol

```bash
STUDY_ID=<id from above>
curl -X PUT http://localhost:8000/api/v1/tertiary/studies/$STUDY_ID/protocol \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "research_questions": ["What synthesis methods are used in SE secondary studies?"],
    "secondary_study_types": ["SLR", "SMS"],
    "inclusion_criteria": ["Protocol explicitly documented", "Published after 2010"],
    "recency_cutoff_year": 2010,
    "synthesis_approach": "narrative",
    "version_id": 0
  }'
```

### 3. Import Seed Studies

```bash
curl -X POST http://localhost:8000/api/v1/tertiary/studies/$STUDY_ID/seed-imports \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_study_id": <existing_sms_study_id>}'
```

### 4. Check Phase Gate

```bash
curl http://localhost:8000/api/v1/studies/$STUDY_ID/phases \
  -H "Authorization: Bearer $TOKEN"
# Expect phases 1–3 unlocked after validated protocol + seeded papers
```

### 5. Generate Report

```bash
curl "http://localhost:8000/api/v1/tertiary/studies/$STUDY_ID/report?format=json" \
  -H "Authorization: Bearer $TOKEN" | jq '.landscape_of_secondary_studies'
```

---

## New Files Created by This Feature

```text
db/src/db/models/tertiary.py              # ORM models: TertiaryStudyProtocol, SecondaryStudySeedImport, TertiaryDataExtraction
db/alembic/versions/0017_tertiary_studies_workflow.py  # Alembic migration

backend/src/backend/api/v1/tertiary/
├── __init__.py                           # Router registration
├── protocol.py                           # Protocol endpoints
├── seed_imports.py                       # Seed import endpoints
├── extractions.py                        # Extraction endpoints
└── report.py                             # Report endpoint

backend/src/backend/services/
├── tertiary_phase_gate.py                # get_tertiary_unlocked_phases()
├── tertiary_report_service.py            # TertiaryReportService
└── tertiary_extraction_service.py        # TertiaryExtractionService

backend/src/backend/jobs/
└── tertiary_extraction_job.py            # ARQ job: AI-assisted extraction

backend/tests/
├── test_tertiary_protocol.py
├── test_tertiary_seed_import.py
├── test_tertiary_extraction.py
├── test_tertiary_phase_gate.py
└── test_tertiary_report.py

frontend/src/
├── components/tertiary/
│   ├── TertiaryProtocolForm.tsx
│   ├── SeedImportPanel.tsx
│   ├── TertiaryExtractionForm.tsx
│   └── TertiaryReportPage.tsx
└── pages/TertiaryStudyPage.tsx
```
