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

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SynthesisPage from '../SynthesisPage';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const { mockStartMutate } = vi.hoisted(() => ({
  mockStartMutate: vi.fn(),
}));

vi.mock('../../../hooks/slr/useSynthesis', () => ({
  useSynthesisResults: vi.fn(),
  useStartSynthesis: vi.fn(() => ({
    mutate: mockStartMutate,
    isPending: false,
    isError: false,
    error: null,
  })),
  useSynthesisResult: vi.fn(() => ({ data: null, isLoading: true })),
}));

vi.mock('../../../components/slr/SynthesisConfigForm', () => ({
  default: ({ onSubmit }: { onSubmit: (d: Record<string, unknown>) => void }) => (
    <form
      data-testid="synthesis-config-form"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          approach: 'meta_analysis',
          model_type: 'auto',
          heterogeneity_threshold: 0.1,
          confidence_interval: 0.95,
          papers: [
            { label: 'P1', effect_size: 0.5, se: 0.1, ci_lower: 0.3, ci_upper: 0.7, weight: 1.0 },
          ],
        });
      }}
    >
      <button type="submit">Start Synthesis</button>
    </form>
  ),
}));

vi.mock('../../../components/slr/ForestPlotViewer', () => ({
  default: () => <div data-testid="forest-plot">Forest Plot</div>,
}));
vi.mock('../../../components/slr/FunnelPlotViewer', () => ({
  default: () => <div data-testid="funnel-plot">Funnel Plot</div>,
}));

import { useSynthesisResults, useSynthesisResult } from '../../../hooks/slr/useSynthesis';

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
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: true,
        error: null,
        data: undefined,
      } as never);
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

    it('clicking a result row selects it and shows detail', async () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: { results: [makeResult({ id: 7, approach: 'descriptive', status: 'completed' })] },
      } as never);
      vi.mocked(useSynthesisResult).mockReturnValue({
        data: makeResult({ id: 7, approach: 'descriptive', status: 'completed' }),
        isLoading: false,
      } as never);
      renderPage();
      const { fireEvent } = await import('@testing-library/react');
      fireEvent.click(screen.getByText('descriptive'));
      // Result detail shows result ID
      expect(screen.getByText(/Result #7/)).toBeInTheDocument();
    });
  });

  describe('handleSubmit', () => {
    it('calls startMutation.mutate when form is submitted', async () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: { results: [] },
      } as never);
      renderPage();
      const { fireEvent } = await import('@testing-library/react');
      fireEvent.submit(screen.getByTestId('synthesis-config-form'));
      expect(mockStartMutate).toHaveBeenCalled();
    });
  });

  describe('ResultDetail', () => {
    it('shows in-progress alert for pending result', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: { results: [makeResult({ id: 5, status: 'pending' })] },
      } as never);
      vi.mocked(useSynthesisResult).mockReturnValue({
        data: makeResult({ id: 5, status: 'pending' }),
        isLoading: false,
      } as never);
      renderPage();
      fireEvent.click(screen.getByText('pending'));
      expect(screen.getByText(/polling for updates/i)).toBeInTheDocument();
    });

    it('shows error alert for failed result', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: { results: [makeResult({ id: 5, status: 'failed', error_message: 'Boom' })] },
      } as never);
      vi.mocked(useSynthesisResult).mockReturnValue({
        data: makeResult({ id: 5, status: 'failed', error_message: 'Boom' }),
        isLoading: false,
      } as never);
      renderPage();
      fireEvent.click(screen.getByText('failed'));
      expect(screen.getByText('Boom')).toBeInTheDocument();
    });

    it('shows forest and funnel plots for completed result', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: { results: [makeResult({ id: 5, status: 'completed' })] },
      } as never);
      vi.mocked(useSynthesisResult).mockReturnValue({
        data: makeResult({ id: 5, status: 'completed' }),
        isLoading: false,
      } as never);
      renderPage();
      fireEvent.click(screen.getByText('completed'));
      expect(screen.getByTestId('forest-plot')).toBeInTheDocument();
      expect(screen.getByTestId('funnel-plot')).toBeInTheDocument();
    });

    it('shows qualitative themes table when present', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: {
          results: [
            makeResult({
              id: 5,
              status: 'completed',
              qualitative_themes: { themes: { 'Theme A': [1, 2], 'Theme B': [3] } },
            }),
          ],
        },
      } as never);
      vi.mocked(useSynthesisResult).mockReturnValue({
        data: makeResult({
          id: 5,
          status: 'completed',
          qualitative_themes: { themes: { 'Theme A': [1, 2], 'Theme B': [3] } },
        }),
        isLoading: false,
      } as never);
      renderPage();
      fireEvent.click(screen.getByText('completed'));
      expect(screen.getByText('Theme A')).toBeInTheDocument();
      expect(screen.getByText('1, 2')).toBeInTheDocument();
    });

    it('shows sensitivity analysis when present', () => {
      vi.mocked(useSynthesisResults).mockReturnValue({
        isLoading: false,
        error: null,
        data: {
          results: [
            makeResult({ id: 5, status: 'completed', sensitivity_analysis: { key: 'value' } }),
          ],
        },
      } as never);
      vi.mocked(useSynthesisResult).mockReturnValue({
        data: makeResult({ id: 5, status: 'completed', sensitivity_analysis: { key: 'value' } }),
        isLoading: false,
      } as never);
      renderPage();
      fireEvent.click(screen.getByText('completed'));
      expect(screen.getByText(/Sensitivity Analysis/)).toBeInTheDocument();
    });
  });
});
