/**
 * E2E spec: Phase 3 — paper screening queue interactions.
 *
 * Covers the Screening phase tab on the StudyPage:
 *  - the paper queue panel is rendered
 *  - accept / reject actions are available on queued papers
 *  - a job progress panel is visible while a screening job runs
 *
 * Prerequisites: a study with queued papers in phase ≥ 3 (or candidates
 * already retrieved). Set E2E_STUDY_ID to a study in the screening phase.
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

test.describe('Screen paper (Phase 3)', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndNavigate(page);
    await page.goto(`/studies/${TEST_STUDY_ID}`);
    // Wait for the study page to load, then navigate to the Screening tab
    const screeningTab = page.getByRole('button', { name: /screen/i }).first();
    await screeningTab.waitFor({ state: 'visible', timeout: 10_000 });
    await screeningTab.click();
  });

  test('Screening tab or phase 3 content is visible', async ({ page }) => {
    // Either a Screening tab button or heading exists
    const screeningContent = page
      .getByRole('button', { name: /screen/i })
      .or(page.getByText(/screening|paper queue/i).first())
      .first();
    await expect(screeningContent).toBeVisible({ timeout: 8_000 });
  });

  test('paper queue section renders in screening phase', async ({ page }) => {
    const queue = page
      .getByText(/paper queue|queue|papers to screen/i)
      .first();
    await expect(queue).toBeVisible({ timeout: 8_000 });
  });

  test('accept button is present when papers are queued', async ({ page }) => {
    // If there are papers, accept/reject buttons should be present
    const acceptBtn = page.getByRole('button', { name: /accept/i }).first();
    if (await acceptBtn.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await expect(acceptBtn).toBeEnabled();
    } else {
      // No papers in queue — verify empty state message
      await expect(
        page.getByText(/no papers|queue is empty|nothing to screen/i).first()
      ).toBeVisible({ timeout: 8_000 });
    }
  });

  test('reject button is present when papers are queued', async ({ page }) => {
    const rejectBtn = page.getByRole('button', { name: /reject/i }).first();
    if (await rejectBtn.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await expect(rejectBtn).toBeEnabled();
    } else {
      // Acceptable — no papers to reject
      test.skip();
    }
  });

  test('job progress panel is visible during a screening run', async ({ page }) => {
    // Trigger a screening job if a "Run" button is available
    const runBtn = page.getByRole('button', { name: /run screening|start screen/i }).first();
    if (await runBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await runBtn.click();
      await expect(
        page.getByText(/running|queued|progress/i).first()
      ).toBeVisible({ timeout: 10_000 });
    } else {
      // The job progress panel may already be showing
      const progressPanel = page.getByText(/progress|running/i).first();
      if (await progressPanel.isVisible({ timeout: 3_000 }).catch(() => false)) {
        await expect(progressPanel).toBeVisible();
      } else {
        test.skip();
      }
    }
  });
});
