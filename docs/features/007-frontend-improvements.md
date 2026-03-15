# Feature: Frontend Improvements

**Feature ID**: 007-frontend-improvements
**Depends On**: 001-repo-setup, 002-sms-workflow
**Reference**: `docs/todo.md` (Frontend Improvements section)

---

## Overview

Improve the frontend application with three independent improvements: API documentation exposure, a Material UI design system migration, and a user preferences section with security features (password change, two-factor authentication, and display theme selection).

---

## Scope

### API Documentation Endpoint

- Expose a Swagger/OpenAPI documentation endpoint for the backend API accessible from the frontend.
- The API documentation must be auto-generated from the existing backend route definitions (using the framework's native OpenAPI support, e.g., FastAPI's `/docs` and `/redoc` endpoints, or an equivalent).
- The documentation must be accessible at a stable URL visible within the application (e.g., linked from the application's navigation or admin panel).
- The documentation must accurately reflect all current API endpoints, request/response schemas, authentication requirements, and error codes.

### Material UI Migration

- Migrate the frontend component library to Material UI (MUI).
- All existing UI pages and components must be updated to use MUI components and the MUI theming system.
- The migration must support the light/dark mode theming introduced in the User Preferences section below.
- The MUI theme configuration should be stored centrally and applied globally via the MUI `ThemeProvider`.

### User Preferences Section

Implement a User Preferences section accessible from the user's profile/account area. The section contains three subsections:

#### Password Change

- Users can change their password by providing their current password and a new password (with confirmation).
- Password change follows security best practices:
  - Minimum length and complexity requirements enforced and communicated to the user.
  - Current password must be verified before accepting the change.
  - New password must not be the same as the current password.
  - On successful change, all existing sessions except the current one are invalidated.

#### Two-Factor Authentication (2FA)

- Users can enable or disable 2FA on their account.
- 2FA implementation uses TOTP (Time-based One-Time Password) compatible with authenticator apps (Google Authenticator, Authy, etc.).
- Setup flow:
  1. User clicks "Enable 2FA".
  2. System generates a TOTP secret and displays a QR code and manual entry key.
  3. User confirms setup by entering a valid TOTP code from their authenticator app.
  4. System generates and displays one-time backup codes; user acknowledges they have saved them.
  5. 2FA is activated on the account.
- When 2FA is enabled, the login flow requires a TOTP code after successful password authentication.
- Users can disable 2FA by confirming with their current password and a valid TOTP code.
- Backup codes can be regenerated from the 2FA settings page (requires current password + valid TOTP code).

#### Display Preference (Theme)

- Users can select one of three display modes:
  - **Light Mode**: Light background theme.
  - **Dark Mode**: Dark background theme.
  - **System Default**: Follows the OS/browser's `prefers-color-scheme` setting.
- The selected preference is persisted to the user's profile in the database and applied on all sessions for that user.
- The theme switches immediately on selection without requiring a page reload.

---

## Integration Points

- The 2FA feature requires a server-side TOTP library (e.g., `pyotp` for the backend) and a QR code generation library.
- User preferences (theme, 2FA status) are stored in the `User` model/table, requiring a database migration.
- The Material UI migration touches all frontend components; this should be coordinated with other frontend development work to avoid merge conflicts.

---

## Success Criteria

- The OpenAPI documentation is accessible at a stable URL within the application and accurately reflects all backend API endpoints.
- All frontend pages use MUI components and the centralized MUI theme.
- A user can successfully change their password following the documented security requirements.
- A user can enable TOTP-based 2FA, and subsequent logins require a valid TOTP code.
- A user can select Light, Dark, or System Default display mode, and the selection persists across sessions.
- Theme switching occurs without a full page reload.
