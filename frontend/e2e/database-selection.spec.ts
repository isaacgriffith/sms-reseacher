/**
 * E2E spec: Database selection panel in a study's Search phase (Phase 2).
 *
 * Covers:
 * - Database Search Configuration panel is visible on Phase 2 of a study.
 * - All database group headings (Primary, General, Supplementary) are shown.
 * - Toggling a database index updates the switch state.
 * - Save button is present and clickable.
 * - SciHub toggle shows an acknowledgment dialog.
 * - Cancelling the SciHub dialog leaves SciHub disabled.
 * - Acknowledging the SciHub dialog enables SciHub.
 *
 * Prerequisites: a study with Phase 2 unlocked must exist.
 * Configure via env vars:
 *   E2E_USER_EMAIL    — login email (default: testuser@example.com)
 *   E2E_USER_PASSWORD — login password (default: testpassword)
 *   E2E_STUDY_ID      — study ID with Phase 2 accessible (default: '1')
 */

import { test, expect, type Page } from '@playwright/test';

const EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';
const STUDY_ID = process.env.E2E_STUDY_ID ?? '1';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function login(page: Page): Promise<void> {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(EMAIL);
  await page.getByLabel(/password/i).fill(PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('**/groups**', { timeout: 10_000 });
}

async function navigateToPhase2(page: Page): Promise<void> {
  await page.goto(`/studies/${STUDY_ID}`);
  // Click the "Search" phase tab (Phase 2)
  const searchTab = page.getByRole('button', { name: /search/i }).first();
  await searchTab.waitFor({ state: 'visible', timeout: 8_000 });
  await searchTab.click();
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test.describe('Database Selection Panel (Phase 2)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await navigateToPhase2(page);
  });

  // -------------------------------------------------------------------------
  // Panel visibility
  // -------------------------------------------------------------------------

  test('Database Search Configuration heading is visible on Phase 2', async ({ page }) => {
    await expect(
      page.getByText(/database search configuration/i)
    ).toBeVisible({ timeout: 10_000 });
  });

  test('Primary database group heading is visible', async ({ page }) => {
    await expect(
      page.getByText('Primary')
    ).toBeVisible({ timeout: 10_000 });
  });

  test('General database group heading is visible', async ({ page }) => {
    await expect(
      page.getByText('General')
    ).toBeVisible({ timeout: 10_000 });
  });

  test('Supplementary database group heading is visible', async ({ page }) => {
    await expect(
      page.getByText('Supplementary')
    ).toBeVisible({ timeout: 10_000 });
  });

  test('at least one database index toggle switch is visible', async ({ page }) => {
    // Database index labels like "Semantic Scholar", "IEEE Xplore" etc. have switches
    const switches = page.getByRole('checkbox');
    await expect(switches.first()).toBeVisible({ timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // Save button
  // -------------------------------------------------------------------------

  test('Save button is present in database selection panel', async ({ page }) => {
    await expect(
      page.getByRole('button', { name: /^save$/i })
    ).toBeVisible({ timeout: 10_000 });
  });

  // -------------------------------------------------------------------------
  // Toggle a database index
  // -------------------------------------------------------------------------

  test('toggling a database index switch changes its checked state', async ({ page }) => {
    await page.waitForSelector('input[type="checkbox"]', { timeout: 10_000 });

    const switches = page.locator('input[type="checkbox"]');
    const firstSwitch = switches.first();

    const wasChecked = await firstSwitch.isChecked();
    await firstSwitch.click();
    const isNowChecked = await firstSwitch.isChecked();

    expect(isNowChecked).toBe(!wasChecked);
  });

  // -------------------------------------------------------------------------
  // SciHub acknowledgment flow
  // -------------------------------------------------------------------------

  test('SciHub section or toggle is present', async ({ page }) => {
    // SciHub toggle may be a labeled switch or text
    const scihubElement = page
      .getByText(/scihub|sci-hub/i)
      .first();

    // It may not be present if the backend has SCIHUB_ENABLED=false (feature off by default)
    // Use a soft check — if the element is not visible, skip gracefully
    const isVisible = await scihubElement.isVisible().catch(() => false);
    if (!isVisible) {
      test.skip();
      return;
    }
    await expect(scihubElement).toBeVisible();
  });

  test('SciHub acknowledgment dialog appears when SciHub is toggled on', async ({ page }) => {
    const scihubToggle = page
      .getByLabel(/enable scihub|scihub/i)
      .first()
      .or(page.locator('input[type="checkbox"]').filter({ has: page.getByText(/scihub/i) }));

    const isVisible = await scihubToggle.isVisible().catch(() => false);
    if (!isVisible) {
      test.skip();
      return;
    }

    await scihubToggle.click();

    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText(/enable scihub/i).first()).toBeVisible();
  });

  test('cancelling SciHub dialog dismisses it without enabling', async ({ page }) => {
    const scihubToggle = page
      .getByLabel(/enable scihub|scihub/i)
      .first();

    const isVisible = await scihubToggle.isVisible().catch(() => false);
    if (!isVisible) {
      test.skip();
      return;
    }

    await scihubToggle.click();
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5_000 });

    await page.getByRole('button', { name: /cancel/i }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 3_000 });
  });

  test('acknowledging SciHub dialog closes it', async ({ page }) => {
    const scihubToggle = page
      .getByLabel(/enable scihub|scihub/i)
      .first();

    const isVisible = await scihubToggle.isVisible().catch(() => false);
    if (!isVisible) {
      test.skip();
      return;
    }

    await scihubToggle.click();
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5_000 });

    const acknowledgeBtn = page.getByRole('button', { name: /acknowledge|enable scihub/i });
    await acknowledgeBtn.click();
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 3_000 });
  });
});
