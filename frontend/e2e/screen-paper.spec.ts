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
    const queue = page.getByText(/paper queue|queue|papers to screen/i).first();
    await expect(queue).toBeVisible({ timeout: 8_000 });
  });

  // GAP: ReviewerPanel — a complete accept/reject/duplicate UI that POSTs to
  // /studies/{id}/papers/{candidate}/decisions — and PaperCard are both fully
  // built but imported by nothing, so Phase 3 renders a read-only PaperQueue
  // and a human cannot record a screening decision at all.
  // See docs/feature-gaps.md (G18).
  test.fixme('accept button is present when papers are queued', async ({ page }) => {
    await expect(page.getByRole('button', { name: /accept/i }).first()).toBeEnabled();
  });

  test.fixme('reject button is present when papers are queued', async ({ page }) => {
    await expect(page.getByRole('button', { name: /reject/i }).first()).toBeEnabled();
  });

  // GAP: AI screening *is* reachable — "Run Full Search" (StudyPage.tsx) starts
  // a job whose search_job.py pipeline screens every candidate, and its progress
  // does render. What is missing is a way to re-screen an existing candidate set
  // against revised criteria, which is what this test's /run screening/ button
  // would trigger. See docs/feature-gaps.md (G18, "Correction — 2026-08-06").
  test.fixme('job progress panel is visible during a screening run', async ({ page }) => {
    await page.getByRole('button', { name: /run screening/i }).click();
    await expect(page.getByText(/running|queued|progress/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });
});
