/**
 * Tests for QualityReport component.
 *
 * Mocks api.get / api.post to verify:
 * - Score cards render with score/max for all five rubrics
 * - Recommendation list displays priority labels
 * - Total score is shown in the header
 * - "Run Evaluation" button triggers api.post
 * - Empty state shown when no reports exist
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

import { api } from '../../../services/api';
import QualityReport from '../QualityReport';

const STUDY_ID = 3;
const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  patch: ReturnType<typeof vi.fn>;
};

const MOCK_SUMMARY = [
  { id: 1, version: 1, total_score: 7, generated_at: '2026-03-12T10:00:00Z' },
];

const MOCK_DETAIL = {
  id: 1,
  study_id: STUDY_ID,
  version: 1,
  score_need_for_review: 2,
  score_search_strategy: 1,
  score_search_evaluation: 2,
  score_extraction_classification: 1,
  score_study_validity: 1,
  total_score: 7,
  rubric_details: {
    need_for_review: { score: 2, justification: 'Clear motivation with defined population.' },
    search_strategy: { score: 1, justification: 'Multiple databases used but test-retest not performed.' },
    search_evaluation: { score: 2, justification: 'Two reviewers; conflicts identified but not formally resolved.' },
    extraction_classification: { score: 1, justification: 'Schema defined; single reviewer applied it.' },
    study_validity: { score: 1, justification: 'All six validity dimensions discussed.' },
  },
  recommendations: [
    { priority: 1, action: 'Perform test-retest search validation.', target_rubric: 'search_strategy' },
    { priority: 2, action: 'Define formal conflict resolution process.', target_rubric: 'search_evaluation' },
    { priority: 3, action: 'Add a second reviewer for extraction.', target_rubric: 'extraction_classification' },
  ],
  generated_at: '2026-03-12T10:00:00Z',
};

describe('QualityReport', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.get.mockImplementation((url: string) => {
      if (url.includes('/quality-reports/1')) return Promise.resolve(MOCK_DETAIL);
      if (url.includes('/quality-reports')) return Promise.resolve(MOCK_SUMMARY);
      return Promise.resolve([]);
    });
    mockApi.post.mockResolvedValue({ job_id: 'qe-job-001', study_id: STUDY_ID });
  });

  describe('score cards', () => {
    it('renders score/max for Need for Review', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => expect(screen.getByText(/2\/2/)).toBeTruthy());
    });

    it('renders score/max for Search Strategy', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => expect(screen.getByText(/1\/2/)).toBeTruthy());
    });

    it('renders score/max for Search Evaluation', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => expect(screen.getByText('2/3')).toBeTruthy());
    });

    it('renders score/max for Extraction & Classification', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => expect(screen.getByText('1/3')).toBeTruthy());
    });

    it('renders score/max for Study Validity', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => expect(screen.getByText('1/1')).toBeTruthy());
    });

    it('shows total score in the header', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => expect(screen.getByText(/7\/11/)).toBeTruthy());
    });

    it('renders justification text for each rubric', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByText(/Clear motivation with defined population/)).toBeTruthy()
      );
    });
  });

  describe('recommendation list', () => {
    it('displays High priority recommendation', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => expect(screen.getByText('High')).toBeTruthy());
    });

    it('displays Medium priority recommendation', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => expect(screen.getByText('Medium')).toBeTruthy());
    });

    it('displays recommendation action text', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByText(/Perform test-retest search validation/)).toBeTruthy()
      );
    });

    it('renders Address button for each recommendation', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => {
        const buttons = screen.getAllByRole('button', { name: /address/i });
        expect(buttons.length).toBe(3);
      });
    });
  });

  describe('Run Evaluation button', () => {
    it('calls api.post when clicked', async () => {
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() => screen.getByRole('button', { name: /run evaluation/i }));
      fireEvent.click(screen.getByRole('button', { name: /run evaluation/i }));
      await waitFor(() =>
        expect(mockApi.post).toHaveBeenCalledWith(
          `/api/v1/studies/${STUDY_ID}/quality-reports`,
          {}
        )
      );
    });
  });

  describe('empty state', () => {
    it('shows empty message when no reports exist', async () => {
      mockApi.get.mockResolvedValue([]);
      render(<QualityReport studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByText(/No quality evaluations yet/i)).toBeTruthy()
      );
    });
  });
});
