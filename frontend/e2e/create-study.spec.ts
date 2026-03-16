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
    await expect(page.getByRole('dialog').or(page.locator('[data-testid="new-study-wizard"]'))).toBeVisible();
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

    // Fill in study name
    await page.getByLabel(/study name|name/i).fill(studyName);

    // Fill in topic if present
    const topicField = page.getByLabel(/topic/i);
    if (await topicField.isVisible()) {
      await topicField.fill('Automated testing in agile projects');
    }

    // Submit the wizard (may be multi-step — keep clicking Next until done)
    for (let step = 0; step < 5; step++) {
      const nextBtn = page.getByRole('button', { name: /next|create study|finish/i });
      if (await nextBtn.isVisible()) {
        await nextBtn.click();
        // If we've reached the list (wizard closed), stop
        if (await page.getByText(studyName).isVisible().catch(() => false)) break;
      } else {
        break;
      }
    }

    // The new study should appear in the list
    await expect(page.getByText(studyName)).toBeVisible({ timeout: 10_000 });
  });
});
