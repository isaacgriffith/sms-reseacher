# Research: Mono-Repo Setup for SMS Researcher

**Branch**: `001-repo-setup` | **Date**: 2026-03-08 | **Phase**: 0

---

## 1. UV Workspace Structure for Python Mono-repo

**Decision**: Use a root-level UV workspace with `pyproject.toml` containing `[tool.uv.workspace]`, with `backend`, `agents`, and `db` as workspace members.

**Rationale**:
- UV workspaces (analogous to Cargo workspaces or npm workspaces) allow multiple packages to share a single lockfile (`uv.lock`) at the repository root while maintaining independent `pyproject.toml` per package.
- Inter-package dependencies are expressed as path dependencies: e.g., `backend` depends on `agents` and `db` via `agents = { path = "../agents" }`.
- A single `uv sync` at the root installs all workspace members; `uv sync --package backend` installs only one.
- Virtual environments are managed per-workspace by UV; `.venv` lives at the workspace root.

**Root `pyproject.toml` snippet**:
```toml
[tool.uv.workspace]
members = ["backend", "agents", "db"]
```

**Member inter-dependency** (in `backend/pyproject.toml`):
```toml
[project]
dependencies = [
    "agents",
    "db",
    "fastapi>=0.111",
    "uvicorn[standard]>=0.29",
]

[tool.uv.sources]
agents = { workspace = true }
db    = { workspace = true }
```

**Alternatives considered**:
- Independent venvs per sub-project: simpler but no shared lockfile, requires manual version alignment.
- Poetry workspaces: mature but slower than UV and requires Poetry installation.

---

## 2. Python Version

**Decision**: Python 3.14 (minimum), targeting 3.14.

**Rationale**:
- Python 3.14 brings further performance improvements, improved typing features, and continued ecosystem maturation.
- FastAPI 0.111+, SQLAlchemy 2.x, and all major tooling support 3.14.
- `pyproject.toml` sets `requires-python = ">=3.14"`.

**Alternatives considered**:
- 3.13: Acceptable fallback if 3.14 is unavailable in a target environment; all dependencies are compatible.
- 3.12: Not recommended; lacks improvements present in 3.13 and 3.14.

---

## 3. Python Static Analysis Toolchain

**Decision**: Ruff (linting + formatting), MyPy (type checking), pydocstyle via Ruff (docstring style), pytest (testing). All configured in `pyproject.toml`.

**Rationale**:
- **Ruff** replaces Flake8, isort, pyupgrade, and pydocstyle in a single, extremely fast tool. Configured via `[tool.ruff]` in `pyproject.toml`. Includes `pydocstyle`-equivalent rules under the `D` ruleset.
- **MyPy** remains the gold standard for Python static type checking. Configured via `[tool.mypy]` in `pyproject.toml`.
- **pytest** with `pytest-cov` for coverage and `pytest-asyncio` for async FastAPI routes.
- **UV run** is used to execute all tools: `uv run ruff check .`, `uv run mypy .`, `uv run pytest`.

**pyproject.toml configuration pattern**:
```toml
[tool.ruff]
line-length = 100
select = ["E", "W", "F", "I", "D", "UP", "B", "C4"]
ignore = ["D203", "D213"]  # docstring style choices

[tool.mypy]
python_version = "3.14"
strict = true
ignore_missing_imports = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Alternatives considered**:
- Flake8 + isort + black: Multiple tools requiring separate configs; Ruff is strictly superior.
- Pyright: Faster than MyPy but MyPy has broader ecosystem support and is specified in the requirements.

---

## 4. Pre-commit Strategy for Python Sub-projects

**Decision**: Use the `pre-commit` framework (`.pre-commit-config.yaml`) at each sub-project root, using `local` hooks that invoke UV.

**Rationale**:
- `pre-commit` is the standard Python-ecosystem hook manager; `.pre-commit-config.yaml` is declarative and version-pinned.
- For a UV-managed project, hooks use `language: system` or `language: python` with `uv run` as the entry point to avoid a separate pre-commit environment.
- Alternatively, a root-level `.pre-commit-config.yaml` can cover all sub-projects.

**Root `.pre-commit-config.yaml` pattern**:
```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-backend
        name: Ruff (backend)
        entry: bash -c 'cd backend && uv run ruff check . && uv run ruff format --check .'
        language: system
        pass_filenames: false
      - id: mypy-backend
        name: MyPy (backend)
        entry: bash -c 'cd backend && uv run mypy .'
        language: system
        pass_filenames: false
      - id: pytest-backend
        name: pytest (backend)
        entry: bash -c 'cd backend && uv run pytest'
        language: system
        pass_filenames: false
      # ...repeat for agents, db
```

**Alternatives considered**:
- Husky (Node-only): Not appropriate for Python sub-projects; only suitable for `frontend`.
- Per-sub-project `.pre-commit-config.yaml`: More granular but requires `pre-commit install` in each directory.

---

## 5. TypeScript/React Frontend Scaffold

**Decision**: Vite 5.x + React 18.x + TypeScript 5.x template; tested with Vitest.

**Rationale**:
- **Vite** is the current industry standard for React SPA scaffolding (2024-2025): sub-second HMR, native ESM, excellent TypeScript support.
- **React 18.x** is the current stable LTS (19.x is available but ecosystem stabilisation still ongoing).
- **TypeScript 5.4+** for best-in-class type safety.
- **Vitest** replaces Jest for Vite projects: native ES modules, 5-10x faster, Jest-compatible API.

**Alternatives considered**:
- Create React App: Deprecated/unmaintained, not suitable for new projects.
- Next.js: Adds SSR complexity not needed for a researcher-facing SPA.
- Jest + ts-jest: Viable but slower; Vitest is preferred when using Vite.

---

## 6. TypeScript ESLint + Prettier Configuration

**Decision**: ESLint 9.x flat config (`eslint.config.js`) + `typescript-eslint` + `eslint-plugin-react` + `eslint-plugin-react-hooks` + `eslint-config-prettier`.

**Rationale**:
- ESLint 9 standardises on flat config; `.eslintrc.*` is deprecated.
- `typescript-eslint` v8 (2024) provides `strictTypeChecked` preset.
- `eslint-config-prettier` disables all ESLint formatting rules so Prettier owns formatting.
- Prettier 3.x with `.prettierrc` for consistent formatting.
- `lint-staged` with `husky` runs ESLint + Prettier on staged files before each commit.

**Alternatives considered**:
- Legacy `.eslintrc` config: Deprecated; not suitable for new projects.
- `eslint-plugin-prettier`: Runs Prettier as an ESLint rule; creates slow feedback loop; the separate `eslint-config-prettier` approach is preferred.

---

## 7. FastAPI Project Layout

**Decision**: Layered architecture — `api/` (routers), `services/` (business logic), `models/` (SQLAlchemy ORM models), `schemas/` (Pydantic request/response schemas), `core/` (config, dependencies).

**Rationale**:
- Clearly separates HTTP concerns (routers) from business logic (services) and data access (models).
- Pydantic v2 (required by FastAPI 0.100+) provides fast validation with `model_config`.
- FastAPI dependency injection (`Depends`) handles DB sessions, auth, and shared services.

**Directory layout**:
```
backend/
├── pyproject.toml
├── src/
│   └── backend/
│       ├── __init__.py
│       ├── main.py           # FastAPI app factory
│       ├── core/
│       │   ├── config.py     # Settings (pydantic-settings)
│       │   └── database.py   # SQLAlchemy engine + session
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── router.py
│       │       └── studies.py
│       ├── models/           # SQLAlchemy ORM models (imported from db/)
│       ├── schemas/          # Pydantic request/response schemas
│       └── services/         # Business logic
└── tests/
    ├── unit/
    ├── integration/
    └── contract/
```

**Alternatives considered**:
- Monolithic `main.py`: Only appropriate for trivial APIs.
- Domain-driven layout (feature folders): Good for very large apps; overkill at this stage.

---

## 8. Database: ORM and Migration Strategy

**Decision**: SQLAlchemy 2.x (async) with Alembic migrations; PostgreSQL for production, SQLite for local development.

**Rationale**:
- SQLAlchemy 2.x introduces `mapped_column` / `Mapped` type annotations for fully type-checked models.
- Alembic is the standard migration tool for SQLAlchemy; integrates well with UV-managed projects.
- PostgreSQL is appropriate for production (JSONB for flexible metadata, full-text search for paper abstracts).
- SQLite (with `aiosqlite`) allows zero-infrastructure local dev.
- `db/` sub-project contains only SQLAlchemy model definitions and Alembic migration scripts; `backend/` imports them.

**Alternatives considered**:
- SQLModel: Merges Pydantic and SQLAlchemy models; reduces boilerplate but adds coupling between layers.
- Tortoise ORM: Django-style async ORM; less ecosystem support than SQLAlchemy.
- Prisma (Python client): Excellent DX but Python client is less mature than JS counterpart.

---

## 9. Backend ↔ Agents Communication Pattern

**Decision**: Direct Python import — `agents` is a UV workspace package; `backend` imports it as a library dependency.

**Rationale**:
- For MVP, the simplest approach is direct import: no second process to manage, no network overhead, easy to unit-test in isolation.
- Clean module boundary is maintained by keeping `agents` in its own package with a well-defined public API (exported from `agents/__init__.py`).
- HTTP can be introduced in a later phase when agents need to scale independently or become long-running async workers.

**Import pattern** (`backend/pyproject.toml`):
```toml
[project]
dependencies = ["agents", "db", "fastapi>=0.111", ...]

[tool.uv.sources]
agents = { workspace = true }
db     = { workspace = true }
```

**Alternatives considered**:
- HTTP microservice: Adds a second process to run locally, complicates development and testing; premature for scaffold.
- Celery + Redis: Appropriate for production async workloads; deferred to a later feature.

---

## 10. Pre-commit Strategy for Frontend

**Decision**: Husky v9 + lint-staged for the `frontend/` sub-project.

**Rationale**:
- Husky v9 uses plain shell scripts in `.husky/`; minimal config.
- `lint-staged` runs ESLint + Prettier only on staged `.ts/.tsx` files, keeping hook execution fast.
- Consistent with Node ecosystem conventions.

**Configuration**:
```json
// package.json
"lint-staged": {
  "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
  "*.{json,md,css}": ["prettier --write"]
}
```

**Alternatives considered**:
- `pre-commit` Python framework: Appropriate for polyglot; for a Node-only project, Husky is lighter.

---

## 11. Test Coverage Enforcement

**Decision**: 85% line/branch coverage minimum enforced via `pytest-cov` (Python) and Vitest's built-in coverage (via `@vitest/coverage-v8`) for TypeScript. Coverage thresholds configured to fail the test run below 85%.

**Rationale**:
- 85% is a practical threshold that catches most missing tests without requiring trivial coverage of boilerplate.
- `pytest-cov` with `--cov-fail-under=85` integrates cleanly into the existing pytest workflow.
- Vitest's `coverage.thresholds` config enforces the same minimum for TypeScript.
- Coverage is measured at every CI run; pre-commit runs unit tests only so partial coverage is expected locally — the full threshold is enforced in CI against the full suite.

**Python configuration**:
```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=85"
```

**TypeScript configuration**:
```typescript
// vitest.config.ts
coverage: {
  provider: 'v8',
  thresholds: { lines: 85, branches: 85, functions: 85, statements: 85 }
}
```

**Alternatives considered**:
- 100% coverage: Expensive to maintain; forces coverage of trivial code; false sense of quality.
- No threshold (report only): Insufficient — coverage tends to drift downward without enforcement.

---

## 12. Mutation Testing

**Decision**: `mutmut` for Python sub-projects; `Stryker` (`@stryker-mutator/core` + `@stryker-mutator/vitest-runner`) for the TypeScript frontend. Mutation testing runs in CI only (too slow for pre-commit or every test run).

**Rationale**:
- AI-generated tests are prone to "test theatre" — tests that pass trivially without actually verifying behaviour. Mutation testing catches this by introducing small code changes (mutants) and checking that at least one test fails for each mutant.
- **mutmut** is the most widely used Python mutation testing tool; integrates with pytest; HTML reports; supports incremental runs.
- **Stryker** is the dominant JavaScript/TypeScript mutation testing framework; has first-class Vitest integration via `@stryker-mutator/vitest-runner`.
- Mutation score target: ≥85% (mutants killed / total mutants), consistent with the coverage threshold.

**Python usage**:
```bash
uv run mutmut run
uv run mutmut results
uv run mutmut html  # generates html/index.html
```

**TypeScript usage** (via `stryker.config.mjs`):
```js
export default {
  testRunner: 'vitest',
  coverageAnalysis: 'perTest',
  thresholds: { high: 90, low: 85, break: 85 }
}
```

**Alternatives considered**:
- `cosmic-ray` (Python): More comprehensive than mutmut but significantly more complex to configure; mutmut is sufficient for this project.
- `jest-stryker` / manual mutation: Stryker is the clear standard for JS/TS.

---

## 13. Metamorphic Testing for Agents

**Decision**: Implement metamorphic testing for the `agents` sub-project using custom pytest fixtures with `hypothesis` for metamorphic relation (MR) generation. No dedicated metamorphic testing framework — implement MRs as parameterised pytest tests.

**Rationale**:
- The `agents` sub-project will implement AI-assisted research tasks (abstract screening, data extraction, synthesis). These tasks produce outputs that are hard to verify with exact oracle assertions because the "correct" answer depends on nuanced judgement.
- **Metamorphic testing** addresses the oracle problem by defining *relations* between pairs of related inputs and their outputs, rather than asserting exact output values.
- Example metamorphic relations for an abstract screener:
  - **MR-1 (Permutation invariance)**: Screening a batch of abstracts in a different order should produce the same inclusion/exclusion decisions per abstract.
  - **MR-2 (Addition of irrelevant papers)**: Adding clearly out-of-scope papers to a batch should not change the decision for already-screened in-scope papers.
  - **MR-3 (Consistency)**: If an abstract is excluded in isolation, it should also be excluded when embedded in a larger batch of similar papers.
- `hypothesis` is used to generate varied input combinations for each MR, making the tests property-based rather than example-based.

**Implementation pattern**:
```python
# agents/tests/metamorphic/test_screener_mr.py
import pytest
from hypothesis import given, strategies as st
from agents.services.screener import screen_abstract

@given(st.lists(st.text(min_size=50), min_size=2, max_size=5))
def test_mr1_permutation_invariance(abstracts):
    """Decision per abstract must not depend on batch order."""
    results_fwd = screen_abstract(abstracts)
    results_rev = screen_abstract(list(reversed(abstracts)))
    assert results_fwd == dict(zip(reversed(abstracts), reversed(list(results_rev.values()))))
```

**Test structure**:
```
agents/tests/
├── unit/              # Standard unit tests; run in pre-commit
├── integration/       # Integration tests; run in CI
└── metamorphic/       # MR-based tests; run in CI; tagged with pytest marker
```

**Alternatives considered**:
- Standard assertion testing: Impossible for non-deterministic AI outputs; wrong tool for this use case.
- `deepeval` / `ragas`: LLM evaluation frameworks; better suited for evaluating output quality than structural correctness; complementary, not a replacement for metamorphic testing.
- **`GeMTest`** (`https://github.com/tum-i4/gemtest`): A dedicated Python metamorphic testing framework from TU Munich. Provides a declarative `@metamorphic` decorator and built-in support for defining and composing metamorphic relations, reducing boilerplate compared to raw pytest + hypothesis. A strong candidate to adopt instead of the custom pytest approach if the team prefers a framework with first-class MR concepts. Evaluate after the scaffold phase — if the custom approach becomes unwieldy, migrate to GeMTest.
- A dedicated metamorphic testing library (`pytest-metamorphic`): Immature; implementing MRs directly in pytest is simpler and more flexible.

---

## 14. LLM Provider Abstraction (Agents + agent-eval)

**Decision**: `litellm` as the unified LLM client in both `agents` and `agent-eval`; Ollama served locally and exposed via `OLLAMA_BASE_URL`; provider/model selection fully driven by pydantic-settings environment variables.

**Rationale**:
- `litellm` provides a single `litellm.completion()` interface that transparently routes to Anthropic (`anthropic/claude-*`), Ollama (`ollama/llama3.2`), OpenAI, and 100+ other providers. No provider-specific branching in application code.
- Ollama runs LLMs locally via a REST API compatible with the OpenAI spec; `litellm` treats it as `ollama/<model>` or via `api_base` override — no separate client needed.
- All provider configuration lives in `core/config.py` (pydantic-settings); switching from Anthropic to Ollama requires only env var changes, no code changes.
- `deepeval` supports custom LLM judges via its `DeepEvalBaseLLM` interface; wrapping `litellm` behind this interface makes both local and cloud judges work identically.

**Configuration model** (shared pattern for `agents` and `agent-eval`):
```python
# core/config.py
from pydantic_settings import BaseSettings

class LLMSettings(BaseSettings):
    llm_provider: str = "anthropic"          # "anthropic" | "ollama"
    llm_model: str = "claude-sonnet-4-6"     # e.g. "llama3.2:3b" for Ollama
    ollama_base_url: str = "http://localhost:11434"
    anthropic_api_key: str = ""

    @property
    def litellm_model(self) -> str:
        if self.llm_provider == "ollama":
            return f"ollama/{self.llm_model}"
        return f"anthropic/{self.llm_model}"
```

**LiteLLM call pattern**:
```python
import litellm
from agents.core.config import settings

response = litellm.completion(
    model=settings.litellm_model,
    messages=[{"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt}],
    api_base=settings.ollama_base_url if settings.llm_provider == "ollama" else None,
)
```

**deepeval judge wrapper**:
```python
# agent_eval/judge.py
from deepeval.models.base_model import DeepEvalBaseLLM
import litellm

class LiteLLMJudge(DeepEvalBaseLLM):
    def __init__(self, settings: LLMSettings):
        self.settings = settings

    def load_model(self): return self

    def generate(self, prompt: str) -> str:
        r = litellm.completion(
            model=self.settings.litellm_model,
            messages=[{"role": "user", "content": prompt}],
            api_base=self.settings.ollama_base_url if self.settings.llm_provider == "ollama" else None,
        )
        return r.choices[0].message.content

    async def a_generate(self, prompt: str) -> str:
        r = await litellm.acompletion(
            model=self.settings.litellm_model,
            messages=[{"role": "user", "content": prompt}],
            api_base=self.settings.ollama_base_url if self.settings.llm_provider == "ollama" else None,
        )
        return r.choices[0].message.content

    def get_model_name(self) -> str:
        return self.settings.litellm_model
```

**Env var matrix**:

| Scenario | `LLM_PROVIDER` | `LLM_MODEL` | `OLLAMA_BASE_URL` | `ANTHROPIC_API_KEY` |
|----------|---------------|-------------|-------------------|---------------------|
| Anthropic cloud | `anthropic` | `claude-sonnet-4-6` | (unused) | required |
| Local Ollama | `ollama` | `llama3.2:3b` | `http://localhost:11434` | (unused) |
| Remote Ollama | `ollama` | `llama3.2:70b` | `http://gpu-server:11434` | (unused) |

**Alternatives considered**:
- Provider-specific clients (`anthropic` SDK + `ollama` Python SDK): Requires branching logic everywhere an LLM is called; breaks open/closed principle.
- LangChain as abstraction: Heavy dependency; introduces its own abstractions on top; LiteLLM is lighter and more direct.
- Direct Ollama REST calls via `httpx`: Works but duplicates what LiteLLM already provides.

---

## 15. `agent-eval` Sub-project: CLI Framework

**Decision**: `typer` with `rich` for terminal output; packaged as `sms-agent-eval` in the UV workspace.

**Rationale**:
- `typer` is the modern standard for Python CLIs: FastAPI-style type annotations, automatic `--help`, shell completion, and Pydantic v2 integration. Minimal boilerplate.
- `rich` provides beautiful tables, progress bars, and coloured output with zero effort alongside Typer.
- As a UV workspace member, `agent-eval` can depend on `agents` directly (library import) and run evaluations in-process with no network overhead.

**CLI command surface** (`agent-eval <command>`):
```
evaluate   Run a test suite against an agent and score with LLM-as-a-Judge
report     Display or export results from a previous evaluation run
compare    Compare scores between two agent versions or prompt variants
improve    Suggest prompt revisions based on low-scoring evaluation cases
```

**Alternatives considered**:
- `click` directly: Lower-level than Typer; more boilerplate; Typer is strictly better for typed Python.
- `argparse`: Standard library but verbose and lacks rich output integration.

---

## 16. LLM-as-a-Judge Tooling

**Decision**: `deepeval` as the primary evaluation framework for structured LLM-as-a-Judge metrics; Anthropic API (via `anthropic` SDK) used directly for custom judge prompts specific to research tasks.

**Rationale**:
- **`deepeval`** provides battle-tested, ready-made metrics: `GEval` (custom criteria via LLM), `FaithfulnessMetric`, `AnswerRelevancyMetric`, `HallucinationMetric`, and more. Integrates with pytest via `deepeval.test_case`. Supports any LLM as the judge, including Claude.
- For research-specific metrics (e.g., "Did the agent correctly apply PICO criteria when screening this abstract?"), custom judge prompts written in Markdown and evaluated via the Anthropic API give full control.
- The two approaches are complementary: deepeval for generic quality metrics, custom Anthropic calls for domain-specific research criteria.

**Usage pattern**:
```python
# agent_eval/evaluators/screener.py
from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase

screening_accuracy = GEval(
    name="Screening Accuracy",
    criteria="The agent's inclusion/exclusion decision correctly applies the stated research criteria.",
    model="claude-sonnet-4-6",
)

def run_eval(test_cases: list[LLMTestCase]) -> EvalReport:
    return evaluate(test_cases, [screening_accuracy])
```

**Alternatives considered**:
- `ragas`: Focused on RAG pipelines (retrieval + generation); less suited to agent task evaluation.
- `promptfoo`: CLI-first, YAML-driven; better suited to prompt A/B testing than programmatic agent evaluation.
- `openai-evals`: OpenAI-specific framing; less idiomatic with Anthropic/Claude.
- Pure custom implementation: More control but high development cost; deepeval covers 80% of needed metrics.

---

## 17. Prompt Template Management

**Decision**: Store system and user prompts as Markdown files under `agents/prompts/{agent_type}/`; use Jinja2 for variable substitution at runtime. `agent-eval improve` command reads, evaluates, and proposes updated versions of these files.

**Rationale**:
- Markdown is human-readable, diff-friendly, and renders well in GitHub. Prompt engineers can edit prompts without touching Python code.
- Jinja2 is the standard Python templating engine; `{{ variable }}` syntax is familiar and allows conditional blocks for complex prompts.
- Versioning prompts as files in git gives full change history and enables `agent-eval compare` to diff performance between prompt versions.
- The `improve` command uses LLM-as-a-Judge scores to identify weak cases, then calls the Anthropic API to suggest prompt revisions, writing candidates back to the filesystem for human review.

**Directory structure**:
```
agents/
└── prompts/
    ├── screener/
    │   ├── system.md          # System prompt for abstract screener
    │   └── user.md.j2         # Jinja2 user prompt template
    ├── extractor/
    │   ├── system.md
    │   └── user.md.j2
    └── synthesiser/
        ├── system.md
        └── user.md.j2
```

**Prompt loader**:
```python
# agents/core/prompt_loader.py
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def load_prompt(agent_type: str, role: str, **kwargs: str) -> str:
    env = Environment(loader=FileSystemLoader(Path(__file__).parent.parent / "prompts"))
    template = env.get_template(f"{agent_type}/{role}.md.j2")
    return template.render(**kwargs)
```

**Alternatives considered**:
- Hardcoded strings in Python: Not editable without code changes; no diff history of prompt iterations.
- YAML/TOML prompt files: Less readable for multi-paragraph prompts; Markdown is better for prose.
- LangChain `PromptTemplate`: Adds LangChain as a dependency; unnecessary when Jinja2 suffices.

---

## 18. Dockerfile Design: Backend

**Decision**: Multi-stage build from the repo root (workspace context). Stage 1 installs UV and syncs production deps; stage 2 is a minimal `python:3.14-slim` runtime.

**Rationale**:
- Building from the repo root lets the backend Dockerfile access the full UV workspace (`agents/`, `db/`) as path dependencies — the only clean way to package a UV workspace member for production.
- Multi-stage keeps the final image small: the UV cache and build tools stay in stage 1.
- `uv sync --frozen --no-dev` installs exactly what `uv.lock` specifies, producing reproducible images.
- Running as a non-root user (`USER appuser`) follows Docker security best practices.

**Dockerfile pattern**:
```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /workspace
COPY pyproject.toml uv.lock ./
COPY backend/ ./backend/
COPY agents/  ./agents/
COPY db/      ./db/
RUN uv sync --frozen --no-dev --package sms-backend

FROM python:3.14-slim AS runtime
RUN adduser --disabled-password appuser
COPY --from=builder /workspace/.venv /app/.venv
COPY --from=builder /workspace/backend/src /app/src
WORKDIR /app
USER appuser
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build context**: repo root (`.`) with `backend/Dockerfile`.

**Alternatives considered**:
- `uv export` → pip install: Decouples from UV but loses workspace path dependency resolution.
- Build from `backend/` subdirectory only: Cannot resolve `agents`/`db` workspace siblings.

---

## 19. Dockerfile Design: Frontend

**Decision**: Multi-stage build — Stage 1: `node:20-alpine` runs `npm ci && npm run build`; Stage 2: `nginx:alpine` serves the compiled static files.

**Rationale**:
- Vite produces a static bundle (`dist/`) that can be served by nginx with no Node runtime in production, yielding a very small image (~25 MB).
- `npm ci` (not `npm install`) uses the lockfile exactly, ensuring reproducible builds.
- A custom `nginx.conf` enables `try_files` fallback for React Router client-side routing.

**Dockerfile pattern**:
```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**nginx.conf** (SPA fallback):
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    location / { try_files $uri $uri/ /index.html; }
}
```

**Alternatives considered**:
- `node:20-alpine` as runtime serving via `vite preview`: Much larger image; not suited for production.
- `caddy:alpine`: Excellent alternative to nginx; equally valid but nginx is more universally familiar.

---

## 20. Dockerfile Validation Tooling

**Decision**: `hadolint` for Dockerfile linting (pre-commit + CI); `trivy` for container vulnerability scanning (CI only after image build).

**Rationale**:
- **`hadolint`**: The standard Dockerfile linter. Checks shell best practices (via ShellCheck), Docker layer caching patterns, `apt`/`apk` pinning, non-root user rules, and more. Runs in <1 second per Dockerfile — fast enough for pre-commit.
- **`trivy`**: The leading open-source vulnerability scanner for container images (Aqua Security). Scans OS packages and language-specific deps (Python, npm) against CVE databases. Must run after `docker build`; CI-only.
- Both are free, widely adopted, and have official GitHub Actions.

**Pre-commit integration** (adds to root `.pre-commit-config.yaml`):
```yaml
- repo: https://github.com/hadolint/hadolint
  rev: v2.12.0
  hooks:
    - id: hadolint
      args: ["--ignore", "DL3008"]  # DL3008: apt pin versions (acceptable in slim)
```

**CI integration** (adds to `.github/workflows/ci.yml`):
```yaml
- name: Build backend image
  run: docker build -f backend/Dockerfile -t sms-backend:ci .

- name: Trivy scan — backend
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: sms-backend:ci
    format: sarif
    severity: CRITICAL,HIGH
    exit-code: '1'
```

**Alternatives considered**:
- `dockle`: CIS Dockerfile benchmark; complementary to hadolint but overlapping; hadolint covers most of the same rules.
- `docker scout`: Docker's built-in scanner (replaces Snyk integration); requires Docker subscription for full features; trivy is fully free.
- `snyk container`: Good but requires Snyk account; trivy is simpler to integrate.

---

## 21. Docker Compose: Local Deployment

**Decision**: Single `docker-compose.yml` at the repo root with four services: `db` (PostgreSQL), `backend`, `frontend`, `ollama`. The `ollama` service uses a **Compose profile** (`--profile ollama`) so it is opt-in — operators using a remote Ollama or Anthropic omit it.

**Rationale**:
- Docker Compose profiles (v2 feature) cleanly model optional services without separate compose files.
- `OLLAMA_BASE_URL` env var in `backend` and `agent-eval` points to either the compose `ollama` service or a remote URL — no service code changes needed.
- Health checks on `db` and `ollama` ensure `backend` doesn't start until dependencies are ready.
- Named volumes for `pgdata` and `ollama_data` survive container restarts.

**Service matrix**:

| Service | Image / Build | Ports | Profile |
|---------|--------------|-------|---------|
| `db` | `postgres:16-alpine` | 5432 | always |
| `backend` | build `backend/Dockerfile` (context: root) | 8000 | always |
| `frontend` | build `frontend/Dockerfile` (context: `frontend/`) | 3000→80 | always |
| `ollama` | `ollama/ollama` | 11434 | `ollama` |

**Usage**:
```bash
# Anthropic cloud — no Ollama
docker compose up

# Local Ollama
docker compose --profile ollama up

# Pull a model into running Ollama
docker compose exec ollama ollama pull llama3.2:3b
```

**Alternatives considered**:
- Separate `docker-compose.ollama.yml` override file: Works but requires `--file` flags and is harder to discover.
- Always-on Ollama service: Wastes GPU/CPU resources when using Anthropic; profiles are strictly better.
- Kubernetes/Helm: Overkill for local development; Compose is the right tool at this stage.

---

## 22. `researcher-mcp` Sub-project: FastMCP Framework

**Decision**: `FastMCP` (the high-level Python MCP framework by Anthropic/jlowin) to implement the `researcher-mcp` MCP server; run as a standalone HTTP/SSE server on port 8002.

**Rationale**:
- FastMCP provides `@mcp.tool()`, `@mcp.resource()`, and `@mcp.prompt()` decorators, turning plain Python functions into MCP-compliant tools with zero protocol boilerplate.
- Running as a standalone HTTP/SSE server decouples the tool implementation from the agent runtime — the same `researcher-mcp` server can serve multiple agent instances and future MCP clients (e.g., Claude Desktop, other AI tools).
- FastMCP's `Client` can also be used for in-process testing without a network hop.
- `researcher-mcp` is a UV workspace member; `agents` declares it as a workspace dependency for local testing, but connects to it via HTTP at runtime.

**Package structure**:
```
researcher-mcp/
├── pyproject.toml          # sms-researcher-mcp; deps: fastmcp, httpx, pydantic
└── src/researcher_mcp/
    ├── server.py           # FastMCP app instance + entry point
    ├── core/
    │   └── config.py       # Settings (API keys, SciHub URL, source preferences)
    └── tools/
        ├── search.py       # search_papers, search_authors
        ├── metadata.py     # get_paper, get_author, list_papers_by_author
        └── fetch.py        # fetch_paper_pdf (Unpaywall → arXiv → SciHub)
```

**Server entry point**:
```python
# researcher_mcp/server.py
from fastmcp import FastMCP
mcp = FastMCP("SMS Researcher MCP")

# Tools imported from tool modules
from researcher_mcp.tools import search, metadata, fetch  # noqa: F401

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8002)
```

**Alternatives considered**:
- Raw `mcp` SDK: Lower-level; FastMCP is the recommended high-level abstraction.
- Implement as a library (no HTTP server): Loses MCP protocol benefits; prevents use by non-Python MCP clients.
- Expose tools directly in `agents` without MCP: Tightly couples tool implementation to agent runtime.

---

## 23. MCP Configuration Placement: `agents` Sub-project

**Decision**: Configure the MCP client connection in `agents/core/mcp_client.py`; `agents` connects to `researcher-mcp` via HTTP/SSE using FastMCP's `Client`; discovered tools are converted to LiteLLM function-call format for use in agent prompts.

**Rationale**:
- The `agents` sub-project contains the AI agent logic that uses tools — it is the natural owner of the MCP client configuration.
- The `backend` orchestrates agents but does not directly call MCP tools; placing MCP config in `backend` would create an unnecessary coupling.
- FastMCP's `Client` provides `get_tools()` which returns tool definitions compatible with LiteLLM's `tools` parameter format after a small transformation.
- `AGENT_MCP_URL` env var (default: `http://researcher-mcp:8002/sse`) controls the server location; `agents` can target a local process or a remote server without code changes.

**Integration pattern**:
```python
# agents/core/mcp_client.py
from fastmcp import Client
from agents.core.config import settings

async def get_mcp_tools() -> list[dict]:
    """Return MCP tools as LiteLLM-compatible function definitions."""
    async with Client(settings.researcher_mcp_url) as client:
        tools = await client.list_tools()
        return [
            {"type": "function",
             "function": {"name": t.name, "description": t.description,
                          "parameters": t.inputSchema}}
            for t in tools
        ]
```

**Env var**:
```
AGENT_MCP_URL=http://researcher-mcp:8002/sse   # docker-compose default
AGENT_MCP_URL=http://localhost:8002/sse   # local dev default
```

**Alternatives considered**:
- Configure MCP in `backend`: Backend would need to know about agent tools; violates separation of concerns.
- Hardcode tool list in `agents`: Loses dynamic tool discovery; breaks when `researcher-mcp` adds new tools.

---

## 24. Paper Search APIs

**Decision**: Multi-source search with priority order: **Semantic Scholar** → **OpenAlex** → **CrossRef**. All three are free and require no authentication for basic use.

**Rationale**:
- **Semantic Scholar** (Allen Institute): Comprehensive academic graph (200M+ papers), free API, supports full-text search, citation data, author profiles, and abstracts. Rate limit: 100 req/5min unauthenticated, 1 req/s with free API key.
- **OpenAlex** (OurResearch): 250M+ works, fully open, DOI/ORCID/ROR integration, rich filtering. No auth required; polite pool at 100k req/day.
- **CrossRef**: DOI metadata authority; best for resolving DOIs and getting citation counts. Free with `mailto` header for polite pool.
- Sources are tried in order; results are merged and deduplicated by DOI.

**Tool signatures**:
```python
@mcp.tool()
async def search_papers(
    query: str,
    limit: int = 20,
    year_from: int | None = None,
    year_to: int | None = None,
    source: Literal["semantic_scholar", "openalex", "crossref", "all"] = "all",
) -> list[PaperResult]: ...

@mcp.tool()
async def get_paper(doi: str) -> PaperDetail: ...

@mcp.tool()
async def search_authors(name: str, limit: int = 10) -> list[AuthorResult]: ...

@mcp.tool()
async def get_author(author_id: str, source: str = "semantic_scholar") -> AuthorDetail: ...

@mcp.tool()
async def list_papers_by_author(author_id: str, limit: int = 50) -> list[PaperResult]: ...
```

**Alternatives considered**:
- PubMed/MEDLINE: Biomedical focus; useful but covered by Semantic Scholar.
- IEEE Xplore / ACM DL: Paywalled APIs; not suitable for free-tier use.
- CORE API: Open access focused; good complement; add in later phase.

---

## 25. Paper PDF Fetching Strategy

**Decision**: Attempt PDF sources in priority order: **Unpaywall** (legal open access) → **arXiv** (for preprints) → **SciHub** (opt-in, disabled by default, configured via `SCIHUB_ENABLED=true`).

**Rationale**:
- **Unpaywall**: Free, legal API that resolves DOIs to open-access PDFs. Covers ~50% of recent papers. Requires only an email address (`email` param). Zero legal risk.
- **arXiv**: Free, legal. Direct PDF download for preprints. Many CS/physics/math papers are available here even if paywalled in journals.
- **SciHub**: Widely used in the research community but operates in a legal grey area (copyright litigation in multiple jurisdictions). Included as a configurable, opt-in option with clear documentation of legal/ethical implications. **Disabled by default.** Users enable it by setting `SCIHUB_ENABLED=true` and `SCIHUB_URL` in their environment.

**Fetch tool**:
```python
@mcp.tool()
async def fetch_paper_pdf(
    doi: str,
    output_path: str,
) -> FetchResult:
    """
    Attempt to fetch a paper PDF in order: Unpaywall → arXiv → SciHub (if enabled).
    Returns the path to the saved PDF and the source used.
    """
```

**Legal/ethical note**: SciHub integration is documented with a prominent warning in the README. It is the user's responsibility to comply with applicable laws in their jurisdiction.

**Alternatives considered**:
- Unpaywall only: Misses ~50% of papers; researchers find this too limiting.
- No PDF fetch: Removes a key capability for systematic review workflows.
- Browser automation (Playwright): More complex, fragile; API-first approach preferred.

---

## Summary of All Decisions

| Topic | Decision |
|-------|----------|
| Python workspace | UV workspace with shared lockfile |
| Python version | 3.14+ |
| Python lint/format | Ruff (all-in-one) |
| Python type check | MyPy (strict) |
| Python test | pytest + pytest-asyncio + pytest-cov |
| Python pre-commit | `pre-commit` framework with `uv run` local hooks |
| Frontend scaffold | Vite 5 + React 18 + TypeScript 5 |
| Frontend test | Vitest + @testing-library/react |
| Frontend lint | ESLint 9 flat config + typescript-eslint + react plugins |
| Frontend format | Prettier 3 + eslint-config-prettier |
| Frontend pre-commit | Husky v9 + lint-staged |
| Backend framework | FastAPI 0.111+ with Pydantic v2 |
| ORM | SQLAlchemy 2.x async |
| Migrations | Alembic |
| Database (prod) | PostgreSQL |
| Database (dev) | SQLite via aiosqlite |
| Agents integration | Direct Python import (UV workspace dependency) |
| Schema sharing | `db/` workspace member imported by `backend/` |
| LLM provider abstraction | LiteLLM (Anthropic + Ollama, config-driven) |
| Backend Dockerfile | Multi-stage; UV workspace context from repo root |
| Frontend Dockerfile | Multi-stage; node:20-alpine build + nginx:alpine runtime |
| Dockerfile linting | hadolint (pre-commit + CI) |
| Container vuln scanning | trivy (CI only, after image build) |
| Local deployment | docker-compose.yml; ollama via Compose profile |
| agent-eval CLI | Typer + Rich |
| LLM-as-a-Judge | deepeval + LiteLLMJudge wrapper |
| Prompt templates | Markdown files + Jinja2 in `agents/prompts/` |
| MCP server | FastMCP; HTTP/SSE; port 8002 |
| MCP client | `agents/core/mcp_client.py`; LiteLLM function-call conversion |
| Paper search | Semantic Scholar → OpenAlex cascade; CrossRef DOI resolution |
| PDF fetch | Unpaywall → arXiv → SciHub (opt-in, default off) |
| API failure | Cascade fallback + tenacity retry (max 3, exp backoff + jitter) |
| Rate limiting | Per-source env vars (SEMANTIC_SCHOLAR_RPM, OPEN_ALEX_RPM) |
| researcher-mcp Docker | Multi-stage python:3.14-slim; repo root context |
