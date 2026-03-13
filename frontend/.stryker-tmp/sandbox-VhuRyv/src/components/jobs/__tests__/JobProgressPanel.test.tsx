/**
 * Tests for JobProgressPanel component.
 *
 * Mocks useJobProgress hook to test all render states:
 * - null jobId → renders nothing
 * - running/queued status → "Search Running" + detail labels
 * - completed status → "Search Complete" + paper count summary
 * - failed status → "Search Failed" + error message
 * - progress percentage reflected in bar width style
 */
// @ts-nocheck


import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('../../../services/jobs', () => ({
  useJobProgress: vi.fn(),
}));

import { useJobProgress } from '../../../services/jobs';
import JobProgressPanel from '../JobProgressPanel';

const mockUseJobProgress = useJobProgress as ReturnType<typeof vi.fn>;

describe('JobProgressPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('null jobId', () => {
    it('renders nothing when jobId is null', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'idle',
        progressPct: 0,
        detail: null,
        error: null,
      });
      const { container } = render(<JobProgressPanel jobId={null} />);
      expect(container.firstChild).toBeNull();
    });
  });

  describe('running state', () => {
    it('shows "Search Running" heading when status is running', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'running',
        progressPct: 40,
        detail: { phase: 'searching', current_database: 'acm', papers_found: 10 },
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText(/search running/i)).toBeTruthy();
    });

    it('shows "Search Running" when status is queued', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'queued',
        progressPct: 0,
        detail: null,
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText(/search running/i)).toBeTruthy();
    });

    it('displays current database label when running', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'running',
        progressPct: 30,
        detail: { phase: 'searching', current_database: 'ieee', papers_found: 5 },
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText('ieee')).toBeTruthy();
    });

    it('displays papers found counter when greater than zero', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'running',
        progressPct: 30,
        detail: { phase: 'searching', current_database: 'scopus', papers_found: 42 },
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText('42')).toBeTruthy();
    });

    it('reflects progressPct in progress bar inner div width style', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'running',
        progressPct: 65,
        detail: null,
        error: null,
      });
      const { container } = render(<JobProgressPanel jobId="job-123" />);
      // The inner progress bar has inline style width: 65%
      const barInner = container.querySelector('[style*="65%"]');
      expect(barInner).not.toBeNull();
    });
  });

  describe('completed state', () => {
    it('shows "Search Complete" heading', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'completed',
        progressPct: 100,
        detail: { total_identified: 100, accepted: 40, rejected: 55, duplicates: 5 },
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText(/search complete/i)).toBeTruthy();
    });

    it('displays accepted paper count', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'completed',
        progressPct: 100,
        detail: { total_identified: 100, accepted: 40, rejected: 55, duplicates: 5 },
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText('40')).toBeTruthy();
    });

    it('displays total identified count', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'completed',
        progressPct: 100,
        detail: { total_identified: 120, accepted: 50, rejected: 65, duplicates: 5 },
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText('120')).toBeTruthy();
    });

    it('progress bar at 100% on completion', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'completed',
        progressPct: 100,
        detail: { total_identified: 10, accepted: 5, rejected: 4, duplicates: 1 },
        error: null,
      });
      const { container } = render(<JobProgressPanel jobId="job-123" />);
      const barInner = container.querySelector('[style*="100%"]');
      expect(barInner).not.toBeNull();
    });
  });

  describe('failed state', () => {
    it('shows "Search Failed" heading', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'failed',
        progressPct: 0,
        detail: null,
        error: 'Connection lost',
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText(/search failed/i)).toBeTruthy();
    });

    it('shows the error message', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'failed',
        progressPct: 0,
        detail: null,
        error: 'Redis unavailable',
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText('Redis unavailable')).toBeTruthy();
    });

    it('shows fallback error text when error is null', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'failed',
        progressPct: 0,
        detail: null,
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText(/an error occurred/i)).toBeTruthy();
    });
  });

  describe('status badge', () => {
    it('renders the status value as a badge label', () => {
      mockUseJobProgress.mockReturnValue({
        status: 'running',
        progressPct: 20,
        detail: null,
        error: null,
      });
      render(<JobProgressPanel jobId="job-123" />);
      expect(screen.getByText('running')).toBeTruthy();
    });
  });
});
