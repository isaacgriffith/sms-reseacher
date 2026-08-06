/**
 * E2E spec: Two-factor authentication full lifecycle.
 *
 * Prerequisites: a running backend and `scripts/seed_e2e_user.py` having been
 * run. No authenticator app or code-generation library is needed — none of
 * these tests requires a *valid* TOTP code.
 *
 * The lockout test leaves its account locked for `totp_lockout_minutes`
 * (default 15). CI seeds a fresh database before every run, so this is
 * deterministic there; re-running locally without re-seeding will fail until
 * the lock expires. Re-run the seed script to reset it immediately.
 */

import { test, expect } from '@playwright/test';

const TEST_EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const TEST_PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';

// A dedicated account with 2FA already switched on, created by
// scripts/seed_e2e_user.py. Neither test below needs a *valid* TOTP code — one
// checks the prompt appears, the other deliberately submits wrong codes — so no
// authenticator or code-generation library is required.
const TOTP_EMAIL = process.env.E2E_TOTP_EMAIL ?? 'totpuser@example.com';
const TOTP_PASSWORD = process.env.E2E_TOTP_PASSWORD ?? 'testpassword';
// A locked account is refused at the password step too, so the lockout test
// uses its own user and cannot poison the prompt test above.
const TOTP_LOCKOUT_EMAIL = process.env.E2E_TOTP_LOCKOUT_EMAIL ?? 'totplockout@example.com';

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(TEST_EMAIL);
  await page.getByLabel(/password/i).fill(TEST_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('**/groups**');
}

test.describe('2FA setup flow', () => {
  test('Enable 2FA button opens QR dialog', async ({ page }) => {
    await login(page);
    await page.goto('/preferences');
    await page.getByRole('tab', { name: /two-factor/i }).click();
    await page.getByRole('button', { name: /enable 2fa/i }).click();
    await expect(page.getByAltText('TOTP QR code')).toBeVisible();
    await expect(page.getByRole('button', { name: /next/i })).toBeVisible();
  });

  test('QR dialog can be cancelled', async ({ page }) => {
    await login(page);
    await page.goto('/preferences');
    await page.getByRole('tab', { name: /two-factor/i }).click();
    await page.getByRole('button', { name: /enable 2fa/i }).click();
    await page.getByRole('button', { name: /cancel/i }).click();
    // Dialog should close and Enable 2FA button reappears
    await expect(page.getByRole('button', { name: /enable 2fa/i })).toBeVisible();
  });
});

test.describe('2FA login — TOTP second step', () => {
  test('user with 2FA enabled sees TOTP prompt after password login', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(TOTP_EMAIL);
    await page.getByLabel(/password/i).fill(TOTP_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();

    // Correct credentials must not grant a session on their own.
    await expect(page.getByLabel(/authentication code/i)).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });

  test('five wrong TOTP codes lock the account', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(TOTP_LOCKOUT_EMAIL);
    await page.getByLabel(/password/i).fill(TOTP_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page.getByLabel(/authentication code/i)).toBeVisible();

    // Send 5 wrong codes. The seed script resets totp_failed_attempts, so the
    // counter starts at zero on every run.
    for (let i = 0; i < 5; i++) {
      await page.getByLabel(/authentication code/i).fill('000000');
      await page.getByRole('button', { name: /verify/i }).click();
      await expect(page.getByRole('alert')).toContainText(/invalid/i);
    }

    // The fifth failure applies the lock; the banner surfaces on the next
    // attempt, when the request is rejected with 429 before verification.
    await page.getByLabel(/authentication code/i).fill('000000');
    await page.getByRole('button', { name: /verify/i }).click();
    await expect(page.getByRole('alert')).toContainText(/locked/i);
  });
});
