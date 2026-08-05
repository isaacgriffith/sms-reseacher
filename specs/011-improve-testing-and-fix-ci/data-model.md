# Data Model: Improve Testing and Fix CI

This feature does not introduce new database entities, ORM models, or schema migrations. All changes are to configuration files, CI workflows, documentation, and package metadata.

## Configuration Entities (non-database)

### Package Identity

Each Python subproject has a `name` field in its `pyproject.toml` that serves as the package identifier for `uv` workspace management, CI matrix references, Docker build targets, and GHCR image tags.

| Package Directory | Current Name         | New Name             |
| ----------------- | -------------------- | -------------------- |
| `backend/`        | `sms-backend`        | `backend`            |
| `agent-eval/`     | `sms-agent-eval`     | `agent-eval`         |
| `researcher-mcp/` | `sms-researcher-mcp` | `researcher-mcp`     |
| `agents/`         | `agents`             | `agents` (no change) |
| `db/`             | `db`                 | `db` (no change)     |
| `frontend/`       | `sms-frontend`       | `frontend`           |

### CI Coverage Matrix

Each CI test matrix entry maps a package name to its test directory and coverage source path.

| Field     | Description                                  |
| --------- | -------------------------------------------- |
| `package` | UV package name (used with `--package` flag) |
| `testdir` | Path to test directory                       |
| `covdir`  | Path prefix for coverage XML output          |
| `covsrc`  | Path to source directory for `--cov` flag    |

### Pre-Commit Hook Configuration

Each hook in `.pre-commit-config.yaml` has:

| Field             | Description                                |
| ----------------- | ------------------------------------------ |
| `id`              | Unique hook identifier                     |
| `name`            | Human-readable name                        |
| `language`        | Execution environment (`system` or `node`) |
| `entry`           | Command to execute                         |
| `args`            | Command arguments                          |
| `pass_filenames`  | Whether to pass changed files              |
| `types` / `files` | File matching patterns                     |
