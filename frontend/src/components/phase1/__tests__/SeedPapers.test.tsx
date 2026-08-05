/**
 * Tests for SeedPapers component.
 * Verifies list rendering, add/remove actions, Librarian and Expert AI button calls.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

vi.mock('../../../services/jobs', () => ({
  useJobProgress: vi.fn(() => ({ status: 'queued', progressPct: 0, detail: null, error: null })),
}));

import { api } from '../../../services/api';
import SeedPapers from '../SeedPapers';

const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe('SeedPapers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('shows empty state when no seeds', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      renderWithQuery(<SeedPapers studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/no seed papers yet/i)).toBeTruthy();
      });
    });

    it('renders seed paper items when seeds are returned', async () => {
      mockApi.get.mockResolvedValueOnce([
        {
          id: 1,
          paper: { id: 10, title: 'Paper A', doi: '10.1/a', authors: [], year: 2022, venue: 'TSE' },
          added_by: 'user',
        },
      ]);
      renderWithQuery(<SeedPapers studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Paper A')).toBeTruthy();
      });
    });
  });

  describe('Add by DOI', () => {
    it('calls api.post with doi when Add by DOI is clicked', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 2,
        paper: {
          id: 20,
          title: '10.1145/test',
          doi: '10.1145/test',
          authors: [],
          year: null,
          venue: null,
        },
        added_by: 'user',
      });
      renderWithQuery(<SeedPapers studyId={1} />);

      const doiInput = screen.getByPlaceholderText(/doi/i);
      fireEvent.change(doiInput, { target: { value: '10.1145/test' } });

      const addButton = screen.getByRole('button', { name: /add by doi/i });
      fireEvent.click(addButton);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/studies/1/seeds/papers', {
          doi: '10.1145/test',
        });
      });
    });
  });

  describe('Librarian AI button', () => {
    it('calls POST /seeds/librarian when Suggest with Librarian AI is clicked', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({ suggestions: { papers: [] } });
      renderWithQuery(<SeedPapers studyId={1} />);

      await waitFor(() => screen.getByText(/no seed papers yet/i));

      const libButton = screen.getByRole('button', { name: /librarian ai/i });
      fireEvent.click(libButton);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/studies/1/seeds/librarian', {});
      });
    });

    it('shows librarian suggestions after successful call', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        suggestions: {
          papers: [
            {
              title: 'Suggested Paper X',
              authors: ['A. Smith'],
              year: 2022,
              venue: 'JSS',
              doi: null,
              rationale: 'Relevant.',
            },
          ],
        },
      });
      renderWithQuery(<SeedPapers studyId={1} />);
      await waitFor(() => screen.getByText(/no seed papers yet/i));

      fireEvent.click(screen.getByRole('button', { name: /librarian ai/i }));

      await waitFor(() => {
        expect(screen.getByText('Suggested Paper X')).toBeTruthy();
      });
    });
  });

  describe('Add Manually', () => {
    it('calls api.post with title when Add Manually is clicked', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 3,
        paper: { id: 30, title: 'Manual Paper', doi: null, authors: [], year: null, venue: null },
        added_by: 'user',
      });
      renderWithQuery(<SeedPapers studyId={1} />);

      const titleInput = screen.getByPlaceholderText(/paper title/i);
      fireEvent.change(titleInput, { target: { value: 'Manual Paper' } });
      fireEvent.click(screen.getByRole('button', { name: /add manually/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/studies/1/seeds/papers', {
          title: 'Manual Paper',
        });
      });
    });

    it('does not submit when title is empty', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      renderWithQuery(<SeedPapers studyId={1} />);
      await waitFor(() => screen.getByText(/no seed papers yet/i));
      fireEvent.click(screen.getByRole('button', { name: /add manually/i }));
      // post should not be called (only the initial get)
      expect(mockApi.post).not.toHaveBeenCalled();
    });
  });

  describe('Delete seed', () => {
    it('calls api.delete when remove button is clicked', async () => {
      mockApi.get.mockResolvedValueOnce([
        {
          id: 5,
          paper: { id: 10, title: 'Paper A', doi: '10.1/a', authors: [], year: 2022, venue: 'TSE' },
          added_by: 'user',
        },
      ]);
      mockApi.delete.mockResolvedValueOnce(undefined);
      renderWithQuery(<SeedPapers studyId={1} />);
      await waitFor(() => screen.getByText('Paper A'));
      // The delete button shows ✕
      const deleteBtn = screen.getByRole('button', { name: /✕/ });
      fireEvent.click(deleteBtn);
      await waitFor(() => {
        expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/studies/1/seeds/papers/5');
      });
    });
  });

  describe('Expert AI button', () => {
    it('renders Find with Expert AI button', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      renderWithQuery(<SeedPapers studyId={1} />);
      await waitFor(() => screen.getByText(/no seed papers yet/i));
      expect(screen.getByRole('button', { name: /expert ai/i })).toBeTruthy();
    });

    it('calls POST /seeds/expert and sets jobId when clicked', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({ job_id: 'abc-123' });
      renderWithQuery(<SeedPapers studyId={1} />);
      await waitFor(() => screen.getByText(/no seed papers yet/i));

      fireEvent.click(screen.getByRole('button', { name: /expert ai/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/studies/1/seeds/expert', {});
      });
    });
  });

  describe('Error handling', () => {
    it('shows error message when add fails', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockRejectedValueOnce(new Error('fail'));
      renderWithQuery(<SeedPapers studyId={1} />);

      const doiInput = screen.getByPlaceholderText(/doi/i);
      fireEvent.change(doiInput, { target: { value: '10.1/fail' } });
      fireEvent.click(screen.getByRole('button', { name: /add by doi/i }));

      await waitFor(() => {
        expect(screen.getByText(/failed to add paper/i)).toBeTruthy();
      });
    });

    it('shows empty suggestions when librarian fails', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockRejectedValueOnce(new Error('fail'));
      renderWithQuery(<SeedPapers studyId={1} />);
      await waitFor(() => screen.getByText(/no seed papers yet/i));

      fireEvent.click(screen.getByRole('button', { name: /librarian ai/i }));

      await waitFor(() => {
        expect(screen.getByText(/no suggestions available/i)).toBeTruthy();
      });
    });
  });

  describe('Keyboard shortcuts', () => {
    it('submits DOI on Enter key', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 4,
        paper: { id: 40, title: 'Enter Paper', doi: '10.1/enter', authors: [], year: null, venue: null },
        added_by: 'user',
      });
      renderWithQuery(<SeedPapers studyId={1} />);

      const doiInput = screen.getByPlaceholderText(/doi/i);
      fireEvent.change(doiInput, { target: { value: '10.1/enter' } });
      fireEvent.keyDown(doiInput, { key: 'Enter' });

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalled();
      });
    });
  });
});
