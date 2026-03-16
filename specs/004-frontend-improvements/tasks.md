# Tasks: Frontend Improvements

**Input**: Design documents from `/specs/004-frontend-improvements/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on in-progress tasks)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install new dependencies and create directory/file skeletons before any implementation begins.

- [x] T001 Add `pyotp>=2.9`, `qrcode[pil]>=7.4`, `cryptography>=42` to `backend/pyproject.toml` dependencies; run `uv sync --all-packages`
- [x] T002 [P] Add `@mui/material@^5.16`, `@mui/icons-material@^5.16`, `@emotion/react@^11`, `@emotion/styled@^11`, `swagger-ui-react@^5`, `@types/swagger-ui-react` to `frontend/package.json`; run `npm install` in `frontend/`
- [x] T003 [P] Create backend skeleton files: `backend/src/backend/api/v1/me/__init__.py`, `backend/src/backend/services/__init__.py` (if absent), stub files `backend/src/backend/core/encryption.py`, `backend/src/backend/core/totp.py`, `backend/src/backend/services/password_service.py`, `backend/src/backend/services/totp_service.py`, `backend/src/backend/services/audit_service.py`
- [x] T004 [P] Create frontend skeleton files: `frontend/src/theme/theme.ts`, `frontend/src/theme/ThemeContext.tsx`, `frontend/src/hooks/useColorMode.ts`, `frontend/src/hooks/useTotp.ts`, `frontend/src/services/preferences.ts`, `frontend/src/components/preferences/` (directory), `frontend/src/components/api-docs/` (directory)

**Checkpoint**: Dependencies installed; skeleton files in place for parallel Phase 2 work.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: DB schema, auth infrastructure, and MUI theme bootstrap that every user story depends on.

**⚠️ CRITICAL**: All user story phases require this phase to be complete first.

- [x] T005 Add `ThemePreference` enum (`light`, `dark`, `system`) and new columns to `User` in `db/src/db/models/users.py`: `theme_preference` (Enum, default `system`), `totp_enabled` (Boolean, default `False`), `totp_secret_encrypted` (Text, nullable), `totp_failed_attempts` (Integer, default `0`), `totp_locked_until` (DateTime tz, nullable), `token_version` (Integer, default `0`), `password_changed_at` (DateTime tz, server_default now), `updated_at` (DateTime tz, server_default now, onupdate now)
- [x] T006 [P] Create `BackupCode` model in `db/src/db/models/backup_codes.py`: columns `id`, `user_id` (FK→user CASCADE), `hashed_code` (String 255), `used_at` (DateTime tz nullable), `created_at`, `updated_at`; relationship back to User
- [x] T007 [P] Create `SecurityAuditEvent` model and `SecurityEventType` enum (`password_changed`, `totp_enabled`, `totp_disabled`, `backup_codes_regenerated`, `totp_locked`) in `db/src/db/models/security_audit.py`: columns `id`, `user_id` (FK→user CASCADE), `event_type` (Enum), `ip_address` (String 45, nullable), `created_at`, `updated_at`
- [x] T008 Export `BackupCode`, `SecurityAuditEvent`, `ThemePreference`, `SecurityEventType` from `db/src/db/models/__init__.py`; add `backup_codes` and `security_audit_events` relationships to `User` (depends on T005, T006, T007)
- [x] T009 Generate Alembic migration: `uv run alembic revision --autogenerate -m "add_user_security_preference_columns"` — review generated file to confirm `theme_preference_enum` type is created before the column
- [x] T010 [P] Generate Alembic migration: `uv run alembic revision --autogenerate -m "create_backup_code_table"` — verify FK and CASCADE in generated file
- [x] T011 [P] Generate Alembic migration: `uv run alembic revision --autogenerate -m "create_security_audit_event_table"` — verify `security_event_type_enum` creation and FK
- [x] T012 Apply all pending migrations: `uv run alembic upgrade head`; confirm zero errors (depends on T009, T010, T011)
- [x] T013 Update `backend/src/backend/core/auth.py`: (a) add `iat: datetime.now(UTC)` and `ver: user.token_version` claims to `create_access_token()`; (b) add `db: AsyncSession = Depends(get_db)` parameter to `get_current_user()`; (c) after JWT decode, load User from DB, verify `payload["ver"] == user.token_version` — raise 401 if mismatch; (d) reject tokens with `payload.get("stage") == "totp_required"` — raise 401 with detail "Authentication incomplete"
- [x] T014 Update unit tests in `backend/tests/test_auth.py` to cover: `create_access_token` now includes `iat` and `ver`; `get_current_user` rejects tokens with wrong `token_version`; `get_current_user` rejects partial tokens — run tests before proceeding (depends on T013)
- [x] T015 [P] Create `backend/src/backend/core/encryption.py`: `encrypt_secret(plaintext: str) -> str` and `decrypt_secret(ciphertext: str) -> str` using Fernet with a key derived via HKDF-SHA256 (32 bytes) from `settings.secret_key`; both functions use `get_settings()`; Google-style docstrings
- [x] T016 [P] Create `backend/src/backend/services/audit_service.py`: `async create_security_audit_event(db: AsyncSession, user_id: int, event_type: SecurityEventType, ip_address: str | None = None) -> SecurityAuditEvent` — inserts record and calls `logger.info("security_event", ...)` via structlog; Google-style docstring
- [x] T017 [P] Add `totp_lockout_attempts: int = 5` and `totp_lockout_minutes: int = 15` to `backend/src/backend/core/config.py` Settings class (Pydantic BaseSettings); update `.env.example` with commented defaults
- [x] T018 Implement `frontend/src/theme/theme.ts`: export `createAppTheme(mode: PaletteMode): Theme` using MUI `createTheme()` with primary/secondary palette; JSDoc comment
- [x] T019 Implement `frontend/src/theme/ThemeContext.tsx`: context type `{ mode: PaletteMode; setThemePreference: (pref: ThemePreference) => void }`; `ThemeProvider` component wraps children with MUI `ThemeProvider` + `CssBaseline`; export `useThemeContext()` hook; initial mode defaults to `'light'` (wired to user preference in T032)
- [x] T020 Update `frontend/src/main.tsx`: wrap `<App />` with `<ThemeProvider>` from `frontend/src/theme/ThemeContext.tsx` (depends on T019)
- [x] T021 Update `backend/src/backend/api/v1/auth.py` GET `/auth/me` response schema and handler to include `theme_preference` and `totp_enabled` fields from User (depends on T005)
- [x] T022 Update `frontend/src/services/api.ts`: in the login response handler, detect `requires_totp: true` and return a typed discriminated union `{ type: 'totp_required'; partial_token: string } | { type: 'success'; access_token: string; user_id: number; display_name: string }` — add Zod schema for each branch

**Checkpoint**: DB schema migrated; auth token_version guard active; MUI ThemeProvider wired; foundation ready for all four user story phases.

---

## Phase 3: User Story 1 — User Changes Password (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can change their password via `/preferences`. All other sessions are invalidated on success. Security event is logged.

**Independent Test**: Navigate to `/preferences` → Password section. Submit wrong current password → error. Submit new password that is same as current → error. Submit valid new password → success message. Log in with new password in a second session tab → old JWT rejected (401).

- [x] T023 [US1] Create `backend/src/backend/services/password_service.py`: `async change_password(db: AsyncSession, user_id: int, current_password: str, new_password: str, ip_address: str | None) -> None` — verify current password with `verify_password()`; check complexity (min 12 chars, uppercase, digit, special); reject if same as current; hash and store new password; increment `user.token_version`; set `user.password_changed_at`; call `audit_service.create_security_audit_event(..., SecurityEventType.PASSWORD_CHANGED)`; Google-style docstring; raise `HTTPException` for each failure mode
- [x] T024 [P] [US1] Write unit tests in `backend/tests/test_password_service.py` covering all 5 acceptance scenarios from spec.md: wrong current password → 400; complexity failure → 422 with requirements; same password → 400; confirmation mismatch (validated at request schema level); success → token_version incremented
- [x] T025 [US1] Create `backend/src/backend/api/v1/me/password.py`: `PUT /me/password` route; `PasswordChangeRequest(current_password: str, new_password: str)` Pydantic model; delegates to `password_service.change_password()`; extracts client IP from `Request`; returns `{"message": "Password changed successfully"}` on 200 (depends on T023)
- [x] T026 [US1] Register `me/` sub-router in `backend/src/backend/api/v1/router.py`; include `password`, `preferences`, and `totp` routers under `/me` prefix (depends on T025)
- [x] T027 [P] [US1] Write integration tests in `backend/tests/integration/test_me_password.py`: test PUT `/me/password` end-to-end against SQLite test DB for all acceptance scenarios including token_version increment
- [x] T028 [US1] Implement `frontend/src/services/preferences.ts`: `changePassword(currentPassword: string, newPassword: string): Promise<void>` — authenticated fetch to `PUT /api/v1/me/password`; Zod schema for error responses; throws typed error on 400/422 (depends on T022)
- [x] T029 [US1] Create `frontend/src/components/preferences/PasswordChangeForm.tsx`: react-hook-form + Zod schema (min 12 chars, uppercase, digit, special); `useWatch` on `newPassword` field for real-time complexity indicator; MUI `TextField`/`Button`/`Alert`; calls `changePassword()` service; displays success or field-level errors; ≤100 JSX lines; named props interface
- [x] T030 [US1] Create `frontend/src/components/preferences/UserPreferencesPage.tsx`: MUI `Tabs` (Password / Theme / Two-Factor Authentication); renders `PasswordChangeForm` in Password tab; placeholder panels for other tabs (wired in later phases); named props interface; ≤100 JSX lines
- [x] T031 [US1] Add `/preferences` route inside `RequireAuth` in `frontend/src/App.tsx` rendering `UserPreferencesPage`; add "Preferences" `ListItemButton` to `frontend/src/components/layout/SideNav.tsx`

**Checkpoint**: Password change fully functional end-to-end. `UserPreferencesPage` route live with Password tab operational.

---

## Phase 4: User Story 2 — User Selects Display Theme (Priority: P2)

**Goal**: Users can select Light, Dark, or System Default theme. Change takes effect immediately without page reload. Preference persists across sessions.

**Independent Test**: Log in → `/preferences` → Theme tab → select Dark → entire UI switches to dark theme instantly (no reload). Log out and back in → dark theme applies on load. Select System Default → switch OS to dark → app follows.

- [x] T032 [US2] Implement `frontend/src/hooks/useColorMode.ts`: accepts `themePref: ThemePreference`; maps `'light'`→`'light'`, `'dark'`→`'dark'`, `'system'`→ `matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'`; registers `useEffect` listener on `matchMedia` change event with cleanup return; returns resolved `PaletteMode`
- [x] T033 [US2] Update `frontend/src/theme/ThemeContext.tsx`: read `theme_preference` from auth store (from `/auth/me` response); call `useColorMode(pref)` to resolve mode; call `createAppTheme(mode)` and pass to MUI `ThemeProvider`; `setThemePreference` calls `updateTheme()` API then updates local auth state (depends on T032, T035)
- [x] T034 [US2] Create `backend/src/backend/api/v1/me/preferences.py`: `GET /me/preferences` returns `{theme_preference, totp_enabled}`; `PUT /me/preferences/theme` accepts `{theme: ThemePreference}`, validates enum, updates `user.theme_preference`, returns updated value; register in `router.py` (depends on T026)
- [x] T035 [P] [US2] Implement `frontend/src/services/preferences.ts` theme functions: `getPreferences()` returning `{theme_preference, totp_enabled}` with Zod schema; `updateTheme(theme: ThemePreference): Promise<void>` — PATCH to `PUT /api/v1/me/preferences/theme`
- [x] T036 [P] [US2] Write integration tests for `GET /me/preferences` and `PUT /me/preferences/theme` in `backend/tests/integration/test_me_preferences.py`
- [x] T037 [US2] Create `frontend/src/components/preferences/ThemeSelector.tsx`: MUI `ToggleButtonGroup` with Light/Dark/System options; calls `setThemePreference` from `useThemeContext()` on change; selected state reflects current preference; ≤100 JSX lines; named props interface
- [x] T038 [US2] Update `frontend/src/components/preferences/UserPreferencesPage.tsx`: render `ThemeSelector` in Theme tab
- [x] T039 [P] [US2] MUI migration — `frontend/src/components/auth/LoginPage.tsx`: replace all inline styles with MUI `Box`, `TextField`, `Button`, `Typography`, `Paper`; preserve all existing behaviour; update TOTP step (wired in T062) to use same MUI components
- [x] T040 [P] [US2] MUI migration — `frontend/src/components/layout/AppShell.tsx`: MUI `AppBar`, `Toolbar`, `Drawer`, `Box`; `frontend/src/components/layout/SideNav.tsx`: MUI `List`, `ListItem`, `ListItemButton`, `ListItemIcon`, `ListItemText`
- [x] T041 [P] [US2] MUI migration — `frontend/src/pages/StudiesPage.tsx`, `frontend/src/pages/StudyPage.tsx`: MUI `Container`, `Grid`, `Typography`, `Button`, `Card`
- [x] T042 [P] [US2] MUI migration — `frontend/src/pages/AdminPage.tsx`, `frontend/src/pages/ResultsPage.tsx`, `frontend/src/pages/ExtractionPage.tsx`: MUI `Container`, `Grid`, `Paper`, `Typography`
- [x] T043 [P] [US2] MUI migration — `frontend/src/components/studies/NewStudyWizard.tsx`: MUI `Stepper`, `Step`, `StepLabel`, `TextField`, `Button`, `Box`
- [x] T044 [P] [US2] MUI migration — `frontend/src/components/groups/GroupsPage.tsx`, `frontend/src/components/groups/GroupCard.tsx`: MUI `Grid`, `Card`, `CardContent`, `CardActions`, `Typography`, `Button`
- [x] T045 [P] [US2] MUI migration — `frontend/src/components/phase1/PICOForm.tsx`, `frontend/src/components/phase1/SeedPapers.tsx`: MUI `TextField`, `Select`, `Button`, `Box`
- [x] T046 [P] [US2] MUI migration — `frontend/src/components/phase2/CriteriaForm.tsx`, `PaperQueue.tsx`, `ReviewerPanel.tsx`, `SearchStringEditor.tsx`, `MetricsDashboard.tsx`, `TestRetest.tsx`: MUI `Table`, `TableBody`, `TableRow`, `TableCell`, `Card`, `TextField`, `Chip`
- [x] T047 [P] [US2] MUI migration — `frontend/src/components/phase3/ExtractionView.tsx`, `frontend/src/components/phase4/ValidityForm.tsx`, `frontend/src/components/phase5/QualityReport.tsx`: MUI `Paper`, `TextField`, `FormControl`, `Typography`
- [x] T048 [P] [US2] MUI migration — `frontend/src/components/results/ChartGallery.tsx`, `DomainModelViewer.tsx`, `ExportPanel.tsx`: MUI `Card`, `Button`, `Box` wrappers; D3 and Recharts internals unchanged
- [x] T049 [P] [US2] MUI migration — `frontend/src/components/shared/DiffViewer.tsx`, `PaperCard.tsx`, `frontend/src/components/jobs/JobProgressPanel.tsx`, `frontend/src/components/admin/JobRetryPanel.tsx`, `ServiceHealthPanel.tsx`: MUI `Paper`, `LinearProgress`, `IconButton`, `Chip`, `Alert`
- [x] T050 [P] [US2] Write vitest tests in `frontend/src/hooks/useColorMode.test.ts` (system pref resolution, matchMedia subscription/cleanup) and `frontend/src/components/preferences/ThemeSelector.test.tsx` (renders 3 options, fires setThemePreference on click)

**Checkpoint**: Full MUI migration complete; theme switching live. All components render correctly in both light and dark modes.

---

## Phase 5: User Story 3 — User Enables Two-Factor Authentication (Priority: P3)

**Goal**: Users can optionally enable TOTP 2FA. Setup flow presents QR code + backup codes. Login prompts for TOTP code when 2FA active. Brute-force lockout enforced. 2FA can be disabled with password + TOTP.

**Independent Test**: Enable 2FA, scan QR with authenticator app, confirm with live code → backup codes shown. Log out → log in → TOTP prompt appears → enter valid code → access granted. Enter wrong code 5× → lockout message. Use backup code → login succeeds and code is invalidated. Disable 2FA with password + TOTP → subsequent login has no TOTP step.

- [x] T051 Implement `backend/src/backend/core/totp.py`: `generate_secret() -> str` (pyotp.random_base32()); `get_provisioning_uri(secret: str, email: str, issuer: str) -> str`; `generate_qr_base64(uri: str) -> str` (qrcode PNG → base64); `verify_code(secret: str, code: str, valid_window: int = 1) -> bool` (pyotp.TOTP.verify); Google-style docstrings
- [x] T052 Implement `backend/src/backend/services/totp_service.py`: `initiate_2fa_setup(db, user)` → stores temp encrypted secret, returns `TOTPSetupData(qr_code_image, manual_key, issuer)`; `confirm_2fa_setup(db, user, totp_code)` → verifies code against temp secret, sets `totp_enabled=True`, generates and hashes 10 backup codes, returns plaintext codes list; `disable_2fa(db, user, password, totp_code)` → verifies both, clears totp fields, deletes backup codes, logs audit event; `regenerate_backup_codes(db, user, password, totp_code)` → verifies both, deletes old codes, generates new batch, logs audit event; `check_and_enforce_lockout(db, user)` → raises 429 if `totp_locked_until > now()`; `record_failed_attempt(db, user)` → increment `totp_failed_attempts`; lock if ≥ settings.totp_lockout_attempts; `verify_backup_code(db, user_id, code) -> bool` → finds unused code matching bcrypt hash, sets `used_at`
- [x] T053 [P] Write unit tests in `backend/tests/test_totp_service.py` covering: successful setup/confirm; wrong code on confirm → reject; lockout after N failures; lockout message contains expiry; backup code use → invalidated; disable with correct creds; regenerate clears old codes
- [x] T054 Create `backend/src/backend/api/v1/me/totp.py`: `POST /me/2fa/setup` (calls `initiate_2fa_setup`), `POST /me/2fa/confirm` (calls `confirm_2fa_setup`, returns backup codes), `POST /me/2fa/disable` (calls `disable_2fa`), `POST /me/2fa/backup-codes/regenerate` (calls `regenerate_backup_codes`); all request/response models match `contracts/api-contracts.md`; register in `router.py`
- [x] T055 Update `backend/src/backend/api/v1/auth.py`: modify `POST /auth/login` — after password verification, if `user.totp_enabled`, call `check_and_enforce_lockout`, then return partial token + `requires_totp: true` instead of full JWT; add `POST /auth/login/totp` endpoint — validate partial token `stage=="totp_required"`, call `check_and_enforce_lockout`, call `totp.verify_code()` (valid_window=1), if fail call `record_failed_attempt()`, if success reset failure counter and return full JWT; also attempt `verify_backup_code()` if TOTP fails (depends on T051, T052, T022)
- [x] T056 [P] Write integration tests for 2FA login flow in `backend/tests/integration/test_auth_totp.py`: login with 2FA enabled returns `requires_totp: true`; `/auth/login/totp` with valid code returns full JWT; invalid code increments counter; 5 failures → 429; backup code works once; partial token rejected by protected endpoints
- [x] T057 [P] Write integration tests for `/me/2fa/*` endpoints in `backend/tests/integration/test_me_totp.py`: setup → confirm → disable cycle; backup code regeneration invalidates old codes; `POST /me/2fa/confirm` with wrong code → 422
- [x] T058 Implement `frontend/src/hooks/useTotp.ts`: `useTotpSetup()` — TanStack Query mutation for `POST /me/2fa/setup`; `useTotpConfirm()` — mutation for `POST /me/2fa/confirm`; `useTotpDisable()` — mutation for `POST /me/2fa/disable`; `useBackupCodesRegenerate()` — mutation for `POST /me/2fa/backup-codes/regenerate`; all typed with Zod response schemas from `preferences.ts`
- [x] T059 Implement `frontend/src/services/preferences.ts` 2FA functions: `setup2fa()`, `confirm2fa(totpCode)`, `disable2fa(password, totpCode)`, `regenerateBackupCodes(password, totpCode)` — authenticated fetch calls matching `contracts/api-contracts.md`; Zod schemas for all responses (depends on T028)
- [x] T060 Create `frontend/src/components/preferences/TwoFactorSetupDialog.tsx`: `useReducer` managing 4 steps (`idle → qr_display → code_entry → backup_codes`); Step 1: initiate button calls `useTotpSetup()`; Step 2: MUI `Dialog` with base64 QR image + manual key; Step 3: TOTP code `TextField` + confirm calls `useTotpConfirm()`; Step 4: backup codes list with copy-all button + "I have saved these" acknowledge button; MUI `Stepper`; ≤100 JSX lines (split sub-components if needed); named props interface
- [x] T061 [P] Create `frontend/src/components/preferences/TwoFactorSettings.tsx`: shows current 2FA status badge; if disabled — "Enable 2FA" button opens `TwoFactorSetupDialog`; if enabled — "Disable 2FA" form (password + TOTP code) calling `useTotpDisable()`; "Regenerate Backup Codes" form calling `useBackupCodesRegenerate()`; MUI `Paper`/`Alert`/`Button`; ≤100 JSX lines; named props interface
- [x] T062 Update `frontend/src/components/preferences/UserPreferencesPage.tsx`: render `TwoFactorSettings` in Two-Factor Authentication tab (depends on T061)
- [x] T063 Update `frontend/src/components/auth/LoginPage.tsx`: after `api.login()` returns `{ type: 'totp_required' }`, show a second screen with TOTP code input (`TextField`) and submit button calling `POST /auth/login/totp`; on 429 show lockout duration message; on success complete normal login flow (store token, redirect)
- [x] T064 [P] Write vitest component tests in `frontend/src/components/preferences/TwoFactorSetupDialog.test.tsx` and `TwoFactorSettings.test.tsx`: step transitions, mutation calls, error display, backup code acknowledge gate

**Checkpoint**: 2FA fully functional end-to-end. Login prompts TOTP when enabled. Brute-force lockout active.

---

## Phase 6: User Story 4 — Developer Browses API Documentation (Priority: P4)

**Goal**: Authenticated users can access an interactive API documentation page at `/api-docs`. The schema is auto-generated and up-to-date. Unauthenticated access redirects to login.

**Independent Test**: Navigate to `/api-docs` while logged in → Swagger UI loads listing all backend API endpoints. Log out → navigate to `/api-docs` → redirected to login. Add a new test endpoint in backend → refresh `/api-docs` → new endpoint appears with no manual documentation step.

- [x] T065 Update `backend/src/backend/main.py`: set `openapi_url=None`, `docs_url=None`, `redoc_url=None` on `FastAPI(...)` instantiation to disable default unauthenticated docs endpoints
- [x] T066 Create `backend/src/backend/api/v1/openapi_route.py`: `GET /openapi.json` route requiring `current_user: CurrentUser = Depends(get_current_user)` (full JWT); returns `JSONResponse(app.openapi())`; register in `router.py` (depends on T065)
- [x] T067 [P] Write integration test in `backend/tests/integration/test_openapi_auth.py`: unauthenticated `GET /api/v1/openapi.json` → 401; authenticated → 200 with valid OpenAPI schema object containing at least one path
- [x] T068 Create `frontend/src/components/api-docs/APIDocsPage.tsx`: TanStack Query `useQuery` fetching `GET /api/v1/openapi.json` with `Authorization` header from auth store; renders `<SwaggerUI spec={data} />` from `swagger-ui-react`; MUI `CircularProgress` loading state; MUI `Alert` error state; ≤100 JSX lines; named props interface
- [x] T069 Add `/api-docs` route inside `RequireAuth` in `frontend/src/App.tsx` rendering `APIDocsPage`; add "API Docs" `ListItemButton` to `frontend/src/components/layout/SideNav.tsx` (depends on T040, T068)

**Checkpoint**: API docs page live, authenticated, and auto-updating with backend changes.

---

## Final Phase: Polish, Tests & Documentation

- [x] T070 [P] Write Playwright e2e test in `frontend/e2e/preferences-password.spec.ts`: wrong current password → error message visible; valid password change → success; old JWT rejected on next protected request
- [x] T071 [P] Write Playwright e2e test in `frontend/e2e/two-factor-auth.spec.ts`: enable 2FA full flow → backup codes shown; logout + login → TOTP prompt; wrong code 5× → lockout banner; backup code login; disable 2FA
- [x] T072 [P] Write Playwright e2e test in `frontend/e2e/theme.spec.ts`: select Dark → no page reload + dark theme active; logout + login → dark theme persists; select System Default → app respects OS preference
- [x] T073 [P] Write Playwright e2e test in `frontend/e2e/api-docs.spec.ts`: logged-in user sees Swagger UI; unauthenticated request to `/api-docs` redirects to login
- [x] T074 Run full Python coverage: `uv run pytest backend/tests/ db/tests/ --cov=src/backend --cov=src/db --cov-report=term-missing --cov-fail-under=85`; resolve any gaps
- [x] T075 [P] Run full frontend coverage: `cd frontend && npm run test:coverage`; verify ≥85% threshold passes (vite.config.ts enforces)
- [x] T076 [P] Run Playwright e2e suite against Docker Compose stack: `cd frontend && npx playwright test`; all e2e tests green
- [x] T077 [P] Update `CLAUDE.md` Active Technologies section: add `pyotp`, `qrcode[pil]`, `cryptography (Fernet)`, `MUI v5`, `swagger-ui-react` entries for feature `004-frontend-improvements`
- [x] T078 [P] Update root `README.md`: document `/preferences` and `/api-docs` frontend routes; note MUI migration complete; note 2FA and password change features
- [x] T079 [P] Update root `CHANGELOG.md`: add `## [Unreleased]` entries for password change, 2FA, theme selector, API docs page, MUI migration
- [x] T080 [P] Update `frontend/CHANGELOG.md` with all frontend additions (MUI migration, preferences page, theme, 2FA UI, API docs page)
- [x] T081 [P] Update `backend/CHANGELOG.md` with all backend additions (password change endpoint, 2FA endpoints, authenticated openapi.json, token_version, security audit log)

---

## Dependencies

```
Phase 1 (T001–T004)
  └─► Phase 2 (T005–T022)
        ├─► Phase 3: US1 Password Change (T023–T031)
        │     └─► Phase 4: US2 Theme (T032–T050) [UserPreferencesPage extended]
        │           └─► Phase 5: US3 2FA (T051–T064) [UserPreferencesPage extended]
        └─► Phase 6: US4 API Docs (T065–T069) [independent of US1–US3]
              └─► Final Phase (T070–T081)
```

**Parallel opportunities per phase**:
- Phase 2: T006, T007 parallel; T010, T011 parallel; T015, T016, T017 parallel
- Phase 3: T024, T027 parallel with T023; T027, T029 parallel after T023
- Phase 4: T035, T036, T039–T049 all parallel after T032; MUI component migrations fully parallel with each other
- Phase 5: T053, T056, T057, T064 parallel; T058–T061 parallel after T059
- Phase 6: T067 parallel with T066; T069 after T068+T040
- Final: T070–T073 parallel; T075–T081 parallel

---

## Implementation Strategy

**MVP (Phase 3 only — ~2 days)**: Deliver `PUT /me/password` backend + `PasswordChangeForm` frontend. Session invalidation via `token_version`. Security audit log. Independently testable and shippable.

**Increment 2 (Phase 4 — ~3 days)**: Add theme selector + full MUI migration. Theme preference persists. All components use MUI design system.

**Increment 3 (Phase 5 — ~4 days)**: Full 2FA with TOTP, QR setup, backup codes, login flow update, brute-force lockout.

**Increment 4 (Phase 6 — ~0.5 day)**: Authenticated API docs page. Lowest risk, highest developer value.

**Total tasks**: 81
**Parallelisable tasks**: 47 [P]
**User story breakdown**: US1 (9 tasks), US2 (19 tasks incl. MUI migration), US3 (14 tasks), US4 (5 tasks), Foundational (22 tasks), Final (12 tasks)
