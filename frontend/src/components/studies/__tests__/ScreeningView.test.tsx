/**
 * Tests for ScreeningView component.
 *
 * Composes PaperQueue + ReviewerPanel + PaperCard + MetricsDashboard behind one
 * screen. Mocks api.get / api.post to answer each child's endpoint (papers list,
 * criteria inclusion/exclusion, decisions history, metrics funnel).
 *
 * Covers:
 * - T011: selecting a queue row opens the reviewer panel bound to that candidate
 * - T012: reasons/annotation already entered survive a 409 stale_state
 *   re-confirmation prompt (FR-025)
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../../services/api')>();
  return {
    ...actual,
    api: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

import { api, ApiError } from '../../../services/api';
import ScreeningView from '../ScreeningView';

const mockApi = api as unknown as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const CANDIDATE_A = {
  id: 42,
  study_id: 1,
  paper_id: 10,
  phase_tag: 'initial-search',
  current_status: 'pending' as const,
  duplicate_of_id: null,
  conflict_flag: false,
  paper: {
    id: 10,
    title: 'TDD in Practice',
    abstract: 'An abstract.',
    doi: '10.1/tdd',
    authors: [{ name: 'Alice Smith' }],
    year: 2023,
    venue: 'JSS',
  },
};

const CANDIDATE_B = {
  ...CANDIDATE_A,
  id: 43,
  paper_id: 11,
  paper: { ...CANDIDATE_A.paper, id: 11, title: 'Another Paper' },
};

function mockGetImplementation(url: string) {
  if (url.includes('/papers?')) return Promise.resolve([CANDIDATE_A, CANDIDATE_B]);
  if (url.includes('/criteria/inclusion')) {
    return Promise.resolve([{ id: 1, description: 'Peer-reviewed', order_index: 0 }]);
  }
  if (url.includes('/criteria/exclusion')) return Promise.resolve([]);
  if (url.includes('/decisions')) return Promise.resolve([]);
  if (url.includes('/metrics')) return Promise.resolve({ study_id: 1, phases: [], totals: {} });
  return Promise.resolve([]);
}

describe('ScreeningView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.get.mockImplementation(mockGetImplementation);
    mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted', is_override: false });
  });

  it('renders the screening view root', async () => {
    renderWithQuery(<ScreeningView studyId={1} />);
    expect(screen.getByTestId('screening-view')).toBeTruthy();
  });

  describe('T011: selecting a paper opens the reviewer panel', () => {
    it('reviewer panel is not shown before a paper is selected', async () => {
      renderWithQuery(<ScreeningView studyId={1} />);
      await waitFor(() => screen.getByText('TDD in Practice'));
      expect(screen.queryByTestId('reviewer-panel')).toBeNull();
    });

    it('clicking a queue row opens the reviewer panel and paper card for that candidate', async () => {
      renderWithQuery(<ScreeningView studyId={1} />);
      await waitFor(() => screen.getByText('TDD in Practice'));

      const items = screen.getAllByTestId('paper-queue-item');
      fireEvent.click(items[0]);

      await waitFor(() => expect(screen.getByTestId('reviewer-panel')).toBeTruthy());
      expect(screen.getByTestId('paper-card')).toBeTruthy();
      // ReviewerPanel for the selected candidate fetches its criteria
      await waitFor(() =>
        expect(mockApi.get).toHaveBeenCalledWith(expect.stringContaining('/criteria/inclusion')),
      );
    });

    it('selecting via keyboard (Enter) opens the reviewer panel', async () => {
      renderWithQuery(<ScreeningView studyId={1} />);
      await waitFor(() => screen.getByText('TDD in Practice'));

      const items = screen.getAllByTestId('paper-queue-item');
      fireEvent.keyDown(items[0], { key: 'Enter' });

      await waitFor(() => expect(screen.getByTestId('reviewer-panel')).toBeTruthy());
    });

    it('selecting the second row binds the panel to the second candidate', async () => {
      renderWithQuery(<ScreeningView studyId={1} />);
      await waitFor(() => screen.getByText('Another Paper'));

      const items = screen.getAllByTestId('paper-queue-item');
      fireEvent.click(items[1]);

      await waitFor(() => expect(screen.getByTestId('reviewer-panel')).toBeTruthy());
      // Only one paper card shown, and it is for the selected (second) candidate
      expect(screen.getAllByTestId('paper-card')).toHaveLength(1);
    });
  });

  describe('T012: entered reasons/annotation survive a stale-state re-confirmation', () => {
    it('keeps the selected reason and annotation text visible after a 409 stale_state response', async () => {
      renderWithQuery(<ScreeningView studyId={1} />);
      await waitFor(() => screen.getByText('TDD in Practice'));

      fireEvent.click(screen.getAllByTestId('paper-queue-item')[0]);
      await waitFor(() => screen.getByTestId('reviewer-panel'));

      // Enter a decision, a criterion reason, an annotation
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      await waitFor(() => screen.getByText('Peer-reviewed'));
      fireEvent.click(screen.getByLabelText('Peer-reviewed'));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '7' } });
      fireEvent.change(screen.getByPlaceholderText(/optional annotation/i), {
        target: { value: 'Looks solid on second read' },
      });

      mockApi.post.mockRejectedValueOnce(
        new ApiError(409, {
          error: 'stale_state',
          observed_status: 'pending',
          current_status: 'accepted',
        } as unknown as string),
      );

      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      // Re-confirmation prompt appears naming old and new status
      await waitFor(() => expect(screen.getByTestId('stale-state-prompt')).toBeTruthy());
      expect(screen.getByTestId('stale-state-prompt').textContent).toMatch(/pending/i);
      expect(screen.getByTestId('stale-state-prompt').textContent).toMatch(/accepted/i);

      // The already-entered reason and annotation are still present (FR-025)
      expect((screen.getByLabelText('Peer-reviewed') as HTMLInputElement).checked).toBe(true);
      expect(
        (screen.getByPlaceholderText(/optional annotation/i) as HTMLTextAreaElement).value,
      ).toBe('Looks solid on second read');
    });

    it('resubmits with the updated observed_status when the re-confirmation is confirmed', async () => {
      renderWithQuery(<ScreeningView studyId={1} />);
      await waitFor(() => screen.getByText('TDD in Practice'));

      fireEvent.click(screen.getAllByTestId('paper-queue-item')[0]);
      await waitFor(() => screen.getByTestId('reviewer-panel'));

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '7' } });

      mockApi.post.mockRejectedValueOnce(
        new ApiError(409, {
          error: 'stale_state',
          observed_status: 'pending',
          current_status: 'accepted',
        } as unknown as string),
      );
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));
      await waitFor(() => expect(screen.getByTestId('stale-state-prompt')).toBeTruthy());

      mockApi.post.mockResolvedValueOnce({ id: 2, decision: 'accepted', is_override: false });
      fireEvent.click(screen.getByRole('button', { name: /confirm and resubmit/i }));

      await waitFor(() => {
        const lastCall = mockApi.post.mock.calls.at(-1);
        expect(lastCall?.[1]).toMatchObject({ observed_status: 'accepted' });
      });
    });
  });
});
