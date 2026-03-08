/**
 * Tests for ExportPanel component.
 *
 * Mocks api.post / api.get to test:
 * - All four format radio buttons are rendered
 * - Default selection is full_archive
 * - Clicking a format radio button changes selection
 * - "Export" button triggers api.post with selected format
 * - Progress bar appears while job is running
 * - "Download" button appears when job status is completed
 * - Error message is shown on POST failure
 */
// @ts-nocheck


import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Mock the api module before importing the component
vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

import { api } from '../../../services/api';
import ExportPanel from '../ExportPanel';

const STUDY_ID = 7;
const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  patch: ReturnType<typeof vi.fn>;
};

describe('ExportPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default: POST resolves to a queued job
    mockApi.post.mockResolvedValue({ job_id: 'job-001', study_id: STUDY_ID });
    // Default: GET returns running status (no poll needed for most tests)
    mockApi.get.mockResolvedValue({
      id: 'job-001',
      status: 'running',
      progress_pct: 30,
      progress_detail: null,
      error_message: null,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('format radio buttons', () => {
    it('renders all four format options', () => {
      render(<ExportPanel studyId={STUDY_ID} />);
      expect(screen.getByText(/svg only/i)).toBeTruthy();
      expect(screen.getByText(/json only/i)).toBeTruthy();
      expect(screen.getByText(/csv\s*\+\s*json/i)).toBeTruthy();
      expect(screen.getByText(/full archive/i)).toBeTruthy();
    });

    it('full_archive is selected by default', () => {
      render(<ExportPanel studyId={STUDY_ID} />);
      const radios = screen.getAllByRole('radio') as HTMLInputElement[];
      const fullArchiveRadio = radios.find((r) => r.value === 'full_archive');
      expect(fullArchiveRadio?.checked).toBe(true);
    });

    it('clicking another format radio changes the selection', () => {
      render(<ExportPanel studyId={STUDY_ID} />);
      const radios = screen.getAllByRole('radio') as HTMLInputElement[];
      const jsonOnlyRadio = radios.find((r) => r.value === 'json_only')!;
      fireEvent.click(jsonOnlyRadio);
      expect(jsonOnlyRadio.checked).toBe(true);
    });
  });

  describe('Export button', () => {
    it('renders Export button initially', () => {
      render(<ExportPanel studyId={STUDY_ID} />);
      expect(screen.getByRole('button', { name: /^export$/i })).toBeTruthy();
    });

    it('calls api.post with selected format when Export is clicked', async () => {
      render(<ExportPanel studyId={STUDY_ID} />);

      // Select SVG Only
      const radios = screen.getAllByRole('radio') as HTMLInputElement[];
      const svgRadio = radios.find((r) => r.value === 'svg_only')!;
      fireEvent.click(svgRadio);

      const exportBtn = screen.getByRole('button', { name: /^export$/i });
      fireEvent.click(exportBtn);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          `/api/v1/studies/${STUDY_ID}/export`,
          { format: 'svg_only' }
        );
      });
    });

    it('calls api.post with full_archive when no format changed', async () => {
      render(<ExportPanel studyId={STUDY_ID} />);
      const exportBtn = screen.getByRole('button', { name: /^export$/i });
      fireEvent.click(exportBtn);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          `/api/v1/studies/${STUDY_ID}/export`,
          { format: 'full_archive' }
        );
      });
    });
  });

  describe('Progress bar', () => {
    it('shows progress bar after job is enqueued and status is running', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-002', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-002',
        status: 'running',
        progress_pct: 50,
        progress_detail: null,
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledTimes(1);
      });

      // Advance timer to trigger poll (async-aware)
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByText(/exporting/i)).toBeTruthy();
      });
    });
  });

  describe('Download button', () => {
    it('shows Download button when job status is completed', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-003', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-003',
        status: 'completed',
        progress_pct: 100,
        progress_detail: { download_url: '/exports/job-003.zip', size_bytes: 1024, format: 'json_only' },
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledTimes(1);
      });

      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /download/i })).toBeTruthy();
      });
    });

    it('shows success message when job is completed', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-004', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-004',
        status: 'completed',
        progress_pct: 100,
        progress_detail: { download_url: '/exports/job-004.json', size_bytes: 512, format: 'json_only' },
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));

      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByText(/export ready/i)).toBeTruthy();
      });
    });
  });

  describe('Error handling', () => {
    it('shows error message when api.post fails', async () => {
      mockApi.post.mockRejectedValue(new Error('Network error'));

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));

      await waitFor(() => {
        expect(screen.queryByText(/network error/i)).toBeTruthy();
      });
    });

    it('shows "Export failed" message when job status is failed', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-fail-001', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-fail-001',
        status: 'failed',
        progress_pct: 0,
        progress_detail: null,
        error_message: 'Agent crashed',
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));

      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByText(/export failed/i)).toBeTruthy();
      });
    });
  });

  describe('New Export button', () => {
    it('shows New Export button when job is completed', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-newexp', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-newexp',
        status: 'completed',
        progress_pct: 100,
        progress_detail: { download_url: '/exports/file.zip', size_bytes: 2048, format: 'full_archive' },
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /new export/i })).toBeTruthy();
      });
    });

    it('clicking New Export resets to Export button', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-reset', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-reset',
        status: 'completed',
        progress_pct: 100,
        progress_detail: { download_url: '/exports/file.zip', size_bytes: 512, format: 'csv_json' },
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);
      await waitFor(() => screen.queryByRole('button', { name: /new export/i }));

      fireEvent.click(screen.getByRole('button', { name: /new export/i }));

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /^export$/i })).toBeTruthy();
      });
    });
  });

  describe('Export button when job failed', () => {
    it('shows Export button again when job status is failed', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-refail', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-refail',
        status: 'failed',
        progress_pct: 0,
        progress_detail: null,
        error_message: 'Timeout',
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /^export$/i })).toBeTruthy();
      });
    });
  });

  describe('Error message from non-Error throw', () => {
    it('shows "Failed to start export job" when non-Error thrown', async () => {
      mockApi.post.mockRejectedValue('string error');

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));

      await waitFor(() => {
        expect(screen.queryByText(/failed to start export job/i)).toBeTruthy();
      });
    });
  });

  describe('Size display with null size_bytes', () => {
    it('does not show file size when size_bytes is undefined', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-nosize', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-nosize',
        status: 'completed',
        progress_pct: 100,
        progress_detail: { download_url: '/exports/f.zip', format: 'json_only' }, // no size_bytes
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => screen.queryByRole('button', { name: /download/i }));
      // No B/KB/MB indicator
      expect(screen.queryByText(/ B$/)).toBeNull();
      expect(screen.queryByText(/ KB$/)).toBeNull();
    });
  });

  describe('Export failed message error_message', () => {
    it('shows "Unknown error" when error_message is null in failed job', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-errnull', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-errnull',
        status: 'failed',
        progress_pct: 0,
        progress_detail: null,
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByText(/unknown error/i)).toBeTruthy();
      });
    });

    it('shows error_message when present in failed job', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-errmsg', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-errmsg',
        status: 'failed',
        progress_pct: 0,
        progress_detail: null,
        error_message: 'Disk quota exceeded',
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByText(/Disk quota exceeded/)).toBeTruthy();
      });
    });
  });

  describe('Radio button disabled during active job', () => {
    it('radio buttons are disabled when job is running', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-disabled', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-disabled',
        status: 'running',
        progress_pct: 20,
        progress_detail: null,
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        const radios = screen.getAllByRole('radio') as HTMLInputElement[];
        expect(radios.some(r => r.disabled)).toBe(true);
      });
    });

    it('radio buttons are enabled after job completes', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-enabled', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-enabled',
        status: 'completed',
        progress_pct: 100,
        progress_detail: { download_url: '/exports/f.zip', size_bytes: 100, format: 'json_only' },
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        const radios = screen.getAllByRole('radio') as HTMLInputElement[];
        expect(radios.every(r => !r.disabled)).toBe(true);
      });
    });
  });

  describe('Progress bar percentage display', () => {
    it('shows progress percentage value in the progress bar', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });

      mockApi.post.mockResolvedValue({ job_id: 'job-pct', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-pct',
        status: 'running',
        progress_pct: 75,
        progress_detail: null,
        error_message: null,
      });

      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);

      await waitFor(() => {
        expect(screen.queryByText('75%')).toBeTruthy();
      });
    });
  });

  describe('file size display', () => {
    it('shows size in bytes for small files (< 1024)', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });
      mockApi.post.mockResolvedValue({ job_id: 'job-sz-b', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-sz-b', status: 'completed', progress_pct: 100,
        progress_detail: { download_url: '/exports/f.zip', size_bytes: 512, format: 'json_only' },
        error_message: null,
      });
      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);
      await waitFor(() => expect(screen.queryByText('512 B')).toBeTruthy());
    });

    it('shows size in KB for files >= 1024 bytes', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });
      mockApi.post.mockResolvedValue({ job_id: 'job-sz-kb', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-sz-kb', status: 'completed', progress_pct: 100,
        progress_detail: { download_url: '/exports/f.zip', size_bytes: 2048, format: 'json_only' },
        error_message: null,
      });
      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);
      await waitFor(() => expect(screen.queryByText('2.0 KB')).toBeTruthy());
    });

    it('shows size in MB for files >= 1024 * 1024 bytes', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });
      mockApi.post.mockResolvedValue({ job_id: 'job-sz-mb', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-sz-mb', status: 'completed', progress_pct: 100,
        progress_detail: { download_url: '/exports/f.zip', size_bytes: 1024 * 1024 * 2, format: 'json_only' },
        error_message: null,
      });
      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);
      await waitFor(() => expect(screen.queryByText('2.0 MB')).toBeTruthy());
    });

    it('shows bytes (not KB) for exactly 1023 bytes', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });
      mockApi.post.mockResolvedValue({ job_id: 'job-sz-1023', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-sz-1023', status: 'completed', progress_pct: 100,
        progress_detail: { download_url: '/exports/f.zip', size_bytes: 1023, format: 'json_only' },
        error_message: null,
      });
      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);
      await waitFor(() => expect(screen.queryByText('1023 B')).toBeTruthy());
    });

    it('shows exactly 1.0 KB for exactly 1024 bytes', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });
      mockApi.post.mockResolvedValue({ job_id: 'job-sz-1024', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-sz-1024', status: 'completed', progress_pct: 100,
        progress_detail: { download_url: '/exports/f.zip', size_bytes: 1024, format: 'json_only' },
        error_message: null,
      });
      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);
      await waitFor(() => expect(screen.queryByText('1.0 KB')).toBeTruthy());
    });

    it('shows exactly 1.0 MB for exactly 1024*1024 bytes', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });
      mockApi.post.mockResolvedValue({ job_id: 'job-sz-1mb', study_id: STUDY_ID });
      mockApi.get.mockResolvedValue({
        id: 'job-sz-1mb', status: 'completed', progress_pct: 100,
        progress_detail: { download_url: '/exports/f.zip', size_bytes: 1024 * 1024, format: 'json_only' },
        error_message: null,
      });
      render(<ExportPanel studyId={STUDY_ID} />);
      fireEvent.click(screen.getByRole('button', { name: /^export$/i }));
      await waitFor(() => expect(mockApi.post).toHaveBeenCalledTimes(1));
      await vi.advanceTimersByTimeAsync(2500);
      await waitFor(() => expect(screen.queryByText('1.0 MB')).toBeTruthy());
    });
  });
});
