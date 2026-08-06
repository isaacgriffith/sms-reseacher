/**
 * E2E spec: Create a new study via the New Study wizard.
 *
 * Prerequisites: the dev server is running and the backend API is reachable.
 * The tests authenticate as a seeded test user before navigating to the
 * studies list. All API interactions use the live backend in integration mode
 * (or a mock API server configured via PLAYWRIGHT_BASE_URL).
 */

import { test, expect } from '@playwright/test';

// Seeded test credentials — must exist in the running backend.
const TEST_EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const TEST_PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';
const TEST_GROUP_ID = process.env.E2E_GROUP_ID ?? '1';

/**
 * Log in via the UI login form and wait for the groups page.
 */
async function loginAndNavigate(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(TEST_EMAIL);
  await page.getByLabel(/password/i).fill(TEST_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  // After login, the app redirects to /groups
  await page.waitForURL('**/groups**');
}

/**
 * Fill step 1 of NewStudyWizard and click through to the end.
 *
 * The wizard always has five steps: step 1 requires name + topic (its Next
 * button calls trigger() on both), steps 2–4 are optional, and step 5 submits.
 * That is fixed, so the walk is unconditional — the previous version probed
 * each control with isVisible(), which has no timeout and silently skipped
 * fields whenever it lost the race with the render.
 */
async function fillWizard(
  page: import('@playwright/test').Page,
  studyName: string,
  opts: { topic: string; studyType?: string },
) {
  await page.getByLabel(/study name/i).fill(studyName);
  await page.getByLabel(/topic/i).fill(opts.topic);
  if (opts.studyType) {
    await page.getByLabel(/study type/i).selectOption(opts.studyType);
  }

  // Drive off the wizard's own "Step N of 5" indicator so each click waits for
  // the step it belongs to, rather than firing a fixed number of times and
  // racing the re-render.
  for (let step = 1; step < 5; step++) {
    await expect(page.getByText(`Step ${step} of 5`)).toBeVisible({ timeout: 10_000 });
    // Anchored + case-insensitive: MUI uppercases button labels via CSS, and
    // Chromium computes the accessible name from the rendered text, so
    // { name: 'Next', exact: true } is case-sensitive against "NEXT".
    await page.getByRole('button', { name: /^next$/i }).click();
  }
  await expect(page.getByText('Step 5 of 5')).toBeVisible({ timeout: 10_000 });
  await page.getByRole('button', { name: /^create study$/i }).click();
}

test.describe('Create study', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndNavigate(page);
  });

  test('navigates to studies page for the test group', async ({ page }) => {
    await page.goto(`/groups/${TEST_GROUP_ID}/studies`);
    await expect(page.getByRole('heading', { name: /studies/i })).toBeVisible();
  });

  test('opens New Study wizard when New Study button is clicked', async ({ page }) => {
    await page.goto(`/groups/${TEST_GROUP_ID}/studies`);
    await page.getByRole('button', { name: /new study/i }).click();
    // The wizard should be visible — look for its first step heading or form field
    await expect(
      page.getByRole('dialog').or(page.locator('[data-testid="new-study-wizard"]')).first(),
    ).toBeVisible();
  });

  test('shows validation error when submitting empty study name', async ({ page }) => {
    await page.goto(`/groups/${TEST_GROUP_ID}/studies`);
    await page.getByRole('button', { name: /new study/i }).click();

    // Try to proceed without filling in the study name
    const nextBtn = page.getByRole('button', { name: /next|create|submit/i }).first();
    await nextBtn.click();

    // A validation message should appear
    await expect(page.getByText(/required|cannot be empty/i).first()).toBeVisible();
  });

  test('creates a study and shows it in the list', async ({ page }) => {
    const studyName = `E2E Study ${Date.now()}`;

    await page.goto(`/groups/${TEST_GROUP_ID}/studies`);
    await page.getByRole('button', { name: /new study/i }).click();

    await fillWizard(page, studyName, { topic: 'Automated testing in agile projects' });

    // The new study should appear in the list
    await expect(page.getByText(studyName)).toBeVisible({ timeout: 10_000 });
  });
});
