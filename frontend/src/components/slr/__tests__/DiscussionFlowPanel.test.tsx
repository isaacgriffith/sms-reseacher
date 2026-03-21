/**
 * Tests for DiscussionFlowPanel component (feature 007, T048).
 *
 * Covers:
 * - Returns null when record.threshold_met === true.
 * - Renders when threshold_met === false.
 * - Lists all disagreed papers.
 * - "Mark resolved" removes a paper from the pending list.
 * - After all resolved, shows "Re-compute Kappa" button.
 * - "Re-compute Kappa" button calls postDiscussion mutation.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import DiscussionFlowPanel from '../DiscussionFlowPanel';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockMutate = vi.fn();

vi.mock('../../../hooks/slr/useInterRater', () => ({
  usePostDiscussionKappa: vi.fn(() => ({ mutate: mockMutate, isPending: false })),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeRecord(threshold_met: boolean) {
  return {
    id: 1,
    study_id: 42,
    reviewer_a_id: 3,
    reviewer_b_id: 4,
    round_type: 'title_abstract',
    phase: 'pre_discussion',
    kappa_value: threshold_met ? 0.8 : 0.3,
    kappa_undefined_reason: null,
    n_papers: 10,
    threshold_met,
    created_at: '2026-01-01T00:00:00Z',
  };
}

const disagreements = [
  { paperId: 1, paperTitle: 'Paper Alpha', decisionA: 'accepted', decisionB: 'rejected' },
  { paperId: 2, paperTitle: 'Paper Beta', decisionA: 'rejected', decisionB: 'accepted' },
];

function renderPanel(threshold_met: boolean, items = disagreements) {
  const qc = new QueryClient();
  const record = makeRecord(threshold_met);
  render(
    <QueryClientProvider client={qc}>
      <DiscussionFlowPanel studyId={42} record={record} disagreements={items} />
    </QueryClientProvider>,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('DiscussionFlowPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Visibility', () => {
    it('renders nothing when threshold_met is true', () => {
      renderPanel(true);
      expect(screen.queryByTestId('discussion-flow-panel')).not.toBeInTheDocument();
    });

    it('renders panel when threshold_met is false', () => {
      renderPanel(false);
      expect(screen.getByTestId('discussion-flow-panel')).toBeInTheDocument();
    });
  });

  describe('Disagreements list', () => {
    it('renders all disagreed papers', () => {
      renderPanel(false);
      expect(screen.getByText('Paper Alpha')).toBeInTheDocument();
      expect(screen.getByText('Paper Beta')).toBeInTheDocument();
    });

    it('shows reviewer decisions side-by-side', () => {
      renderPanel(false);
      expect(screen.getAllByText('accepted').length).toBeGreaterThan(0);
      expect(screen.getAllByText('rejected').length).toBeGreaterThan(0);
    });

    it('renders Mark resolved button for each paper', () => {
      renderPanel(false);
      expect(screen.getByTestId('resolve-btn-1')).toBeInTheDocument();
      expect(screen.getByTestId('resolve-btn-2')).toBeInTheDocument();
    });
  });

  describe('"Mark resolved" state transition', () => {
    it('removes paper from pending list after Mark resolved', () => {
      renderPanel(false);
      fireEvent.click(screen.getByTestId('resolve-btn-1'));
      // Paper Alpha should no longer show its resolve button
      expect(screen.queryByTestId('resolve-btn-1')).not.toBeInTheDocument();
      // Paper Beta still pending
      expect(screen.getByTestId('resolve-btn-2')).toBeInTheDocument();
    });
  });

  describe('Re-compute Kappa', () => {
    it('shows Re-compute Kappa button when all resolved', () => {
      renderPanel(false);
      fireEvent.click(screen.getByTestId('resolve-btn-1'));
      fireEvent.click(screen.getByTestId('resolve-btn-2'));
      expect(screen.getByTestId('recompute-kappa-btn')).toBeInTheDocument();
    });

    it('hides Re-compute Kappa button when not all resolved', () => {
      renderPanel(false);
      fireEvent.click(screen.getByTestId('resolve-btn-1'));
      expect(screen.queryByTestId('recompute-kappa-btn')).not.toBeInTheDocument();
    });

    it('calls postDiscussion mutation on Re-compute click', () => {
      renderPanel(false);
      fireEvent.click(screen.getByTestId('resolve-btn-1'));
      fireEvent.click(screen.getByTestId('resolve-btn-2'));
      fireEvent.click(screen.getByTestId('recompute-kappa-btn'));
      expect(mockMutate).toHaveBeenCalledWith({
        reviewer_a_id: 3,
        reviewer_b_id: 4,
        round_type: 'title_abstract',
      });
    });
  });

  describe('Empty disagreements', () => {
    it('shows 0 of 0 when no disagreements passed', () => {
      renderPanel(false, []);
      expect(screen.getByText(/0 of 0/i)).toBeInTheDocument();
    });
  });
});
