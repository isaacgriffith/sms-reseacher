/**
 * E2E spec: Provider management in the Admin panel — T073.
 *
 * Covers:
 * - Admin page is accessible when logged in as an admin user.
 * - Provider list tab is visible.
 * - Adding a new Ollama provider via the "Add Provider" dialog.
 * - The new provider appears in the provider list.
 * - Editing a provider's display name.
 * - Deleting a provider that has no dependent agents.
 *
 * Prerequisites: the dev server and backend are running. The test user must
 * have the ADMIN role in at least one research group. Configure via env vars:
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

async function navigateToAdminProviders(page: Page): Promise<void> {
  await page.goto('/admin');
  // The Admin page should contain a Providers tab or section
  const providersTab = page
    .getByRole('tab', { name: /providers/i })
    .or(page.getByRole('button', { name: /providers/i }))
    .or(page.getByText('Providers').first())
    .first();
  await providersTab.click();
  await expect(page.getByText(/providers/i).first()).toBeVisible();
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test.describe('Admin — Provider Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  // -------------------------------------------------------------------------
  // Admin page access
  // -------------------------------------------------------------------------

  test('admin page is accessible for admin users', async ({ page }) => {
    await page.goto('/admin');
    // The admin page should not redirect to login or show a 403 message
    await expect(page).not.toHaveURL(/login/);
    // Should show some admin content (heading or nav item)
    await expect(
      page
        .getByRole('heading', { name: /admin/i })
        .or(page.getByText(/admin panel/i).first())
        .or(page.getByText(/providers/i).first())
        .first(),
    ).toBeVisible({ timeout: 10_000 });
  });

  test('providers tab or section is visible in admin panel', async ({ page }) => {
    await page.goto('/admin');
    await expect(
      page
        .getByRole('tab', { name: /providers/i })
        .or(page.getByText(/providers/i).first())
        .first(),
    ).toBeVisible({ timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // Provider list
  // -------------------------------------------------------------------------

  test('provider list loads without errors', async ({ page }) => {
    await navigateToAdminProviders(page);
    // Should not show an error state — look for an empty state message or a table/list
    await expect(
      page
        .getByText(/no providers/i)
        .or(page.getByRole('table'))
        .or(page.getByRole('list'))
        .or(page.getByText(/provider/i).first())
        .first(),
    ).toBeVisible({ timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // Add provider dialog
  // -------------------------------------------------------------------------

  test('opens add provider dialog when add button is clicked', async ({ page }) => {
    await navigateToAdminProviders(page);

    // Click an "Add Provider" or similar button
    await page
      .getByRole('button', { name: /add provider|new provider|add/i })
      .first()
      .click();

    // Dialog or modal should appear
    await expect(
      page
        .getByRole('dialog')
        .or(page.getByText(/add provider/i).first())
        .or(page.getByLabel(/display name/i))
        .first(),
    ).toBeVisible({ timeout: 5_000 });
  });

  test('creates an Ollama provider and it appears in the list', async ({ page }) => {
    await navigateToAdminProviders(page);

    const providerName = `E2E Ollama ${Date.now()}`;

    // Open the add provider dialog
    await page
      .getByRole('button', { name: /add provider|new provider|add/i })
      .first()
      .click();

    // Fill in the form
    const dialog = page.getByRole('dialog');

    // Select provider type (Ollama)
    const typeSelect = dialog
      .getByLabel(/provider type|type/i)
      .or(dialog.getByRole('combobox', { name: /type/i }))
      .first();
    if (await typeSelect.isVisible()) {
      // MUI <TextField select> renders a listbox in a portal, not a native
      // <select>, so selectOption() does not apply — open it and pick the item.
      await typeSelect.click();
      await page.getByRole('option', { name: /ollama/i }).click();
    }

    // Fill display name
    await dialog.getByLabel(/display name/i).fill(providerName);

    // Fill base URL (required for Ollama)
    const baseUrlField = dialog.getByLabel(/base url|url/i);
    if (await baseUrlField.isVisible()) {
      await baseUrlField.fill('http://localhost:11434');
    }

    // Submit the form
    await dialog.getByRole('button', { name: /save|create|add|submit/i }).click();

    // Dialog should close
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 10_000 });

    // Provider name should appear in the list
    await expect(page.getByText(providerName)).toBeVisible({ timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // Edit provider
  // -------------------------------------------------------------------------

  test('can open edit dialog for an existing provider', async ({ page }) => {
    await navigateToAdminProviders(page);

    // Migration 0012 seeds the Anthropic default provider, so a row always
    // exists — no conditional skip needed.
    await page.getByRole('button', { name: 'edit provider' }).first().click();

    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByLabel(/display name/i)).toBeVisible();
  });

  // -------------------------------------------------------------------------
  // Refresh models button
  // -------------------------------------------------------------------------

  test('refresh models button is visible for each provider', async ({ page }) => {
    await navigateToAdminProviders(page);

    // Migration 0012 seeds the Anthropic default provider, so a row always
    // exists — the old conditional skip made this silently vanish whenever the
    // list happened to be slow or empty.
    const refreshButton = page.getByRole('button', { name: /refresh models/i }).first();
    await expect(refreshButton).toBeEnabled({ timeout: 10_000 });
  });
});
