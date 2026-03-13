/**
 * Tests for MetricsDashboard component.
 *
 * Wraps with QueryClientProvider and mocks api.get.
 * Covers:
 * - Loading state shows spinner text
 * - Error state shows error message
 * - Empty state (no phases) shows placeholder text
 * - Renders phase cards with all four funnel bars
 * - Percentage calculations (value/max) rendered correctly
 * - 0-max edge case: percentage shows 0%
 * - Phase tag "all" → "All Phases (Totals)"
 * - Phase tag other → shows exec #N badge
 * - Totals card shown only when >1 phase
 * - All bar labels are rendered (Identified, Accepted, Rejected, Duplicates)
 */

import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

import { api } from '../../../services/api';
import MetricsDashboard from '../MetricsDashboard';

const mockApi = api as { get: ReturnType<typeof vi.fn> };

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const SINGLE_PHASE: import('../../../services/api').StudyMetricsResponse = {
  study_id: 1,
  phases: [
    {
      phase_tag: 'initial-search',
      search_execution_id: 7,
      total_identified: 200,
      accepted: 80,
      rejected: 110,
      duplicates: 10,
    },
  ],
  totals: {
    phase_tag: 'all',
    search_execution_id: 0,
    total_identified: 200,
    accepted: 80,
    rejected: 110,
    duplicates: 10,
  },
} as unknown as never;

const TWO_PHASE_RESPONSE = {
  study_id: 1,
  phases: [
    {
      phase_tag: 'initial-search',
      search_execution_id: 3,
      total_identified: 100,
      accepted: 40,
      rejected: 55,
      duplicates: 5,
    },
    {
      phase_tag: 'snowball-search',
      search_execution_id: 5,
      total_identified: 50,
      accepted: 20,
      rejected: 28,
      duplicates: 2,
    },
  ],
  totals: {
    phase_tag: 'all',
    search_execution_id: 0,
    total_identified: 150,
    accepted: 60,
    rejected: 83,
    duplicates: 7,
  },
};

const EMPTY_RESPONSE = {
  study_id: 1,
  phases: [],
  totals: { phase_tag: 'all', search_execution_id: 0, total_identified: 0, accepted: 0, rejected: 0, duplicates: 0 },
};

describe('MetricsDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('loading state', () => {
    it('shows loading text while query is pending', async () => {
      // Never resolves
      mockApi.get.mockReturnValue(new Promise(() => {}));
      renderWithQuery(<MetricsDashboard studyId={1} />);
      expect(screen.getByText(/loading metrics/i)).toBeTruthy();
    });
  });

  describe('error state', () => {
    it('shows error message when query fails', async () => {
      mockApi.get.mockRejectedValue(new Error('Network failure'));
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/failed to load metrics/i)).toBeTruthy();
      });
    });

    it('shows error message text in error output', async () => {
      mockApi.get.mockRejectedValue(new Error('Network failure'));
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/Network failure/i)).toBeTruthy();
      });
    });
  });

  describe('empty state', () => {
    it('shows empty-state message when phases array is empty', async () => {
      mockApi.get.mockResolvedValue(EMPTY_RESPONSE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/no search metrics yet/i)).toBeTruthy();
      });
    });

    it('does not render the Search Metrics section heading when empty', async () => {
      mockApi.get.mockResolvedValue(EMPTY_RESPONSE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => screen.getByText(/no search metrics yet/i));
      expect(screen.queryByRole('heading', { name: /search metrics/i })).toBeNull();
    });
  });

  describe('single phase rendering', () => {
    it('renders the Search Metrics heading', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/search metrics/i)).toBeTruthy();
      });
    });

    it('renders the phase tag as card heading', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('initial-search')).toBeTruthy();
      });
    });

    it('renders exec # badge for non-all phase tags', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/exec #7/)).toBeTruthy();
      });
    });

    it('renders all four bar labels', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Identified')).toBeTruthy();
        expect(screen.getByText('Accepted')).toBeTruthy();
        expect(screen.getByText('Rejected')).toBeTruthy();
        expect(screen.getByText('Duplicates')).toBeTruthy();
      });
    });

    it('renders the total_identified value', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('200')).toBeTruthy();
      });
    });

    it('renders accepted value', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('80')).toBeTruthy();
      });
    });

    it('renders percentage annotation (accepted/total = 40%)', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        // 80/200 = 40%
        expect(screen.getByText('(40%)')).toBeTruthy();
      });
    });

    it('does not show totals card when only one phase', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => screen.getByText('initial-search'));
      // Totals card is only shown for >1 phase
      expect(screen.queryByText(/all phases \(totals\)/i)).toBeNull();
    });
  });

  describe('multi-phase rendering', () => {
    it('renders both phase cards', async () => {
      mockApi.get.mockResolvedValue(TWO_PHASE_RESPONSE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('initial-search')).toBeTruthy();
        expect(screen.getByText('snowball-search')).toBeTruthy();
      });
    });

    it('renders totals card with "All Phases (Totals)" heading when >1 phase', async () => {
      mockApi.get.mockResolvedValue(TWO_PHASE_RESPONSE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('All Phases (Totals)')).toBeTruthy();
      });
    });

    it('does not render exec # badge for "all" phase tag', async () => {
      mockApi.get.mockResolvedValue(TWO_PHASE_RESPONSE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => screen.getByText('All Phases (Totals)'));
      // The "all" phase card should not have an exec # badge
      expect(screen.queryByText(/exec #0/)).toBeNull();
    });

    it('renders exec badges for each non-all phase', async () => {
      mockApi.get.mockResolvedValue(TWO_PHASE_RESPONSE);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/exec #3/)).toBeTruthy();
        expect(screen.getByText(/exec #5/)).toBeTruthy();
      });
    });
  });

  describe('percentage edge cases', () => {
    it('shows 0% when total_identified is 0', async () => {
      const zeroData = {
        study_id: 1,
        phases: [
          {
            phase_tag: 'empty-run',
            search_execution_id: 1,
            total_identified: 0,
            accepted: 0,
            rejected: 0,
            duplicates: 0,
          },
        ],
        totals: { phase_tag: 'all', search_execution_id: 0, total_identified: 0, accepted: 0, rejected: 0, duplicates: 0 },
      };
      mockApi.get.mockResolvedValue(zeroData);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => screen.getByText('empty-run'));
      // No percentage annotation when max=0 (condition: max > 0)
      const pctTexts = document.body.querySelectorAll('*');
      const hasPercent = Array.from(pctTexts).some((el) => el.textContent?.match(/\(\d+%\)/));
      expect(hasPercent).toBe(false);
    });

    it('rounds percentage to nearest integer', async () => {
      const data = {
        study_id: 1,
        phases: [
          {
            phase_tag: 'test-phase',
            search_execution_id: 1,
            total_identified: 3,
            accepted: 1,
            rejected: 2,
            duplicates: 0,
          },
        ],
        totals: { phase_tag: 'all', search_execution_id: 0, total_identified: 3, accepted: 1, rejected: 2, duplicates: 0 },
      };
      mockApi.get.mockResolvedValue(data);
      renderWithQuery(<MetricsDashboard studyId={1} />);
      await waitFor(() => screen.getByText('test-phase'));
      // 1/3 = 33.33% → rounded to 33%
      expect(screen.getByText('(33%)')).toBeTruthy();
    });
  });

  describe('API query', () => {
    it('calls api.get with correct URL', async () => {
      mockApi.get.mockResolvedValue(SINGLE_PHASE);
      renderWithQuery(<MetricsDashboard studyId={42} />);
      await waitFor(() => {
        expect(mockApi.get).toHaveBeenCalledWith('/api/v1/studies/42/metrics');
      });
    });
  });
});
