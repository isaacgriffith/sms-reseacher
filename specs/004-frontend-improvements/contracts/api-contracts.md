# API Contracts: Frontend Improvements (004)

**Date**: 2026-03-16
**Base path**: `/api/v1`
**Auth**: Bearer JWT in `Authorization: Bearer <token>` header (unless noted)

---

## Modified Endpoints

### POST /auth/login

Modified to support 2FA-enabled accounts.

**Request** (unchanged):
```json
{ "username": "user@example.com", "password": "string" }
```

**Response — 2FA disabled** (unchanged):
```json
{
  "access_token": "<full JWT>",
  "token_type": "bearer",
  "user_id": 42,
  "display_name": "Alice"
}
```

**Response — 2FA enabled** (new):
```json
{
  "requires_totp": true,
  "partial_token": "<short-lived JWT with stage=totp_required>"
}
```
HTTP 200 in both cases. Frontend detects `requires_totp: true` and routes to TOTP entry screen.

---

### GET /auth/me

Returns additional user fields.

**Response** (extended):
```json
{
  "user_id": 42,
  "email": "user@example.com",
  "display_name": "Alice",
  "theme_preference": "system",
  "totp_enabled": false,
  "memberships": [...]
}
```

New fields: `theme_preference` (`"light" | "dark" | "system"`), `totp_enabled` (`boolean`).

---

## New Endpoints

### POST /auth/login/totp

Complete login for 2FA-enabled accounts.

**Auth**: None (unauthenticated endpoint)

**Request**:
```json
{
  "partial_token": "<partial JWT from /auth/login>",
  "totp_code": "123456"
}
```

**Response 200**:
```json
{
  "access_token": "<full JWT>",
  "token_type": "bearer",
  "user_id": 42,
  "display_name": "Alice"
}
```

**Response 401** — invalid/expired partial token:
```json
{ "detail": "Invalid or expired authentication token" }
```

**Response 422** — invalid TOTP code:
```json
{ "detail": "Invalid TOTP code" }
```

**Response 429** — account locked after repeated failures:
```json
{
  "detail": "Too many failed attempts. Account locked until 2026-03-16T14:30:00Z"
}
```

---

### PUT /me/password

Change the authenticated user's password.

**Auth**: Full JWT required

**Request**:
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response 200**:
```json
{ "message": "Password changed successfully" }
```

**Response 400** — current password incorrect:
```json
{ "detail": "Current password is incorrect" }
```

**Response 400** — new password same as current:
```json
{ "detail": "New password must differ from current password" }
```

**Response 422** — complexity requirements not met:
```json
{
  "detail": "Password does not meet complexity requirements",
  "requirements": {
    "min_length": 12,
    "requires_uppercase": true,
    "requires_digit": true,
    "requires_special": true
  }
}
```

**Side effect**: `user.token_version` incremented; all prior JWTs invalidated.

---

### GET /me/preferences

Retrieve the current user's preferences.

**Auth**: Full JWT required

**Response 200**:
```json
{
  "theme_preference": "system",
  "totp_enabled": false
}
```

---

### PUT /me/preferences/theme

Update display theme preference.

**Auth**: Full JWT required

**Request**:
```json
{ "theme": "dark" }
```
Valid values: `"light"`, `"dark"`, `"system"`

**Response 200**:
```json
{ "theme_preference": "dark" }
```

**Response 422** — invalid theme value:
```json
{ "detail": "theme must be one of: light, dark, system" }
```

---

### POST /me/2fa/setup

Begin 2FA enrollment. Generates a TOTP secret (not yet active).

**Auth**: Full JWT required

**Request**: Empty body `{}`

**Response 200**:
```json
{
  "qr_code_image": "<base64-encoded PNG>",
  "manual_key": "JBSWY3DPEHPK3PXP",
  "issuer": "SMS Researcher"
}
```
The `qr_code_image` encodes the `otpauth://` URI. `manual_key` is the human-readable TOTP secret for manual app entry.

---

### POST /me/2fa/confirm

Confirm 2FA enrollment with a valid TOTP code. Activates 2FA and returns backup codes.

**Auth**: Full JWT required

**Request**:
```json
{ "totp_code": "123456" }
```

**Response 200**:
```json
{
  "backup_codes": [
    "A1B2C3D4E5",
    "F6G7H8I9J0",
    "..."
  ]
}
```
10 codes returned. Each is a 10-character uppercase alphanumeric string. Display once — not retrievable again.

**Response 422** — invalid or expired TOTP code:
```json
{ "detail": "Invalid TOTP code. Please try again." }
```

**Response 409** — 2FA already active:
```json
{ "detail": "Two-factor authentication is already enabled" }
```

---

### POST /me/2fa/disable

Disable 2FA. Requires current password and a valid TOTP code.

**Auth**: Full JWT required

**Request**:
```json
{
  "password": "string",
  "totp_code": "123456"
}
```

**Response 200**:
```json
{ "message": "Two-factor authentication disabled" }
```

**Response 400** — incorrect password:
```json
{ "detail": "Current password is incorrect" }
```

**Response 422** — invalid TOTP code:
```json
{ "detail": "Invalid TOTP code" }
```

---

### POST /me/2fa/backup-codes/regenerate

Regenerate backup codes. Invalidates all previous codes.

**Auth**: Full JWT required

**Request**:
```json
{
  "password": "string",
  "totp_code": "123456"
}
```

**Response 200**:
```json
{
  "backup_codes": [
    "A1B2C3D4E5",
    "..."
  ]
}
```
10 new codes. All previous codes are permanently invalidated.

**Response 400** — incorrect password:
```json
{ "detail": "Current password is incorrect" }
```

**Response 422** — invalid TOTP code:
```json
{ "detail": "Invalid TOTP code" }
```

---

### GET /openapi.json

Returns the application's OpenAPI schema.

**Auth**: Full JWT required

**Response 200**: Standard OpenAPI 3.x JSON schema object.

**Response 401**: Redirected to login (frontend handles; raw endpoint returns 401).

---

## Frontend Route Additions

| Route | Component | Auth | Description |
|-------|-----------|------|-------------|
| `/preferences` | `UserPreferencesPage` | Required | Password, 2FA, and theme settings |
| `/api-docs` | `APIDocsPage` | Required | Swagger UI for backend API |

## Error Response Shape (all endpoints)

All error responses follow FastAPI's standard shape:
```json
{ "detail": "Human-readable error message" }
```
or for validation errors:
```json
{
  "detail": [
    { "loc": ["body", "field"], "msg": "message", "type": "type" }
  ]
}
```
