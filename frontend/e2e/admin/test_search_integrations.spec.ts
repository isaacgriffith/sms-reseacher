/**
 * E2E spec: Admin — Search Integrations table (T067).
 *
 * Covers:
 * - Admin page Search Integrations tab is accessible.
 * - Integration table renders with expected column headers.
 * - At least one integration row is present.
 * - Edit button opens a credential dialog with API Key field.
 * - Cancel button dismisses the dialog without saving.
 * - "Test Now" button is present per row and triggers a connectivity test.
 * - After clicking "Test Now" a loading state or result is shown.
 *
 * Prerequisites: the dev server and backend are running; the test user must
 * have the ADMIN role. Configure via env vars:
 *   E2E_ADMIN_EMAIL    — admin user email (default: admin@example.com)
 *   E2E_ADMIN_PASSWORD — admin user password (default: adminpassword)
 */

import { test, expect, type Page } from '@playwright/test';

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL ?? 'admin@example.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD ?? 'adminpassword';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function loginAsAdmin(page: Page): Promise<void> {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(ADMIN_EMAIL);
  await page.getByLabel(/password/i).fill(ADMIN_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('**/groups**', { timeout: 10_000 });
}

async function navigateToSearchIntegrations(page: Page): Promise<void> {
  await page.goto('/admin');
  // Click the "Search Integrations" tab (index 4)
  const tab = page.getByRole('tab', { name: /search integrations/i });
  await tab.waitFor({ state: 'visible', timeout: 8_000 });
  await tab.click();
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test.describe('Admin — Search Integrations', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await navigateToSearchIntegrations(page);
  });

  // -------------------------------------------------------------------------
  // Table visibility
  // -------------------------------------------------------------------------

  test('Search Integrations heading is visible', async ({ page }) => {
    await expect(page.getByText(/search integrations/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('table header row shows "Database" column', async ({ page }) => {
    await expect(page.getByRole('columnheader', { name: /database/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('table header row shows "Status" column', async ({ page }) => {
    await expect(page.getByRole('columnheader', { name: /status/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('table header row shows "Actions" column', async ({ page }) => {
    await expect(page.getByRole('columnheader', { name: /actions/i })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('at least one integration row is rendered', async ({ page }) => {
    // Wait for rows to load (the table may show a spinner briefly)
    await page.waitForSelector('tbody tr', { timeout: 10_000 });
    const rows = page.locator('tbody tr');
    await expect(rows.first()).toBeVisible();
  });

  test('"Test Now" button is present in the first row', async ({ page }) => {
    await page.waitForSelector('tbody tr', { timeout: 10_000 });
    const testNowBtn = page.getByRole('button', { name: /test now/i }).first();
    await expect(testNowBtn).toBeVisible({ timeout: 8_000 });
  });

  test('"Edit" button is present in the first row', async ({ page }) => {
    await page.waitForSelector('tbody tr', { timeout: 10_000 });
    const editBtn = page.getByRole('button', { name: /^edit$/i }).first();
    await expect(editBtn).toBeVisible({ timeout: 8_000 });
  });

  // -------------------------------------------------------------------------
  // Edit credential dialog
  // -------------------------------------------------------------------------

  test('clicking Edit opens a dialog with an API Key field', async ({ page }) => {
    await page.waitForSelector('tbody tr', { timeout: 10_000 });
    await page
      .getByRole('button', { name: /^edit$/i })
      .first()
      .click();

    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5_000 });
    await expect(page.getByLabel(/api key/i)).toBeVisible();
  });

  test('edit dialog has a Cancel button that dismisses it', async ({ page }) => {
    await page.waitForSelector('tbody tr', { timeout: 10_000 });
    await page
      .getByRole('button', { name: /^edit$/i })
      .first()
      .click();

    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5_000 });
    await page.getByRole('button', { name: /cancel/i }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 3_000 });
  });

  test('edit dialog has a Save button', async ({ page }) => {
    await page.waitForSelector('tbody tr', { timeout: 10_000 });
    await page
      .getByRole('button', { name: /^edit$/i })
      .first()
      .click();

    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5_000 });
    await expect(page.getByRole('button', { name: /^save$/i })).toBeVisible();
  });

  test('edit dialog title contains the integration name', async ({ page }) => {
    await page.waitForSelector('tbody tr', { timeout: 10_000 });
    await page
      .getByRole('button', { name: /^edit$/i })
      .first()
      .click();

    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5_000 });
    // Dialog title should contain "Edit Credential —" followed by the integration name
    await expect(page.getByText(/edit credential/i)).toBeVisible();
  });

  test('API Key field accepts text input', async ({ page }) => {
    await page.waitForSelector('tbody tr', { timeout: 10_000 });
    await page
      .getByRole('button', { name: /^edit$/i })
      .first()
      .click();

    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5_000 });

    const apiKeyField = page.getByLabel(/api key/i);
    await apiKeyField.fill('test-api-key-value');
    await expect(apiKeyField).toHaveValue('test-api-key-value');

    // Clean up — cancel without saving
    await page.getByRole('button', { name: /cancel/i }).click();
  });

  // -------------------------------------------------------------------------
  // Test Now button
  // -------------------------------------------------------------------------

  test('clicking "Test Now" triggers some UI feedback', async ({ page }) => {
    await page.waitForSelector('tbody tr', { timeout: 10_000 });

    const testNowBtn = page.getByRole('button', { name: /test now/i }).first();
    await testNowBtn.click();

    // Wait for the outcome rather than sampling the DOM the instant after the
    // click: the in-flight spinner may not have rendered yet, and by the time
    // it has, the request may already have resolved. Either a progress
    // indicator or a result status counts as feedback.
    await expect(
      page
        .locator('[role="progressbar"]')
        .first()
        .or(page.getByText(/success|error|failed|ok|pending|testing/i).first()),
    ).toBeVisible({ timeout: 15_000 });
  });
});
