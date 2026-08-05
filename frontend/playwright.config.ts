/**
 * Playwright configuration for end-to-end tests.
 *
 * Tests run against the local Vite dev server (or CI preview URL).
 * Only Chromium is used for speed; add webkit/firefox in CI matrix as needed.
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  /* Run tests in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Limit workers on CI */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use */
  reporter: 'html',
  use: {
    /* Base URL so tests can use relative paths like page.goto('/') */
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:5173',
    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',
    /* Capture screenshot on failure for debugging */
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  /*
   * Start the Vite dev server before tests, in CI as well as locally.
   * The dev server is what proxies /api to the backend (see vite.config.ts),
   * so `npm run preview` is not a substitute. When PLAYWRIGHT_BASE_URL points
   * at an already-running stack (e.g. Docker Compose), skip starting one.
   */
  webServer: process.env.PLAYWRIGHT_BASE_URL
    ? undefined
    : {
        command: 'npm run dev',
        url: 'http://localhost:5173',
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
});
