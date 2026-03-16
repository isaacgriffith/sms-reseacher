/**
 * E2E spec: Authenticated API documentation page.
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

test.describe('API Docs page', () => {
  test('logged-in user sees Swagger UI with API paths', async ({ page }) => {
    await login(page);
    await page.goto('/api-docs');
    // Swagger UI renders a title from the OpenAPI spec
    await expect(page.locator('.swagger-ui')).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('.info .title')).toContainText(/sms researcher/i);
  });

  test('unauthenticated navigation to /api-docs redirects to login', async ({ page }) => {
    // Navigate without logging in
    await page.goto('/api-docs');
    await expect(page).toHaveURL(/\/login/);
  });

  test('API Docs link appears in the side nav when logged in', async ({ page }) => {
    await login(page);
    await expect(page.getByRole('link', { name: /api docs/i })).toBeVisible();
  });

  test('backend /api/v1/openapi.json returns 401 without a token', async ({ request }) => {
    const response = await request.get('/api/v1/openapi.json');
    expect(response.status()).toBe(401);
  });
});
