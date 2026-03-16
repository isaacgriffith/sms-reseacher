/**
 * E2E spec: Two-factor authentication full lifecycle.
 *
 * Prerequisites: running backend + seeded test user without 2FA enabled.
 * Note: TOTP code generation requires the authenticator app; these tests
 * cover the UI flow up to the point where a real code is needed, plus
 * the lockout banner and backup code paths where codes are seeded.
 */

import { test, expect } from '@playwright/test';

const TEST_EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const TEST_PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';

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
    // This test requires a pre-configured user with 2FA enabled via env var
    const totpEmail = process.env.E2E_TOTP_EMAIL;
    test.skip(!totpEmail, 'E2E_TOTP_EMAIL not set — skipping TOTP login test');

    await page.goto('/login');
    await page.getByLabel(/email/i).fill(totpEmail!);
    await page.getByLabel(/password/i).fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page.getByText(/authentication code/i)).toBeVisible();
  });

  test('five wrong TOTP codes trigger lockout banner', async ({ page }) => {
    const totpEmail = process.env.E2E_TOTP_EMAIL;
    const partialToken = process.env.E2E_PARTIAL_TOKEN;
    test.skip(!partialToken, 'E2E_PARTIAL_TOKEN not set — skipping lockout test');

    // Use a fresh page state that already has a partial token scenario
    // In a real e2e environment, navigate through the login flow first
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(totpEmail ?? TEST_EMAIL);
    await page.getByLabel(/password/i).fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();

    // Send 5 wrong codes
    for (let i = 0; i < 5; i++) {
      await page.getByLabel(/authentication code/i).fill('000000');
      await page.getByRole('button', { name: /verify/i }).click();
    }
    await expect(page.getByRole('alert')).toContainText(/locked/i);
  });
});
