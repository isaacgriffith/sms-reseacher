/**
 * E2E spec: Phase 2 — configure search strings and run paper retrieval.
 *
 * Covers the Search phase tab on the StudyPage:
 *  - viewing the criteria form
 *  - editing the search string
 *  - triggering a test/retest run
 *
 * Prerequisites: a study in phase ≥ 2 must exist. Set E2E_STUDY_ID to its id.
 */

import { test, expect } from '@playwright/test';

const TEST_EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const TEST_PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';
const TEST_STUDY_ID = process.env.E2E_STUDY_ID ?? '1';

async function loginAndNavigate(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(TEST_EMAIL);
  await page.getByLabel(/password/i).fill(TEST_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('**/groups**');
}

test.describe('Search papers (Phase 2)', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndNavigate(page);
    await page.goto(`/studies/${TEST_STUDY_ID}`);
    // Navigate to the Search tab. Match the phase tab specifically — once the
    // tab is open its panel also renders a "Run Test Search" button, so a bare
    // /search/i is ambiguous under Playwright strict mode.
    await page.getByRole('button', { name: /phase 2: search/i }).click();
  });

  test('Search tab is visible on the study page', async ({ page }) => {
    await expect(page.getByRole('button', { name: /phase 2: search/i })).toBeVisible();
  });

  test('criteria form is rendered in the Search tab', async ({ page }) => {
    // The CriteriaForm or its container should be visible
    const criteriaSection = page
      .getByText(/inclusion criteria|exclusion criteria|criteria/i)
      .first();
    await expect(criteriaSection).toBeVisible({ timeout: 8_000 });
  });

  test('search string editor is rendered in the Search tab', async ({ page }) => {
    const editorSection = page.getByText(/search string|query/i).first();
    await expect(editorSection).toBeVisible({ timeout: 8_000 });
  });

  test('test/retest panel is rendered in the Search tab', async ({ page }) => {
    const testRetestSection = page.getByText(/test.*retest|retest|run test/i).first();
    await expect(testRetestSection).toBeVisible({ timeout: 8_000 });
  });

  test('clicking run test queues a test search', async ({ page }) => {
    // The seed creates an active SearchString, so the button is always enabled.
    // The previous version guarded on isVisible() with no timeout — an
    // instantaneous check that raced the render, so this test skipped itself
    // on roughly half of runs instead of asserting anything.
    const runBtn = page.getByRole('button', { name: /run test search/i });
    await expect(runBtn).toBeEnabled({ timeout: 10_000 });

    await runBtn.click();

    await expect(page.getByText(/test search queued/i)).toBeVisible({ timeout: 10_000 });
  });
});
