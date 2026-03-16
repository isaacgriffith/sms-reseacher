# Implementation Plan: Frontend Improvements

**Branch**: `004-frontend-improvements` | **Date**: 2026-03-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-frontend-improvements/spec.md`

---

## Summary

Deliver four independent improvements to the SMS Researcher application: (1) a user preferences section (password change, TOTP-based 2FA, display theme); (2) a full migration of all frontend components to Material UI v5; (3) an authenticated API documentation page powered by Swagger UI; and (4) a backend JWT session-invalidation mechanism tied to password changes. The backend gains three new endpoints groups (`/me/password`, `/me/preferences`, `/me/2fa/*`), two new DB models (`BackupCode`, `SecurityAuditEvent`), and several new columns on `User`. The frontend gains a `ThemeProvider`, a preferences page, and replaces all inline-style components with MUI equivalents.

---

## Technical Context

**Language/Version**: Python 3.14 (backend, db); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**: FastAPI + Pydantic v2, SQLAlchemy 2.0+ async, Alembic, React 18, MUI v5, react-hook-form + Zod, TanStack Query v5, pyotp, qrcode[pil], cryptography (Fernet), swagger-ui-react
**Storage**: PostgreSQL 16 (production/Docker Compose); SQLite + aiosqlite (unit/integration tests)
**Testing**: pytest + asyncio_mode=auto (backend); vitest + @testing-library/react (frontend); Playwright (e2e)
**Target Platform**: Web application (browser frontend + Linux server backend)
**Performance Goals**: Theme switch <500 ms; session invalidation <60 s after password change; TOTP verification within ±30 s clock drift window
**Constraints**: No Redis dependency for session invalidation; JWT remains stateless (token_version column); no new infrastructure services
**Scale/Scope**: ~30 frontend components to migrate; 3 new backend service modules; 3 Alembic migrations; ~12 new API endpoints

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | Pass | Each new service file (password_service, totp_service, audit_service) has a single responsibility |
| SOLID — extension points exist (OCP) where variation expected | Pass | ThemeContext and encryption module are interface-stable; swapping providers doesn't touch callers |
| Structural — no DRY violations (duplication) | Pass | Shared `audit_service` centralises all security event writing; shared `encryption.py` owns Fernet logic |
| Structural — no YAGNI violations (speculative generality) | Pass | No hooks or abstractions beyond current requirements |
| Code clarity — no long methods (>20 lines) in touched code | Pass | Service functions are scoped to single operations; enforce during implementation |
| Code clarity — no switch/if-chain smells in touched code | Pass | Theme resolution uses a dict map, not if-chain; event type is an enum |
| Code clarity — no common code smells identified | Pass | Pre-implementation review completed against existing auth.py and users.py |
| Refactoring — pre-implementation review completed | Pass | `get_current_user` signature change (add `db` param) is backward-compatible via FastAPI `Depends` |
| Refactoring — any found refactors added to task list with tests | Pass | token_version check added to existing `get_current_user` — tests updated accordingly |
| GRASP/patterns — responsibility assignments reviewed | Pass | Controllers → Services → DB layer maintained; no business logic in route handlers |
| Test coverage — existing tests pass; refactor tests written first | Pass | Existing auth tests must be updated before adding token_version logic |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | Pass | pyotp, qrcode[pil], cryptography, MUI v5, swagger-ui-react are all approved additions |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | Pass | All new routes use `async def`, `Depends()`, `HTTPException`; SQLAlchemy 2.0 Mapped[] style |
| Observability (VIII) — new models have audit fields + structlog used | Pass | BackupCode and SecurityAuditEvent have `created_at`/`updated_at`; User gains `updated_at`; audit_service uses structlog |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | Pass | TOTP lockout constants added to existing Settings class |
| Infrastructure (VIII) — Docker services have healthchecks if added | N/A | No new Docker services introduced |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | Pass | All new components follow this constraint; enforce during MUI migration |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | Pass | useColorMode and useTotp designed with stable dep arrays |
| Language (IX) — No React state mutation; no array-index keys in lists | Pass | Backup codes list uses code value as key (unique per batch) |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | Pass | TwoFactorSetupDialog uses useReducer for setup step state |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | Pass | useColorMode's matchMedia listener is cleaned up on unmount |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs | Pass | No speculative React.memo; no imperative child APIs in scope |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | Pass | All react-hook-form usage in new forms uses useWatch |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | Pass | No new env vars exposed to frontend bundle |
| Language (IX) — Python: no plain dict for domain data; pathlib used | Pass | All service return types use Pydantic response models |
| Language (IX) — Python: no mutable defaults; specific exception handling | Pass | Service functions raise HTTPException with specific status codes |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | Pass | ThemePreference represented as `'light' | 'dark' | 'system'` string literal union |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | Pass | API responses validated with Zod schemas in services/preferences.ts |
| Code clarity — all functions/methods/classes have doc comments | Pass | Enforce during implementation; all new Python uses Google-style, TS uses JSDoc |
| Feature completion docs (X) — CLAUDE.md, README, CHANGELOG updates in task list | Pass | TDOC tasks included in tasks.md |

---

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-improvements/
├── plan.md              # This file
├── research.md          # Phase 0 — architectural decisions
├── data-model.md        # Phase 1 — entity definitions and migrations
├── quickstart.md        # Phase 1 — developer setup
├── contracts/
│   └── api-contracts.md # Phase 1 — endpoint request/response shapes
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code Layout

```text
backend/
├── src/backend/
│   ├── api/v1/
│   │   ├── auth.py                   # MODIFIED — 2FA partial token in login
│   │   ├── me/
│   │   │   ├── __init__.py           # NEW — sub-router registration
│   │   │   ├── password.py           # NEW — PUT /me/password
│   │   │   ├── preferences.py        # NEW — GET/PUT /me/preferences/theme
│   │   │   └── totp.py               # NEW — POST /me/2fa/{setup,confirm,disable,backup-codes/regenerate}
│   │   ├── openapi_route.py          # NEW — GET /openapi.json with JWT guard
│   │   └── router.py                 # MODIFIED — register me/ and openapi sub-routers
│   ├── core/
│   │   ├── auth.py                   # MODIFIED — token_version check, partial token, db param
│   │   ├── encryption.py             # NEW — Fernet encrypt/decrypt for TOTP secret
│   │   └── totp.py                   # NEW — pyotp wrappers, QR code generation
│   ├── services/
│   │   ├── password_service.py       # NEW — password change + token_version increment
│   │   ├── totp_service.py           # NEW — 2FA lifecycle + backup code management
│   │   └── audit_service.py          # NEW — SecurityAuditEvent creation
│   └── main.py                       # MODIFIED — disable default /docs; /openapi.json

db/
└── src/db/
    ├── models/
    │   ├── users.py                  # MODIFIED — add columns, ThemePreference enum
    │   ├── backup_codes.py           # NEW — BackupCode model
    │   ├── security_audit.py         # NEW — SecurityAuditEvent model
    │   └── __init__.py               # MODIFIED — export new models and enums
    └── alembic/versions/
        ├── xxxx_add_user_security_preference_columns.py  # NEW
        ├── xxxx_create_backup_code_table.py              # NEW
        └── xxxx_create_security_audit_event_table.py    # NEW

frontend/
└── src/
    ├── App.tsx                       # MODIFIED — add /preferences and /api-docs routes; ThemeProvider wrap
    ├── main.tsx                      # MODIFIED — wrap with ThemeProvider
    ├── theme/
    │   ├── theme.ts                  # NEW — MUI createTheme factory
    │   └── ThemeContext.tsx          # NEW — context, provider, useThemeContext hook
    ├── hooks/
    │   ├── useColorMode.ts           # NEW — system/light/dark resolution + matchMedia listener
    │   └── useTotp.ts                # NEW — 2FA setup/confirm mutation hooks
    ├── components/
    │   ├── auth/LoginPage.tsx        # MODIFIED — MUI migration + 2FA TOTP step
    │   ├── layout/
    │   │   ├── AppShell.tsx          # MODIFIED — MUI migration + preferences link
    │   │   └── SideNav.tsx           # MODIFIED — MUI migration
    │   ├── preferences/
    │   │   ├── UserPreferencesPage.tsx    # NEW
    │   │   ├── PasswordChangeForm.tsx     # NEW
    │   │   ├── TwoFactorSettings.tsx      # NEW
    │   │   ├── TwoFactorSetupDialog.tsx   # NEW
    │   │   └── ThemeSelector.tsx          # NEW
    │   ├── api-docs/
    │   │   └── APIDocsPage.tsx       # NEW — swagger-ui-react wrapper
    │   └── [all existing components] # MODIFIED — MUI migration (inline styles → MUI)
    ├── pages/
    │   └── [all existing pages]      # MODIFIED — MUI migration
    └── services/
        ├── api.ts                    # MODIFIED — handle requires_totp response in login
        └── preferences.ts            # NEW — typed fetch wrappers for preferences + 2FA endpoints
```

---

## Complexity Tracking

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| `get_current_user` gains DB param | Refactor | Required for token_version security check; all callers use `Depends()` so no manual call-site changes needed |
| MUI migration touches ~30 components | Scope | Specified in requirements (FR-022–024); no alternative; mitigated by systematic component-by-component approach |
| TwoFactorSetupDialog multi-step state | UI complexity | 4-step wizard (initiate → QR → confirm → backup codes); managed with `useReducer` to avoid >3 useState — constitution compliant |
| Fernet key derivation from SECRET_KEY | Security design | Avoids new secret management; uses HKDF-SHA256 which is standard and safe; documented in research.md Decision 2 |
