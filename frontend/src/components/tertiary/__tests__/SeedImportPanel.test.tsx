/**
 * Unit tests for SeedImportPanel component (feature 009, T045).
 *
 * Covers:
 * - Shows loading spinner while data is fetching.
 * - Shows error alert when query fails.
 * - Shows empty-state info alert when no imports exist.
 * - Renders import list when imports are present.
 * - "Import from Platform Study" button opens the import dialog.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SeedImportPanel from '../SeedImportPanel';

// ---------------------------------------------------------------------------
// Mock hooks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/tertiary/useSeedImports', () => ({
  useSeedImports: vi.fn(),
  useCreateSeedImport: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
    reset: vi.fn(),
    error: null,
    isError: false,
    isSuccess: false,
  })),
  useGroupStudies: vi.fn(() => ({
    data: [],
    isLoading: false,
  })),
}));

import { useSeedImports, useGroupStudies, useCreateSeedImport } from '../../../hooks/tertiary/useSeedImports';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Wrap the component under test in a QueryClientProvider.
 *
 * @param ui - The React element to render.
 * @returns Testing library render result.
 */
function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const SEED_IMPORT_FIXTURE = {
  id: 1,
  target_study_id: 10,
  source_study_id: 5,
  source_study_title: 'Source SLR Study',
  source_study_type: 'SLR',
  imported_at: '2026-01-15T12:00:00Z',
  records_added: 7,
  records_skipped: 2,
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('SeedImportPanel', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('loading state', () => {
    it('shows a loading indicator while fetching', () => {
      vi.mocked(useSeedImports).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      } as ReturnType<typeof useSeedImports>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      // MUI CircularProgress renders an SVG role="progressbar"
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('shows an error alert when the query fails', () => {
      vi.mocked(useSeedImports).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error('Network error'),
      } as ReturnType<typeof useSeedImports>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      expect(screen.getByText(/failed to load seed imports/i)).toBeInTheDocument();
    });
  });

  describe('empty state', () => {
    it('shows info alert when no imports exist', () => {
      vi.mocked(useSeedImports).mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      } as ReturnType<typeof useSeedImports>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      expect(screen.getByText(/no seed imports yet/i)).toBeInTheDocument();
    });
  });

  describe('populated state', () => {
    it('renders import list rows when imports exist', () => {
      vi.mocked(useSeedImports).mockReturnValue({
        data: [SEED_IMPORT_FIXTURE],
        isLoading: false,
        error: null,
      } as ReturnType<typeof useSeedImports>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      // The table renders "<title> (<type>)" in the same Typography element.
      expect(screen.getByText(/Source SLR Study/)).toBeInTheDocument();
    });

    it('displays records_added count', () => {
      vi.mocked(useSeedImports).mockReturnValue({
        data: [SEED_IMPORT_FIXTURE],
        isLoading: false,
        error: null,
      } as ReturnType<typeof useSeedImports>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      expect(screen.getByText(/7/)).toBeInTheDocument();
    });

    it('shows "Study #ID" fallback when source_study_title is null', () => {
      vi.mocked(useSeedImports).mockReturnValue({
        data: [{ ...SEED_IMPORT_FIXTURE, source_study_title: null, source_study_type: null }],
        isLoading: false,
        error: null,
      } as ReturnType<typeof useSeedImports>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      expect(screen.getByText(/Study #1/)).toBeInTheDocument();
    });
  });

  describe('import dialog', () => {
    beforeEach(() => {
      vi.mocked(useSeedImports).mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      } as ReturnType<typeof useSeedImports>);
    });

    it('renders "Import from Platform Study" button', () => {
      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      expect(
        screen.getByRole('button', { name: /import from platform study/i }),
      ).toBeInTheDocument();
    });

    it('opens the import dialog when button is clicked', () => {
      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));
      // After opening the dialog, the title text appears multiple times
      // (button + dialog title), so we verify at least two matches.
      const matches = screen.getAllByText(/import from platform study/i);
      expect(matches.length).toBeGreaterThanOrEqual(2);
    });

    it('renders study list in dialog when group studies are available', () => {
      vi.mocked(useGroupStudies).mockReturnValue({
        data: [
          { id: 5, name: 'My SLR Study', study_type: 'SLR', current_phase: 3 },
          { id: 6, name: 'My SMS Study', study_type: 'SMS', current_phase: 2 },
        ],
        isLoading: false,
      } as ReturnType<typeof useGroupStudies>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));
      expect(screen.getByText('My SLR Study')).toBeInTheDocument();
      expect(screen.getByText('My SMS Study')).toBeInTheDocument();
    });

    it('shows already imported studies as disabled in dialog', () => {
      vi.mocked(useSeedImports).mockReturnValue({
        data: [{ ...SEED_IMPORT_FIXTURE, source_study_id: 5 }],
        isLoading: false,
        error: null,
      } as ReturnType<typeof useSeedImports>);

      vi.mocked(useGroupStudies).mockReturnValue({
        data: [{ id: 5, name: 'Already Imported Study', study_type: 'SLR', current_phase: 3 }],
        isLoading: false,
      } as ReturnType<typeof useGroupStudies>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));
      expect(screen.getByText(/already imported/i)).toBeInTheDocument();
    });

    it('shows "Importing…" text in Import button when mutation isPending', () => {
      vi.mocked(useCreateSeedImport).mockReturnValue({
        mutate: vi.fn(),
        isPending: true,
        reset: vi.fn(),
        error: null,
        isError: false,
        isSuccess: false,
      } as unknown as ReturnType<typeof useCreateSeedImport>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));
      expect(screen.getByText(/Importing…/i)).toBeInTheDocument();
    });

    it('shows loading spinner in dialog while group studies are loading', () => {
      vi.mocked(useGroupStudies).mockReturnValue({
        data: [],
        isLoading: true,
      } as unknown as ReturnType<typeof useGroupStudies>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));
      // CircularProgress inside dialog
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('shows mutation error in dialog when import fails', () => {
      vi.mocked(useCreateSeedImport).mockReturnValue({
        mutate: vi.fn(),
        isPending: false,
        reset: vi.fn(),
        error: new Error('Import server error'),
        isError: true,
        isSuccess: false,
      } as unknown as ReturnType<typeof useCreateSeedImport>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));
      expect(screen.getByText(/Import server error/i)).toBeInTheDocument();
    });

    it('Cancel button is clickable in the dialog', () => {
      const reset = vi.fn();
      vi.mocked(useCreateSeedImport).mockReturnValue({
        mutate: vi.fn(),
        isPending: false,
        reset,
        error: null,
        isError: false,
        isSuccess: false,
      } as unknown as ReturnType<typeof useCreateSeedImport>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));
      const cancelBtn = screen.getByRole('button', { name: /^cancel$/i });
      fireEvent.click(cancelBtn);
      // reset is called as part of handleClose
      expect(reset).toHaveBeenCalled();
    });

    it('calls mutate when a study is selected and Import is clicked', () => {
      const mutate = vi.fn();
      vi.mocked(useCreateSeedImport).mockReturnValue({
        mutate,
        isPending: false,
        reset: vi.fn(),
        error: null,
        isError: false,
        isSuccess: false,
      } as unknown as ReturnType<typeof useCreateSeedImport>);

      vi.mocked(useGroupStudies).mockReturnValue({
        data: [{ id: 5, name: 'My SLR', study_type: 'SLR', current_phase: 3 }],
        isLoading: false,
      } as unknown as ReturnType<typeof useGroupStudies>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));

      // Click on the study to select it.
      fireEvent.click(screen.getByText('My SLR'));

      // Click Import button.
      const importBtn = screen.getByRole('button', { name: /^Import$/i });
      fireEvent.click(importBtn);
      expect(mutate).toHaveBeenCalledWith(5, expect.objectContaining({ onSuccess: expect.any(Function) }));
    });

    it('invokes handleImportSuccess callback (closes dialog, resets mutation) on success', () => {
      const reset = vi.fn();
      const mutate = vi.fn().mockImplementation((_id: number, options: { onSuccess?: () => void }) => {
        options?.onSuccess?.();
      });
      vi.mocked(useCreateSeedImport).mockReturnValue({
        mutate,
        isPending: false,
        reset,
        error: null,
        isError: false,
        isSuccess: false,
      } as unknown as ReturnType<typeof useCreateSeedImport>);

      vi.mocked(useGroupStudies).mockReturnValue({
        data: [{ id: 5, name: 'My SLR 2', study_type: 'SLR', current_phase: 2 }],
        isLoading: false,
      } as unknown as ReturnType<typeof useGroupStudies>);

      renderWithQuery(<SeedImportPanel studyId={10} groupId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /import from platform study/i }));
      fireEvent.click(screen.getByText('My SLR 2'));
      fireEvent.click(screen.getByRole('button', { name: /^Import$/i }));

      // onSuccess calls handleImportSuccess which calls importMutation.reset()
      expect(reset).toHaveBeenCalled();
    });
  });
});
