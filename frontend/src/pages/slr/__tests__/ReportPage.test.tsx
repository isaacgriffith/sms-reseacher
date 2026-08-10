/**
 * Tests for ReportPage component (feature 007, T088).
 *
 * Covers:
 * - Renders format radio buttons (LaTeX, Markdown, JSON, CSV).
 * - Download button is enabled when synthesisComplete=true.
 * - Download button is disabled when synthesisComplete=false.
 * - Clicking download calls downloadSLRReport.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ReportPage from '../ReportPage';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

vi.mock('../../../services/slr/reportApi', () => ({
  downloadSLRReport: vi.fn().mockResolvedValue(undefined),
}));

// TFIX11 mounted ValidityThreatPanel on this page, which queries the threats
// endpoint. An empty list is the two-reviewer case, and keeps these tests
// about the export controls rather than about threats — the panel has its own
// suite in components/validity/__tests__.
vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ threats: [] }),
    patch: vi.fn(),
  },
}));

import { downloadSLRReport } from '../../../services/slr/reportApi';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderPage(synthesisComplete: boolean) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <ReportPage studyId={42} synthesisComplete={synthesisComplete} />
    </QueryClientProvider>,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ReportPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Format radio buttons', () => {
    it('renders Markdown radio option', () => {
      renderPage(true);
      expect(screen.getByLabelText(/markdown/i)).toBeInTheDocument();
    });

    it('renders LaTeX radio option', () => {
      renderPage(true);
      expect(screen.getByLabelText(/latex/i)).toBeInTheDocument();
    });

    it('renders JSON radio option', () => {
      renderPage(true);
      expect(screen.getByLabelText(/json/i)).toBeInTheDocument();
    });

    it('renders CSV radio option', () => {
      renderPage(true);
      expect(screen.getByLabelText(/csv/i)).toBeInTheDocument();
    });
  });

  describe('Download button state', () => {
    it('download button is enabled when synthesisComplete=true', () => {
      renderPage(true);
      const btn = screen.getByTestId('download-report-btn');
      expect(btn).not.toBeDisabled();
    });

    it('download button is disabled when synthesisComplete=false', () => {
      renderPage(false);
      const btn = screen.getByTestId('download-report-btn');
      expect(btn).toBeDisabled();
    });
  });

  describe('Download action', () => {
    it('calls downloadSLRReport with studyId and selected format on click', async () => {
      renderPage(true);
      const btn = screen.getByTestId('download-report-btn');
      fireEvent.click(btn);
      await waitFor(() => {
        expect(downloadSLRReport).toHaveBeenCalledWith(42, 'markdown');
      });
    });

    it('calls downloadSLRReport with json format when JSON is selected', async () => {
      renderPage(true);
      const jsonRadio = screen.getByLabelText(/json/i);
      fireEvent.click(jsonRadio);
      const btn = screen.getByTestId('download-report-btn');
      fireEvent.click(btn);
      await waitFor(() => {
        expect(downloadSLRReport).toHaveBeenCalledWith(42, 'json');
      });
    });

    it('shows error alert when download fails', async () => {
      (downloadSLRReport as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error('Network error'),
      );
      renderPage(true);
      fireEvent.click(screen.getByTestId('download-report-btn'));
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });
    });
  });
});
