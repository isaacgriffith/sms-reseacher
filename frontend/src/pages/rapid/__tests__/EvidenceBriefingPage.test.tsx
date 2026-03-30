/**
 * Unit tests for EvidenceBriefingPage (feature 008).
 *
 * Covers rendering of page header, generate button, empty state alert,
 * briefing version panel visibility, and generate error on 422.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import EvidenceBriefingPage from '../EvidenceBriefingPage';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/rapid/useBriefingVersions', () => ({
  useBriefings: vi.fn(),
  useGenerateBriefing: vi.fn(),
}));

vi.mock('../../../services/rapid/briefingApi', () => ({
  getBriefing: vi.fn(),
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

vi.mock('../../../components/rapid/BriefingVersionPanel', () => ({
  default: ({ onSelectBriefing }: { studyId: number; onSelectBriefing: (id: number) => void; selectedBriefingId: number | null }) => (
    <div data-testid="briefing-version-panel">
      <button onClick={() => onSelectBriefing(1)}>Select Briefing 1</button>
    </div>
  ),
}));

vi.mock('../../../components/rapid/BriefingPreview', () => ({
  default: ({ briefing }: { briefing: { title: string } }) => (
    <div data-testid="briefing-preview">{briefing.title}</div>
  ),
}));

import { useBriefings, useGenerateBriefing } from '../../../hooks/rapid/useBriefingVersions';
import { getBriefing, ApiError } from '../../../services/rapid/briefingApi';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const BRIEFING_SUMMARY = {
  id: 1,
  study_id: 42,
  version_number: 1,
  status: 'draft' as const,
  title: 'Test Briefing',
  generated_at: '2026-01-01T00:00:00Z',
  pdf_available: true,
  html_available: false,
};

const BRIEFING_DETAIL = {
  ...BRIEFING_SUMMARY,
  summary: 'Summary text',
  findings: { '0': 'Finding A' },
  target_audience: 'Practitioners',
  reference_complementary: null,
  institution_logos: [],
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('EvidenceBriefingPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useGenerateBriefing).mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as ReturnType<typeof useGenerateBriefing>);
  });

  describe('page header', () => {
    it('renders the Evidence Briefing heading', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);
      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      expect(screen.getByText('Evidence Briefing')).toBeTruthy();
    });

    it('renders the Generate New Version button', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);
      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      expect(screen.getByRole('button', { name: /generate new version/i })).toBeTruthy();
    });

    it('renders the phase description text', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);
      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      expect(screen.getByText(/phase 6/i)).toBeTruthy();
    });
  });

  describe('empty state', () => {
    it('shows info alert when no briefings exist', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);
      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      expect(screen.getByText(/no briefings yet/i)).toBeTruthy();
    });

    it('shows info alert when briefings is undefined', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: undefined } as ReturnType<typeof useBriefings>);
      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      expect(screen.getByText(/no briefings yet/i)).toBeTruthy();
    });

    it('does not show empty state when generation is pending', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);
      vi.mocked(useGenerateBriefing).mockReturnValue({
        mutate: vi.fn(),
        isPending: true,
      } as ReturnType<typeof useGenerateBriefing>);
      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      expect(screen.queryByText(/no briefings yet/i)).toBeNull();
    });
  });

  describe('briefing version panel', () => {
    it('renders BriefingVersionPanel when briefings exist', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BRIEFING_SUMMARY] } as ReturnType<typeof useBriefings>);
      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      expect(screen.getByTestId('briefing-version-panel')).toBeTruthy();
    });

    it('does not render BriefingVersionPanel when no briefings', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);
      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      expect(screen.queryByTestId('briefing-version-panel')).toBeNull();
    });
  });

  describe('generate button', () => {
    it('calls generateMutation.mutate when button is clicked', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);
      const mutate = vi.fn();
      vi.mocked(useGenerateBriefing).mockReturnValue({
        mutate,
        isPending: false,
      } as ReturnType<typeof useGenerateBriefing>);

      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /generate new version/i }));
      expect(mutate).toHaveBeenCalledWith(undefined, expect.any(Object));
    });

    it('disables the button when generation is pending', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);
      vi.mocked(useGenerateBriefing).mockReturnValue({
        mutate: vi.fn(),
        isPending: true,
      } as ReturnType<typeof useGenerateBriefing>);

      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      const btn = screen.getByRole('button', { name: /queuing/i }) as HTMLButtonElement;
      expect(btn.disabled).toBe(true);
    });

    it('disables button when any briefing is still generating', () => {
      const generatingBriefing = { ...BRIEFING_SUMMARY, pdf_available: false };
      vi.mocked(useBriefings).mockReturnValue({ data: [generatingBriefing] } as ReturnType<typeof useBriefings>);

      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      const btn = screen.getByRole('button', { name: /generate new version/i }) as HTMLButtonElement;
      expect(btn.disabled).toBe(true);
    });
  });

  describe('generate error handling', () => {
    it('shows 422 error message when synthesis is not complete', async () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);

      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useGenerateBriefing).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useGenerateBriefing>);

      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /generate new version/i }));

      // Simulate 422 error
      const err = new ApiError(422, 'Synthesis not complete');
      capturedOnError?.(err);

      await waitFor(() => {
        expect(screen.getByText(/cannot generate a briefing/i)).toBeTruthy();
      });
    });

    it('shows generic error message for non-422 errors', async () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);

      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useGenerateBriefing).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useGenerateBriefing>);

      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /generate new version/i }));

      const err = new Error('Server error');
      capturedOnError?.(err);

      await waitFor(() => {
        expect(screen.getByText('Server error')).toBeTruthy();
      });
    });

    it('dismisses error when close button on Alert is clicked', async () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [] } as ReturnType<typeof useBriefings>);

      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useGenerateBriefing).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useGenerateBriefing>);

      renderWithQuery(<EvidenceBriefingPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /generate new version/i }));

      capturedOnError?.(new Error('Some failure'));

      await waitFor(() => {
        expect(screen.getByText('Some failure')).toBeTruthy();
      });

      // Close the alert
      const closeBtn = screen.getByTitle('Close');
      fireEvent.click(closeBtn);

      await waitFor(() => {
        expect(screen.queryByText('Some failure')).toBeNull();
      });
    });
  });

  describe('briefing preview', () => {
    it('renders BriefingPreview after selecting a briefing', async () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BRIEFING_SUMMARY] } as ReturnType<typeof useBriefings>);
      vi.mocked(getBriefing).mockResolvedValue(BRIEFING_DETAIL);

      renderWithQuery(<EvidenceBriefingPage studyId={42} />);

      // Click "Select Briefing 1" in the mocked BriefingVersionPanel
      fireEvent.click(screen.getByText('Select Briefing 1'));

      await waitFor(() => {
        expect(screen.getByTestId('briefing-preview')).toBeTruthy();
      });

      expect(getBriefing).toHaveBeenCalledWith(42, 1);
    });
  });
});
