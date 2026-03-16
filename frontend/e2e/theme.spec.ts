/**
 * E2E spec: Theme preference selection and persistence.
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

test.describe('Theme preference', () => {
  test('Theme tab renders Light / Dark / System options', async ({ page }) => {
    await login(page);
    await page.goto('/preferences');
    await page.getByRole('tab', { name: /theme/i }).click();
    await expect(page.getByRole('button', { name: /light/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /dark/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /system/i })).toBeVisible();
  });

  test('selecting Dark applies dark palette without page reload', async ({ page }) => {
    await login(page);
    await page.goto('/preferences');
    await page.getByRole('tab', { name: /theme/i }).click();
    await page.getByRole('button', { name: /dark/i }).click();
    // MUI dark palette sets the root background to a dark colour
    const bgColor = await page.evaluate(() =>
      window.getComputedStyle(document.body).backgroundColor,
    );
    // Should not be the default white background
    expect(bgColor).not.toBe('rgb(255, 255, 255)');
  });

  test('theme preference persists after logout and login', async ({ page }) => {
    await login(page);
    await page.goto('/preferences');
    await page.getByRole('tab', { name: /theme/i }).click();
    await page.getByRole('button', { name: /dark/i }).click();

    // Logout
    await page.getByRole('button', { name: /sign out/i }).click();
    await page.waitForURL('**/login**');

    // Log back in
    await login(page);
    await page.goto('/preferences');
    await page.getByRole('tab', { name: /theme/i }).click();
    // Dark should still be selected
    const darkBtn = page.getByRole('button', { name: /dark/i });
    await expect(darkBtn).toHaveAttribute('aria-pressed', 'true');
  });
});
