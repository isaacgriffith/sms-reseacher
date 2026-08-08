/**
 * E2E spec: Phase 3 — recording a screening decision.
 *
 * Covers the Screening phase on the StudyPage, for the two study types that
 * reach it down different paths:
 *
 *  - the queue renders and a row can be selected
 *  - accept and reject controls become available once a paper is selected
 *  - a decision is recorded end-to-end, with reasons and an annotation, and the
 *    queue reflects the new status without the reviewer doing anything further
 *
 * Studies are opened by **name** rather than by id. `scripts/seed_e2e_user.py`
 * assigns ids in creation order, so the SLR study's id depends on what the
 * database already held — its name does not.
 *
 * Prerequisites: `scripts/seed_e2e_user.py` has been run against the backend's
 * database. It seeds both studies at phase 3 with pending candidates, and
 * clears any decision an earlier run of this spec recorded on them.
 */

import { test, expect, type Page } from '@playwright/test';

const TEST_EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const TEST_PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';
const TEST_GROUP_ID = process.env.E2E_GROUP_ID ?? '1';

const SMS_STUDY_NAME = process.env.E2E_STUDY_NAME ?? 'E2E Seed Study';
const SLR_STUDY_NAME = process.env.E2E_SLR_STUDY_NAME ?? 'E2E SLR Seed Study';

/** A pending candidate on the SMS study — SEED_PAPERS[0] in the seed script. */
const SMS_PENDING_PAPER = 'Continuous integration practices in agile teams';
/** A pending candidate on the SLR study — SLR_PAPERS[0] in the seed script. */
const SLR_PENDING_PAPER = 'Effectiveness of code review at scale';

async function login(page: Page): Promise<void> {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(TEST_EMAIL);
  await page.getByLabel(/password/i).fill(TEST_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('**/groups**');
}

/** Open the named study from the group's study list and land on its Screening phase. */
async function openScreening(page: Page, studyName: string): Promise<void> {
  await page.goto(`/groups/${TEST_GROUP_ID}/studies`);
  await page.getByText(studyName, { exact: true }).click();

  // The tab's accessible name is its whole rendered text — icon, "Phase 3:",
  // the label, and a padlock when locked. Anchoring on "Screening" alone
  // matches nothing.
  const screeningTab = page.getByRole('button', { name: /phase 3: screening/i });
  await expect(screeningTab).toBeEnabled({ timeout: 10_000 });
  await screeningTab.click();
  await expect(page.getByTestId('screening-view')).toBeVisible({ timeout: 10_000 });
}

/** Select the queue row for *title* and wait for its reviewer panel. */
async function selectPaper(page: Page, title: string) {
  const row = page.getByTestId('paper-queue-item').filter({ hasText: title });
  await expect(row).toBeVisible({ timeout: 10_000 });
  await row.click();
  await expect(page.getByTestId('reviewer-panel')).toBeVisible();
  return row;
}

/**
 * Record a decision through the reviewer panel: outcome, one criterion reason,
 * and a free-text annotation.
 */
async function recordDecision(
  page: Page,
  outcome: 'accepted' | 'rejected',
  annotation: string,
): Promise<void> {
  const panel = page.getByTestId('reviewer-panel');

  // MUI capitalises the label via CSS, which does not change the accessible
  // name — that still comes from the rendered text node, lower case.
  await panel.getByRole('button', { name: outcome, exact: true }).click();

  // The reason selector renders only once an outcome is chosen, and only for a
  // study that has criteria (FR-002 — reasons are drawn from the study's own).
  await panel.getByRole('checkbox').first().check();

  await panel.getByPlaceholder(/optional annotation/i).fill(annotation);
  await panel.getByRole('button', { name: /^submit decision$/i }).click();
}

test.describe('Screen paper (Phase 3) — SMS study', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await openScreening(page, SMS_STUDY_NAME);
  });

  test('the paper queue lists candidate papers', async ({ page }) => {
    await expect(page.getByTestId('paper-queue-item').first()).toBeVisible();
    await expect(
      page.getByTestId('paper-queue-item').filter({ hasText: SMS_PENDING_PAPER }),
    ).toBeVisible();
  });

  test('selecting a paper opens its card and reviewer panel', async ({ page }) => {
    await selectPaper(page, SMS_PENDING_PAPER);
    await expect(page.getByTestId('paper-card')).toBeVisible();
  });

  test('accept button is enabled once a queued paper is selected', async ({ page }) => {
    await selectPaper(page, SMS_PENDING_PAPER);
    await expect(
      page.getByTestId('reviewer-panel').getByRole('button', { name: 'accepted', exact: true }),
    ).toBeEnabled();
  });

  test('reject button is enabled once a queued paper is selected', async ({ page }) => {
    await selectPaper(page, SMS_PENDING_PAPER);
    await expect(
      page.getByTestId('reviewer-panel').getByRole('button', { name: 'rejected', exact: true }),
    ).toBeEnabled();
  });

  test('records an accept decision, and the queue reflects it', async ({ page }) => {
    const annotation = 'Accepted during the SMS e2e run.';
    const row = await selectPaper(page, SMS_PENDING_PAPER);

    await recordDecision(page, 'accepted', annotation);

    await expect(page.getByText('Decision submitted.')).toBeVisible({ timeout: 10_000 });

    // FR-003 — the queue updates without the reviewer taking further action.
    await expect(row.getByText('accepted', { exact: true })).toBeVisible({ timeout: 10_000 });

    // The annotation round-trips through the API and back into the paper card,
    // which is what makes it a stored field rather than local form state.
    await expect(page.getByTestId('decision-annotation').first()).toContainText(annotation);
  });
});

test.describe('Screen paper (Phase 3) — SLR study', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await openScreening(page, SLR_STUDY_NAME);
  });

  test('records a reject decision, and the queue reflects it', async ({ page }) => {
    const annotation = 'Rejected during the SLR e2e run.';
    const row = await selectPaper(page, SLR_PENDING_PAPER);

    await recordDecision(page, 'rejected', annotation);

    await expect(page.getByText('Decision submitted.')).toBeVisible({ timeout: 10_000 });
    await expect(row.getByText('rejected', { exact: true })).toBeVisible({ timeout: 10_000 });
    await expect(page.getByTestId('decision-annotation').first()).toContainText(annotation);
  });

  test('the inter-rater agreement panel accompanies the SLR queue', async ({ page }) => {
    // SLR reaches ScreeningView through SLRScreeningView, which adds this panel.
    // Asserting it is what distinguishes the SLR path from the SMS one.
    await expect(page.getByText(/inter-rater|agreement/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });

  // GAP: re-screening an existing candidate set against revised criteria is
  // US4's control (T049), not US1's. AI screening during a *search* is already
  // reachable — "Run Full Search" starts a job whose pipeline screens every
  // candidate — but nothing yet re-runs it over papers already retrieved, which
  // is what this test's /run screening/ button would trigger.
  // See specs/012-wire-up-unreachable-workflows/tasks.md (T049).
  test.fixme('job progress panel is visible during a screening run', async ({ page }) => {
    await page.getByRole('button', { name: /run screening/i }).click();
    await expect(page.getByText(/running|queued|progress/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });
});
