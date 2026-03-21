/**
 * Tests for ProtocolReviewReport component (feature 007, T037).
 *
 * Covers:
 * - Shows loading skeleton when status === "under_review".
 * - Shows empty-state alert when review_report is null.
 * - Shows empty-state alert when protocol is null.
 * - Renders issues list with correct severity chips.
 * - Renders overall_assessment text.
 * - Shows success alert when issues list is empty.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProtocolReviewReport from '../ProtocolReviewReport';
import type { ReviewProtocol } from '../../../services/slr/protocolApi';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Builds a ReviewProtocol fixture with the given overrides.
 *
 * @param overrides - Partial protocol fields to override.
 * @returns A complete ReviewProtocol fixture.
 */
function makeProtocol(overrides: Partial<ReviewProtocol> = {}): ReviewProtocol {
  return {
    id: 1,
    study_id: 42,
    status: 'draft',
    background: 'Background',
    rationale: 'Rationale',
    research_questions: ['RQ1'],
    pico_population: 'Pop',
    pico_intervention: 'Int',
    pico_comparison: 'Comp',
    pico_outcome: 'Out',
    pico_context: null,
    search_strategy: 'Strategy',
    inclusion_criteria: ['IC1'],
    exclusion_criteria: ['EC1'],
    data_extraction_strategy: 'Extract',
    synthesis_approach: 'descriptive',
    dissemination_strategy: 'Journal',
    timetable: 'Q1-Q4',
    review_report: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ProtocolReviewReport', () => {
  describe('Loading state', () => {
    it('shows loading message when status is under_review', () => {
      const protocol = makeProtocol({ status: 'under_review' });
      render(<ProtocolReviewReport protocol={protocol} />);
      expect(screen.getByText(/ai review in progress/i)).toBeInTheDocument();
    });

    it('renders skeleton elements when under_review', () => {
      const protocol = makeProtocol({ status: 'under_review' });
      const { container } = render(<ProtocolReviewReport protocol={protocol} />);
      // MUI Skeleton renders with a specific class
      expect(container.querySelector('[aria-label="Review loading"]')).toBeInTheDocument();
    });
  });

  describe('Empty state', () => {
    it('shows empty-state alert when protocol is null', () => {
      render(<ProtocolReviewReport protocol={null} />);
      expect(screen.getByTestId('review-empty-state')).toBeInTheDocument();
    });

    it('shows empty-state alert when review_report is null', () => {
      const protocol = makeProtocol({ review_report: null });
      render(<ProtocolReviewReport protocol={protocol} />);
      expect(screen.getByTestId('review-empty-state')).toBeInTheDocument();
    });

    it('shows submit instructions in empty-state message', () => {
      render(<ProtocolReviewReport protocol={null} />);
      expect(screen.getByText(/submit the protocol for ai review/i)).toBeInTheDocument();
    });
  });

  describe('Issues rendering', () => {
    it('renders issue count message', () => {
      const protocol = makeProtocol({
        review_report: {
          issues: [
            {
              section: 'search_strategy',
              severity: 'major',
              description: 'Boolean operators missing.',
              suggestion: 'Add AND/OR.',
            },
          ],
          overall_assessment: 'One major issue.',
        },
      });
      render(<ProtocolReviewReport protocol={protocol} />);
      expect(screen.getByText(/1 issue found/i)).toBeInTheDocument();
    });

    it('renders severity chip for each issue', () => {
      const protocol = makeProtocol({
        review_report: {
          issues: [
            {
              section: 'background',
              severity: 'critical',
              description: 'Missing.',
              suggestion: 'Add background.',
            },
          ],
          overall_assessment: 'Critical issue.',
        },
      });
      render(<ProtocolReviewReport protocol={protocol} />);
      expect(screen.getByText('critical')).toBeInTheDocument();
    });

    it('renders issue description and suggestion', () => {
      const protocol = makeProtocol({
        review_report: {
          issues: [
            {
              section: 'timetable',
              severity: 'minor',
              description: 'Timetable is vague.',
              suggestion: 'Add specific dates.',
            },
          ],
          overall_assessment: 'Minor issue.',
        },
      });
      render(<ProtocolReviewReport protocol={protocol} />);
      expect(screen.getByText('Timetable is vague.')).toBeInTheDocument();
      expect(screen.getByText(/add specific dates/i)).toBeInTheDocument();
    });

    it('renders multiple issues', () => {
      const protocol = makeProtocol({
        review_report: {
          issues: [
            { section: 'a', severity: 'major', description: 'Issue A', suggestion: 'Fix A' },
            { section: 'b', severity: 'minor', description: 'Issue B', suggestion: 'Fix B' },
          ],
          overall_assessment: 'Two issues.',
        },
      });
      render(<ProtocolReviewReport protocol={protocol} />);
      expect(screen.getByText(/2 issues found/i)).toBeInTheDocument();
      expect(screen.getByText('Issue A')).toBeInTheDocument();
      expect(screen.getByText('Issue B')).toBeInTheDocument();
    });
  });

  describe('No-issues state', () => {
    it('shows success alert when issues list is empty', () => {
      const protocol = makeProtocol({
        review_report: {
          issues: [],
          overall_assessment: 'Protocol is sound.',
        },
      });
      render(<ProtocolReviewReport protocol={protocol} />);
      expect(screen.getByText(/no issues found/i)).toBeInTheDocument();
    });
  });

  describe('Overall assessment', () => {
    it('renders overall_assessment text', () => {
      const protocol = makeProtocol({
        review_report: {
          issues: [],
          overall_assessment: 'This is an excellent protocol.',
        },
      });
      render(<ProtocolReviewReport protocol={protocol} />);
      expect(screen.getByText('This is an excellent protocol.')).toBeInTheDocument();
    });
  });
});
