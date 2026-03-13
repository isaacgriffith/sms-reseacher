/**
 * Tests for TestRetest component.
 * Verifies iteration recall display, run test button, and approve/reject buttons.
 */
// @ts-nocheck


import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

import { api } from '../../../services/api';
import TestRetest from '../TestRetest';

const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  patch: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const MOCK_ITERATION_PENDING = {
  id: 5,
  iteration_number: 1,
  result_set_count: 42,
  test_set_recall: 0.75,
  ai_adequacy_judgment: 'Good coverage of TDD terms.',
  human_approved: null,
};

const MOCK_SEARCH_STRINGS = [
  {
    id: 1,
    version: 1,
    string_text: '("TDD" OR "test-driven") AND quality',
    is_active: false,
    created_by_agent: null,
    iterations: [MOCK_ITERATION_PENDING],
  },
];

const MOCK_STRINGS_NO_ITERATIONS = [
  {
    id: 1,
    version: 1,
    string_text: '("TDD") AND quality',
    is_active: false,
    created_by_agent: null,
    iterations: [],
  },
];

describe('TestRetest', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Empty state', () => {
    it('shows "No search strings yet" when list is empty', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/no search strings yet/i)).toBeTruthy();
      });
    });

    it('shows "No test iterations yet" when string has no iterations', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_STRINGS_NO_ITERATIONS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/no test iterations yet/i)).toBeTruthy();
      });
    });
  });

  describe('Rendering iterations', () => {
    it('displays iteration recall percentage', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('75.0%')).toBeTruthy();
      });
    });

    it('displays iteration result count', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('42')).toBeTruthy();
      });
    });

    it('displays Pending status for unapproved iteration', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Pending')).toBeTruthy();
      });
    });

    it('displays Approved status for approved iteration', async () => {
      const approved = { ...MOCK_ITERATION_PENDING, human_approved: true };
      mockApi.get.mockResolvedValueOnce([
        { ...MOCK_SEARCH_STRINGS[0], iterations: [approved] },
      ]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Approved')).toBeTruthy();
      });
    });

    it('displays Rejected status for rejected iteration', async () => {
      const rejected = { ...MOCK_ITERATION_PENDING, human_approved: false };
      mockApi.get.mockResolvedValueOnce([
        { ...MOCK_SEARCH_STRINGS[0], iterations: [rejected] },
      ]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Rejected')).toBeTruthy();
      });
    });

    it('displays AI judgment text', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Good coverage of TDD terms.')).toBeTruthy();
      });
    });
  });

  describe('Run test search', () => {
    it('renders Run Test Search button', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /run test search/i })).toBeTruthy();
      });
    });

    it('calls api.post to trigger test search', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      mockApi.post.mockResolvedValueOnce({ job_id: 'job-abc', search_string_id: 1 });

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));

      fireEvent.click(screen.getByRole('button', { name: /run test search/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/search-strings/1/test',
          expect.objectContaining({ databases: expect.any(Array) }),
        );
      });
    });
  });

  describe('Search string selector', () => {
    it('shows "(active)" for active strings in selector', async () => {
      const activeString = { ...MOCK_SEARCH_STRINGS[0], is_active: true };
      mockApi.get.mockResolvedValueOnce([activeString]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/\(active\)/)).toBeTruthy();
      });
    });

    it('does not show "(active)" for non-active strings', async () => {
      // MOCK_SEARCH_STRINGS[0] has is_active: false
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      expect(screen.queryByText(/\(active\)/)).toBeNull();
    });

    it('shows "[AI]" for AI-generated strings in selector', async () => {
      const aiString = { ...MOCK_SEARCH_STRINGS[0], created_by_agent: 'search-builder' };
      mockApi.get.mockResolvedValueOnce([aiString]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/\[AI\]/)).toBeTruthy();
      });
    });
  });

  describe('Databases input', () => {
    it('passes parsed databases to api.post on run', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      mockApi.post.mockResolvedValueOnce({ job_id: 'job-db', search_string_id: 1 });

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));

      const dbInput = screen.getByPlaceholderText(/acm,ieee,scopus/i);
      fireEvent.change(dbInput, { target: { value: 'acm, ieee, scopus' } });
      fireEvent.click(screen.getByRole('button', { name: /run test search/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/search-strings/1/test',
          { databases: ['acm', 'ieee', 'scopus'] },
        );
      });
    });

    it('passes empty databases array when input is empty', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      mockApi.post.mockResolvedValueOnce({ job_id: 'job-emptydb', search_string_id: 1 });

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      fireEvent.click(screen.getByRole('button', { name: /run test search/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/search-strings/1/test',
          { databases: [] },
        );
      });
    });
  });

  describe('Success and error state', () => {
    it('shows "Test search queued" message after successful run', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      mockApi.post.mockResolvedValueOnce({ job_id: 'job-queued', search_string_id: 1 });

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      fireEvent.click(screen.getByRole('button', { name: /run test search/i }));

      await waitFor(() => {
        expect(screen.getByText(/test search queued/i)).toBeTruthy();
      });
    });

    it('shows error message when run fails', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      const { ApiError: MockApiError } = await import('../../../services/api');
      const err = new MockApiError('Test search failed due to queue error');
      (err as { detail?: string }).detail = 'Queue is full';
      mockApi.post.mockRejectedValueOnce(err);

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      fireEvent.click(screen.getByRole('button', { name: /run test search/i }));

      await waitFor(() => {
        expect(screen.getByText('Queue is full')).toBeTruthy();
      });
    });
  });

  describe('Recall color thresholds', () => {
    it('shows green for recall >= 0.8', async () => {
      const highRecall = { ...MOCK_ITERATION_PENDING, test_set_recall: 0.8 };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [highRecall] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => expect(screen.getByText('80.0%')).toBeTruthy());
      // Green color for high recall
      const recallSpan = screen.getByText('80.0%');
      expect(recallSpan.style.color).toBe('rgb(22, 163, 74)'); // #16a34a
    });

    it('shows amber for recall 0.5 <= x < 0.8', async () => {
      const midRecall = { ...MOCK_ITERATION_PENDING, test_set_recall: 0.5 };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [midRecall] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => expect(screen.getByText('50.0%')).toBeTruthy());
      const recallSpan = screen.getByText('50.0%');
      expect(recallSpan.style.color).toBe('rgb(217, 119, 6)'); // #d97706
    });

    it('shows red for recall < 0.5', async () => {
      const lowRecall = { ...MOCK_ITERATION_PENDING, test_set_recall: 0.3 };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [lowRecall] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => expect(screen.getByText('30.0%')).toBeTruthy());
      const recallSpan = screen.getByText('30.0%');
      expect(recallSpan.style.color).toBe('rgb(220, 38, 38)'); // #dc2626
    });

    it('shows 79.9% in amber (just below 0.8 threshold)', async () => {
      const nearHigh = { ...MOCK_ITERATION_PENDING, test_set_recall: 0.799 };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [nearHigh] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => expect(screen.getByText('79.9%')).toBeTruthy());
      const recallSpan = screen.getByText('79.9%');
      expect(recallSpan.style.color).toBe('rgb(217, 119, 6)');
    });
  });

  describe('Approve/Reject button visibility', () => {
    it('Approve button is NOT shown for already-approved iteration', async () => {
      const approved = { ...MOCK_ITERATION_PENDING, human_approved: true };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [approved] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('Approved'));
      expect(screen.queryByRole('button', { name: /^approve$/i })).toBeNull();
    });

    it('Reject button is NOT shown for already-rejected iteration', async () => {
      const rejected = { ...MOCK_ITERATION_PENDING, human_approved: false };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [rejected] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('Rejected'));
      expect(screen.queryByRole('button', { name: /^reject$/i })).toBeNull();
    });

    it('Approve button IS shown for rejected iteration', async () => {
      const rejected = { ...MOCK_ITERATION_PENDING, human_approved: false };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [rejected] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('Rejected'));
      expect(screen.queryByRole('button', { name: /^approve$/i })).toBeTruthy();
    });

    it('Reject button IS shown for approved iteration', async () => {
      const approved = { ...MOCK_ITERATION_PENDING, human_approved: true };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [approved] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('Approved'));
      expect(screen.queryByRole('button', { name: /^reject$/i })).toBeTruthy();
    });
  });

  describe('AI adequacy judgment', () => {
    it('shows "—" when ai_adequacy_judgment is null', async () => {
      const noJudgment = { ...MOCK_ITERATION_PENDING, ai_adequacy_judgment: null };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [noJudgment] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => expect(screen.getByText('—')).toBeTruthy());
    });
  });

  describe('Active string selection', () => {
    it('auto-selects active string when no explicit selection', async () => {
      const activeString = { ...MOCK_SEARCH_STRINGS[0], id: 10, is_active: true };
      const inactiveString = { ...MOCK_SEARCH_STRINGS[0], id: 11, is_active: false, iterations: [] };
      mockApi.get.mockResolvedValueOnce([inactiveString, activeString]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      // The select should show the active string's value
      const select = screen.getByRole('combobox') as HTMLSelectElement;
      expect(select.value).toBe('10');
    });

    it('falls back to first string when no active string exists', async () => {
      const strings = [
        { ...MOCK_SEARCH_STRINGS[0], id: 20, is_active: false },
        { ...MOCK_SEARCH_STRINGS[0], id: 21, is_active: false, iterations: [] },
      ];
      mockApi.get.mockResolvedValueOnce(strings);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      const select = screen.getByRole('combobox') as HTMLSelectElement;
      expect(select.value).toBe('20');
    });

    it('selecting a string from dropdown switches active string', async () => {
      const strings = [
        { ...MOCK_SEARCH_STRINGS[0], id: 30, version: 1, is_active: true, iterations: [MOCK_ITERATION_PENDING] },
        { ...MOCK_SEARCH_STRINGS[0], id: 31, version: 2, is_active: false, iterations: [] },
      ];
      mockApi.get.mockResolvedValueOnce(strings);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));

      // Initially shows iterations for string 30 (v1)
      expect(screen.getByText(/Iterations for v1/)).toBeTruthy();

      // Change to string 31 (v2)
      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: '31' } });

      await waitFor(() => {
        expect(screen.getByText(/no test iterations yet/i)).toBeTruthy();
      });
    });
  });

  describe('Iteration display in table', () => {
    it('shows iteration_number in table', async () => {
      const iterN3 = { ...MOCK_ITERATION_PENDING, iteration_number: 3 };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [iterN3] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => expect(screen.getByText('3')).toBeTruthy());
    });

    it('shows result_set_count formatted', async () => {
      const bigCount = { ...MOCK_ITERATION_PENDING, result_set_count: 1000 };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [bigCount] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        // toLocaleString may format 1000 as "1,000" or "1000" depending on locale
        const cell = screen.getByText(/1[,.]?000/);
        expect(cell).toBeTruthy();
      });
    });

    it('iterations table NOT shown when string has no iterations', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_STRINGS_NO_ITERATIONS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText(/no test iterations yet/i));
      // Table header should not be present when no iterations
      expect(screen.queryByText(/^#$/)).toBeNull();
      expect(screen.queryByText(/^Results$/)).toBeNull();
      expect(screen.queryByText(/^Recall$/)).toBeNull();
    });

    it('"No test iterations yet" NOT shown when iterations exist', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('75.0%'));
      expect(screen.queryByText(/no test iterations yet/i)).toBeNull();
    });
  });

  describe('Exact human_approved status display', () => {
    it('"Approved" NOT shown for pending iteration (human_approved === null)', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('Pending'));
      expect(screen.queryByText('Approved')).toBeNull();
    });

    it('"Rejected" NOT shown for pending iteration', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('Pending'));
      expect(screen.queryByText('Rejected')).toBeNull();
    });

    it('"Pending" NOT shown for approved iteration', async () => {
      const approved = { ...MOCK_ITERATION_PENDING, human_approved: true };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [approved] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('Approved'));
      expect(screen.queryByText('Pending')).toBeNull();
    });

    it('"Pending" NOT shown for rejected iteration', async () => {
      const rejected = { ...MOCK_ITERATION_PENDING, human_approved: false };
      mockApi.get.mockResolvedValueOnce([{ ...MOCK_SEARCH_STRINGS[0], iterations: [rejected] }]);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByText('Rejected'));
      expect(screen.queryByText('Pending')).toBeNull();
    });
  });

  describe('Test search error fallback', () => {
    it('shows "Test search failed" when non-ApiError thrown', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      mockApi.post.mockRejectedValueOnce(new Error('generic error'));

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      fireEvent.click(screen.getByRole('button', { name: /run test search/i }));

      await waitFor(() => {
        expect(screen.getByText('Test search failed')).toBeTruthy();
      });
    });

    it('"Test search queued" NOT shown before running test', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      expect(screen.queryByText(/test search queued/i)).toBeNull();
    });
  });

  describe('Run test with correct string id', () => {
    it('posts to correct URL with string id different from version', async () => {
      const stringWithDifferentIdAndVersion = {
        ...MOCK_SEARCH_STRINGS[0],
        id: 99,
        version: 5,
        iterations: [MOCK_ITERATION_PENDING],
      };
      mockApi.get.mockResolvedValueOnce([stringWithDifferentIdAndVersion]);
      mockApi.post.mockResolvedValueOnce({ job_id: 'job-x', search_string_id: 99 });

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /run test search/i }));
      fireEvent.click(screen.getByRole('button', { name: /run test search/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/search-strings/99/test',
          expect.anything(),
        );
      });
    });
  });

  describe('Approve button', () => {
    it('renders Approve button for pending iteration', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /^approve$/i })).toBeTruthy();
      });
    });

    it('calls api.patch with human_approved=true when Approve is clicked', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      mockApi.patch.mockResolvedValueOnce({ ...MOCK_ITERATION_PENDING, human_approved: true });

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /^approve$/i }));

      fireEvent.click(screen.getByRole('button', { name: /^approve$/i }));

      await waitFor(() => {
        expect(mockApi.patch).toHaveBeenCalledWith(
          '/api/v1/studies/1/search-strings/1/iterations/5',
          { human_approved: true },
        );
      });
    });
  });

  describe('Reject button', () => {
    it('renders Reject button for pending iteration', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /^reject$/i })).toBeTruthy();
      });
    });

    it('calls api.patch with human_approved=false when Reject is clicked', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      mockApi.patch.mockResolvedValueOnce({ ...MOCK_ITERATION_PENDING, human_approved: false });

      renderWithQuery(<TestRetest studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /^reject$/i }));

      fireEvent.click(screen.getByRole('button', { name: /^reject$/i }));

      await waitFor(() => {
        expect(mockApi.patch).toHaveBeenCalledWith(
          '/api/v1/studies/1/search-strings/1/iterations/5',
          { human_approved: false },
        );
      });
    });
  });
});
