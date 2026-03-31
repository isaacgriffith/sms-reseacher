# Quickstart: Research Protocol Definition (Feature 010)

**Branch**: `010-research-protocol-definition`
**Date**: 2026-03-30

---

## Prerequisites

Assumes the existing dev stack is already running (see root `CLAUDE.md` → Developer Workflow).

```bash
# Ensure you are on the feature branch
git checkout 010-research-protocol-definition

# Sync Python dependencies (if new packages added)
uv sync --all-packages

# Sync frontend dependencies
cd frontend && npm install && cd ..
```

---

## Apply the Migration

```bash
# Apply migration 0018 (creates all new tables and seeds default protocol templates)
uv run alembic upgrade head

# Verify seeded data
uv run python -c "
import asyncio
from db.database import get_session
from db.models.protocols import ResearchProtocol

async def check():
    async with get_session() as db:
        from sqlalchemy import select
        result = await db.execute(select(ResearchProtocol).where(ResearchProtocol.is_default_template == True))
        protos = result.scalars().all()
        for p in protos:
            print(f'{p.study_type}: {p.name} ({len(p.nodes)} nodes)')

asyncio.run(check())
"
```

Expected output:
```
SMS: Default SMS Protocol (10 nodes)
SLR: Default SLR Protocol (12 nodes)
Rapid: Default Rapid Review Protocol (10 nodes)
Tertiary: Default Tertiary Study Protocol (9 nodes)
```

---

## Run the Tests

```bash
# Backend unit + integration tests (new protocol service + API)
uv run --package sms-backend pytest backend/tests/api/v1/test_protocols.py -v
uv run --package sms-backend pytest backend/tests/services/test_protocol_service.py -v
uv run --package sms-backend pytest backend/tests/services/test_protocol_executor.py -v

# DB model tests (new ORM models)
uv run --package sms-db pytest db/tests/test_protocol_models.py -v

# Full backend suite with coverage
uv run --package sms-backend pytest backend/tests/ \
  --cov=src/backend --cov-report=term-missing --cov-fail-under=85

# Frontend component tests
cd frontend && npm test -- --run src/components/protocols/ src/services/protocols/

# Full frontend suite with coverage
cd frontend && npm run test:coverage
```

---

## Key Source Files

### Backend

| File | Purpose |
|------|---------|
| `db/src/db/models/protocols.py` | ORM models: ResearchProtocol, ProtocolNode, ProtocolEdge, QualityGate, TaskExecutionState, etc. |
| `db/alembic/versions/0018_research_protocol_definition.py` | Migration + default template seeding |
| `backend/src/backend/services/protocol_service.py` | CRUD + graph validation (cycle, dangling inputs) |
| `backend/src/backend/services/protocol_executor.py` | Runtime task activation + quality gate evaluation |
| `backend/src/backend/services/protocol_yaml.py` | YAML export/import (serialize/deserialize graph) |
| `backend/src/backend/api/v1/protocols/__init__.py` | Protocol library endpoints (GET/POST/PUT/DELETE/export/import) |
| `backend/src/backend/api/v1/studies/protocol_assignment.py` | Study assignment endpoints |
| `backend/src/backend/api/v1/studies/execution_state.py` | Execution state endpoints (get, complete, approve) |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/services/protocols/protocolsApi.ts` | API client (protocol library + assignment + execution state) |
| `frontend/src/hooks/protocols/useProtocol.ts` | TanStack Query hooks for protocol data |
| `frontend/src/hooks/protocols/useExecutionState.ts` | Polling hook for task execution state |
| `frontend/src/components/protocols/ProtocolGraph.tsx` | D3.js visual graph editor |
| `frontend/src/components/protocols/ProtocolTextEditor.tsx` | YAML text editor with syntax highlight |
| `frontend/src/components/protocols/ProtocolNodePanel.tsx` | Node detail + edit panel (inputs, outputs, assignees, gates) |
| `frontend/src/components/protocols/EdgeConditionBuilder.tsx` | Point-and-click condition builder |
| `frontend/src/components/protocols/QualityGateEditor.tsx` | Gate type selector + config form |
| `frontend/src/components/protocols/ExecutionStateView.tsx` | Study runtime task status board |
| `frontend/src/pages/protocols/ProtocolLibraryPage.tsx` | List + manage researcher's protocols |
| `frontend/src/pages/protocols/ProtocolEditorPage.tsx` | Dual visual/text editor for one protocol |

---

## Dev Workflow: Protocol Editing Flow

1. Start backend: `uv run uvicorn backend.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to a study → Protocol tab (new)
4. For a default template: view-only graph renders with D3
5. Click "Copy to Custom Protocol" → named copy created, redirects to editor
6. Editor shows dual panels (visual left, YAML right)
7. Drag node in visual editor → YAML updates immediately
8. Edit YAML → visual graph updates immediately
9. Save → PUT /protocols/{id} with current version_id
10. Assign protocol to study → Study runtime uses assigned protocol

---

## Testing the Execution Flow Manually

```bash
# 1. Create a study (SMS type)
curl -X POST http://localhost:8000/api/v1/studies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Protocol Study", "study_type": "SMS"}'

# 2. Check assigned protocol (auto-assigned to default in migration)
curl http://localhost:8000/api/v1/studies/{id}/protocol-assignment \
  -H "Authorization: Bearer $TOKEN"

# 3. Check execution state
curl http://localhost:8000/api/v1/studies/{id}/execution-state \
  -H "Authorization: Bearer $TOKEN"

# 4. Complete the define_pico task
curl -X POST http://localhost:8000/api/v1/studies/{id}/execution-state/define_pico/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Linting & Type Checking

```bash
# Python
uv run ruff check backend/src/backend/api/v1/protocols/ \
  backend/src/backend/services/protocol_service.py \
  backend/src/backend/services/protocol_executor.py \
  db/src/db/models/protocols.py

uv run mypy backend/src/backend/api/v1/protocols/ \
  backend/src/backend/services/protocol_service.py \
  backend/src/backend/services/protocol_executor.py \
  db/src/db/models/protocols.py

# Frontend
cd frontend && npm run lint && npm run format:check
```
