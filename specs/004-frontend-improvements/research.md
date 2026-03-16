# Research: Frontend Improvements (004)

**Date**: 2026-03-16
**Branch**: `004-frontend-improvements`

---

## Decision 1: Session Invalidation Strategy

**Decision**: Add `token_version: int` (default 0) to the `User` model. Embed a `ver` claim in every JWT. On password change, increment `user.token_version`. `get_current_user` loads the User from DB and rejects tokens where `payload.ver != user.token_version`.

**Rationale**: The current auth is stateless JWT stored in `localStorage`. A Redis token blocklist (JTI approach) adds an infrastructure dependency. Storing `password_changed_at` and comparing against `iat` is equivalent but requires timestamp arithmetic across timezones. `token_version` is an integer comparison, cleaner, and also enables revocation for other future security events. The DB lookup (PK lookup on User) is required anyway for the 2FA `token_version` check and is a negligible overhead for a research tool.

**Alternatives considered**:
- **JTI blocklist in Redis**: Rejected — requires Redis in all environments including CI; adds infrastructure complexity disproportionate to scale.
- **`password_changed_at` + `iat` comparison**: Rejected — timezone handling complexity; functionally equivalent to `token_version`.
- **Short-lived tokens with refresh tokens**: Rejected — out of scope; requires session management infrastructure not present in the codebase.

**Side effect**: `get_current_user` in `backend/core/auth.py` gains a `db: AsyncSession` parameter via `Depends(get_db)`. All existing protected routes inject it via `Depends(get_current_user)` so no call-site changes are needed.

---

## Decision 2: TOTP Secret Storage

**Decision**: Encrypt the TOTP secret with Fernet symmetric encryption (`cryptography` library) using a key derived from `settings.secret_key` via HKDF-SHA256 (32 bytes). Store the encrypted value as a base64 string in `user.totp_secret_encrypted`.

**Rationale**: TOTP secrets in plaintext in the database create a catastrophic breach risk (an attacker with DB access could immediately generate valid codes for all 2FA-enabled users). Fernet is simple, authenticated (AEAD), and already available via the `cryptography` package (a transitive dependency of `bcrypt`). Key derivation from `settings.secret_key` avoids a new secret management requirement.

**Alternatives considered**:
- **Database-level encryption (pgcrypto)**: Rejected — tied to PostgreSQL; breaks SQLite test parity.
- **Plaintext storage**: Rejected — unacceptable security posture.
- **Dedicated KMS/HSM**: Rejected — over-engineering for a research tool; out of scope.

---

## Decision 3: Backup Code Storage

**Decision**: Generate 10 backup codes of 10 uppercase alphanumeric characters each (approx. 51 bits of entropy). Hash each code with bcrypt using `hash_password()` (existing util). Store in a new `BackupCode` model with `user_id` FK, `hashed_code`, `used_at` (nullable), `created_at`, `updated_at`.

**Rationale**: Hashing backup codes prevents an attacker with DB read access from using them. 10 codes × 10 chars is consistent with industry conventions (GitHub, Google). bcrypt reuse avoids a new hashing dependency. The `BackupCode` model is a separate entity to allow independent invalidation and clean DB semantics.

**Alternatives considered**:
- **SHA-256 hashed codes**: Rejected — SHA-256 is fast and brute-forceable; bcrypt's cost factor makes offline attacks impractical.
- **Storing codes inline in User model (JSON array)**: Rejected — violates normalisation; harder to mark individual codes as used without full array rewrite.

---

## Decision 4: Two-Factor Login Flow

**Decision**: Two-step login. Step 1: `POST /api/v1/auth/login` — if user has 2FA enabled, returns a short-lived "partial JWT" with claim `{"sub": user_id, "stage": "totp_required", "exp": now+5min}` instead of a full token. The HTTP response also includes `{"requires_totp": true}`. Step 2: `POST /api/v1/auth/login/totp` — accepts `{partial_token, totp_code}`, validates both, returns a full JWT. `get_current_user` rejects tokens with `stage == "totp_required"`.

**Rationale**: Avoids server-side session storage for the intermediate state. The partial JWT is short-lived (5 minutes), signed, and explicitly scoped to the 2FA step via the `stage` claim. This pattern is self-contained and requires no infrastructure changes.

**Alternatives considered**:
- **Server-side TOTP challenge (UUID stored in cache)**: Rejected — requires Redis or DB cache table; adds infrastructure for a short-lived state.
- **Single-step login returning 202 with a challenge ID**: Rejected — requires a new session concept incompatible with the current stateless architecture.

---

## Decision 5: API Documentation Authentication

**Decision**: Disable FastAPI's default `/openapi.json`, `/docs`, and `/redoc` routes. Expose a custom `GET /api/v1/openapi.json` endpoint that requires a valid JWT and returns `app.openapi()`. In the frontend, add an `APIDocsPage` component that fetches this JSON via TanStack Query and renders it with `swagger-ui-react` (npm package). The page is protected by the existing `RequireAuth` wrapper.

**Rationale**: FastAPI's default schema endpoint has no auth mechanism. A custom route wraps it behind the existing JWT guard. Using `swagger-ui-react` in the frontend is the cleanest approach: the user's auth token is available in the browser context and can be injected into `swagger-ui`'s `requestInterceptor` for "Try it out" calls.

**Alternatives considered**:
- **HTTP Basic auth on /docs**: Rejected — different auth scheme from the rest of the app; confusing UX.
- **Middleware-based protection on /docs URL**: Rejected — FastAPI serves Swagger UI as a static HTML file; there is no clean hook to inject bearer auth into it without custom JavaScript injection.
- **Redoc-only page**: Rejected — Redoc is read-only; `swagger-ui` supports "Try it out" which is valuable for developers.

---

## Decision 6: Material UI Version

**Decision**: `@mui/material@^5.16` with `@emotion/react@^11` and `@emotion/styled@^11` (MUI v5 stable). Theme created with `createTheme({ palette: { mode: 'light' | 'dark' } })`. A `ThemeProvider` wraps the full app tree. `CssBaseline` resets browser defaults.

**Rationale**: MUI v5 is the production-stable release. v6 (alpha) introduces breaking changes and is not yet recommended for production. MUI v5 has mature React 18 support, TypeScript types, and extensive component coverage. Emotion is the recommended CSS-in-JS engine for MUI v5.

**Alternatives considered**:
- **MUI v6**: Rejected — alpha stability; breaking changes from v5.
- **Tailwind CSS**: Rejected — requires a different theming approach; would not satisfy the spec's explicit MUI requirement.
- **Chakra UI / Ant Design**: Rejected — spec explicitly requires Material UI.

---

## Decision 7: Theme Implementation Pattern

**Decision**: `useColorMode` custom hook reads `user.theme_preference` from auth state. Maps `'light'` → `'light'`, `'dark'` → `'dark'`, `'system'` → result of `window.matchMedia('(prefers-color-scheme: dark)').matches`. Hook subscribes to `matchMedia` change events via `useEffect` + cleanup for live system theme updates. `ThemeContext` holds the resolved `PaletteMode` and a `setTheme` callback. `ThemeProvider` re-creates the MUI theme when mode changes.

**Rationale**: `useSyncExternalStore` would be ideal for `matchMedia` but `useEffect` + cleanup is simpler and well-supported. The resolved mode (light/dark) is the single truth passed to MUI; the three-way preference (light/dark/system) lives in the user's profile.

**Alternatives considered**:
- **CSS custom properties for theming**: Rejected — MUI's theming system supersedes manual CSS variables; maintaining two systems is a DRY violation.
- **Redux/Zustand for theme state**: Rejected — YAGNI; React context is sufficient for a single scalar value consumed app-wide.

---

## Decision 8: TOTP Clock Drift Tolerance

**Decision**: Accept codes from `t-1`, `t`, `t+1` windows using `pyotp.TOTP.verify(code, valid_window=1)`. This provides ±30 seconds = 90 seconds total tolerance.

**Rationale**: RFC 6238 §5.2 recommends network delay tolerance. `valid_window=1` is the `pyotp` parameter for ±1 window. Specified directly in the clarified spec.

---

## Decision 9: TOTP Brute-Force Lockout

**Decision**: Add `totp_failed_attempts: Mapped[int]` (default 0) and `totp_locked_until: Mapped[datetime | None]` to User. After 5 consecutive failed TOTP attempts, set `totp_locked_until = now() + 15 minutes`. Reset both fields to 0 / None on successful TOTP. Lock applies to both login TOTP step and backup code entry.

**Rationale**: 5 attempts with 15-minute lockout is consistent with NIST SP 800-63B recommendations. Stored in User avoids a Redis dependency. The fields are nullable/default-zero so existing users are unaffected.

---

## Dependencies to Add

### Backend (`backend/pyproject.toml`)
- `pyotp>=2.9` — TOTP secret generation and verification
- `qrcode[pil]>=7.4` — QR code image generation (returns base64 PNG)
- `cryptography>=42` — Fernet encryption for TOTP secret (likely already transitive)

### Frontend (`frontend/package.json`)
- `@mui/material@^5.16` — MUI component library
- `@mui/icons-material@^5.16` — MUI icon set
- `@emotion/react@^11` — MUI CSS-in-JS engine
- `@emotion/styled@^11` — MUI styled component factory
- `swagger-ui-react@^5` — Swagger UI React wrapper for API docs page
- `swagger-ui-react` types: `@types/swagger-ui-react` (if available, else `declare module`)
