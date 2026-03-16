/**
 * E2E spec: Password change via /preferences page.
 *
 * Prerequisites: running backend + seeded test user.
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

test.describe('Password change', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('shows error when current password is wrong', async ({ page }) => {
    await page.goto('/preferences');
    await page.getByLabel(/current password/i).fill('wrong-password-123');
    await page.getByLabel(/new password/i).first().fill('NewSecure@Password1');
    await page.getByLabel(/confirm new password/i).fill('NewSecure@Password1');
    await page.getByRole('button', { name: /change password/i }).click();
    await expect(page.getByRole('alert')).toContainText(/incorrect|invalid/i);
  });

  test('rejects new password that fails complexity rules', async ({ page }) => {
    await page.goto('/preferences');
    await page.getByLabel(/current password/i).fill(TEST_PASSWORD);
    await page.getByLabel(/new password/i).first().fill('short');
    await page.getByLabel(/confirm new password/i).fill('short');
    await page.getByRole('button', { name: /change password/i }).click();
    // Client-side or server-side validation should block this
    await expect(
      page.getByText(/at least 12|too short|complexity/i),
    ).toBeVisible();
  });
});
