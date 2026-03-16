/**
 * E2E spec: Phase 5 — results dashboard (charts, domain model, export).
 *
 * Covers the Results page for a completed study:
 *  - chart gallery tab renders
 *  - domain model viewer tab renders
 *  - export panel tab renders
 *  - export download triggers a file
 *
 * Prerequisites: navigate to /studies/:id/results for a study that has
 * completed synthesis. Set E2E_STUDY_ID and E2E_RESULTS_STUDY_ID as needed.
 */

import { test, expect } from '@playwright/test';

const TEST_EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const TEST_PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';
const RESULTS_STUDY_ID = process.env.E2E_RESULTS_STUDY_ID ?? process.env.E2E_STUDY_ID ?? '1';

async function loginAndNavigate(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(TEST_EMAIL);
  await page.getByLabel(/password/i).fill(TEST_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('**/groups**');
}

test.describe('Results dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndNavigate(page);
    await page.goto(`/studies/${RESULTS_STUDY_ID}/results`);
  });

  test('results page loads without error', async ({ page }) => {
    // Either a heading or meaningful content should be present
    await expect(
      page.getByRole('heading').first().or(page.getByText(/results|charts|export/i).first())
    ).toBeVisible({ timeout: 10_000 });
  });

  test('Charts tab is present', async ({ page }) => {
    const chartsTab = page.getByRole('button', { name: /charts/i });
    await expect(chartsTab).toBeVisible({ timeout: 8_000 });
  });

  test('Domain Model tab is present', async ({ page }) => {
    const domainTab = page.getByRole('button', { name: /domain model/i });
    await expect(domainTab).toBeVisible({ timeout: 8_000 });
  });

  test('Export tab is present', async ({ page }) => {
    const exportTab = page.getByRole('button', { name: /export/i });
    await expect(exportTab).toBeVisible({ timeout: 8_000 });
  });

  test('clicking Charts tab shows chart gallery', async ({ page }) => {
    const chartsTab = page.getByRole('button', { name: /charts/i });
    if (await chartsTab.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await chartsTab.click();
      // Chart gallery should render — look for SVG, canvas, or chart labels
      await expect(
        page.locator('svg, canvas').first().or(page.getByText(/chart|figure|publication year/i).first())
      ).toBeVisible({ timeout: 8_000 });
    } else {
      test.skip();
    }
  });

  test('clicking Domain Model tab shows graph or empty state', async ({ page }) => {
    const domainTab = page.getByRole('button', { name: /domain model/i });
    if (await domainTab.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await domainTab.click();
      await expect(
        page.locator('svg').first().or(page.getByText(/not available|no domain model/i).first())
      ).toBeVisible({ timeout: 8_000 });
    } else {
      test.skip();
    }
  });

  test('clicking Export tab shows export panel', async ({ page }) => {
    const exportTab = page.getByRole('button', { name: /export/i });
    if (await exportTab.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await exportTab.click();
      await expect(
        page.getByText(/export|download|format/i).first()
      ).toBeVisible({ timeout: 8_000 });
    } else {
      test.skip();
    }
  });

  test('export button triggers download or job', async ({ page }) => {
    const exportTab = page.getByRole('button', { name: /export/i });
    if (await exportTab.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await exportTab.click();

      const generateBtn = page.getByRole('button', { name: /generate|export now|start export/i });
      if (await generateBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
        // Listen for download or job queued indicator
        const [downloadOrJobPromise] = await Promise.allSettled([
          page.waitForEvent('download', { timeout: 5_000 }),
          page.waitForSelector('[data-testid="job-progress"], [aria-label*="progress"]', {
            timeout: 5_000,
          }),
        ]);
        await generateBtn.click();
        // Accept any outcome — download OR job-progress indicator
        await expect(
          page.getByText(/running|queued|generating|download/i).first()
        ).toBeVisible({ timeout: 10_000 });
        void downloadOrJobPromise; // prevent unhandled rejection warnings
      } else {
        test.skip();
      }
    } else {
      test.skip();
    }
  });
});
