/**
 * Tests for InterRaterPanel component (feature 007, T047).
 *
 * Covers:
 * - Shows loading spinner when data is loading.
 * - Shows empty state when no records exist.
 * - Renders Kappa values from records.
 * - Shows threshold status badge (✓ met / ✗ below).
 * - "Compute Kappa" button is visible when computeBody is provided.
 * - "Compute Kappa" button is absent when computeBody is not provided.
 * - Error alert shown when fetch fails.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import InterRaterPanel from '../InterRaterPanel';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/slr/useInterRater', () => ({
  useInterRaterRecords: vi.fn(),
  useComputeKappa: vi.fn(() => ({ mutate: vi.fn(), isPending: false, isError: false })),
}));

import { useInterRaterRecords } from '../../../hooks/slr/useInterRater';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeRecord(overrides = {}) {
  return {
    id: 1,
    study_id: 42,
    reviewer_a_id: 3,
    reviewer_b_id: 4,
    round_type: 'title_abstract',
    phase: 'pre_discussion',
    kappa_value: 0.75,
    kappa_undefined_reason: null,
    n_papers: 10,
    threshold_met: true,
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

function renderPanel(studyId = 42, computeBody?: object) {
  const qc = new QueryClient();
  render(
    <QueryClientProvider client={qc}>
      <InterRaterPanel studyId={studyId} computeBody={computeBody as never} />
    </QueryClientProvider>,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('InterRaterPanel', () => {
  describe('Loading state', () => {
    it('shows loading spinner when data is loading', () => {
      vi.mocked(useInterRaterRecords).mockReturnValue({ isLoading: true });
      renderPanel();
      expect(screen.getByLabelText(/loading inter-rater/i)).toBeInTheDocument();
    });
  });

  describe('Error state', () => {
    it('shows error alert when fetch fails', () => {
      vi.mocked(useInterRaterRecords).mockReturnValue({
        isLoading: false,
        error: new Error('Network error'),
      });
      renderPanel();
      expect(screen.getByTestId('irr-error')).toBeInTheDocument();
    });
  });

  describe('Empty state', () => {
    it('shows empty state message when no records exist', () => {
      vi.mocked(useInterRaterRecords).mockReturnValue({
        isLoading: false,
        error: null,
        data: { records: [] },
      });
      renderPanel();
      expect(screen.getByTestId('irr-empty')).toBeInTheDocument();
    });
  });

  describe('Records rendering', () => {
    it('renders kappa value from records', () => {
      vi.mocked(useInterRaterRecords).mockReturnValue({
        isLoading: false,
        error: null,
        data: { records: [makeRecord({ kappa_value: 0.75 })] },
      });
      renderPanel();
      expect(screen.getByText('0.750')).toBeInTheDocument();
    });

    it('renders threshold met badge', () => {
      vi.mocked(useInterRaterRecords).mockReturnValue({
        isLoading: false,
        error: null,
        data: { records: [makeRecord({ threshold_met: true })] },
      });
      renderPanel();
      expect(screen.getByText(/threshold met/i)).toBeInTheDocument();
    });

    it('renders below threshold badge', () => {
      vi.mocked(useInterRaterRecords).mockReturnValue({
        isLoading: false,
        error: null,
        data: { records: [makeRecord({ threshold_met: false })] },
      });
      renderPanel();
      expect(screen.getByText(/below threshold/i)).toBeInTheDocument();
    });

    it('renders undefined kappa reason when kappa_value is null', () => {
      vi.mocked(useInterRaterRecords).mockReturnValue({
        isLoading: false,
        error: null,
        data: {
          records: [
            makeRecord({ kappa_value: null, kappa_undefined_reason: 'Zero-variance decisions' }),
          ],
        },
      });
      renderPanel();
      expect(screen.getByText('Zero-variance decisions')).toBeInTheDocument();
    });

    it('renders n_papers count in table', () => {
      vi.mocked(useInterRaterRecords).mockReturnValue({
        isLoading: false,
        error: null,
        data: { records: [makeRecord({ n_papers: 42 })] },
      });
      renderPanel();
      expect(screen.getByText('42')).toBeInTheDocument();
    });
  });

  describe('Compute Kappa button', () => {
    beforeEach(() => {
      vi.mocked(useInterRaterRecords).mockReturnValue({
        isLoading: false,
        error: null,
        data: { records: [] },
      });
    });

    it('shows Compute Kappa button when computeBody is provided', () => {
      renderPanel(42, { reviewer_a_id: 3, reviewer_b_id: 4, round_type: 'title_abstract' });
      expect(screen.getByTestId('compute-kappa-btn')).toBeInTheDocument();
    });

    it('hides Compute Kappa button when computeBody is not provided', () => {
      renderPanel(42);
      expect(screen.queryByTestId('compute-kappa-btn')).not.toBeInTheDocument();
    });
  });
});
