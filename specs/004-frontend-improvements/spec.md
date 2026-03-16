# Feature Specification: Frontend Improvements

**Feature Branch**: `004-frontend-improvements`
**Created**: 2026-03-16
**Status**: Draft
**Input**: User description: "004 frontend-improvements docs/features/007-frontend-improvements.md"

## Clarifications

### Session 2026-03-16

- Q: Should the API documentation page require authentication to view? → A: Authenticated users only — requires login to view docs.
- Q: Should security-sensitive events (password change, 2FA enable/disable) be recorded in an audit trail? → A: Yes — log with timestamp and user identity.
- Q: Should the TOTP verification prompt enforce brute-force protection? → A: Temporary lockout — 2FA prompt locked for a period after N consecutive failures.
- Q: What clock-drift tolerance should TOTP verification apply? → A: ±1 window — accept current, previous, and next 30-second codes (90-second total tolerance).
- Q: Is 2FA mandatory for any user role, or optional for all? → A: Optional for all users — any user may enable or skip 2FA.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Changes Password (Priority: P1)

A researcher who has been using the system for a while wants to update their password for security reasons. They navigate to their account preferences, provide their current password, enter and confirm a new password, and receive confirmation that their password was changed successfully. All other active sessions are ended automatically.

**Why this priority**: Password management is a foundational security feature. It delivers immediate user value independently and establishes the account security patterns used by 2FA.

**Independent Test**: Can be fully tested by navigating to User Preferences → Password Change, completing the form, and verifying the change takes effect on re-login; delivers secure account management without any other preference feature present.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the Password Change form, **When** they submit a valid current password and a new password meeting complexity requirements, **Then** the password is updated, a success message is shown, and all other sessions are invalidated.
2. **Given** a user submitting the Password Change form, **When** the current password provided is incorrect, **Then** the change is rejected with a clear error and no session is invalidated.
3. **Given** a user submitting the Password Change form, **When** the new password does not meet minimum complexity requirements, **Then** the system rejects the change and communicates the unmet requirements.
4. **Given** a user submitting the Password Change form, **When** the new password matches the current password, **Then** the change is rejected with a message indicating the new password must differ.
5. **Given** a user submitting the Password Change form, **When** the new password and confirmation field do not match, **Then** the change is rejected with a validation error before submission.

---

### User Story 2 - User Selects Display Theme (Priority: P2)

A researcher working late at night wants to switch the application to dark mode. They navigate to User Preferences, select Dark Mode, and the application immediately switches to a dark theme without reloading. The next time they log in from any device, their dark theme preference is applied automatically.

**Why this priority**: Theme preference directly improves daily usability and comfort. It is self-contained, has no security implications, and can be shipped independently to provide immediate value.

**Independent Test**: Can be fully tested by selecting a theme in User Preferences and verifying the visual change takes effect immediately and persists on a fresh login; delivers a better user experience without requiring 2FA or any other feature.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the Display Preference section, **When** they select Dark Mode, **Then** the entire application switches to the dark theme immediately without a page reload.
2. **Given** a logged-in user on the Display Preference section, **When** they select System Default, **Then** the application theme matches the operating system or browser color-scheme preference.
3. **Given** a user who previously selected Dark Mode, **When** they log in again, **Then** the dark theme is applied automatically from the start of their session.
4. **Given** a user on a device set to dark OS mode with System Default selected, **When** the OS mode is switched to light, **Then** the application theme updates to light without requiring a manual preference change.

---

### User Story 3 - User Enables Two-Factor Authentication (Priority: P3)

A security-conscious researcher wants to add a second factor to their login. They navigate to User Preferences → 2FA, scan a QR code with their authenticator app, confirm setup with a valid code, save their backup codes, and from then on must provide a TOTP code at each login. They can also disable 2FA later using their password and a TOTP code.

**Why this priority**: 2FA significantly strengthens account security but is optional and more complex to implement than password change. It depends on the password-change security patterns already being established.

**Independent Test**: Can be fully tested by enabling 2FA, logging out, and logging back in to confirm the TOTP code prompt appears; delivers enhanced account security independently of theme or API documentation features.

**Acceptance Scenarios**:

1. **Given** a user with 2FA disabled, **When** they initiate 2FA setup and confirm with a valid TOTP code from their authenticator app, **Then** 2FA is activated and backup codes are displayed for the user to save.
2. **Given** a user who has completed 2FA setup, **When** they log in with correct credentials, **Then** they are prompted for a TOTP code and cannot complete login without a valid code.
3. **Given** a user with 2FA enabled who has lost their authenticator, **When** they enter a valid single-use backup code at the TOTP prompt, **Then** they are granted access and that backup code is consumed.
4. **Given** a user with 2FA enabled, **When** they disable 2FA by providing their current password and a valid TOTP code, **Then** 2FA is deactivated and subsequent logins no longer require a TOTP code.
5. **Given** a user with 2FA enabled, **When** they regenerate backup codes (using their password and a valid TOTP code), **Then** new backup codes are issued and all previous backup codes are invalidated.
6. **Given** a user at the TOTP prompt who submits N consecutive incorrect codes, **When** the threshold is reached, **Then** the prompt is locked for a defined period, further attempts are blocked, and the user is shown the lockout duration.

---

### User Story 4 - Developer Browses API Documentation (Priority: P4)

A developer integrating with the research platform needs to understand the available API endpoints. They navigate to the API documentation link in the application and see an up-to-date, interactive reference listing all endpoints, request/response schemas, authentication requirements, and error codes.

**Why this priority**: API documentation improves developer productivity and reduces support burden but does not affect end-user research workflows. It is fully independent of all other stories.

**Independent Test**: Can be fully tested by navigating to the documentation URL and verifying all current API endpoints are listed with accurate schemas; delivers developer value without any other preference feature present.

**Acceptance Scenarios**:

1. **Given** an authenticated user or developer, **When** they navigate to the API documentation URL, **Then** they see an interactive page listing all backend API endpoints with request/response schemas, authentication requirements, and error codes.
1a. **Given** an unauthenticated visitor, **When** they navigate to the API documentation URL, **Then** they are redirected to the login page.
2. **Given** the backend API has been updated with a new endpoint, **When** a user views the API documentation, **Then** the new endpoint appears automatically without any manual documentation update.
3. **Given** a user browsing the application, **When** they look for the API documentation, **Then** a visible link or navigation item leads them to the documentation page.

---

### Edge Cases

- What happens when a user changes their password while another session is active — are they notified on the other device?
- How does the system handle a TOTP code submitted at the edge of a window? — The ±1 window tolerance (FR-011) ensures codes from adjacent windows are also accepted, eliminating edge-of-window failures due to clock drift.
- What happens when a user has consumed all backup codes and cannot access their authenticator — is there an account recovery path?
- What happens if a user selects System Default theme but their browser does not report a color-scheme preference?
- How does the API documentation page behave if the backend is temporarily unavailable?
- What happens when a user submits N consecutive failed TOTP codes — they are locked out temporarily (see FR-014b).

## Requirements *(mandatory)*

### Functional Requirements

**Password Change**

- **FR-001**: Users MUST be able to change their password by providing their current password, a new password, and a confirmation of the new password.
- **FR-002**: System MUST reject password changes where the current password provided is incorrect.
- **FR-003**: System MUST enforce minimum password complexity requirements (minimum length and character variety) and communicate unmet requirements to the user.
- **FR-004**: System MUST reject a new password that is identical to the current password.
- **FR-005**: System MUST invalidate all user sessions except the currently active one upon a successful password change.
- **FR-006**: System MUST provide a success confirmation message after a password is changed successfully.
- **FR-006a**: System MUST record an audit event whenever a password is changed, capturing the user identity and timestamp.

**Two-Factor Authentication**

- **FR-007**: Two-factor authentication is optional for all users. Users MUST be able to enable TOTP-based 2FA from their account preferences, and no user role is required to activate it.
- **FR-008**: The 2FA setup flow MUST display a QR code and a manual entry key for use with standard TOTP authenticator apps.
- **FR-009**: Users MUST confirm 2FA setup by entering a valid TOTP code before activation is complete.
- **FR-010**: System MUST generate and display one-time backup codes upon successful 2FA activation; the user must acknowledge they have saved the codes.
- **FR-011**: When 2FA is active on an account, users MUST provide a valid TOTP code after password authentication to complete login. The system MUST accept codes from the current, immediately preceding, and immediately following 30-second time windows (±1 window, 90-second total tolerance) to accommodate minor clock drift.
- **FR-012**: Backup codes MUST be accepted as an alternative to a TOTP code during login, and each backup code MUST be invalidated after a single use.
- **FR-013**: Users MUST be able to disable 2FA by providing their current password and a valid TOTP code.
- **FR-014**: Users MUST be able to regenerate backup codes from the 2FA settings page by providing their current password and a valid TOTP code; previously issued backup codes MUST be invalidated on regeneration.
- **FR-014a**: System MUST record an audit event whenever 2FA is enabled, disabled, or backup codes are regenerated, capturing the user identity and timestamp.
- **FR-014b**: System MUST temporarily lock the TOTP verification prompt after a configurable number of consecutive failed attempts; the user MUST be informed of the lockout and its duration.

**Display Theme**

- **FR-015**: Users MUST be able to select one of three display modes: Light, Dark, or System Default.
- **FR-016**: Theme selection MUST take effect immediately upon selection without requiring a page reload.
- **FR-017**: The selected theme preference MUST be persisted to the user's account and applied automatically on all subsequent sessions.
- **FR-018**: When System Default is selected, the application MUST follow the operating system or browser color-scheme preference and update dynamically if that preference changes.

**API Documentation**

- **FR-019**: The application MUST expose an API documentation page at a stable URL accessible only to authenticated users; unauthenticated requests MUST be redirected to the login page.
- **FR-020**: The API documentation MUST be auto-generated from the backend route definitions and MUST accurately reflect all current endpoints, request/response schemas, authentication requirements, and error codes.
- **FR-021**: A visible navigation element MUST link to the API documentation page from within the application.

**UI Component Library**

- **FR-022**: All existing frontend pages and components MUST be updated to use the Material UI component library and its theming system.
- **FR-023**: The MUI theme configuration MUST be defined centrally and applied globally to the entire application.
- **FR-024**: The MUI theme MUST support the Light and Dark modes introduced by the Display Preference feature.

### Key Entities

- **User**: A registered researcher or administrator. Gains attributes: theme preference (light/dark/system), 2FA enabled flag, TOTP secret, active backup codes list.
- **2FA Backup Code**: A single-use recovery code tied to a user account, generated in a batch; invalidated individually on use or collectively on regeneration.
- **Session**: An authenticated user session. Multiple sessions may exist per user; all non-current sessions are invalidated on password change.
- **Security Audit Event**: An immutable record of a security-sensitive action (password change, 2FA enabled, 2FA disabled, backup codes regenerated). Attributes: user identity, event type, timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can complete the password change flow (from opening preferences to receiving confirmation) in under 2 minutes.
- **SC-002**: A user can complete the full 2FA enrollment flow (initiate setup, scan QR, confirm code, save backup codes) in under 5 minutes.
- **SC-003**: Theme switching takes effect within 500 milliseconds of selection with no full page reload occurring.
- **SC-004**: The selected theme is applied within 1 second of a user's page load on subsequent sessions, with no flash of the wrong theme visible.
- **SC-005**: The API documentation page reflects all current backend endpoints; 100% of endpoints are documented with no manual authoring required.
- **SC-006**: All frontend pages render correctly using the Material UI design system, with no legacy component library code remaining.
- **SC-007**: TOTP codes from the current or adjacent 30-second windows (±1 window, up to 90 seconds of clock drift) are accepted; codes outside this tolerance are rejected. Each accepted code is valid for one use only within its window.
- **SC-008**: After a password change, all sessions other than the active one are invalidated within 60 seconds.

## Assumptions

- The application already has a user authentication system (login/logout) that this feature builds upon.
- "All other sessions invalidated" on password change means server-side session tokens are revoked; the exact notification to other devices is not in scope for this feature.
- System Default theme falls back to Light mode if the browser does not report a color-scheme preference.
- Backup codes are alphanumeric, single-use tokens; the exact format and count (e.g., 8 codes of 10 characters) is an implementation detail.
- Account recovery when a user loses both their authenticator and all backup codes is out of scope for this feature (requires separate admin recovery workflow).
- The API documentation is accessible to any authenticated user; no further role-based restriction (e.g., admin-only) is applied beyond requiring login.
- The MUI migration is a visual/structural change; no existing user-facing behavior is altered by the migration itself.
