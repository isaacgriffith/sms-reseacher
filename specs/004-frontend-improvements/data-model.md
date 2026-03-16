# Data Model: Frontend Improvements (004)

**Date**: 2026-03-16
**Branch**: `004-frontend-improvements`

---

## Overview

This feature adds three new persistent entities (`BackupCode`, `SecurityAuditEvent`) and extends the existing `User` entity with security and preference fields. All changes require Alembic migrations.

---

## Existing Entity: User (Extended)

**Table**: `user`
**File**: `db/src/db/models/users.py`

### New Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `theme_preference` | `Enum(ThemePreference)` | No | `'system'` | User display mode: light, dark, or system |
| `totp_enabled` | `Boolean` | No | `False` | Whether TOTP 2FA is active |
| `totp_secret_encrypted` | `Text` | Yes | `NULL` | Fernet-encrypted TOTP secret; null when 2FA disabled |
| `totp_failed_attempts` | `Integer` | No | `0` | Consecutive failed TOTP attempts since last success |
| `totp_locked_until` | `DateTime(tz=True)` | Yes | `NULL` | Lockout expiry; null means not locked |
| `token_version` | `Integer` | No | `0` | Incremented on password change to invalidate prior JWTs |
| `password_changed_at` | `DateTime(tz=True)` | No | `func.now()` | Timestamp of last password change (informational) |
| `updated_at` | `DateTime(tz=True)` | No | `func.now()` | Auto-updated on every row change (constitution requirement) |

### New Enum

```python
class ThemePreference(str, enum.Enum):
    """User's preferred colour scheme."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
```

**SQLAlchemy type**: `Enum(ThemePreference, name="theme_preference_enum")`

### Updated Relationships

```python
backup_codes: Mapped[list["BackupCode"]] = relationship(
    "BackupCode", back_populates="user", cascade="all, delete-orphan"
)
security_audit_events: Mapped[list["SecurityAuditEvent"]] = relationship(
    "SecurityAuditEvent", back_populates="user", cascade="all, delete-orphan"
)
```

### State Transitions (2FA lifecycle)

```
[totp_enabled=False, totp_secret_encrypted=NULL]
        │
        │ POST /me/2fa/setup
        ▼
[totp_enabled=False, totp_secret_encrypted=<temp>]  ← setup in progress
        │
        │ POST /me/2fa/confirm (valid TOTP code)
        ▼
[totp_enabled=True, totp_secret_encrypted=<encrypted>]
        │
        │ POST /me/2fa/disable (valid password + TOTP)
        ▼
[totp_enabled=False, totp_secret_encrypted=NULL]
```

### State Transitions (token version / session invalidation)

```
token_version=N  →  password changed  →  token_version=N+1
All JWTs with ver=N are now rejected by get_current_user
```

---

## New Entity: BackupCode

**Table**: `backup_code`
**File**: `db/src/db/models/backup_codes.py`

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `Integer` PK | No | autoincrement | Primary key |
| `user_id` | `Integer` FK→`user.id` | No | — | Owner |
| `hashed_code` | `String(255)` | No | — | bcrypt hash of the one-time backup code |
| `used_at` | `DateTime(tz=True)` | Yes | `NULL` | Set when code is redeemed; null = unused |
| `created_at` | `DateTime(tz=True)` | No | `func.now()` | Batch creation timestamp |
| `updated_at` | `DateTime(tz=True)` | No | `func.now()` | Updated when `used_at` is set |

### Relationships

```python
user: Mapped["User"] = relationship("User", back_populates="backup_codes")
```

### Constraints

- `CASCADE DELETE` on `user_id` — codes deleted when user is deleted.
- No unique constraint on `hashed_code` (different users may theoretically hash to same value; lookup is always user-scoped).

### Business Rules

- 10 codes generated per batch (constant `BACKUP_CODE_COUNT = 10`).
- Each code is 10 uppercase alphanumeric characters, generated via `secrets.token_urlsafe` then uppercased and truncated.
- On redemption: `used_at = now()`. The code remains in the table for audit; it is not deleted.
- On regeneration or 2FA disable: all rows for the user are deleted (hard delete), then new rows inserted.

---

## New Entity: SecurityAuditEvent

**Table**: `security_audit_event`
**File**: `db/src/db/models/security_audit.py`

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `Integer` PK | No | autoincrement | Primary key |
| `user_id` | `Integer` FK→`user.id` | No | — | Subject user |
| `event_type` | `Enum(SecurityEventType)` | No | — | Categorises the event |
| `ip_address` | `String(45)` | Yes | `NULL` | Requestor IP; IPv4 or IPv6 |
| `created_at` | `DateTime(tz=True)` | No | `func.now()` | Immutable event timestamp |
| `updated_at` | `DateTime(tz=True)` | No | `func.now()` | Required by constitution; logically stable |

### New Enum

```python
class SecurityEventType(str, enum.Enum):
    """Classifies security-sensitive account events."""
    PASSWORD_CHANGED = "password_changed"
    TOTP_ENABLED = "totp_enabled"
    TOTP_DISABLED = "totp_disabled"
    BACKUP_CODES_REGENERATED = "backup_codes_regenerated"
    TOTP_LOCKED = "totp_locked"
```

**SQLAlchemy type**: `Enum(SecurityEventType, name="security_event_type_enum")`

### Relationships

```python
user: Mapped["User"] = relationship("User", back_populates="security_audit_events")
```

### Constraints

- `CASCADE DELETE` on `user_id`.
- Records are logically immutable after insert (no update path in service layer).

---

## Alembic Migrations Required

| Migration | Description |
|-----------|-------------|
| `add_user_security_preference_columns` | Adds `theme_preference`, `totp_*`, `token_version`, `password_changed_at`, `updated_at` to `user` table; creates `theme_preference_enum` type |
| `create_backup_code_table` | Creates `backup_code` table |
| `create_security_audit_event_table` | Creates `security_audit_event` table; creates `security_event_type_enum` type |

Each migration must have a corresponding `downgrade()` that drops added columns/tables and their enum types in reverse order.

---

## Model Export Updates

`db/src/db/models/__init__.py` must export:
- `BackupCode`
- `SecurityAuditEvent`
- `ThemePreference` (enum)
- `SecurityEventType` (enum)

---

## JWT Payload Shape (Updated)

```python
# Full access token
{
    "sub": str(user_id),       # existing
    "exp": datetime,           # existing
    "iat": datetime,           # NEW — issued-at, UTC
    "ver": int,                # NEW — token_version at issuance
}

# Partial token (2FA pending)
{
    "sub": str(user_id),
    "exp": datetime,           # now + 5 minutes
    "iat": datetime,
    "stage": "totp_required",  # sentinel — rejected by get_current_user
}
```
