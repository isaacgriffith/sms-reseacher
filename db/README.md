# sms-db

SQLAlchemy 2.x async models and Alembic migrations for SMS Researcher.

## Schema Entities

### Study

Represents a systematic research study.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | Auto-increment |
| `name` | String(255) | Required |
| `study_type` | Enum | `SMS`, `SLR`, `Tertiary`, `Rapid` |
| `status` | Enum | `draft` → `active` → `completed` / `archived` |
| `created_at` | DateTime(tz) | Server default `NOW()` |
| `updated_at` | DateTime(tz) | Server default `NOW()`, auto-updated |

### Paper

Represents a single academic paper.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | Auto-increment |
| `title` | Text | Required |
| `abstract` | Text | Nullable |
| `doi` | String(255) | Unique, nullable |
| `metadata` | JSON | Flexible bibliographic fields |
| `created_at` | DateTime(tz) | Server default `NOW()` |

### StudyPaper (join table)

Links a `Study` to a `Paper` with an inclusion decision.

| Column | Type | Notes |
|--------|------|-------|
| `study_id` | Integer FK → study.id | Composite PK, CASCADE delete |
| `paper_id` | Integer FK → paper.id | Composite PK, CASCADE delete |
| `inclusion_status` | Enum | `pending`, `included`, `excluded` |

## Alembic Usage

```bash
# Apply all migrations to head
uv run alembic upgrade head

# Generate a new migration after model changes
uv run alembic revision --autogenerate -m "describe_change"

# Downgrade one step
uv run alembic downgrade -1
```

Migrations live in `db/alembic/versions/`. The first migration (`0001_initial_schema.py`) creates all three tables.

## Importing from backend

```python
from db.models import Study, Paper, StudyPaper
from db.base import engine_factory, get_session

engine = engine_factory("sqlite+aiosqlite:///./dev.db")

async with get_session(engine) as session:
    study = Study(name="My SMS", study_type="SMS")
    session.add(study)
    await session.commit()
```

The `db` package is a UV workspace member. Backend declares it as a workspace dependency in `backend/pyproject.toml`.
