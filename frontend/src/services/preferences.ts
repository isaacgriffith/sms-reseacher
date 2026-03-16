/**
 * User preferences and 2FA API service functions.
 */

import { z } from 'zod';

import { api, ApiError } from './api';
import type { ThemePreference } from '../theme/ThemeContext';

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

const PreferencesSchema = z.object({
  theme_preference: z.enum(['light', 'dark', 'system']),
  totp_enabled: z.boolean(),
});

export type Preferences = z.infer<typeof PreferencesSchema>;

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

const ErrorDetailSchema = z.object({ detail: z.string() });

// ---------------------------------------------------------------------------
// Password change
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Theme preference
// ---------------------------------------------------------------------------

/** Fetch the current user's preferences from the server. */
export async function getPreferences(): Promise<Preferences> {
  const raw = await api.get<unknown>('/api/v1/me/preferences');
  return PreferencesSchema.parse(raw);
}

/**
 * Persist a new theme preference for the authenticated user.
 *
 * @throws {ApiError} On 422 if the theme value is invalid.
 */
export async function updateTheme(theme: ThemePreference): Promise<void> {
  await api.put<{ theme_preference: string }>('/api/v1/me/preferences/theme', { theme });
}

// ---------------------------------------------------------------------------
// 2FA — Zod schemas
// ---------------------------------------------------------------------------

export const TotpSetupSchema = z.object({
  qr_code_image: z.string(),
  manual_key: z.string(),
  issuer: z.string(),
});
export type TotpSetupData = z.infer<typeof TotpSetupSchema>;

export const TotpConfirmSchema = z.object({
  backup_codes: z.array(z.string()),
});
export type TotpConfirmData = z.infer<typeof TotpConfirmSchema>;

// ---------------------------------------------------------------------------
// 2FA — service functions
// ---------------------------------------------------------------------------

/** Initiate TOTP 2FA setup; returns QR image and manual key. */
export async function setup2fa(): Promise<TotpSetupData> {
  const raw = await api.post<unknown>('/api/v1/me/2fa/setup', {});
  return TotpSetupSchema.parse(raw);
}

/** Confirm 2FA enrollment with a valid TOTP code; returns backup codes. */
export async function confirm2fa(totpCode: string): Promise<TotpConfirmData> {
  const raw = await api.post<unknown>('/api/v1/me/2fa/confirm', { totp_code: totpCode });
  return TotpConfirmSchema.parse(raw);
}

/** Disable 2FA; requires current password and TOTP code. */
export async function disable2fa(password: string, totpCode: string): Promise<void> {
  await api.post<unknown>('/api/v1/me/2fa/disable', {
    password,
    totp_code: totpCode,
  });
}

/** Regenerate backup codes; requires current password and TOTP code. */
export async function regenerateBackupCodes(
  password: string,
  totpCode: string,
): Promise<TotpConfirmData> {
  const raw = await api.post<unknown>('/api/v1/me/2fa/backup-codes/regenerate', {
    password,
    totp_code: totpCode,
  });
  return TotpConfirmSchema.parse(raw);
}

// ---------------------------------------------------------------------------
// Password change
// ---------------------------------------------------------------------------

/**
 * Change the authenticated user's password.
 *
 * @throws {ApiError} On 400 (wrong current password or same password) or
 *   422 (complexity failure).
 */
export async function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<void> {
  try {
    await api.put<{ message: string }>('/api/v1/me/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  } catch (err) {
    if (err instanceof ApiError) {
      // Propagate with typed detail
      const parsed = ErrorDetailSchema.safeParse({ detail: err.detail });
      throw new ApiError(err.status, parsed.success ? parsed.data.detail : err.detail);
    }
    throw err;
  }
}
