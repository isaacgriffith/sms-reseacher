/**
 * Unit tests for reportApi.ts (feature 007, T085).
 *
 * Covers the downloadSLRReport function which uses fetch + URL.createObjectURL
 * to trigger a browser file download.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { downloadSLRReport } from '../reportApi';

// jsdom does not implement URL.createObjectURL / revokeObjectURL — define them
if (!URL.createObjectURL) {
  URL.createObjectURL = vi.fn().mockReturnValue('blob:test-url');
}
if (!URL.revokeObjectURL) {
  URL.revokeObjectURL = vi.fn();
}

describe('downloadSLRReport', () => {
  let appendChildSpy: ReturnType<typeof vi.spyOn>;
  let removeChildSpy: ReturnType<typeof vi.spyOn>;
  let createObjectURLSpy: ReturnType<typeof vi.spyOn>;
  let revokeObjectURLSpy: ReturnType<typeof vi.spyOn>;
  let fetchSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    // Mock localStorage
    vi.spyOn(Storage.prototype, 'getItem').mockReturnValue('test-token');

    // Mock fetch
    fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('file-content', { status: 200 }),
    );

    // Mock URL methods
    createObjectURLSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test-url');
    revokeObjectURLSpy = vi.spyOn(URL, 'revokeObjectURL').mockReturnValue(undefined);

    // Mock DOM methods
    appendChildSpy = vi.spyOn(document.body, 'appendChild').mockReturnValue(
      document.createElement('a'),
    );
    removeChildSpy = vi.spyOn(document.body, 'removeChild').mockReturnValue(
      document.createElement('a'),
    );

    // Mock click
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockReturnValue(undefined);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('calls fetch with the correct URL and auth header', async () => {
    await downloadSLRReport(42, 'markdown');
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/v1/slr/studies/42/export/slr-report?format=markdown',
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: 'Bearer test-token' }) }),
    );
  });

  it('creates an object URL from the response blob', async () => {
    await downloadSLRReport(42, 'json');
    expect(createObjectURLSpy).toHaveBeenCalled();
  });

  it('appends and removes the anchor element', async () => {
    await downloadSLRReport(42, 'csv');
    expect(appendChildSpy).toHaveBeenCalled();
    expect(removeChildSpy).toHaveBeenCalled();
  });

  it('revokes the object URL after download', async () => {
    await downloadSLRReport(42, 'markdown');
    expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:test-url');
  });

  it('uses .tex extension for latex format', async () => {
    let capturedAnchor: HTMLAnchorElement | null = null;
    appendChildSpy.mockImplementation((node: Node) => {
      capturedAnchor = node as HTMLAnchorElement;
      return node as HTMLAnchorElement;
    });

    await downloadSLRReport(42, 'latex');
    expect(capturedAnchor).not.toBeNull();
    expect((capturedAnchor as unknown as HTMLAnchorElement).download).toBe('slr-report-42.tex');
  });

  it('uses format as extension for non-latex formats', async () => {
    let capturedAnchor: HTMLAnchorElement | null = null;
    appendChildSpy.mockImplementation((node: Node) => {
      capturedAnchor = node as HTMLAnchorElement;
      return node as HTMLAnchorElement;
    });

    await downloadSLRReport(99, 'csv');
    expect(capturedAnchor).not.toBeNull();
    expect((capturedAnchor as unknown as HTMLAnchorElement).download).toBe('slr-report-99.csv');
  });

  it('throws when response is not ok', async () => {
    fetchSpy.mockResolvedValue(new Response('', { status: 500 }));
    await expect(downloadSLRReport(1, 'json')).rejects.toThrow('Download failed: 500');
  });
});
