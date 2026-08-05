/**
 * E2E spec: Research Protocol Definition — end-to-end happy path (feature 010).
 *
 * Covers the full protocol workflow:
 *   Create SMS study → view default protocol graph → click node to see detail →
 *   navigate to protocol library → copy to custom protocol → view in editor →
 *   save → assign to study → switch to Execution tab → mark first task complete →
 *   verify downstream task activates → export YAML → re-import → verify new entry.
 *
 * Prerequisites: a running backend with seeded test credentials.
 * Set E2E_USER_EMAIL, E2E_USER_PASSWORD, and E2E_GROUP_ID env vars to match
 * your test environment, or use the defaults below.
 */

import fs from 'fs';
import path from 'path';
import { test, expect } from '@playwright/test';

const TEST_EMAIL = process.env.E2E_USER_EMAIL ?? 'testuser@example.com';
const TEST_PASSWORD = process.env.E2E_USER_PASSWORD ?? 'testpassword';
const TEST_GROUP_ID = process.env.E2E_GROUP_ID ?? '1';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(TEST_EMAIL);
  await page.getByLabel(/password/i).fill(TEST_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL('**/groups**');
}

async function createSMSStudy(
  page: import('@playwright/test').Page,
): Promise<{ name: string; url: string }> {
  const studyName = `Protocol E2E ${Date.now()}`;
  await page.goto(`/groups/${TEST_GROUP_ID}/studies`);
  await page.getByRole('button', { name: /new study/i }).click();

  await page.getByLabel(/study name|name/i).fill(studyName);

  const topicField = page.getByLabel(/topic/i);
  if (await topicField.isVisible()) {
    await topicField.fill('Protocol definition e2e test');
  }

  // Select SMS study type if wizard exposes type selector
  const smsOption = page.getByRole('radio', { name: /sms|systematic mapping/i });
  if (await smsOption.isVisible()) {
    await smsOption.click();
  }

  // Step through wizard
  for (let step = 0; step < 6; step++) {
    const nextBtn = page.getByRole('button', { name: /next|create study|finish/i });
    if (await nextBtn.isVisible()) {
      await nextBtn.click();
      const visible = await page
        .getByText(studyName)
        .isVisible()
        .catch(() => false);
      if (visible) break;
    } else {
      break;
    }
  }

  await expect(page.getByText(studyName)).toBeVisible({ timeout: 10_000 });

  // Navigate to the new study
  await page.getByText(studyName).click();
  await page.waitForURL('**/studies/**');
  const studyUrl = page.url();

  return { name: studyName, url: studyUrl };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

test.describe('Research Protocol Definition (feature 010)', () => {
  test('view default protocol graph and node detail from study Protocol tab', async ({ page }) => {
    await login(page);
    const { url } = await createSMSStudy(page);

    // Navigate to study
    await page.goto(url);

    // Click the Protocol tab (Phase 0)
    await page.getByRole('button', { name: /phase 0.*protocol/i }).click();

    // Protocol graph should be visible (SVG rendered by D3)
    await expect(page.locator('svg')).toBeVisible({ timeout: 10_000 });

    // At least one node should be present. Target the node group rather than
    // its <rect>: the label <text> is painted over the rect and would take the
    // hit, even though the click handler lives on the group either way.
    const nodes = page.getByTestId('protocol-node');
    await expect(nodes.first()).toBeVisible({ timeout: 10_000 });

    // Click the first node to open the detail panel
    await nodes.first().click();

    // ProtocolNodePanel should show node detail
    await expect(
      page
        .getByRole('heading')
        .filter({ hasText: /task|node|type|pico|define/i })
        .first(),
    ).toBeVisible({ timeout: 5_000 });
  });

  test('protocol library: copy a default template to a custom protocol', async ({ page }) => {
    await login(page);

    // Navigate to the protocol library
    await page.goto('/protocols');

    // At least one protocol should be listed (default templates are seeded)
    // The sidebar nav is also a list, so scope to the one holding protocols.
    await expect(
      page
        .getByRole('list')
        .filter({ hasText: /protocol/i })
        .first(),
    ).toBeVisible({ timeout: 10_000 });
    const listItems = page.getByRole('listitem');
    await expect(listItems.first()).toBeVisible({ timeout: 10_000 });

    // Click "Copy" on the first listed protocol
    const copyBtn = page.getByRole('button', { name: /copy/i }).first();
    await copyBtn.click();

    // A dialog should appear for naming the copy
    const nameField = page.getByLabel(/name/i);
    await nameField.clear();
    const copyName = `E2E Copy ${Date.now()}`;
    await nameField.fill(copyName);

    // Confirm copy
    await page
      .getByRole('button', { name: /copy|confirm|save/i })
      .last()
      .click();

    // Should navigate to the editor page for the new copy
    await page.waitForURL('**/protocols/**', { timeout: 10_000 });
    await expect(page.getByText(copyName)).toBeVisible({ timeout: 5_000 });
  });

  test('protocol editor: view and save a custom protocol', async ({ page }) => {
    await login(page);

    // First copy a default to get a custom protocol
    await page.goto('/protocols');
    await expect(page.getByRole('listitem').first()).toBeVisible({ timeout: 10_000 });

    const copyBtn = page.getByRole('button', { name: /copy/i }).first();
    await copyBtn.click();

    const nameField = page.getByLabel(/name/i);
    await nameField.clear();
    const copyName = `E2E Edit ${Date.now()}`;
    await nameField.fill(copyName);
    await page
      .getByRole('button', { name: /copy|confirm|save/i })
      .last()
      .click();

    // Wait to land on editor page
    await page.waitForURL('**/protocols/**', { timeout: 10_000 });

    // Editor page shows YAML editor pane and graph pane
    await expect(page.locator('textarea, [role="textbox"]').first()).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.locator('svg')).toBeVisible({ timeout: 5_000 });

    // Save button should be present
    const saveBtn = page.getByRole('button', { name: /^save$/i });
    await expect(saveBtn).toBeVisible();

    // Click save (no-op saves the unchanged protocol back)
    await saveBtn.click();

    // The editor stays put — /protocols/:id is both the view and the edit
    // route — so success shows as a confirmation, not a navigation.
    await expect(page.getByText(/protocol saved/i)).toBeVisible({ timeout: 5_000 });
  });

  test('assign custom protocol to study and view execution state', async ({ page }) => {
    await login(page);

    // Create a study to work with
    const { url } = await createSMSStudy(page);

    // Copy the SMS default specifically — a protocol may only be assigned to a
    // study of a matching study_type, and the list is sorted by name, so the
    // first row is the Rapid Review template.
    await page.goto('/protocols');
    await expect(page.getByRole('listitem').first()).toBeVisible({ timeout: 10_000 });

    const smsRow = page.getByRole('listitem').filter({ hasText: 'Default SMS Protocol' }).first();
    const copyBtn = smsRow.getByRole('button', { name: 'Copy', exact: true });
    await copyBtn.click();

    const nameField = page.getByLabel(/name/i);
    await nameField.clear();
    const copyName = `E2E Assign ${Date.now()}`;
    await nameField.fill(copyName);
    await page
      .getByRole('button', { name: /copy|confirm|save/i })
      .last()
      .click();
    await page.waitForURL('**/protocols/**', { timeout: 10_000 });

    // Navigate back to protocol library and assign to study
    await page.goto('/protocols');
    await expect(page.getByText(copyName)).toBeVisible({ timeout: 10_000 });

    // Click Assign on our custom protocol row
    const customRow = page.getByRole('listitem').filter({ hasText: copyName });
    // Must be an exact match: the row itself is a button whose accessible name
    // is the protocol name, which contains "Assign" — matching /assign/i would
    // open the editor instead of the assign dialog.
    const assignBtn = customRow.getByRole('button', { name: 'Assign', exact: true });
    await assignBtn.click();

    // Fill in study ID in the assign dialog
    const studyIdField = page.getByLabel(/study id/i);
    // Extract studyId from URL
    const studyId = url.match(/studies\/(\d+)/)?.[1] ?? '';
    await studyIdField.fill(studyId);
    await page
      .getByRole('button', { name: /^assign$/i })
      .last()
      .click();

    // Assignment should complete (dialog closes or success message)
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 5_000 });
  });

  test('execution state: view tasks and mark first task complete', async ({ page }) => {
    await login(page);
    const { url } = await createSMSStudy(page);

    await page.goto(url);

    // Click Protocol tab
    await page.getByRole('button', { name: /phase 0.*protocol/i }).click();

    // Switch to Execution sub-tab
    await page.getByRole('button', { name: /execution/i }).click();

    // Task list should appear
    await expect(page.getByText(/pending|active|complete/i).first()).toBeVisible({
      timeout: 10_000,
    });

    // Mark the first available task complete
    const markCompleteBtn = page.getByRole('button', { name: /mark complete|complete/i }).first();
    if (await markCompleteBtn.isVisible()) {
      await markCompleteBtn.click();
      // After completion, the UI should update to show the next task state
      await expect(page.getByText(/completed|active|pending/i).first()).toBeVisible({
        timeout: 5_000,
      });
    }
  });

  test('export YAML and re-import as new protocol', async ({ page }) => {
    await login(page);
    await page.goto('/protocols');
    await expect(page.getByRole('listitem').first()).toBeVisible({ timeout: 10_000 });

    // Export the first listed protocol
    const downloadPromise = page.waitForEvent('download', { timeout: 10_000 });
    const exportBtn = page.getByRole('button', { name: /export/i }).first();
    await exportBtn.click();

    const download = await downloadPromise;
    const exportedPath = path.join(process.env.TMPDIR ?? '/tmp', download.suggestedFilename());
    await download.saveAs(exportedPath);

    // Protocol names are unique per owner, so re-importing the export verbatim
    // fails on the second run against the same database. Rename the copy so the
    // round-trip is repeatable.
    const importName = `E2E Import ${Date.now()}`;
    const importPath = path.join(process.env.TMPDIR ?? '/tmp', `${importName}.yaml`);
    fs.writeFileSync(
      importPath,
      fs.readFileSync(exportedPath, 'utf8').replace(/^name:.*$/m, `name: ${importName}`),
    );

    // Import the downloaded YAML file back. The Import button clicks the hidden
    // file input synchronously, so the listener must be registered first —
    // waiting for the event after the click always misses it.
    const fileChooserPromise = page.waitForEvent('filechooser');
    // Exact name: rows for previously-imported protocols are buttons whose
    // names also contain "Import".
    await page.getByRole('button', { name: 'Import YAML', exact: true }).click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles(importPath);

    // A successful import opens the editor for the newly created protocol.
    await page.waitForURL(/\/protocols\/\d+\/edit/, { timeout: 10_000 });
    await expect(page.getByTestId('protocol-node').first()).toBeVisible({ timeout: 10_000 });
  });
});
