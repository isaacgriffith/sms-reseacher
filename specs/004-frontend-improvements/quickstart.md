# Developer Quickstart: Frontend Improvements (004)

**Date**: 2026-03-16
**Branch**: `004-frontend-improvements`

---

## Prerequisites

- Python 3.14 with `uv` installed
- Node 20 LTS with `npm` installed
- Docker (for PostgreSQL + Redis in integration tests)
- Follow the main `CLAUDE.md` environment setup first

---

## New Dependencies

### Backend

```bash
# Add to backend/pyproject.toml dependencies, then sync
uv add --package sms-backend "pyotp>=2.9" "qrcode[pil]>=7.4" "cryptography>=42"
uv sync --all-packages
```

### Frontend

```bash
cd frontend
npm install @mui/material@^5.16 @mui/icons-material@^5.16 \
  @emotion/react@^11 @emotion/styled@^11 \
  swagger-ui-react@^5
# Type stubs (if not bundled with swagger-ui-react)
npm install -D @types/swagger-ui-react
cd ..
```

---

## Key New Files

### Backend

| File | Purpose |
|------|---------|
| `backend/src/backend/core/totp.py` | TOTP secret generation, verification, QR code rendering |
| `backend/src/backend/core/encryption.py` | Fernet encrypt/decrypt for TOTP secret storage |
| `backend/src/backend/services/password_service.py` | Password change logic, token version increment |
| `backend/src/backend/services/totp_service.py` | 2FA setup/confirm/disable/backup code logic |
| `backend/src/backend/services/audit_service.py` | Security audit event creation via structlog |
| `backend/src/backend/api/v1/me/password.py` | `PUT /me/password` route |
| `backend/src/backend/api/v1/me/preferences.py` | `GET/PUT /me/preferences` routes |
| `backend/src/backend/api/v1/me/totp.py` | 2FA routes under `/me/2fa/` |
| `backend/src/backend/api/v1/openapi_route.py` | `GET /openapi.json` with JWT guard |
| `db/src/db/models/backup_codes.py` | `BackupCode` model |
| `db/src/db/models/security_audit.py` | `SecurityAuditEvent` model |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/theme/theme.ts` | MUI theme factory (`createTheme`) |
| `frontend/src/theme/ThemeContext.tsx` | Context + provider; resolves user pref to MUI PaletteMode |
| `frontend/src/hooks/useColorMode.ts` | Reads preference, subscribes to `matchMedia` for system mode |
| `frontend/src/components/preferences/UserPreferencesPage.tsx` | Preferences page container |
| `frontend/src/components/preferences/PasswordChangeForm.tsx` | Password change form |
| `frontend/src/components/preferences/TwoFactorSettings.tsx` | 2FA enable/disable UI |
| `frontend/src/components/preferences/TwoFactorSetupDialog.tsx` | QR code + confirm + backup codes dialog |
| `frontend/src/components/preferences/ThemeSelector.tsx` | Light/Dark/System selector |
| `frontend/src/components/api-docs/APIDocsPage.tsx` | Swagger UI wrapper |
| `frontend/src/services/preferences.ts` | API calls for preferences + 2FA |

---

## Database Migrations

After implementing the model changes:

```bash
# Generate migrations (run from repo root)
uv run alembic revision --autogenerate -m "add_user_security_preference_columns"
uv run alembic revision --autogenerate -m "create_backup_code_table"
uv run alembic revision --autogenerate -m "create_security_audit_event_table"

# Apply
uv run alembic upgrade head
```

Review each generated migration before applying to ensure enum types are created before columns that use them.

---

## Running Tests

```bash
# Backend — all packages
uv run pytest backend/tests/ db/tests/ \
  --cov=src/backend --cov=src/db \
  --cov-report=term-missing \
  --cov-fail-under=85

# Frontend unit + component tests
cd frontend && npm test

# E2e (requires full stack)
cp .env.example .env  # set DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY
docker compose up -d
cd frontend && PLAYWRIGHT_BASE_URL=http://localhost:5173 npx playwright test
```

---

## Environment Variables

No new required env vars. Encryption key is derived from the existing `SECRET_KEY`.

Optional:
```
TOTP_ISSUER_NAME=SMS Researcher   # Displayed in authenticator app (default: app_name from settings)
TOTP_LOCKOUT_ATTEMPTS=5           # Failed attempts before lockout (default: 5)
TOTP_LOCKOUT_MINUTES=15           # Lockout duration (default: 15)
```

These should be added to `backend/src/backend/core/config.py` as `Pydantic BaseSettings` fields with defaults.

---

## Verifying the Feature

### Theme
1. Log in → navigate to `/preferences` → select Dark
2. Verify application switches immediately without page reload
3. Log out and back in → verify dark theme applies on load

### Password Change
1. Navigate to `/preferences` → Password section
2. Submit with wrong current password → verify rejection
3. Submit with valid new password → verify success + re-login required

### 2FA
1. Navigate to `/preferences` → Two-Factor Authentication → Enable
2. Scan QR code with Google Authenticator or Authy
3. Enter valid code → verify backup codes displayed
4. Log out → log in → verify TOTP prompt appears
5. Use a backup code → verify it works once and is invalidated

### API Documentation
1. Navigate to `/api-docs` (must be logged in)
2. Verify all backend endpoints are listed
3. Log out → navigate to `/api-docs` → verify redirect to login
