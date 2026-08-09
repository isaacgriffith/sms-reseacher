/**
 * Tests for QualityScoreForm component (feature 007, T060; migrated for TFIX5).
 *
 * TFIX5 removes the client-supplied `reviewerId` prop — the same shape TFIX4
 * removed from screening decisions. Identity is now resolved server-side, and
 * the quality-scores response carries a `viewer_reviewer_id: number | null`
 * field used only to prefill the reviewer's own prior scores. `null` means
 * the caller has never scored; it must never be coerced to `0`.
 *
 * Covers:
 * - Renders a checkbox for binary scoring items.
 * - Renders a slider for scale_1_3 items.
 * - Renders notes TextFields for each item.
 * - Prefills the viewer's own prior score, matched via `viewer_reviewer_id`
 *   rather than array order (not the first reviewer in the list).
 * - Prefills correctly when `viewer_reviewer_id` is legitimately `0`, guarding
 *   against a falsy-coercion bug (`viewer_reviewer_id || …` would drop it).
 * - Submits scores without a client-supplied `reviewer_id` in the payload.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
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
  useQualityScores: vi.fn(),
  useSubmitScores: vi.fn(() => ({
    mutate: mockMutate,
    isPending: false,
  })),
}));

import { useQualityScores } from '../../../hooks/slr/useQualityAssessment';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Renders the form with no `reviewerId` — that prop no longer exists on
 * {@link QualityScoreForm} per TFIX5. `QualityScoreFormProps` in the
 * component still declares it as required today, so this call is expected
 * to produce a `tsc` error until the prop is deleted; that error is part of
 * this task's RED evidence, not a mistake to work around.
 */
function renderForm(candidatePaperId = 5, studyId = 1) {
  return render(<QualityScoreForm candidatePaperId={candidatePaperId} studyId={studyId} />);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('QualityScoreForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useQualityScores).mockReturnValue({
      data: { candidate_paper_id: 5, viewer_reviewer_id: null, reviewer_scores: [] },
    } as never);
  });

  it('renders a checkbox for binary scoring items', () => {
    // Arrange / Act
    renderForm();

    // Assert
    expect(screen.getByLabelText('binary-score-10')).toBeInTheDocument();
  });

  it('renders a slider for scale_1_3 items', () => {
    // Arrange / Act
    renderForm();

    // Assert
    expect(screen.getByLabelText('scale-score-11')).toBeInTheDocument();
  });

  it('renders notes fields for each item', () => {
    // Arrange / Act
    renderForm();

    // Assert
    expect(screen.getByLabelText('notes-10')).toBeInTheDocument();
    expect(screen.getByLabelText('notes-11')).toBeInTheDocument();
  });

  it("prefills the viewer's own prior score, matched by viewer_reviewer_id and not array order", () => {
    // Arrange: two reviewers have scored. The viewer is reviewer 7, listed
    // *second* — a match by array order (e.g. the first entry) would wrongly
    // prefill reviewer 3's answer instead.
    vi.mocked(useQualityScores).mockReturnValue({
      data: {
        candidate_paper_id: 5,
        viewer_reviewer_id: 7,
        reviewer_scores: [
          {
            reviewer_id: 3,
            items: [{ checklist_item_id: 10, score_value: 0, notes: 'not the viewer' }],
            aggregate_quality_score: 0,
          },
          {
            reviewer_id: 7,
            items: [{ checklist_item_id: 10, score_value: 1, notes: "the viewer's own note" }],
            aggregate_quality_score: 1,
          },
        ],
      },
    } as never);

    // Act
    renderForm();

    // Assert
    expect(screen.getByLabelText('binary-score-10')).toBeChecked();
    expect(screen.getByLabelText('notes-10')).toHaveValue("the viewer's own note");
  });

  it('prefills correctly when viewer_reviewer_id is legitimately 0, not just truthy', () => {
    // Arrange: viewer_reviewer_id is 0 — a real reviewer id, not an absent
    // one. A naive `viewer_reviewer_id || fallback` implementation treats 0
    // as falsy and would silently drop this prefill.
    vi.mocked(useQualityScores).mockReturnValue({
      data: {
        candidate_paper_id: 5,
        viewer_reviewer_id: 0,
        reviewer_scores: [
          {
            reviewer_id: 3,
            items: [{ checklist_item_id: 10, score_value: 0, notes: 'not the viewer' }],
            aggregate_quality_score: 0,
          },
          {
            reviewer_id: 0,
            items: [{ checklist_item_id: 10, score_value: 1, notes: 'reviewer zero scored this' }],
            aggregate_quality_score: 1,
          },
        ],
      },
    } as never);

    // Act
    renderForm();

    // Assert
    expect(screen.getByLabelText('binary-score-10')).toBeChecked();
    expect(screen.getByLabelText('notes-10')).toHaveValue('reviewer zero scored this');
  });

  it('submits scores without a client-supplied reviewer_id', async () => {
    // Arrange
    renderForm();

    // Act
    fireEvent.click(screen.getByRole('button', { name: /submit scores/i }));

    // Assert: the mutate payload carries only `scores` — reviewer identity is
    // resolved server-side (TFIX5 point 2), the same shape TFIX4 established
    // for screening decisions.
    await waitFor(() => expect(mockMutate).toHaveBeenCalledTimes(1));
    const payload = mockMutate.mock.calls[0][0] as Record<string, unknown>;
    expect(Object.keys(payload).sort()).toEqual(['scores']);
  });
});
