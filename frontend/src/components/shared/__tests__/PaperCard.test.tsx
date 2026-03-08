/**
 * Tests for PaperCard component.
 *
 * Mocks api.get (decisions) and api.post (resolve-conflict).
 * Covers:
 * - Paper title and metadata rendered
 * - Status badge rendered
 * - Conflict badge "⚠ CONFLICT" visible when conflictFlag=true
 * - Conflict badge absent when conflictFlag=false
 * - Decision history list rendered when decisions present
 * - Conflict resolution panel shown when conflictFlag=true and ≥2 decisions
 * - "Resolve as accepted/rejected" buttons call onResolve
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import { api } from '../../../services/api';
import PaperCard from '../PaperCard';

const mockApi = api as unknown as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const MOCK_PAPER = {
  id: 10,
  title: 'Test-Driven Development Practices',
  abstract: 'A comprehensive study of TDD adoption.',
  doi: '10.1/tdd',
  authors: [{ name: 'Alice Smith' }, { name: 'Bob Jones' }],
  year: 2023,
  venue: 'JSS',
};

const BASE_PROPS = {
  studyId: 1,
  candidateId: 42,
  paperId: 10,
  paper: MOCK_PAPER,
  currentStatus: 'accepted',
  conflictFlag: false,
  phaseTag: 'initial-search',
};

const MOCK_DECISIONS = [
  {
    id: 1,
    candidate_paper_id: 42,
    reviewer_id: 1,
    decision: 'accepted' as const,
    reasons: [{ text: 'Peer-reviewed' }],
    is_override: false,
    overrides_decision_id: null,
  },
  {
    id: 2,
    candidate_paper_id: 42,
    reviewer_id: 2,
    decision: 'rejected' as const,
    reasons: null,
    is_override: false,
    overrides_decision_id: null,
  },
];

describe('PaperCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.get.mockResolvedValue([]);
    mockApi.post.mockResolvedValue({});
  });

  describe('Metadata rendering', () => {
    it('renders paper title', async () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} />);
      expect(screen.getByText('Test-Driven Development Practices')).toBeTruthy();
    });

    it('renders paper year', () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} />);
      expect(screen.getByText('2023')).toBeTruthy();
    });

    it('renders paper venue', () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} />);
      expect(screen.getByText('JSS')).toBeTruthy();
    });

    it('renders phase tag', () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} />);
      expect(screen.getByText('initial-search')).toBeTruthy();
    });

    it('renders current status badge', () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} currentStatus="accepted" />);
      expect(screen.getByText('accepted')).toBeTruthy();
    });

    it('renders paper abstract', () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} />);
      expect(screen.getByText(/comprehensive study of TDD/i)).toBeTruthy();
    });

    it('renders author names', () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} />);
      expect(screen.getByText(/Alice Smith/)).toBeTruthy();
    });
  });

  describe('Conflict badge', () => {
    it('shows CONFLICT badge when conflictFlag is true', () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={true} />);
      expect(screen.getByText(/conflict/i)).toBeTruthy();
    });

    it('does not show CONFLICT badge when conflictFlag is false', () => {
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={false} />);
      expect(screen.queryByText(/⚠/)).toBeNull();
    });
  });

  describe('Decision history', () => {
    it('renders decision history when decisions are present', async () => {
      mockApi.get.mockResolvedValue([MOCK_DECISIONS[0]]);
      renderWithQuery(<PaperCard {...BASE_PROPS} />);
      await waitFor(() =>
        expect(screen.getByText(/audit trail/i)).toBeTruthy()
      );
    });

    it('shows decision entries with reviewer IDs', async () => {
      mockApi.get.mockResolvedValue(MOCK_DECISIONS);
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={true} />);
      await waitFor(() => {
        expect(screen.getAllByText(/reviewer #1/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/reviewer #2/i).length).toBeGreaterThan(0);
      });
    });

    it('shows override annotation on override decisions', async () => {
      const overrideDecision = { ...MOCK_DECISIONS[0], is_override: true };
      mockApi.get.mockResolvedValue([overrideDecision]);
      renderWithQuery(<PaperCard {...BASE_PROPS} />);
      await waitFor(() =>
        expect(screen.getByText(/override/i)).toBeTruthy()
      );
    });
  });

  describe('Conflict resolution panel', () => {
    it('shows "Conflict Resolution Required" when conflictFlag=true and ≥2 decisions', async () => {
      mockApi.get.mockResolvedValue(MOCK_DECISIONS);
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={true} />);
      await waitFor(() =>
        expect(screen.getByText(/conflict resolution required/i)).toBeTruthy()
      );
    });

    it('does not show resolution panel when conflictFlag=false', async () => {
      mockApi.get.mockResolvedValue(MOCK_DECISIONS);
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={false} />);
      await waitFor(() => {
        expect(screen.queryByText(/conflict resolution required/i)).toBeNull();
      });
    });

    it('shows "Resolve as accepted" button in conflict panel', async () => {
      mockApi.get.mockResolvedValue(MOCK_DECISIONS);
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={true} />);
      await waitFor(() =>
        expect(screen.getByText(/resolve as accepted/i)).toBeTruthy()
      );
    });

    it('shows "Resolve as rejected" button in conflict panel', async () => {
      mockApi.get.mockResolvedValue(MOCK_DECISIONS);
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={true} />);
      await waitFor(() =>
        expect(screen.getByText(/resolve as rejected/i)).toBeTruthy()
      );
    });

    it('calls api.post with correct body when resolve button clicked', async () => {
      mockApi.get.mockResolvedValue(MOCK_DECISIONS);
      mockApi.post.mockResolvedValue({ id: 3, decision: 'accepted', is_override: true });
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={true} />);

      await waitFor(() =>
        expect(screen.getByText(/resolve as accepted/i)).toBeTruthy()
      );

      fireEvent.click(screen.getByText(/resolve as accepted/i));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          expect.stringContaining('/resolve-conflict'),
          expect.objectContaining({ decision: 'accepted' })
        );
      });
    });

    it('does not show resolution panel when fewer than 2 decisions', async () => {
      mockApi.get.mockResolvedValue([MOCK_DECISIONS[0]]);
      renderWithQuery(<PaperCard {...BASE_PROPS} conflictFlag={true} />);
      await waitFor(() => {
        // Only one decision → panel should not appear
        expect(screen.queryByText(/conflict resolution required/i)).toBeNull();
      });
    });
  });
});
