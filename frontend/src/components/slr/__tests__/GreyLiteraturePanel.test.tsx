/**
 * Tests for GreyLiteraturePanel component (feature 007, T096).
 *
 * Covers:
 * - Renders empty state when no sources exist.
 * - Renders table rows when sources exist.
 * - "Add Source" button opens the dialog.
 * - Delete button calls useDeleteSource mutation.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import GreyLiteraturePanel from '../GreyLiteraturePanel';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/slr/useGreyLiterature', () => ({
  useGreyLiterature: vi.fn(),
  useAddSource: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
    isError: false,
    error: null,
  })),
  useDeleteSource: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
  })),
}));

import {
  useGreyLiterature,
  useDeleteSource,
} from '../../../hooks/slr/useGreyLiterature';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeSource(overrides = {}) {
  return {
    id: 1,
    study_id: 42,
    source_type: 'technical_report',
    title: 'Test Report',
    authors: 'Jane Doe',
    year: 2024,
    url: null,
    description: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

function renderPanel(studyId = 42) {
  const qc = new QueryClient();
  render(
    <QueryClientProvider client={qc}>
      <GreyLiteraturePanel studyId={studyId} />
    </QueryClientProvider>,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('GreyLiteraturePanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Loading state', () => {
    it('shows loading spinner when data is loading', () => {
      (useGreyLiterature as ReturnType<typeof vi.fn>).mockReturnValue({ isLoading: true });
      renderPanel();
      expect(screen.getByLabelText(/loading grey literature/i)).toBeInTheDocument();
    });
  });

  describe('Error state', () => {
    it('shows error alert when fetch fails', () => {
      (useGreyLiterature as ReturnType<typeof vi.fn>).mockReturnValue({
        isLoading: false,
        error: new Error('Network error'),
      });
      renderPanel();
      expect(screen.getByTestId('grey-lit-error')).toBeInTheDocument();
    });
  });

  describe('Empty state', () => {
    it('shows empty state message when no sources exist', () => {
      (useGreyLiterature as ReturnType<typeof vi.fn>).mockReturnValue({
        isLoading: false,
        error: null,
        data: { sources: [] },
      });
      renderPanel();
      expect(screen.getByTestId('grey-lit-empty')).toBeInTheDocument();
    });
  });

  describe('Source rows', () => {
    it('renders table rows when sources exist', () => {
      (useGreyLiterature as ReturnType<typeof vi.fn>).mockReturnValue({
        isLoading: false,
        error: null,
        data: {
          sources: [
            makeSource({ id: 1, title: 'Technical Report A' }),
            makeSource({ id: 2, title: 'Dissertation B', source_type: 'dissertation' }),
          ],
        },
      });
      renderPanel();
      expect(screen.getByText('Technical Report A')).toBeInTheDocument();
      expect(screen.getByText('Dissertation B')).toBeInTheDocument();
    });

    it('renders type chip for each source', () => {
      (useGreyLiterature as ReturnType<typeof vi.fn>).mockReturnValue({
        isLoading: false,
        error: null,
        data: { sources: [makeSource({ source_type: 'technical_report' })] },
      });
      renderPanel();
      expect(screen.getByText('Technical Report')).toBeInTheDocument();
    });
  });

  describe('Add Source button', () => {
    beforeEach(() => {
      (useGreyLiterature as ReturnType<typeof vi.fn>).mockReturnValue({
        isLoading: false,
        error: null,
        data: { sources: [] },
      });
    });

    it('"Add Source" button is rendered', () => {
      renderPanel();
      expect(screen.getByTestId('add-source-btn')).toBeInTheDocument();
    });

    it('clicking "Add Source" opens the dialog', () => {
      renderPanel();
      fireEvent.click(screen.getByTestId('add-source-btn'));
      expect(screen.getByText('Add Grey Literature Source')).toBeInTheDocument();
    });
  });

  describe('Delete button', () => {
    it('delete button calls useDeleteSource mutation with source id', () => {
      const mockMutate = vi.fn();
      (useDeleteSource as ReturnType<typeof vi.fn>).mockReturnValue({
        mutate: mockMutate,
        isPending: false,
      });
      (useGreyLiterature as ReturnType<typeof vi.fn>).mockReturnValue({
        isLoading: false,
        error: null,
        data: { sources: [makeSource({ id: 99 })] },
      });
      renderPanel();
      fireEvent.click(screen.getByTestId('delete-source-99'));
      expect(mockMutate).toHaveBeenCalledWith(99);
    });
  });
});
