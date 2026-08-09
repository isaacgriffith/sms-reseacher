/**
 * E2E spec: the Tertiary Study workflow (feature 012, US2).
 *
 * Tertiary was unreachable before T024 — `StudyPage` fell through every
 * `!isSLR && !isRapid` branch and silently rendered the mapping-study
 * workspace instead (G19). This is the first e2e coverage that workflow has
 * ever had (FR-021). It drives the full journey through the UI in one
 * sequential test, because each leg depends on state the previous leg wrote:
 *
 *   protocol → seed import → screening → extraction → report
 *
 * **TFIX7 / TFIX8 caveat — read before trusting legs 4 and 5 as reachability
 * evidence.** `scripts/seed_e2e_user.py` (`_seed_tertiary_study`) writes a
 * `QualityAssessmentScore` and two `validated` `TertiaryDataExtraction` rows
 * directly through the ORM, because:
 *
 *  - **TFIX7**: `tertiary_phase_gate.py` unlocks phase 4 only when a
 *    `QualityAssessmentScore` exists, and the only writer of that table is
 *    reached through `QualityScoreForm.tsx` — which nothing in the app
 *    imports but its own test. No UI path can create one.
 *  - **TFIX8**: phase 5 requires ≥2 extractions with
 *    `extraction_status == "validated"`, but `TertiaryExtractionForm.tsx`
 *    hardcodes `extraction_status: 'human_reviewed'` on save. Nothing in
 *    `backend/src` or `frontend/src` ever writes `"validated"`.
 *
 * So this spec reaching phases 4 and 5 demonstrates those panels render and
 * behave correctly for data that already exists — it does **not**
 * demonstrate a user can navigate there and produce that data themselves.
 * Both gaps are open in `tasks.md`; treating this test's pass as proof of
 * reachability for phases 4/5 would be exactly the "green and wrong"
 * artefact feature 012 exists to delete.
 *
 * **Frontend cache staleness, not a backend defect**: `useValidateTertiaryProtocol`
 * invalidates only the `tertiary-protocol` query key, not `['study', studyId]`
 * — the key `StudyPage` reads `unlocked_phases` from. `GET /studies/{id}`
 * itself is computed live (`get_tertiary_unlocked_phases` re-runs every
 * call), so the backend is correct the instant the protocol is validated; it
 * is the already-fetched React Query cache that is stale. This spec reloads
 * once after validating to observe the newly unlocked phases, which is a
 * real, deterministic step — not an `isVisible()` guard — but a user who
 * does not think to refresh would see every phase still locked.
 *
 * Prerequisites: `scripts/seed_e2e_user.py` has been run against the
 * backend's database. It seeds `E2E Tertiary Seed Study` with no protocol row
 * (deliberately — this journey validates one through the UI), two accepted
 * and two pending candidates, the TFIX7 quality score, and the TFIX8
 * extractions, and resets all of that (via `reset_tertiary_workspace`) on
 * every re-seed so this spec can run repeatedly.
 */

import { test, expect, type Page } from '@playwright/test';

const TEST_EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const TEST_PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';
const TEST_GROUP_ID = process.env.E2E_GROUP_ID ?? '1';

const TERTIARY_STUDY_NAME = process.env.E2E_TERTIARY_STUDY_NAME ?? 'E2E Tertiary Seed Study';
/** T006 in the seed script — an SMS with accepted papers, offerable as an import source. */
const SOURCE_STUDY_NAME = process.env.E2E_SOURCE_STUDY_NAME ?? 'E2E Source Mapping Study';

/** One of TERTIARY_ACCEPTED_PAPERS in the seed script — has the TFIX8 validated extraction. */
const TERTIARY_ACCEPTED_PAPER = 'Systematic reviews of test case prioritization: a tertiary study';
/** One of SOURCE_PAPERS in the seed script — imported into the Tertiary study by this spec. */
const SOURCE_PAPER_TITLE = 'A systematic mapping of DevOps adoption';

async function login(page: Page): Promise<void> {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(TEST_EMAIL);
  await page.getByLabel(/password/i).fill(TEST_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('**/groups**');
}

/**
 * Open the Tertiary study by name and land on its Workspace tab.
 *
 * A takeover study type (`STUDY_TYPE_TAKEOVER`) has `StudyPage` render a
 * two-button "🔗 Protocol Graph" / "🧭 Workspace" strip instead of the usual
 * `Phase 0…7` tabs, and `activePhase` defaults to 1 (Workspace), so opening
 * the study lands directly on `TertiaryStudyPage` — no extra click needed.
 */
async function openTertiaryWorkspace(page: Page): Promise<void> {
  await page.goto(`/groups/${TEST_GROUP_ID}/studies`);
  await page.getByText(TERTIARY_STUDY_NAME, { exact: true }).click();
  await page.waitForURL('**/studies/**');
  await expect(page.getByRole('button', { name: /🧭 Workspace/i })).toBeVisible({
    timeout: 10_000,
  });
  // TertiaryStudyPage's own Phase 1: Protocol panel, distinct from the outer
  // "Protocol Graph" tab.
  await expect(page.getByRole('heading', { name: /Tertiary Study Protocol/i })).toBeVisible({
    timeout: 10_000,
  });
}

/** Click one of TertiaryStudyPage's internal phase tabs (its own PhaseTabs, not StudyPage's). */
function innerPhaseTab(page: Page, pattern: RegExp) {
  return page.getByRole('button', { name: pattern });
}

test.describe('Tertiary workflow (US2) — protocol through report', () => {
  test('drives protocol, seed import, screening, extraction, and report through the UI', async ({
    page,
  }) => {
    await login(page);
    await openTertiaryWorkspace(page);

    // -----------------------------------------------------------------
    // Leg 1 — Protocol
    // -----------------------------------------------------------------
    await test.step('Protocol: fill, save, and validate', async () => {
      const form = page.getByRole('form', { name: /Tertiary Protocol form/i });
      await expect(form).toBeVisible();

      await form
        .getByLabel('background', { exact: true })
        .fill(
          'A tertiary review of secondary studies on software testing practices, seeded by ' +
            'the e2e run.',
        );
      await form
        .getByLabel('research_questions', { exact: true })
        .fill('What secondary study designs dominate the software testing literature?');
      await form
        .getByLabel('search_strategy', { exact: true })
        .fill('Search IEEE Xplore, ACM DL, and Scopus for secondary studies since 2015.');
      await form
        .getByLabel('inclusion_criteria', { exact: true })
        .fill('Published secondary study (SLR, SMS, or Rapid Review)');
      await form
        .getByLabel('exclusion_criteria', { exact: true })
        .fill('Primary study with no synthesis of prior work');

      // MUI Select: click the combobox trigger (accessible name comes from
      // its labelId, "Synthesis Approach" — distinct from the hidden native
      // input's aria-label "synthesis_approach" on the same element tree),
      // then click the option in the listbox it opens.
      await form.getByLabel('Synthesis Approach', { exact: true }).click();
      await page.getByRole('option', { name: 'Narrative', exact: true }).click();

      await form.getByRole('button', { name: /^save protocol$/i }).click();

      const validateButton = page.getByRole('button', { name: /^validate protocol$/i });
      await expect(validateButton).toBeEnabled({ timeout: 10_000 });
      await validateButton.click();

      await expect(page.getByText('Protocol validated. Phase 2 is now unlocked.')).toBeVisible({
        timeout: 10_000,
      });

      // The validate mutation invalidates only the protocol query, not
      // `['study', studyId]` — see the file docblock. Reload to pick up the
      // now-current `unlocked_phases` from a fresh GET /studies/{id}.
      await page.reload();
      await expect(page.getByRole('heading', { name: /Tertiary Study Protocol/i })).toBeVisible({
        timeout: 10_000,
      });
      await expect(innerPhaseTab(page, /Phase 2.*Search.*Import/i)).toBeEnabled({
        timeout: 10_000,
      });
    });

    // -----------------------------------------------------------------
    // Leg 2 — Seed import
    // -----------------------------------------------------------------
    await test.step('Seed import: import the source study into the Tertiary corpus', async () => {
      await innerPhaseTab(page, /Phase 2.*Search.*Import/i).click();
      await expect(page.getByRole('heading', { name: /Seed Imports/i })).toBeVisible({
        timeout: 10_000,
      });

      await page.getByRole('button', { name: /Import from Platform Study/i }).click();
      const dialog = page.getByRole('dialog', { name: /Import from Platform Study/i });
      await expect(dialog).toBeVisible({ timeout: 10_000 });

      await dialog.getByText(SOURCE_STUDY_NAME, { exact: false }).click();
      const importButton = dialog.getByRole('button', { name: /^import$/i });
      await expect(importButton).toBeEnabled();
      await importButton.click();

      await expect(dialog).not.toBeVisible({ timeout: 10_000 });
      await expect(page.getByText(SOURCE_STUDY_NAME, { exact: false })).toBeVisible({
        timeout: 10_000,
      });
      await expect(page.getByText(/\+2 added/)).toBeVisible({ timeout: 10_000 });
    });

    // -----------------------------------------------------------------
    // Leg 3 — Screening
    // -----------------------------------------------------------------
    await test.step('Screening: the queue lists candidates, including the imported paper', async () => {
      await innerPhaseTab(page, /Phase 3.*Screening/i).click();
      await expect(page.getByTestId('screening-view')).toBeVisible({ timeout: 10_000 });

      const queueItems = page.getByTestId('paper-queue-item');
      await expect(queueItems.first()).toBeVisible({ timeout: 10_000 });
      // Both the fixture's own accepted candidate and the paper just
      // imported from the source study are in the same study-scoped queue.
      await expect(queueItems.filter({ hasText: TERTIARY_ACCEPTED_PAPER })).toBeVisible();
      await expect(queueItems.filter({ hasText: SOURCE_PAPER_TITLE })).toBeVisible();
    });

    // -----------------------------------------------------------------
    // Leg 4 — Extraction
    // -----------------------------------------------------------------
    // TFIX7 caveat applies: phase 4 is reachable only because
    // `_seed_tertiary_study` wrote a `QualityAssessmentScore` no UI path can
    // create. See the file docblock.
    await test.step('Extraction: open a record and save it', async () => {
      await innerPhaseTab(page, /Phase 4.*Quality/i).click();
      await expect(
        page.getByRole('heading', { name: /Quality Assessment.*Extraction/i }),
      ).toBeVisible({ timeout: 10_000 });

      const extractionItem = page.getByText(TERTIARY_ACCEPTED_PAPER, { exact: false });
      await expect(extractionItem).toBeVisible({ timeout: 10_000 });
      // It carries the TFIX8-seeded "validated" status before this edit.
      await expect(page.getByText('validated', { exact: true }).first()).toBeVisible();
      await extractionItem.click();

      const keyFindings = page.getByLabel(/^Key Findings$/i);
      await expect(keyFindings).toBeVisible({ timeout: 10_000 });
      await keyFindings.fill(
        'Updated during the e2e run: test case prioritization dominates the corpus.',
      );

      await page.getByRole('button', { name: /^save extraction$/i }).click();

      // TFIX8: TertiaryExtractionForm hardcodes "human_reviewed" on save, so
      // the list item's status caption changes from "validated" to
      // "human_reviewed" — the deterministic, real-world signal that the
      // save round-tripped through the API, in the absence of any success
      // banner on this form.
      await expect(
        page
          .locator('div')
          .filter({ hasText: TERTIARY_ACCEPTED_PAPER })
          .getByText('human_reviewed', { exact: true })
          .first(),
      ).toBeVisible({ timeout: 10_000 });
    });

    // -----------------------------------------------------------------
    // Leg 5 — Report / Synthesis
    // -----------------------------------------------------------------
    // TFIX8 caveat applies: phase 5 is reachable only because
    // `_seed_tertiary_study` wrote two "validated" extractions no UI path
    // can produce. See the file docblock. This leg does not wait for the
    // synthesis job to complete — no ARQ worker is assumed to be running for
    // this spec — it only asserts the controls FR-021 requires are present
    // and that starting a run visibly begins.
    await test.step('Report: synthesis approach and Run Synthesis are offered', async () => {
      await innerPhaseTab(page, /Phase 5.*Synthesis/i).click();
      await expect(page.getByRole('heading', { name: /Synthesis.*Report/i })).toBeVisible({
        timeout: 10_000,
      });

      const approachSelect = page.getByRole('combobox').last();
      await expect(approachSelect).toContainText('Narrative Synthesis');
      await approachSelect.click();
      await page.getByRole('option', { name: 'Thematic Analysis', exact: true }).click();
      await expect(approachSelect).toContainText('Thematic Analysis');

      const runButton = page.getByRole('button', { name: /run synthesis/i });
      await expect(runButton).toBeEnabled();
      await runButton.click();

      await expect(page.getByText(/running…/i)).toBeVisible({ timeout: 10_000 });
    });
  });
});
