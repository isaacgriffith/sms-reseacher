/**
 * TanStack Query mutations for TOTP 2FA lifecycle operations.
 */

import { useMutation } from '@tanstack/react-query';

import {
  confirm2fa,
  disable2fa,
  regenerateBackupCodes,
  setup2fa,
  type TotpConfirmData,
  type TotpSetupData,
} from '../services/preferences';

/** Initiate TOTP setup — returns QR image and manual key. */
export function useTotpSetup() {
  return useMutation<TotpSetupData, Error, void>({
    mutationFn: () => setup2fa(),
  });
}

/** Confirm TOTP setup with a valid 6-digit code — returns backup codes. */
export function useTotpConfirm() {
  return useMutation<TotpConfirmData, Error, string>({
    mutationFn: (totpCode: string) => confirm2fa(totpCode),
  });
}

export interface TotpCredentials {
  password: string;
  totpCode: string;
}

/** Disable TOTP 2FA — requires current password and TOTP code. */
export function useTotpDisable() {
  return useMutation<void, Error, TotpCredentials>({
    mutationFn: ({ password, totpCode }) => disable2fa(password, totpCode),
  });
}

/** Regenerate backup codes — requires current password and TOTP code. */
export function useBackupCodesRegenerate() {
  return useMutation<TotpConfirmData, Error, TotpCredentials>({
    mutationFn: ({ password, totpCode }) => regenerateBackupCodes(password, totpCode),
  });
}
