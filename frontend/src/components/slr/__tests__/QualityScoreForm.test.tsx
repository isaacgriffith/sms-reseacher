/**
 * Tests for QualityScoreForm component (feature 007, T060).
 *
 * Covers:
 * - Renders a checkbox for binary scoring items.
 * - Renders a slider for scale_1_3 items.
 * - Renders notes TextFields for each item.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import QualityScoreForm from '../QualityScoreForm';

// ---------------------------------------------------------------------------
// Mock hooks
// ---------------------------------------------------------------------------

const mockMutate = vi.fn();

vi.mock('../../../hooks/slr/useQualityAssessment', () => ({
  useChecklist: vi.fn(() => ({
    data: {
      id: 1,
      study_id: 1,
      name: 'Test CL',
      description: null,
      items: [
        { id: 10, order: 1, question: 'Is empirical?', scoring_method: 'binary', weight: 1.0 },
        { id: 11, order: 2, question: 'Sample size?', scoring_method: 'scale_1_3', weight: 2.0 },
      ],
    },
    isLoading: false,
  })),
  useQualityScores: vi.fn(() => ({
    data: { candidate_paper_id: 5, reviewer_scores: [] },
  })),
  useSubmitScores: vi.fn(() => ({
    mutate: mockMutate,
    isPending: false,
  })),
}));

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

function renderForm(candidatePaperId = 5, reviewerId = 1, studyId = 1) {
  return render(
    <QualityScoreForm
      candidatePaperId={candidatePaperId}
      reviewerId={reviewerId}
      studyId={studyId}
    />,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('QualityScoreForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders a checkbox for binary scoring items', () => {
    renderForm();
    expect(screen.getByLabelText('binary-score-10')).toBeInTheDocument();
  });

  it('renders a slider for scale_1_3 items', () => {
    renderForm();
    expect(screen.getByLabelText('scale-score-11')).toBeInTheDocument();
  });

  it('renders notes fields for each item', () => {
    renderForm();
    expect(screen.getByLabelText('notes-10')).toBeInTheDocument();
    expect(screen.getByLabelText('notes-11')).toBeInTheDocument();
  });
});
