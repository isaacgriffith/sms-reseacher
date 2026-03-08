<!--
SYNC IMPACT REPORT
==================
Version change: 1.4.0 → 1.5.0
Bump rationale: MINOR — new mandatory documentation rule added (Principle III and
  Principle IX): all functions, methods, and classes MUST include Google-style (Python)
  or JSDoc (TypeScript) doc comments; CLI command handlers are exempt from parameter /
  return-value documentation sections.

Modified principles:
  - III. Code Clarity & Anti-Pattern Avoidance — new "Documentation" bullet added.
  - IX. Language-Specific Best Practices — new bullet in Python section (Google-style
    docstrings enforcement); new bullet in TypeScript section (JSDoc requirements).

Added sections:
  - Code Quality Standards table: 1 new row (Documentation).

Templates updated:
  ✅ .specify/templates/plan-template.md — Constitution Check table: new gate row added
  ✅ .specify/templates/tasks-template.md — Notes footer: documentation rule added
  ⚠ .specify/templates/spec-template.md — no changes required (generic enough)
  ⚠ .specify/templates/commands/ — directory not present; no updates needed

Deferred TODOs: none
-->

# SMS Researcher Constitution

## Core Principles

### I. SOLID Design Principles

Every module, class, and function MUST conform to the five SOLID principles:

- **Single Responsibility Principle (SRP)**: Each module, class, or function MUST have
  exactly one reason to change. Mix of concerns in a single unit is a blocking violation.
- **Open-Closed Principle (OCP)**: Implementations MUST be open for extension and closed
  for modification. New behavior MUST be added via extension (new types, strategy injection,
  decorators), not by editing existing logic.
- **Liskov Substitution Principle (LSP)**: Subtypes MUST be fully substitutable for their
  base types without altering correctness. Overrides that strengthen preconditions or weaken
  postconditions are forbidden.
- **Interface Segregation Principle (ISP)**: Interfaces and abstract contracts MUST be
  narrow and role-specific. No consumer SHOULD be forced to depend on methods it does not use.
- **Dependency Inversion Principle (DIP)**: High-level modules MUST NOT depend on low-level
  modules. Both MUST depend on abstractions. Concrete implementations MUST be injected, not
  instantiated inside business logic.

*Rationale*: SOLID principles prevent coupling rot, enable independent unit testing, and keep
the codebase open to the iterative requirements of a research platform.

### II. Structural Quality Principles

Code structure MUST reflect the following quality axioms at every layer:

- **Don't Repeat Yourself (DRY)**: Every piece of knowledge or logic MUST have a single,
  authoritative representation. Duplication is a defect, not a convenience.
- **You Aren't Gonna Need It (YAGNI)**: Features, abstractions, and configuration MUST NOT
  be added speculatively. Only implement what is required by the current task.
- **Loose Coupling**: Components MUST interact through stable, minimal interfaces. Internal
  implementation details MUST NOT leak across boundaries.
- **High Cohesion**: Related responsibilities MUST reside together. Unrelated concerns MUST
  be separated into distinct units.
- **Encapsulate What Varies**: Behavior that changes frequently MUST be isolated behind an
  abstraction so the rest of the system remains stable.
- **Separation of Concerns (SoC)**: Data access, business logic, presentation, and I/O MUST
  occupy distinct layers with no cross-cutting bleed.

*Rationale*: These axioms collectively bound complexity growth and ensure that each component
can be understood, tested, and replaced in isolation — critical for a long-lived research tool.

### III. Code Clarity & Anti-Pattern Avoidance

All generated and modified code MUST avoid the following anti-patterns:

- **High Cyclomatic Complexity**: Functions and methods with cyclomatic complexity > 10 MUST
  be decomposed into smaller, single-purpose helpers. Brain methods are forbidden.
- **Long Methods**: Any method exceeding ~20 meaningful lines of logic MUST be refactored into
  composable, named sub-steps. Long methods are a blocking code smell.
- **Switch / If-Chain Smells**: Chains of `if/elif/else` or `switch` blocks that dispatch on
  type or state MUST be replaced with polymorphism, strategy objects, dispatch maps, or
  pattern-matching on sealed types. Type-switching is a design smell, not a solution.
- **Common Code Smells**: The following MUST be actively avoided and remedied on sight:
  Feature Envy, Data Clumps, Primitive Obsession, Shotgun Surgery, Divergent Change,
  Inappropriate Intimacy, Message Chains, Middle Man, Speculative Generality, Dead Code.
- **God Objects / God Modules**: No single class or module MUST accumulate responsibilities
  beyond a focused role. Split proactively before the violation solidifies.
- **Documentation**: All functions, methods, and classes MUST include doc comments.
  - **Python**: Google-style docstrings are REQUIRED, with `Args:`, `Returns:`, and `Raises:`
    sections where applicable. This is enforced by ruff's `D` rule set (with `D203`/`D213`
    ignored for Google-style compatibility).
  - **TypeScript/JavaScript**: JSDoc comments (`/** ... */`) are REQUIRED for all exported
    functions, classes, and methods. A single-sentence description is the minimum; `@param`
    and `@returns` tags MUST be included for non-trivial signatures.
  - **CLI command handlers** are the only exception: they MUST include a brief description of
    the command, but MUST NOT document parameters or return values (these are self-described
    by the CLI framework's help text and would create maintenance duplication).

*Rationale*: Clean, navigable code is a prerequisite for AI-assisted development, peer review,
and long-term maintainability of the SMS research platform.

### IV. Refactoring Discipline

Before writing any new code or modifying existing code, the following MUST be performed:

1. **Pre-modification review**: Examine the code to be changed, its immediate callers, and any
   downstream consumers for existing violations of Principles I–III.
2. **Refactoring identification**: If violations are found that would be improved by the
   current change, they MUST be recorded and added to the implementation plan as explicit tasks
   — not silently fixed inline.
3. **Test-first refactoring**: Every planned refactoring task MUST be covered by tests before
   execution. If adequate tests do not exist, writing them is a prerequisite sub-task that MUST
   appear in the task list and be completed first.
4. **Refactoring isolation**: Refactoring commits MUST be separate from feature commits.
   A single commit MUST NOT mix behavioral change with structural change.

*Rationale*: Disciplined refactoring preserves correctness, keeps the test suite meaningful,
and prevents incremental quality degradation under deadline pressure.

### V. GRASP Principles & Design Patterns

Design decisions MUST be grounded in GRASP (General Responsibility Assignment Software
Patterns) and well-known GoF/architectural design patterns where applicable:

- **GRASP patterns** — Information Expert, Creator, Controller, Low Coupling, High Cohesion,
  Polymorphism, Pure Fabrication, Indirection, Protected Variations — MUST be evaluated when
  assigning responsibilities to new or existing objects.
- **GoF / architectural patterns** — where a recognized pattern cleanly solves the problem at
  hand (e.g., Strategy, Factory, Observer, Repository, Command, Decorator, Adapter), it MUST
  be preferred over ad-hoc solutions.
- Pattern application MUST be justified in the plan or code comment. Applying a pattern for
  its own sake (pattern over-engineering) is itself a violation of YAGNI.

*Rationale*: Shared pattern vocabulary reduces cognitive load during code review and AI-
assisted generation, and ensures design intent is explicit and auditable.

### VI. Testing Discipline

All implemented code MUST meet the following testing requirements before a task is considered
complete. Testing is not optional and MUST be planned as explicit tasks in every feature's
task list.

#### Unit & Integration Coverage

- **Unit tests**: All Python and TypeScript code MUST be covered by unit tests achieving
  a minimum of **85% line/branch coverage**. Coverage MUST be measured with `pytest-cov`
  (Python) and `vitest --coverage` or equivalent (TypeScript). Falling below 85% is a
  blocking gate — the task MUST NOT be marked complete.
- **Integration tests**: All backend services, API endpoints, and data-access layers MUST
  be covered by integration tests achieving a minimum of **85% coverage** across integrated
  paths. Integration tests MUST exercise real database transactions (SQLite for CI, PostgreSQL
  for staging) and real HTTP handlers.
- Coverage reports MUST be generated and attached to every PR. Any intentionally uncovered
  lines MUST be annotated with `# pragma: no cover` (Python) or `/* istanbul ignore */`
  (TypeScript) with an inline justification comment.

#### UI/UX Testing

- All frontend components and user-facing flows MUST be covered by automated UI/UX tests.
  Acceptable tooling includes Playwright, Cypress, or React Testing Library (component level).
- Tests MUST verify: correct rendering of state, user interaction flows (click, input, submit),
  error states, loading states, and accessibility where applicable.
- UI tests MUST be run in CI on every PR targeting the `main` branch.

#### Mutation Testing

- All test suites MUST be validated for quality using mutation testing. The minimum acceptable
  mutation score is **85% mutants killed**.
- Python code MUST use `mutmut` or `cosmic-ray` for mutation analysis.
- TypeScript code MUST use `stryker` for mutation analysis.
- Mutation scores MUST be recorded in the PR description. Scores below 85% require explicit
  remediation tasks to improve test assertions before merge.

#### Agent Metamorphic Testing

- Every AI agent implemented in the `agents/` package MUST be covered by metamorphic tests
  using the `hypothesis` library (Python).
- Metamorphic relations MUST be defined for each agent's core transformation behavior
  (e.g., query expansion monotonicity, screening consistency under paraphrase, result
  ordering stability).
- Metamorphic test files MUST reside in `agents/tests/metamorphic/` and be executed as
  part of the agent's standard test suite in CI.

#### Agent Evaluation Pipelines (deepeval)

- Every AI agent, when first created or substantially modified, MUST have an evaluation
  pipeline added to the `agent-eval` project using `deepeval`.
- The evaluation pipeline MUST define: dataset of representative inputs, expected output
  criteria (metrics such as faithfulness, answer relevancy, contextual precision as
  applicable), and a pass/fail threshold.
- Evaluation pipelines MUST be run against new model versions or significant prompt changes
  before merging to `main`.
- Evaluation results MUST be stored as artifacts and referenced in the PR description.

*Rationale*: High coverage, mutation-validated tests, and agent evaluation pipelines are the
primary safeguards against regression in a research platform where correctness and
reproducibility are non-negotiable. Metamorphic testing is essential for agents whose outputs
cannot be oracle-checked deterministically.

### VII. Technology Stack & Tooling Standards

All subprojects MUST conform to the approved technology stack and toolchain configuration.
Deviation requires a constitution amendment — substituting a different tool or version
without amending this document is a blocking violation.

#### Approved Stack

- **Python runtime**: Python 3.14+ across all Python packages (backend, agents, db,
  researcher-mcp, agent-eval). Python version MUST be pinned in each `pyproject.toml`.
- **TypeScript runtime**: TypeScript 5.4+ with Node 20 LTS for the frontend package.
- **Package management**: `uv` MUST be used for all Python dependency resolution and
  workspace management. `npm` is used for the frontend. No `pip install` commands outside
  of `uv` are permitted in CI or documentation.
- **Workspace layout**: The repository is a `uv` workspace. All Python packages MUST be
  declared as workspace members in the root `pyproject.toml`.

#### Python Toolchain

- **Linting/formatting**: `ruff` MUST be the sole Python linter and formatter. Configured
  with `line-length = 100`, `select = ["E", "W", "F", "I", "D", "UP", "B", "C4"]`, and
  `ignore = ["D203", "D213"]` (Google-style docstrings). All ruff violations MUST be
  resolved before merge; `ruff format` output is canonical.
- **Type checking**: `mypy` with `strict = true` and `python_version = "3.14"` MUST pass
  with zero errors. `ignore_missing_imports = false` is required; stubs MUST be added when
  third-party types are absent.
- **Pre-commit hooks**: `uv run ruff check`, `uv run ruff format --check`, and
  `uv run mypy` MUST all be registered in `.pre-commit-config.yaml` and run against every
  Python source directory. Dockerfile linting via `hadolint` MUST also be registered.
- **Testing framework**: `pytest` with `asyncio_mode = "auto"` is the standard. All async
  tests MUST be written with `async def` and rely on the automatic asyncio event loop.
- **Mutation testing**: `mutmut` on `src/` against `tests/` is the standard tool.

#### TypeScript/Frontend Toolchain

- **Build tool**: Vite 5.3+ is the build and dev server. `tsc && vite build` is the
  production build command.
- **Testing**: `vitest` with `jsdom` environment and `@testing-library/react` MUST be used
  for component and unit tests. The coverage command is `vitest run --coverage`.
- **Mutation testing**: `@stryker-mutator/core` with `@stryker-mutator/vitest-runner` is
  the standard tool.
- **Formatting**: Prettier MUST be configured with `singleQuote: true`,
  `trailingComma: "all"`, `printWidth: 100`, `semi: true`, `tabWidth: 2`.
- **Linting**: `eslint` with `typescript-eslint` and `eslint-plugin-react-hooks` MUST be
  configured and pass clean.
- **Git hooks**: Husky + `lint-staged` MUST run `eslint --fix` and `prettier --write` on
  staged `.ts`/`.tsx` files before commit.
- **TypeScript config**: `strict: true`, `noUnusedLocals`, `noUnusedParameters`, and
  `noFallthroughCasesInSwitch` MUST be enabled.

#### Framework & Library Conventions

- **Backend API**: FastAPI with Pydantic v2 request/response models MUST be used. All route
  handlers MUST use `async def`. Dependencies (DB sessions, auth) MUST be injected via
  FastAPI `Depends()`. Errors MUST be raised as `HTTPException` — never returned as plain
  dicts.
- **ORM**: SQLAlchemy 2.0+ async API MUST be used. Models MUST use `Mapped[T]` annotations
  and `mapped_column()`. Raw SQL or SQLAlchemy 1.x `Column()` style are forbidden in new
  code.
- **Migrations**: Alembic with an async-compatible `env.py` is required. Every schema
  change MUST have a corresponding `upgrade()`/`downgrade()` migration. Migrations MUST be
  applied programmatically on service startup (never manually in production).
- **Background jobs**: ARQ on Redis MUST be used for all deferred/long-running work. Job
  functions MUST be `async def`, receive an ARQ `ctx` dict, and track progress via the
  `BackgroundJob` model.
- **LLM abstraction**: `litellm` MUST be the sole LLM call interface in the `agents/`
  package. Calls MUST go through the shared `LLMClient` in `agents/core/llm_client.py`.
  Direct Anthropic/OpenAI SDK calls in agent service code are forbidden.
- **Prompt management**: Agent prompts MUST be stored as Jinja2 templates under
  `agents/src/agents/prompts/<agent_name>/` with separate `system.md` and `user.md.j2`
  files. Prompts MUST NOT be hardcoded inline in service code.
- **MCP server**: `fastmcp` 2.0+ MUST be used for the researcher-mcp service. Tool
  definitions MUST be declared via the FastMCP decorator API.
- **Frontend state**: TanStack Query (`@tanstack/react-query`) MUST be used for all
  server-state fetching and caching. React's built-in `useState`/`useReducer` is for local
  UI state only.
- **Frontend forms**: `react-hook-form` with `zod` validation schemas MUST be used for all
  user-input forms. Uncontrolled or manual `onChange` form patterns are forbidden.

*Rationale*: A fixed, approved stack eliminates "dependency sprawl", ensures every developer
and AI agent operates with consistent tooling, and makes the CI/pre-commit configuration
authoritative rather than advisory.

### VIII. Observability, Configuration & Infrastructure Standards

All subprojects MUST meet the following operational requirements to ensure consistent
behaviour across development, staging, and production environments.

#### Structured Logging

- **Library**: `structlog` MUST be used for all Python application logging (backend, agents,
  researcher-mcp). `print()` statements as a substitute for logging are forbidden in any
  production code path.
- **Format**: JSON-formatted log output MUST be configurable via the `json_logs` flag
  (driven by environment). Human-readable output is acceptable in development mode.
- **Logger acquisition**: Code MUST obtain a logger via `get_logger(__name__)` (or an
  equivalent bound-logger pattern). Module-level logger instantiation is preferred over
  per-function instantiation.
- **Context**: Log entries for request-scoped work MUST bind relevant context variables
  (e.g., user_id, study_id, job_id) before emitting log lines.

#### Configuration Management

- **Pydantic BaseSettings**: All application configuration MUST be expressed as a Pydantic
  `BaseSettings` subclass. Environment variables are the sole external configuration source.
  Hard-coded default secrets, API keys, or URLs are forbidden.
- **Settings singleton**: Each package MUST expose a `get_settings()` function decorated
  with `@functools.lru_cache()` to ensure a single Settings instance per process.
- **`.env` file**: A `.env` file at the repository root MAY be used for local development.
  It MUST be listed in `.gitignore`. Committed `.env` files with real secrets are a
  critical security violation.
- **Required variables**: `DATABASE_URL`, `SECRET_KEY`, `LLM_PROVIDER`, and
  `ANTHROPIC_API_KEY` (when provider is Anthropic) MUST be documented in a `.env.example`
  file at the repository root.

#### Database Model Standards

- **Audit fields**: Every persistent entity model MUST include `created_at` and `updated_at`
  columns of type `DateTime(timezone=True)` with `server_default=func.now()` and
  `onupdate=func.now()` respectively. Models without audit fields are a blocking violation.
- **Optimistic locking**: Any model that can be concurrently updated by multiple workers or
  users MUST include a `version_id` column and configure SQLAlchemy's optimistic locking
  via `__mapper_args__ = {"version_id_col": version_id}`.
- **Enum columns**: Domain-constrained string columns MUST use Python `enum.Enum` subclasses
  mapped through SQLAlchemy's `Enum` column type with an explicit `name` parameter to ensure
  stable PostgreSQL enum type naming across migrations.
- **Model exports**: All models MUST be exported from `db/src/db/models/__init__.py` so
  consumers can import from a single stable path.

#### Container & Infrastructure Standards

- **Docker images**: All service Dockerfiles MUST use multi-stage builds to minimise final
  image size. Intermediate build artifacts MUST NOT appear in the production image layer.
- **Health checks**: Every service defined in `docker-compose.yml` MUST have a `healthcheck`
  block using the appropriate probe (`curl`, `pg_isready`, `redis-cli ping`, etc.).
- **Service dependencies**: `depends_on` with `condition: service_healthy` MUST be used to
  express startup ordering. Race-condition workarounds (e.g., `sleep`) in entrypoints are
  forbidden.
- **Dockerfile linting**: `hadolint` MUST be registered in pre-commit and all Dockerfile
  lint warnings MUST be resolved before merge.
- **No hardcoded credentials in images**: Environment variables MUST be used for all runtime
  secrets. No credentials, tokens, or API keys may appear in Dockerfiles or
  docker-compose.yml values (only `${VAR}` references are permitted).

*Rationale*: Consistent logging, configuration, model conventions, and container standards
reduce operational surprises, simplify onboarding, and make security audits tractable on a
research platform that handles sensitive academic data and external API credentials.

### IX. Language-Specific Best Practices & Gotcha Avoidance

All code MUST conform to language- and framework-specific best practices enumerated here.
These rules are additive to Principles I–VIII and MUST be enforced during code review and
pre-commit checks.

#### React / Vite Gotchas

The following React and Vite pitfalls are known sources of subtle bugs and MUST be actively
avoided:

- **Vite env variable exposure**: Only variables prefixed with `VITE_` are exposed to
  browser bundles. Server-only secrets MUST NOT use the `VITE_` prefix. Access MUST use
  `import.meta.env.VITE_*`, never `process.env.*` in frontend code.
- **Stale closures in hooks**: `useEffect`, `useCallback`, and `useMemo` callbacks MUST
  declare all referenced variables in their dependency arrays. Omitting a dependency to
  silence a lint warning is forbidden — fix the dependency or use a ref pattern.
- **`React.StrictMode` double-invocation**: Effects run twice in development under
  `StrictMode`. Effect bodies MUST be idempotent and MUST return a cleanup function when
  subscribing to external resources, timers, or event listeners.
- **Unstable list keys**: The `key` prop in list renders MUST be a stable, unique identifier
  from the data (e.g., record ID). Array indices MUST NOT be used as keys for lists that can
  reorder, insert, or delete items.
- **State mutation**: React state MUST be treated as immutable. Direct mutation of state
  objects or arrays (e.g., `arr.push()` before `setState`) is forbidden — always derive new
  values and pass them to the setter.
- **Circular imports**: Vite HMR and bundler tree-shaking break silently on circular
  imports. Module dependency graphs MUST remain acyclic. Use dependency injection or
  event-based patterns to break cycles.
- **Default export tree-shaking**: Named exports MUST be preferred over default exports in
  utility and hook modules to enable correct tree-shaking in production builds.
- **`useEffect` for derived state**: Derived values that can be computed synchronously from
  existing state or props MUST NOT be placed inside `useEffect` with `setState`. Compute
  them inline during render or with `useMemo`.
- **Rules of Hooks**: Hooks MUST be called at the top level of a function component or
  custom hook — never inside conditionals, loops, or early-return branches. Violating the
  Rules of Hooks causes unpredictable state between renders and is a runtime error in React's
  development build. The `eslint-plugin-react-hooks` `rules-of-hooks` lint rule MUST be
  enabled and treated as an error.
- **Inline references in dependency arrays**: Objects, arrays, and functions created inline
  during render MUST NOT appear in `useEffect`, `useMemo`, or `useCallback` dependency
  arrays unless they are first stabilised with their own `useMemo`/`useCallback`. An inline
  `{}` or `[]` literal creates a new reference on every render, causing the hook to fire on
  every render — defeating memoization and risking infinite loops.

#### React Best Practices

- **Functional components only**: Class components MUST NOT be written in new code. All
  components MUST be function components using hooks.
- **Component size (SRP for UI)**: A component MUST have a single clear rendering
  responsibility. Components exceeding ~100 JSX lines MUST be decomposed into named
  sub-components. Inline anonymous components inside render return are forbidden.
- **Custom hooks for shared logic**: Stateful logic shared by two or more components MUST
  be extracted into a custom hook (`use*`) residing in `frontend/src/hooks/`. Hook files
  MUST export a single hook per file.
- **Co-locate state**: State MUST be declared at the lowest component that requires it.
  Lifting state higher than necessary couples components unnecessarily.
- **Prefer `useReducer` over excessive `useState`**: A component MUST NOT accumulate more
  than three independent `useState` calls for related state that transitions together.
  When state has complex update logic, multiple sub-values that change in concert, or
  state transitions driven by action semantics, `useReducer` MUST be used instead. Unrelated
  state values SHOULD each have their own `useState`; values that always change together
  MUST be consolidated into a single state object or `useReducer`.
- **`useCallback` only when justified**: `useCallback` MUST NOT be used as a default wrapper
  for every function defined in a component body. Apply it only when: (a) the function is
  passed as a prop to a `React.memo`-wrapped child where referential equality matters, or (b)
  the function is listed as a dependency of another hook and would otherwise trigger unwanted
  re-executions. Wrapping every handler in `useCallback` "just in case" is a YAGNI violation
  that adds overhead and obscures intent.
- **`useMemo` discipline**: `useMemo` MUST only be applied where a measurable render
  performance problem exists (expensive computation) or where referential stability of an
  object/array is required by a downstream hook or `React.memo` child. Premature memoization
  is a YAGNI violation.
- **`useEffect` cleanup is mandatory**: Every `useEffect` that subscribes to events, creates
  timers, opens network connections, starts animations, or acquires any external resource
  MUST return a cleanup function that fully reverses those operations. Missing cleanup
  functions cause memory leaks, stale event handlers, and double-execution bugs under
  `React.StrictMode`. An effect with side effects and no cleanup function is a blocking
  defect — not a style issue.
- **`React.memo` for expensive pure components**: `React.memo` SHOULD be applied to
  components that render frequently as children of a parent that re-renders often, receive
  stable props (primitives or memoized references), and carry a non-trivial render cost.
  `React.memo` MUST NOT be applied indiscriminately — it adds reconciliation overhead for
  cheap components and is a YAGNI violation when applied speculatively. A component wrapped
  in `React.memo` MUST have its prop functions stabilised with `useCallback` to avoid
  defeating the memoization.
- **`useImperativeHandle` for imperative child APIs**: When a parent component needs to
  imperatively trigger behavior owned by a child (e.g., focus an input, reset a form,
  play/pause media), `useImperativeHandle` combined with `React.forwardRef` MUST be used to
  expose a minimal imperative handle. Direct DOM manipulation from outside the component via
  `querySelector` or untyped refs is forbidden. The exposed handle MUST be typed with an
  explicit TypeScript `interface`.
- **`useWatch` over `watch` in react-hook-form**: When subscribing to form field values
  for conditional rendering, derived display, or cross-field validation, `useWatch` MUST be
  used instead of the `watch()` function returned by `useForm()`. The `watch()` function
  causes the entire form component to re-render on every keystroke; `useWatch` isolates
  re-renders to the subscribing component or hook, preserving form performance. `watch()`
  MAY be used only outside the render path (e.g., in a submit handler or a `useEffect`).
- **Error boundaries**: Every major page section that fetches async data MUST be wrapped in
  an `ErrorBoundary` component. Unhandled render errors MUST NOT crash the entire
  application.
- **Lazy loading**: Routes and heavy components MUST use `React.lazy` + `Suspense` with an
  appropriate fallback. Eager loading of all routes in the bundle is forbidden.
- **Props typing**: All component props MUST be typed with a named TypeScript `interface`
  (not inline object type or `any`). The interface MUST be co-located in the component file
  or in a co-located `*.types.ts` file.
- **Avoid prop drilling beyond two levels**: More than two levels of prop-passing for the
  same value MUST be refactored using React Context, TanStack Query, or a dedicated store.

#### Python Best Practices

- **Type annotations everywhere**: All function signatures (parameters and return type) and
  class attributes MUST carry explicit type annotations. Bare untyped code is a mypy strict
  violation and MUST NOT be merged.
- **Google-style docstrings**: All Python functions, methods, and classes MUST use Google-
  style docstrings with `Args:`, `Returns:`, and `Raises:` sections where applicable.
  Enforced by ruff's `D` rule set with `D203`/`D213` ignored. CLI command handler functions
  are the sole exception: they MUST include a brief one-line description of the command only
  — `Args:` and `Returns:` sections MUST NOT be added to CLI handlers (the CLI framework's
  help text is the authoritative documentation for those).
- **Structured data objects**: Plain `dict` MUST NOT be used to represent domain entities
  or API payloads in internal code. Use Pydantic models (API layer), `dataclasses`, or
  `typing.TypedDict` (where mutability is genuinely needed).
- **`pathlib.Path` over `os.path`**: All filesystem path manipulation MUST use
  `pathlib.Path`. `os.path` string manipulation is forbidden in new code.
- **Context managers for resources**: File handles, database connections, HTTP sessions, and
  locks MUST be acquired via `with` (synchronous) or `async with` (asynchronous) statements.
  Manual open/close patterns without context managers are forbidden.
- **Enums over magic strings/integers**: All domain-constrained constant sets MUST be
  defined as `enum.Enum` (or `enum.StrEnum` for string values) subclasses. Hard-coded
  string literals or integer constants used as discriminants are forbidden.
- **No mutable default arguments**: Function default argument values MUST NOT be mutable
  objects (`[]`, `{}`, `set()`). Use `None` with an internal `if value is None: value = []`
  pattern or `dataclasses.field(default_factory=...)`.
- **Specific exception handling**: `except Exception` and bare `except:` MUST NOT be used
  unless re-raising or at the outermost error boundary with logging. Catch the most specific
  applicable exception type. Use `contextlib.suppress(ExcType)` to silently ignore expected
  exceptions.
- **f-strings for formatting**: All string interpolation MUST use f-strings. `%`-formatting
  and `.format()` are forbidden in new code.
- **Generator expressions for large sequences**: When constructing sequences only to iterate
  over them once, generator expressions (`(x for x in iterable)`) MUST be preferred over
  list comprehensions to avoid unnecessary memory allocation.
- **`functools.cache` / `lru_cache` for pure functions**: Pure, side-effect-free functions
  with expensive computation or repeated identical calls MUST use `@functools.cache` (Python
  3.9+) or `@functools.lru_cache(maxsize=N)`.
- **`typing.Protocol` for structural interfaces**: When defining duck-typed interfaces,
  `typing.Protocol` MUST be used rather than ABCs unless runtime `isinstance` checks against
  the interface are required.
- **Async discipline**: `async def` functions MUST NOT call blocking I/O (file reads,
  `time.sleep`, synchronous DB drivers) without offloading to a thread pool via
  `asyncio.to_thread`. Mixing sync and async boundaries carelessly causes event-loop stalls.
- **`__slots__` for hot-path value objects**: Classes instantiated in tight loops or large
  numbers (e.g., per-document data containers) SHOULD declare `__slots__` to reduce per-
  instance memory overhead.

#### TypeScript Best Practices

- **No `any`**: The `any` type MUST NOT appear in new code. Use `unknown` for genuinely
  unknown external data, then narrow with type guards or Zod parsing. ESLint rule
  `@typescript-eslint/no-explicit-any` MUST be enabled and enforced.
- **JSDoc for exported symbols**: All exported TypeScript functions, classes, and methods
  MUST include JSDoc comments (`/** ... */`). A single-sentence description is the minimum
  required. `@param` and `@returns` tags MUST be included for functions with non-trivial
  signatures (more than one parameter, or a non-void/non-boolean return). CLI command
  handler functions MUST include a brief description of the command only — `@param` and
  `@returns` tags MUST NOT be added to CLI handlers.
- **Discriminated unions over class hierarchies**: When modeling variants of a data type
  (e.g., API response states, job statuses), discriminated unions MUST be preferred over
  class inheritance hierarchies. Example:
  `type Result = { kind: "ok"; value: T } | { kind: "err"; error: string }`.
- **`unknown` + Zod at boundaries**: All data entering the system from external sources
  (API responses, URL params, localStorage) MUST be typed `unknown` and parsed through a Zod
  schema before use. Casting external data directly with `as SomeType` is forbidden.
- **Prefer `interface` for object shapes**: `interface` MUST be used for object type
  declarations that describe data structures or component props. `type` aliases are
  acceptable for union types, intersection types, and utility type expressions.
- **`as const` for literal inference**: Object and array literals used as configuration or
  lookup tables MUST use `as const` to preserve narrow literal types and enable exhaustive
  pattern matching.
- **`satisfies` for safe literal validation**: When a literal object should conform to a
  type without widening its inferred type, use the `satisfies` operator rather than a type
  assertion (`as T`).
- **Avoid TypeScript `enum`**: TypeScript `enum` MUST NOT be used. Prefer string literal
  unions (`type Status = "pending" | "done"`) or `as const` object maps for constant sets.
  Reason: `enum` has unexpected runtime behavior and compiles to non-tree-shakeable code.
- **Utility types over manual repetition**: `Partial<T>`, `Required<T>`, `Pick<T, K>`,
  `Omit<T, K>`, `Readonly<T>`, `ReturnType<F>`, and `Parameters<F>` MUST be used to derive
  types from existing ones rather than duplicating type declarations.
- **Non-null assertion ban**: The non-null assertion operator (`!`) MUST NOT be used except
  in test code or when a value's presence is guaranteed by invariant that cannot be expressed
  in the type system — with an inline comment justifying why. Prefer explicit narrowing
  (`if (value == null) throw ...`) or optional chaining (`value?.field`).
- **Readonly arrays and tuples**: Array parameters and return types that MUST NOT be mutated
  by callers MUST be typed as `readonly T[]` or `ReadonlyArray<T>`. Mutable arrays MUST NOT
  be passed where immutability is a contract.
- **`structuredClone` for deep copies**: Deep copying of plain objects or arrays MUST use
  `structuredClone()`. Manual spread-based deep cloning or `JSON.parse(JSON.stringify(x))`
  are forbidden in new code.
- **Template literal types for string patterns**: String values that follow a structural
  pattern (e.g., route paths, event names) MUST be typed with template literal types
  (`type Route = \`/studies/\${string}\``) rather than plain `string`.

*Rationale*: Language-specific gotchas are responsible for a disproportionate share of
production bugs and developer confusion. Encoding them here as non-negotiable rules—rather
than leaving them to tribal knowledge—ensures consistent quality across AI-assisted and human
contributions.

## Code Quality Standards

The following gates apply at specification, planning, and implementation time:

| Standard | Requirement |
|----------|-------------|
| Cyclomatic complexity | MUST be ≤ 10 per function/method |
| Method length | SHOULD be ≤ 20 logical lines; MUST NOT exceed 40 |
| Class responsibility | MUST satisfy SRP — one primary reason to change |
| Code smell audit | MUST be performed before submitting any PR |
| Duplication | MUST be eliminated before merge; no copy-paste tolerance |
| Test coverage for refactors | MUST reach 100% on changed units before refactoring |
| Pattern justification | MUST be documented in plan or inline comment |
| Dependency direction | MUST flow inward (domain ← application ← infrastructure) |
| Pre-commit / linting | MUST pass `pre-commit run --all-files` clean after every phase |
| Unit test coverage | MUST be ≥ 85% line/branch coverage per module |
| Integration test coverage | MUST be ≥ 85% coverage across integrated paths |
| UI/UX test coverage | MUST cover all user-facing flows and component states |
| Mutation score | MUST be ≥ 85% mutants killed (mutmut / stryker) |
| Agent metamorphic tests | MUST be present in agents/tests/metamorphic/ for every agent |
| Agent deepeval pipeline | MUST exist in agent-eval/ for every agent at creation time |
| Ruff (Python) | MUST pass with line-length 100; no D203/D213; zero violations |
| MyPy (Python) | MUST pass strict mode, zero errors, python_version 3.14 |
| ESLint + Prettier (TS) | MUST pass; Prettier printWidth 100, singleQuote, trailingComma |
| TypeScript compiler | MUST pass strict + noUnusedLocals + noUnusedParameters |
| Audit fields | Every DB model MUST have created_at / updated_at columns |
| Settings pattern | Config MUST use Pydantic BaseSettings + lru_cache get_settings() |
| Logging | MUST use structlog; no print() in production paths |
| Docker health checks | Every compose service MUST have a healthcheck block |
| Documentation | All functions/methods MUST have Google-style (Python) or JSDoc (TS) doc comments; CLI handlers: brief command description only — no Args/Returns/params |
| React components | MUST be functional; MUST have named props interface; MUST be ≤ 100 JSX lines |
| React hooks | MUST follow Rules of Hooks (top-level only); complete dep arrays; no inline refs in deps |
| React state | MUST be treated as immutable; >3 related useState → useReducer |
| React effects | MUST return cleanup function when subscribing to any external resource |
| React.memo | SHOULD be applied to expensive pure children; MUST NOT be applied speculatively |
| useImperativeHandle | MUST use forwardRef + useImperativeHandle for imperative child APIs |
| react-hook-form | MUST use useWatch (not watch) for reactive field subscriptions in render |
| Vite env vars | Client vars MUST use VITE_ prefix; accessed via import.meta.env only |
| Python data objects | Domain entities MUST use Pydantic/dataclass/TypedDict — not plain dict |
| Python paths | MUST use pathlib.Path; os.path string manipulation forbidden in new code |
| Python exceptions | MUST catch specific types; bare except/except Exception forbidden |
| TypeScript any | MUST NOT appear; use unknown + narrowing at all external boundaries |
| TypeScript enum | MUST NOT be used; use string literal unions or as const object maps |
| TypeScript non-null (!) | MUST NOT be used without inline justification comment |

These standards apply to Python (backend, agents, db, researcher-mcp) and TypeScript
(frontend) code equally. Language-idiomatic implementations are preferred (e.g., Python
protocols over ABCs where duck typing suffices; TypeScript discriminated unions over class
hierarchies where pure data is involved).

## Development Workflow

The following workflow MUST be followed for every task in the implementation plan:

1. **Spec → Plan → Tasks**: Specification, planning, and task generation MUST check all
   nine Core Principles. Any violation found at planning time MUST surface as an explicit
   task (refactor or redesign) — not deferred to "Polish".

2. **Pre-implementation code review**: Before starting a task, examine the target file(s)
   and their callers. Document any Principle I–III and Principle IX violations in the task
   description.

3. **Refactoring-before-feature**: If refactoring is required to implement a feature cleanly,
   the refactoring sub-task MUST appear before the feature task in the task list.

4. **Test-first for refactoring**: Write or verify tests for the refactoring target, confirm
   they pass, confirm they would catch a regression, then execute the refactoring.

5. **Separate commits**: `refactor:` commits MUST NOT contain feature changes. `feat:` commits
   MUST NOT contain structural reorganisation.

6. **Checkpoints**: Each task phase ends with a quality gate. The following MUST all pass
   before a phase or task is marked complete:
   - `pre-commit run --all-files` (linting, formatting, and static analysis as configured
     in `.pre-commit-config.yaml`) MUST exit clean with zero violations.
   - Type checker (mypy / tsc) MUST report no errors.
   - Full test suite MUST pass with coverage ≥ 85%.
   - Mutation score MUST be ≥ 85% on changed modules.
   Pre-commit checks are non-negotiable gates — bypassing them with `--no-verify` is
   forbidden except in an emergency, and ANY such bypass MUST be documented in the PR with
   a follow-up remediation task.

7. **Agent tasks**: When implementing or modifying an agent, the task list MUST include:
   - Metamorphic test tasks in `agents/tests/metamorphic/`.
   - A deepeval evaluation pipeline task in `agent-eval/`.
   These tasks MUST be completed before the agent task is marked done.

8. **New dependencies**: Any addition of a new Python or TypeScript dependency MUST be
   reviewed against Principles VII, VIII, and IX. If the dependency introduces a tool that
   duplicates an already-approved tool (e.g., a second HTTP client, a second form library),
   the new dependency MUST NOT be merged without a constitution amendment approving the
   substitution or co-existence.

## Governance

This constitution supersedes all other informal practices, ad-hoc guidelines, and prior
verbal agreements within the SMS Researcher project. It is binding on all human contributors
and AI coding agents operating within this repository.

**Amendment procedure**:
- Amendments MUST be proposed as a pull request modifying this file.
- The version line MUST be incremented following semantic versioning (see below).
- Dependent templates (plan-template.md, spec-template.md, tasks-template.md) MUST be
  reviewed and updated in the same PR if the amendment affects them.
- A Sync Impact Report HTML comment MUST be prepended to this file on each amendment.

**Versioning policy**:
- MAJOR: Removal or redefinition of an existing principle.
- MINOR: Addition of a new principle, section, or materially expanded guidance.
- PATCH: Clarification, wording correction, or non-semantic refinement.

**Compliance review**:
- All PRs MUST verify compliance with Principles I–IX before merging.
- AI agents MUST apply the Constitution Check gate in plan.md before generating code.
- Complexity Tracking in plan.md MUST record any justified violations with rationale.
- Testing Discipline gates (Principle VI) MUST be verified in CI before merge approval.
- Toolchain gates (Principle VII) MUST be confirmed when adding or modifying any build,
  lint, type-check, or test configuration.
- Observability gates (Principle VIII) MUST be confirmed for any new service, model, or
  configuration module.
- Language-specific gates (Principle IX) MUST be checked during code review for all React,
  Python, and TypeScript code changes.

**Version**: 1.5.0 | **Ratified**: 2026-03-11 | **Last Amended**: 2026-03-12
