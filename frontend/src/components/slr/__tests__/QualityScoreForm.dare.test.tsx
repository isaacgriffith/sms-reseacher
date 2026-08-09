/**
 * Tests for QualityScoreForm's anchored `yes_partial_no` scoring (TFIX7 part 3).
 *
 * DARE scores each question Y = 1 / P = 0.5 / N = 0 with three anchor
 * descriptions, and `04-tertiary.md` makes a justification per answer
 * mandatory. Three properties follow, and each of them is the difference
 * between recording an assessment and fabricating one:
 *
 * - Nothing is preselected. Defaulting to a value would submit a judgement the
 *   reviewer never made — precisely the defect TFIX7 part 1 fixed, where the
 *   old rating slider defaulted to 0.5 and `handleSave` posted it.
 * - The anchors are visible beside the option they describe. The corpus is
 *   explicit that they "provide support for the assessment", which requires
 *   the reviewer to be able to read them while choosing.
 * - Submission is blocked until every answered item carries a justification.
 *
 * A separate file from QualityScoreForm.test.tsx because that suite's
 * module-level mock is fixed to binary and scale items.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import QualityScoreForm from '../QualityScoreForm';

const mockMutate = vi.fn();

const DARE_ITEMS = [
  {
    id: 20,
    order: 1,
    question: "Are the review's inclusion and exclusion criteria described?",
    scoring_method: 'yes_partial_no',
    weight: 1.0,
    anchors: {
      '1.0': 'Inclusion criteria explicitly defined in the paper',
      '0.5': 'Inclusion criteria implicit',
      '0.0': 'Not defined and not readily inferable',
    },
  },
  {
    id: 21,
    order: 2,
    question: 'Is the literature search likely to have covered all relevant studies?',
    scoring_method: 'yes_partial_no',
    weight: 1.0,
    anchors: {
      '1.0': 'Searched four or more digital libraries',
      '0.5': 'Searched 3 or 4 libraries with no extra strategies',
      '0.0': 'Searched up to 2 libraries',
    },
  },
];

vi.mock('../../../hooks/slr/useQualityAssessment', () => ({
  useChecklist: vi.fn(() => ({
    data: {
      id: 1,
      study_id: 1,
      name: 'DARE',
      description: null,
      items: DARE_ITEMS,
    },
    isLoading: false,
  })),
  useQualityScores: vi.fn(() => ({ data: undefined })),
  useSubmitScores: vi.fn(() => ({ mutate: mockMutate, isPending: false })),
}));

function renderForm() {
  return render(<QualityScoreForm candidatePaperId={5} studyId={1} />);
}

beforeEach(() => {
  mockMutate.mockClear();
});

describe('QualityScoreForm — yes/partial/no items', () => {
  test('renders one radio per anchor rather than a slider', () => {
    renderForm();

    expect(screen.getByLabelText('ypn-score-20-1')).toBeInTheDocument();
    expect(screen.getByLabelText('ypn-score-20-0.5')).toBeInTheDocument();
    expect(screen.getByLabelText('ypn-score-20-0')).toBeInTheDocument();
    expect(screen.queryByLabelText('scale-score-20')).not.toBeInTheDocument();
  });

  test('shows the anchor text beside each option', () => {
    renderForm();

    expect(
      screen.getByText('Inclusion criteria explicitly defined in the paper'),
    ).toBeInTheDocument();
    expect(screen.getByText('Inclusion criteria implicit')).toBeInTheDocument();
    expect(screen.getByText('Not defined and not readily inferable')).toBeInTheDocument();
  });

  test('preselects nothing, so no judgement is made on the reviewer behalf', () => {
    renderForm();

    for (const value of ['1', '0.5', '0']) {
      expect(screen.getByLabelText(`ypn-score-20-${value}`)).not.toBeChecked();
    }
  });

  test('labels the justification field as required, not optional', () => {
    renderForm();

    expect(screen.queryByText(/Notes \(optional\)/)).not.toBeInTheDocument();
    expect(screen.getByLabelText('notes-20')).toBeInTheDocument();
  });

  test('does not submit when an answered item has no justification', async () => {
    renderForm();

    fireEvent.click(screen.getByLabelText('ypn-score-20-1'));
    fireEvent.click(screen.getByLabelText('ypn-score-21-0.5'));
    fireEvent.click(screen.getByRole('button', { name: /submit scores/i }));

    await waitFor(() => {
      expect(screen.getAllByText(/justification is required/i).length).toBeGreaterThan(0);
    });
    expect(mockMutate).not.toHaveBeenCalled();
  });

  test('does not submit when an item has been left unanswered', async () => {
    renderForm();

    fireEvent.click(screen.getByLabelText('ypn-score-20-1'));
    fireEvent.change(screen.getByLabelText('notes-20'), {
      target: { value: 'Criteria are stated in section 3.' },
    });
    // Item 21 deliberately left unanswered.
    fireEvent.click(screen.getByRole('button', { name: /submit scores/i }));

    await waitFor(() => {
      expect(screen.getAllByText(/select a score/i).length).toBeGreaterThan(0);
    });
    expect(mockMutate).not.toHaveBeenCalled();
  });

  test('submits every answer with its justification once complete', async () => {
    renderForm();

    fireEvent.click(screen.getByLabelText('ypn-score-20-1'));
    fireEvent.change(screen.getByLabelText('notes-20'), {
      target: { value: 'Criteria are stated in section 3.' },
    });
    fireEvent.click(screen.getByLabelText('ypn-score-21-0.5'));
    fireEvent.change(screen.getByLabelText('notes-21'), {
      target: { value: 'Three libraries, no snowballing.' },
    });
    fireEvent.click(screen.getByRole('button', { name: /submit scores/i }));

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledTimes(1);
    });
    expect(mockMutate).toHaveBeenCalledWith({
      scores: [
        {
          checklist_item_id: 20,
          score_value: 1,
          notes: 'Criteria are stated in section 3.',
        },
        {
          checklist_item_id: 21,
          score_value: 0.5,
          notes: 'Three libraries, no snowballing.',
        },
      ],
    });
  });

  test('reports the total on the instrument scale, not as a 0-1 mean', async () => {
    renderForm();

    fireEvent.click(screen.getByLabelText('ypn-score-20-1'));
    fireEvent.click(screen.getByLabelText('ypn-score-21-0.5'));

    // 1 + 0.5 = 1.5 out of 2 items. A "0.75" here would be a number DARE
    // never produces.
    await waitFor(() => {
      expect(screen.getByText(/1\.50 out of 2/)).toBeInTheDocument();
    });
  });
});
