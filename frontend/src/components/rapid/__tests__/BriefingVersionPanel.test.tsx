/**
 * Unit tests for BriefingVersionPanel component (feature 008).
 *
 * Covers loading state, empty state, version display, status chip,
 * generating indicator, Publish button, PDF/HTML download buttons,
 * Copy Share Link button, and row click callback.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import BriefingVersionPanel from '../BriefingVersionPanel';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../services/rapid/briefingApi', () => ({
  exportBriefing: vi.fn().mockResolvedValue(new Blob(['%PDF'], { type: 'application/pdf' })),
}));

vi.mock('../../../hooks/rapid/useBriefingVersions', () => ({
  useBriefings: vi.fn(),
  usePublishBriefing: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useCreateShareToken: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

import { useBriefings, usePublishBriefing } from '../../../hooks/rapid/useBriefingVersions';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const BASE_SUMMARY = {
  id: 1,
  study_id: 42,
  version_number: 1,
  status: 'draft' as const,
  title: 'Briefing 1',
  generated_at: '2026-01-01T10:00:00Z',
  pdf_available: true,
  html_available: true,
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('BriefingVersionPanel', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('loading state', () => {
    it('shows loading indicator when isLoading is true', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: undefined, isLoading: true } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByText(/loading briefings/i)).toBeTruthy();
    });
  });

  describe('empty state', () => {
    it('renders empty fragment when briefings array is empty', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [], isLoading: false } as ReturnType<typeof useBriefings>);
      const { container } = renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      // Should render nothing (empty fragment)
      expect(container.firstChild).toBeNull();
    });

    it('renders empty fragment when data is undefined', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: undefined, isLoading: false } as ReturnType<typeof useBriefings>);
      const { container } = renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(container.firstChild).toBeNull();
    });
  });

  describe('version display', () => {
    it('shows version number in the table', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByText('v1')).toBeTruthy();
    });

    it('shows Draft status chip for draft briefing with pdf_available', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByText('Draft')).toBeTruthy();
    });

    it('shows Published chip for a published briefing', () => {
      const published = { ...BASE_SUMMARY, status: 'published' as const };
      vi.mocked(useBriefings).mockReturnValue({ data: [published], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByText('Published')).toBeTruthy();
    });

    it('shows Generating indicator when pdf_available is false', () => {
      const generating = { ...BASE_SUMMARY, pdf_available: false };
      vi.mocked(useBriefings).mockReturnValue({ data: [generating], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByText(/generating/i)).toBeTruthy();
    });
  });

  describe('action buttons', () => {
    it('shows Publish button for draft briefing with pdf_available', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByRole('button', { name: /publish/i })).toBeTruthy();
    });

    it('does not show Publish button when briefing is generating', () => {
      const generating = { ...BASE_SUMMARY, pdf_available: false };
      vi.mocked(useBriefings).mockReturnValue({ data: [generating], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.queryByRole('button', { name: /publish/i })).toBeNull();
    });

    it('shows PDF button when pdf_available', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByRole('button', { name: 'PDF' })).toBeTruthy();
    });

    it('shows HTML button when html_available', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByRole('button', { name: 'HTML' })).toBeTruthy();
    });

    it('does not show PDF button when pdf_available is false', () => {
      const noPdf = { ...BASE_SUMMARY, pdf_available: false, html_available: false };
      vi.mocked(useBriefings).mockReturnValue({ data: [noPdf], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.queryByRole('button', { name: 'PDF' })).toBeNull();
    });

    it('shows Copy Share Link button for published briefing', () => {
      const published = { ...BASE_SUMMARY, status: 'published' as const };
      vi.mocked(useBriefings).mockReturnValue({ data: [published], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByRole('button', { name: /copy share link/i })).toBeTruthy();
    });

    it('does not show Copy Share Link button for draft briefing', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.queryByRole('button', { name: /copy share link/i })).toBeNull();
    });
  });

  describe('row click callback', () => {
    it('calls onSelectBriefing with briefing id when row is clicked', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      const onSelect = vi.fn();
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={onSelect} selectedBriefingId={null} />,
      );
      fireEvent.click(screen.getByText('v1'));
      expect(onSelect).toHaveBeenCalledWith(1);
    });
  });

  describe('publish action', () => {
    it('calls publish mutation when Publish button is clicked and user confirms', () => {
      const publishMutate = vi.fn();
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      vi.mocked(usePublishBriefing).mockReturnValue({ mutate: publishMutate, isPending: false } as ReturnType<typeof usePublishBriefing>);
      vi.spyOn(window, 'confirm').mockReturnValue(true);

      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      fireEvent.click(screen.getByRole('button', { name: /publish/i }));
      expect(publishMutate).toHaveBeenCalledWith(1);

      vi.restoreAllMocks();
    });

    it('does not call publish mutation when user cancels confirm dialog', () => {
      const publishMutate = vi.fn();
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      vi.mocked(usePublishBriefing).mockReturnValue({ mutate: publishMutate, isPending: false } as ReturnType<typeof usePublishBriefing>);
      vi.spyOn(window, 'confirm').mockReturnValue(false);

      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      fireEvent.click(screen.getByRole('button', { name: /publish/i }));
      expect(publishMutate).not.toHaveBeenCalled();

      vi.restoreAllMocks();
    });
  });

  describe('table headers', () => {
    it('renders table column headers', () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);
      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      expect(screen.getByText('Version')).toBeTruthy();
      expect(screen.getByText('Status')).toBeTruthy();
      expect(screen.getByText('Generated')).toBeTruthy();
      expect(screen.getByText('Actions')).toBeTruthy();
    });
  });

  describe('PDF download', () => {
    it('triggers download when PDF button is clicked', async () => {
      vi.mocked(useBriefings).mockReturnValue({ data: [BASE_SUMMARY], isLoading: false } as ReturnType<typeof useBriefings>);

      // Mock URL.createObjectURL and revokeObjectURL
      const createUrl = vi.fn().mockReturnValue('blob:url');
      const revokeUrl = vi.fn();
      vi.stubGlobal('URL', { createObjectURL: createUrl, revokeObjectURL: revokeUrl });

      renderWithQuery(
        <BriefingVersionPanel studyId={42} onSelectBriefing={vi.fn()} selectedBriefingId={null} />,
      );
      fireEvent.click(screen.getByRole('button', { name: 'PDF' }));

      await waitFor(() => {
        expect(createUrl).toHaveBeenCalled();
      });

      vi.unstubAllGlobals();
    });
  });
});
