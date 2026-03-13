/**
 * Tests for PaperQueue component.
 *
 * Mocks api.get to control data, wraps with QueryClientProvider.
 * Covers:
 * - Renders paper cards with title, status badge, phase tag
 * - Status filter sends correct query param
 * - Phase tag filter sends correct query param
 * - Clear filters button appears when filters active
 * - Empty state message when no papers
 * - Empty state hint changes when filters are active
 * - Pagination buttons render when pages exist
 */
// @ts-nocheck


import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

import { api } from '../../../services/api';
import PaperQueue from '../PaperQueue';

const mockApi = api as unknown as { get: ReturnType<typeof vi.fn> };

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const MOCK_PAPER = {
  id: 1,
  study_id: 1,
  paper_id: 10,
  phase_tag: 'initial-search',
  current_status: 'accepted' as const,
  duplicate_of_id: null,
  paper: {
    id: 10,
    title: 'Test-Driven Development: A Systematic Review',
    abstract: 'A comprehensive review of TDD practices.',
    doi: '10.1/tdd-review',
    authors: [{ name: 'Alice Smith' }],
    year: 2023,
    venue: 'JSS',
  },
};

const MOCK_REJECTED = {
  ...MOCK_PAPER,
  id: 2,
  paper_id: 11,
  current_status: 'rejected' as const,
  paper: { ...MOCK_PAPER.paper, id: 11, title: 'Rejected Paper', doi: '10.1/rej' },
};

describe('PaperQueue', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('shows "Paper Queue" heading', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);
      expect(screen.getByText('Paper Queue')).toBeTruthy();
    });

    it('renders a paper card with title when data loaded', async () => {
      mockApi.get.mockResolvedValue([MOCK_PAPER]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() =>
        expect(screen.getByText('Test-Driven Development: A Systematic Review')).toBeTruthy()
      );
    });

    it('renders paper status badge', async () => {
      mockApi.get.mockResolvedValue([MOCK_PAPER]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => expect(screen.getByText('accepted')).toBeTruthy());
    });

    it('renders phase tag label', async () => {
      mockApi.get.mockResolvedValue([MOCK_PAPER]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => expect(screen.getByText('initial-search')).toBeTruthy());
    });

    it('renders multiple paper cards', async () => {
      mockApi.get.mockResolvedValue([MOCK_PAPER, MOCK_REJECTED]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Test-Driven Development: A Systematic Review')).toBeTruthy();
        expect(screen.getByText('Rejected Paper')).toBeTruthy();
      });
    });
  });

  describe('Empty state', () => {
    it('shows "No candidate papers found" when list is empty', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() =>
        expect(screen.getByText(/no candidate papers found/i)).toBeTruthy()
      );
    });

    it('hints to run a search when no filters applied', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() =>
        expect(screen.getByText(/run a full search/i)).toBeTruthy()
      );
    });
  });

  describe('Filters', () => {
    it('status filter change triggers API call with status param', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);

      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'accepted' } });

      await waitFor(() => {
        expect(mockApi.get).toHaveBeenCalledWith(
          expect.stringContaining('status=accepted')
        );
      });
    });

    it('phase tag filter change triggers API call with phase_tag param', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);

      const input = screen.getByPlaceholderText(/filter by phase tag/i);
      fireEvent.change(input, { target: { value: 'backward-search-1' } });

      await waitFor(() => {
        expect(mockApi.get).toHaveBeenCalledWith(
          expect.stringContaining('phase_tag=backward-search-1')
        );
      });
    });

    it('clear filters button appears when status filter is active', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);

      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'rejected' } });

      await waitFor(() =>
        expect(screen.getByText(/clear filters/i)).toBeTruthy()
      );
    });

    it('clear filters button resets filter state and hides itself', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);

      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'rejected' } });

      await waitFor(() => expect(screen.getByText(/clear filters/i)).toBeTruthy());

      fireEvent.click(screen.getByText(/clear filters/i));

      await waitFor(() => {
        expect(screen.queryByText(/clear filters/i)).toBeNull();
      });
    });

    it('hints to adjust filters when results empty and filter active', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);

      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'duplicate' } });

      await waitFor(() =>
        expect(screen.getByText(/try adjusting your filters/i)).toBeTruthy()
      );
    });
  });

  describe('Refresh button', () => {
    it('renders the Refresh button', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);
      expect(screen.getByText('Refresh')).toBeTruthy();
    });
  });

  describe('Paper metadata display', () => {
    it('renders year when paper.year is present', async () => {
      mockApi.get.mockResolvedValue([MOCK_PAPER]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => expect(screen.getByText('2023')).toBeTruthy());
    });

    it('does not render year when paper.year is null', async () => {
      const paperNoYear = { ...MOCK_PAPER, paper: { ...MOCK_PAPER.paper, year: null } };
      mockApi.get.mockResolvedValue([paperNoYear]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Test-Driven Development: A Systematic Review'));
      expect(screen.queryByText('2023')).toBeNull();
    });

    it('renders venue when paper.venue is present', async () => {
      mockApi.get.mockResolvedValue([MOCK_PAPER]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => expect(screen.getByText('JSS')).toBeTruthy());
    });

    it('does not render venue when paper.venue is null', async () => {
      const paperNoVenue = { ...MOCK_PAPER, paper: { ...MOCK_PAPER.paper, venue: null } };
      mockApi.get.mockResolvedValue([paperNoVenue]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Test-Driven Development: A Systematic Review'));
      expect(screen.queryByText('JSS')).toBeNull();
    });

    it('renders DOI when paper.doi is present', async () => {
      mockApi.get.mockResolvedValue([MOCK_PAPER]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => expect(screen.getByText(/DOI: 10\.1\/tdd-review/)).toBeTruthy());
    });

    it('does not render DOI when paper.doi is null', async () => {
      const paperNoDoi = { ...MOCK_PAPER, paper: { ...MOCK_PAPER.paper, doi: null } };
      mockApi.get.mockResolvedValue([paperNoDoi]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Test-Driven Development: A Systematic Review'));
      expect(screen.queryByText(/DOI:/)).toBeNull();
    });

    it('renders abstract text when paper.abstract is present', async () => {
      mockApi.get.mockResolvedValue([MOCK_PAPER]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() =>
        expect(screen.getByText('A comprehensive review of TDD practices.')).toBeTruthy()
      );
    });

    it('does not render abstract element when paper.abstract is null', async () => {
      const paperNoAbstract = { ...MOCK_PAPER, paper: { ...MOCK_PAPER.paper, abstract: null } };
      mockApi.get.mockResolvedValue([paperNoAbstract]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Test-Driven Development: A Systematic Review'));
      expect(screen.queryByText('A comprehensive review of TDD practices.')).toBeNull();
    });
  });

  describe('Pagination', () => {
    // Build exactly PAGE_SIZE=20 unique papers
    const makePapers = (n: number) =>
      Array.from({ length: n }, (_, i) => ({
        ...MOCK_PAPER,
        id: i + 100,
        paper_id: i + 200,
        paper: { ...MOCK_PAPER.paper, id: i + 200, title: `Paper ${i}` },
      }));

    it('shows pagination when exactly PAGE_SIZE papers returned', async () => {
      mockApi.get.mockResolvedValue(makePapers(20));
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));
      expect(screen.queryByText(/← previous/i)).toBeTruthy();
    });

    it('Previous button is disabled on first page', async () => {
      mockApi.get.mockResolvedValue(makePapers(20));
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));
      const prev = screen.getByRole('button', { name: /← previous/i }) as HTMLButtonElement;
      expect(prev.disabled).toBe(true);
    });

    it('Next button is enabled when exactly PAGE_SIZE papers returned', async () => {
      mockApi.get.mockResolvedValue(makePapers(20));
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));
      const next = screen.getByRole('button', { name: /next →/i }) as HTMLButtonElement;
      expect(next.disabled).toBe(false);
    });

    it('Next button is disabled when fewer than PAGE_SIZE papers returned', async () => {
      mockApi.get.mockResolvedValue(makePapers(5));
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));
      // No pagination bar since page=0 and papers.length < PAGE_SIZE
      expect(screen.queryByRole('button', { name: /next →/i })).toBeNull();
    });

    it('does not show pagination when fewer than PAGE_SIZE and page=0', async () => {
      mockApi.get.mockResolvedValue(makePapers(3));
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));
      expect(screen.queryByText(/page/i)).toBeNull();
    });

    it('clicking Next advances to page 2 and sends correct offset', async () => {
      // First call: 20 papers (enabling next). Second call after click: 0 papers.
      mockApi.get
        .mockResolvedValueOnce(makePapers(20))
        .mockResolvedValueOnce([]);

      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));

      const next = screen.getByRole('button', { name: /next →/i });
      fireEvent.click(next);

      await waitFor(() => {
        expect(mockApi.get).toHaveBeenCalledWith(
          expect.stringContaining('offset=20')
        );
      });
    });

    it('shows "Page 1" text on first page', async () => {
      mockApi.get.mockResolvedValue(makePapers(20));
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));
      expect(screen.getByText('Page 1')).toBeTruthy();
    });

    it('shows pagination even when page > 0 and fewer than PAGE_SIZE papers', async () => {
      // First page: 20 papers. Second page: only 5 papers (but page > 0 so still show pagination).
      mockApi.get
        .mockResolvedValueOnce(makePapers(20))
        .mockResolvedValueOnce(makePapers(5));

      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));

      const next = screen.getByRole('button', { name: /next →/i });
      fireEvent.click(next);

      // On page 2 with only 5 papers — pagination still shows
      await waitFor(() => {
        expect(screen.getByText('Page 2')).toBeTruthy();
      });
    });

    it('clicking Previous goes back to page 1 and Previous is disabled', async () => {
      mockApi.get
        .mockResolvedValueOnce(makePapers(20))
        .mockResolvedValueOnce(makePapers(5));

      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));

      fireEvent.click(screen.getByRole('button', { name: /next →/i }));
      await waitFor(() => screen.getByText('Page 2'));

      const prev = screen.getByRole('button', { name: /← previous/i });
      fireEvent.click(prev);

      await waitFor(() => {
        expect(screen.getByText('Page 1')).toBeTruthy();
        const prevBtn = screen.getByRole('button', { name: /← previous/i }) as HTMLButtonElement;
        expect(prevBtn.disabled).toBe(true);
      });
    });

    it('clicking Previous never goes below page 1 (Math.max protection)', async () => {
      mockApi.get.mockResolvedValue(makePapers(20));

      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));
      expect(screen.getByText('Page 1')).toBeTruthy();

      // Previous button is disabled on page 1 — clicking it should not go to page 0
      const prev = screen.getByRole('button', { name: /← previous/i }) as HTMLButtonElement;
      expect(prev.disabled).toBe(true);
    });

    it('shows Page 2 text after clicking Next once', async () => {
      mockApi.get
        .mockResolvedValueOnce(makePapers(20))
        .mockResolvedValueOnce(makePapers(5));

      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => screen.getByText('Paper 0'));

      fireEvent.click(screen.getByRole('button', { name: /next →/i }));

      await waitFor(() => {
        expect(screen.getByText('Page 2')).toBeTruthy();
      });
    });
  });

  describe('API URL construction', () => {
    it('sends offset=0 and limit=20 in initial request', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);
      await waitFor(() => {
        expect(mockApi.get).toHaveBeenCalledWith(
          expect.stringContaining('offset=0')
        );
        expect(mockApi.get).toHaveBeenCalledWith(
          expect.stringContaining('limit=20')
        );
      });
    });

    it('sends both status and phase_tag params when both filters active', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);

      fireEvent.change(screen.getByRole('combobox'), { target: { value: 'accepted' } });
      const phaseInput = screen.getByPlaceholderText(/filter by phase tag/i);
      fireEvent.change(phaseInput, { target: { value: 'my-phase' } });

      await waitFor(() => {
        const lastCall: string = mockApi.get.mock.calls.at(-1)?.[0] ?? '';
        expect(lastCall).toContain('status=accepted');
        expect(lastCall).toContain('phase_tag=my-phase');
      });
    });

    it('clear filters resets page to 0 (offset=0)', async () => {
      // Start with filter, then clear it
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<PaperQueue studyId={1} />);

      fireEvent.change(screen.getByRole('combobox'), { target: { value: 'accepted' } });
      await waitFor(() => screen.getByText(/clear filters/i));
      fireEvent.click(screen.getByText(/clear filters/i));

      await waitFor(() => {
        const lastCall: string = mockApi.get.mock.calls.at(-1)?.[0] ?? '';
        expect(lastCall).toContain('offset=0');
      });
    });
  });
});
