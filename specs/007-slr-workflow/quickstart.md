# Quickstart: SLR Workflow (007)

**Branch**: `007-slr-workflow` | **Date**: 2026-03-18

## Prerequisites

Ensure the base environment is running (see root `CLAUDE.md` for full setup). This feature adds new dependencies and a database migration.

## 1. Install New Dependencies

```bash
# Python backend (adds scipy, scikit-learn, numpy)
uv sync --all-packages
```

No new frontend dependencies are required.

## 2. Apply Database Migration

```bash
uv run alembic upgrade head
# Applies migration: 0015_slr_workflow
# Creates: review_protocol, quality_assessment_checklist, quality_checklist_item,
#          quality_assessment_score, inter_rater_agreement_record,
#          synthesis_result, grey_literature_source
```

## 3. Run Tests

```bash
# Backend (includes new SLR services and API routes)
uv run --package sms-backend pytest backend/tests/

# Agents (includes protocol reviewer agent)
uv run --package sms-agents pytest agents/tests/

# DB models (includes new SLR ORM models)
uv run --package sms-db pytest db/tests/

# Frontend
cd frontend && npm test
```

## 4. Start Development Stack

```bash
# Copy env example if not done already
cp .env.example .env

# Start all services
docker compose up -d

# Backend (auto-migrates on startup)
# Frontend dev server
cd frontend && npm run dev
```

## 5. SLR Workflow (End-to-End Steps)

### Phase 1: Create SLR Study and Define Protocol

1. Open the app at `http://localhost:5173`
2. Create a new study → select **Systematic Literature Review** as the study type
3. Navigate to **Protocol** tab → fill in all protocol sections (background, RQs, PICO(C), search strategy, etc.)
4. Click **Submit for AI Review** → the system queues the `protocol_review_job` and sets status to `Under Review`
5. When the review completes (polling via TanStack Query), review the AI feedback report
6. Iterate on the protocol draft until ready → click **Approve Protocol**
7. The protocol is now `Validated` and the search phase unlocks

### Phase 2: Search, Screen, and Assess Quality

1. Run database search (existing Phase 2 flow)
2. Two reviewers independently screen papers by title/abstract
3. After both reviewers submit, the system computes Cohen's Kappa automatically
4. If Kappa is below the threshold, the Think-Aloud discussion panel appears; resolve disagreements paper by paper
5. Repeat for introduction/conclusions and full-text stages
6. For each accepted paper, navigate to **Quality Assessment** and complete all checklist items
7. The system computes inter-rater Kappa on quality scores when both reviewers have submitted

### Phase 3: Data Synthesis

1. Navigate to **Synthesis** tab
2. Select approach (Meta-Analysis, Descriptive, or Qualitative)
3. For meta-analysis/descriptive: enter effect-size data per paper or verify extracted values
4. Click **Run Synthesis** → async job starts; page polls for completion
5. When complete, view Forest plot (descriptive) or Funnel plot (meta-analysis) inline
6. Define sensitivity analysis subsets and re-run; compare consistency of conclusions

### Phase 4: Report Export

1. Navigate to **Report** tab
2. Click **Generate Report** → all SLR sections are populated from study data
3. Choose export format: **LaTeX/Markdown** (structured academic template) or **JSON/CSV**
4. Download the file

## 6. Key Configuration

| Env Var | Description | Default |
|---------|-------------|---------|
| `SLR_KAPPA_THRESHOLD` | Minimum Cohen's Kappa before discussion triggered | `0.6` |
| `SLR_MIN_SYNTHESIS_PAPERS` | Minimum accepted papers for synthesis/Forest plot | `3` |

Add these to `.env.example` and `backend/src/backend/core/config.py` (Pydantic `BaseSettings`).
