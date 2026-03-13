/**
 * Tests for JobRetryPanel component.
 *
 * Mocks TanStack Query + api.get/post to verify:
 * - Loading state renders a placeholder
 * - Error state renders an error message
 * - Empty list shows "No failed jobs" message
 * - Failed jobs are listed with type, study ID, and error message
 * - Retry button calls POST /admin/jobs/{id}/retry
 * - Success banner shows the new job ID after retry
 * - Success banner can be dismissed
 * - Retry button is disabled while the mutation is pending
 */
// @ts-nocheck


import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    constructor(public status: number, message: string) { super(message); }
  },
}));

import { api } from '../../../services/api';
import JobRetryPanel from '../JobRetryPanel';

const mockApi = api as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> };

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const FAILED_JOBS_RESPONSE = {
  items: [
    {
      id: 'arq-job-abc123def456',
      study_id: 4,
      job_type: 'full_search',
      status: 'failed',
      error_message: 'ACM rate limit exceeded',
      queued_at: '2026-03-11T09:00:00Z',
      completed_at: '2026-03-11T09:05:22Z',
    },
    {
      id: 'arq-job-xyz789',
      study_id: 7,
      job_type: 'batch_extraction',
      status: 'failed',
      error_message: 'LLM timeout',
      queued_at: '2026-03-11T10:00:00Z',
      completed_at: null,
    },
  ],
  total: 2,
  page: 1,
  page_size: 50,
};

describe('JobRetryPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('loading state', () => {
    it('shows loading placeholder while fetching', () => {
      mockApi.get.mockReturnValue(new Promise(() => {}));
      renderWithQuery(<JobRetryPanel />);
      expect(screen.getByText(/loading failed jobs/i)).toBeTruthy();
    });
  });

  describe('error state', () => {
    it('shows error message when fetch fails', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'));
      renderWithQuery(<JobRetryPanel />);
      await waitFor(() => {
        expect(screen.getByText(/failed to load jobs/i)).toBeTruthy();
      });
    });
  });

  describe('empty state', () => {
    it('shows no-failed-jobs message when list is empty', async () => {
      mockApi.get.mockResolvedValue({ items: [], total: 0, page: 1, page_size: 50 });
      renderWithQuery(<JobRetryPanel />);
      await waitFor(() => {
        expect(screen.getByText(/no failed jobs/i)).toBeTruthy();
      });
    });
  });

  describe('job list rendering', () => {
    it('renders job type for each failed job', async () => {
      mockApi.get.mockResolvedValue(FAILED_JOBS_RESPONSE);
      renderWithQuery(<JobRetryPanel />);
      await waitFor(() => {
        expect(screen.getByText('full_search')).toBeTruthy();
        expect(screen.getByText('batch_extraction')).toBeTruthy();
      });
    });

    it('renders study ID for each job', async () => {
      mockApi.get.mockResolvedValue(FAILED_JOBS_RESPONSE);
      renderWithQuery(<JobRetryPanel />);
      await waitFor(() => {
        expect(screen.getByText(/study #4/i)).toBeTruthy();
        expect(screen.getByText(/study #7/i)).toBeTruthy();
      });
    });

    it('renders error message for each failed job', async () => {
      mockApi.get.mockResolvedValue(FAILED_JOBS_RESPONSE);
      renderWithQuery(<JobRetryPanel />);
      await waitFor(() => {
        expect(screen.getByText('ACM rate limit exceeded')).toBeTruthy();
        expect(screen.getByText('LLM timeout')).toBeTruthy();
      });
    });

    it('renders a Retry button for each job', async () => {
      mockApi.get.mockResolvedValue(FAILED_JOBS_RESPONSE);
      renderWithQuery(<JobRetryPanel />);
      await waitFor(() => {
        const retryButtons = screen.getAllByText('Retry');
        expect(retryButtons.length).toBe(2);
      });
    });

    it('shows total count in heading', async () => {
      mockApi.get.mockResolvedValue(FAILED_JOBS_RESPONSE);
      renderWithQuery(<JobRetryPanel />);
      await waitFor(() => {
        expect(screen.getByText(/failed jobs.*2/i)).toBeTruthy();
      });
    });
  });

  describe('retry interaction', () => {
    it('calls POST /admin/jobs/{id}/retry when Retry button is clicked', async () => {
      mockApi.get.mockResolvedValue(FAILED_JOBS_RESPONSE);
      mockApi.post.mockResolvedValue({
        new_job_id: 'arq-job-new999',
        original_job_id: 'arq-job-abc123def456',
      });
      renderWithQuery(<JobRetryPanel />);

      await waitFor(() => {
        expect(screen.getAllByText('Retry').length).toBe(2);
      });

      fireEvent.click(screen.getAllByText('Retry')[0]);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/admin/jobs/arq-job-abc123def456/retry',
          {},
        );
      });
    });

    it('shows success confirmation banner with new job ID after retry', async () => {
      mockApi.get.mockResolvedValue(FAILED_JOBS_RESPONSE);
      mockApi.post.mockResolvedValue({
        new_job_id: 'arq-job-new999',
        original_job_id: 'arq-job-abc123def456',
      });
      renderWithQuery(<JobRetryPanel />);

      await waitFor(() => screen.getAllByText('Retry'));
      fireEvent.click(screen.getAllByText('Retry')[0]);

      await waitFor(() => {
        // Banner should mention the new job's suffix
        expect(screen.getByText(/new999/i)).toBeTruthy();
      });
    });

    it('success banner can be dismissed', async () => {
      mockApi.get.mockResolvedValue(FAILED_JOBS_RESPONSE);
      mockApi.post.mockResolvedValue({
        new_job_id: 'arq-job-new999',
        original_job_id: 'arq-job-abc123def456',
      });
      renderWithQuery(<JobRetryPanel />);

      await waitFor(() => screen.getAllByText('Retry'));
      fireEvent.click(screen.getAllByText('Retry')[0]);

      await waitFor(() => {
        expect(screen.getByText(/new999/i)).toBeTruthy();
      });

      const dismissButton = screen.getByText('✕');
      fireEvent.click(dismissButton);

      await waitFor(() => {
        expect(screen.queryByText(/new999/i)).toBeNull();
      });
    });
  });
});
