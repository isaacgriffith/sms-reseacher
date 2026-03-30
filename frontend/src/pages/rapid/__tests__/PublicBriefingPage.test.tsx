/**
 * Unit tests for PublicBriefingPage (feature 008).
 *
 * Covers loading state, not-found state, fetch error, successful briefing render,
 * download PDF/HTML buttons.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import PublicBriefingPage from '../PublicBriefingPage';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../services/rapid/briefingApi', () => ({
  getPublicBriefing: vi.fn(),
  exportPublicBriefing: vi.fn().mockResolvedValue(new Blob(['%PDF'])),
  ApiError: class ApiError extends Error {
    status: number;
    detail: string;
    constructor(status: number, detail: string) {
      super(detail);
      this.status = status;
      this.detail = detail;
    }
  },
}));

vi.mock('../../../components/rapid/BriefingPreview', () => ({
  default: ({ briefing }: { briefing: { title: string } }) => (
    <div data-testid="briefing-preview">{briefing.title}</div>
  ),
}));

import { getPublicBriefing, ApiError } from '../../../services/rapid/briefingApi';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderPage(token = 'test-token') {
  return render(
    <MemoryRouter initialEntries={[`/public/briefings/${token}`]}>
      <Routes>
        <Route path="/public/briefings/:token" element={<PublicBriefingPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

const PUBLIC_BRIEFING = {
  id: 1,
  study_id: 42,
  version_number: 1,
  status: 'published' as const,
  title: 'Public Briefing Title',
  generated_at: '2026-01-01T00:00:00Z',
  pdf_available: true,
  html_available: true,
  summary: 'Evidence summary',
  findings: { '0': 'Finding A' },
  target_audience: 'Policy makers',
  reference_complementary: null,
  institution_logos: [],
  threats: [],
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('PublicBriefingPage', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('loading state', () => {
    it('shows loading indicator while fetching', () => {
      vi.mocked(getPublicBriefing).mockImplementation(() => new Promise(() => {}));
      renderPage();
      expect(screen.getByText(/loading briefing/i)).toBeTruthy();
    });
  });

  describe('not found', () => {
    it('shows not-found alert for 404 error', async () => {
      vi.mocked(getPublicBriefing).mockRejectedValue(new ApiError(404, 'Not Found'));
      renderPage();
      await waitFor(() => {
        expect(screen.getByText(/no longer available/i)).toBeTruthy();
      });
    });

    it('shows not-found alert for 410 error', async () => {
      vi.mocked(getPublicBriefing).mockRejectedValue(new ApiError(410, 'Gone'));
      renderPage();
      await waitFor(() => {
        expect(screen.getByText(/no longer available/i)).toBeTruthy();
      });
    });
  });

  describe('fetch error', () => {
    it('shows error alert for network errors', async () => {
      vi.mocked(getPublicBriefing).mockRejectedValue(new Error('Network failure'));
      renderPage();
      await waitFor(() => {
        expect(screen.getByText(/network failure/i)).toBeTruthy();
      });
    });
  });

  describe('successful render', () => {
    it('renders BriefingPreview when briefing is loaded', async () => {
      vi.mocked(getPublicBriefing).mockResolvedValue(PUBLIC_BRIEFING);
      renderPage();
      await waitFor(() => {
        expect(screen.getByTestId('briefing-preview')).toBeTruthy();
      });
    });

    it('shows Evidence Briefing heading', async () => {
      vi.mocked(getPublicBriefing).mockResolvedValue(PUBLIC_BRIEFING);
      renderPage();
      await waitFor(() => {
        expect(screen.getByText('Evidence Briefing')).toBeTruthy();
      });
    });

    it('shows Download PDF button when pdf_available', async () => {
      vi.mocked(getPublicBriefing).mockResolvedValue(PUBLIC_BRIEFING);
      renderPage();
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /download pdf/i })).toBeTruthy();
      });
    });

    it('shows Download HTML button when html_available', async () => {
      vi.mocked(getPublicBriefing).mockResolvedValue(PUBLIC_BRIEFING);
      renderPage();
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /download html/i })).toBeTruthy();
      });
    });

    it('does not show Download HTML button when html_available is false', async () => {
      vi.mocked(getPublicBriefing).mockResolvedValue({ ...PUBLIC_BRIEFING, html_available: false });
      renderPage();
      await waitFor(() => {
        expect(screen.getByTestId('briefing-preview')).toBeTruthy();
      });
      expect(screen.queryByRole('button', { name: /download html/i })).toBeNull();
    });

    it('disables PDF button when pdf_available is false', async () => {
      vi.mocked(getPublicBriefing).mockResolvedValue({ ...PUBLIC_BRIEFING, pdf_available: false });
      renderPage();
      await waitFor(() => {
        const pdfBtn = screen.getByRole('button', { name: /download pdf/i }) as HTMLButtonElement;
        expect(pdfBtn.disabled).toBe(true);
      });
    });
  });
});
