/**
 * Unit tests for SynthesisPage (feature 007, T077).
 *
 * Covers:
 * - Loading state while synthesis list is fetching.
 * - Empty state when no results exist.
 * - Results list rendered when data is available.
 * - Config form is rendered by default.
 * - Error state when synthesis list fetch fails.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SynthesisPage from '../SynthesisPage';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/slr/useSynthesis', () => ({
  useSynthesisResults: vi.fn(),
  useStartSynthesis: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
    isError: false,
  })),
  useSynthesisResult: vi.fn(() => ({ data: null, isLoading: true })),
}));

vi.mock('../../../components/slr/SynthesisConfigForm', () => ({
  default: ({ onSubmit }: { onSubmit: (d: unknown) => void }) => (
    <form data-testid="synthesis-config-form" onSubmit={(e) => { e.preventDefault(); onSubmit({}); }}>
      <button type="submit">Start Synthesis</button>
    </form>
  ),
}));

import { useSynthesisResults } from '../../../hooks/slr/useSynthesis';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeResult(overrides = {}) {
  return {
    id: 1,
    study_id: 42,
    approach: 'descriptive',
    status: 'completed',
    computed_statistics: null,
    forest_plot_svg: null,
    funnel_plot_svg: null,
    qualitative_themes: null,
    sensitivity_analysis: null,
    error_message: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={qc}>
      <SynthesisPage studyId={42} />
    </QueryClientProvider>,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('SynthesisPage', () => {
  describe('Loading state', () => {
    it('shows a spinner while results are loading', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({ isLoading: true, error: null, data: undefined } as never);
      renderPage();
      // MUI CircularProgress renders a role="progressbar" element
      expect(screen.getAllByRole('progressbar').length).toBeGreaterThan(0);
    });
  });

  describe('Error state', () => {
    it('renders empty results list when fetch fails', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: new Error('Network error'),
        data: undefined,
      } as never);
      renderPage();
      // When fetch fails, data is undefined so results fall back to empty array
      expect(screen.getByTestId('synthesis-empty')).toBeInTheDocument();
    });
  });

  describe('Empty state', () => {
    it('shows empty state when no results exist', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: { results: [] },
      } as never);
      renderPage();
      expect(screen.getByTestId('synthesis-empty')).toBeInTheDocument();
    });
  });

  describe('Config form', () => {
    it('renders the synthesis config form by default', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: { results: [] },
      } as never);
      renderPage();
      expect(screen.getByTestId('synthesis-config-form')).toBeInTheDocument();
    });
  });

  describe('Results list', () => {
    it('renders past results in a table when data is available', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: { results: [makeResult({ id: 7, approach: 'descriptive', status: 'completed' })] },
      } as never);
      renderPage();
      expect(screen.getByText('descriptive')).toBeInTheDocument();
      expect(screen.getByText('completed')).toBeInTheDocument();
    });
  });
});
