/**
 * Unit tests for QualityAssessmentPage (feature 007, T057; migrated for TFIX5).
 *
 * TFIX5 wires the "Score Papers" tab: it must list the study's accepted
 * candidate papers and mount `QualityScoreForm` for the selected one, instead
 * of the placeholder string "Select an accepted paper to score it." that
 * implied a selector without ever building one. `reviewerId` is also deleted
 * from the page's props — the same shape TFIX4 removed from screening —
 * because `QualityAssessmentPage` only ever discarded it (`reviewerId:
 * _reviewerId`, unused).
 *
 * Covers:
 * - Renders the "Checklist Setup" tab by default.
 * - Renders the "Score Papers" tab button.
 * - QualityChecklistEditor is rendered in the Checklist Setup tab.
 * - The old placeholder string is gone from the Score Papers tab.
 * - The Score Papers tab lists the study's accepted candidate papers,
 *   fetched for the current study with a `status=accepted` filter.
 * - Selecting an accepted paper mounts QualityScoreForm for it, with no
 *   reviewerId prop passed through.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import QualityAssessmentPage from '../QualityAssessmentPage';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const { mockApiGet, mockScoreFormProps } = vi.hoisted(() => ({
  mockApiGet: vi.fn(),
  mockScoreFormProps: [] as Record<string, unknown>[],
}));

vi.mock('../../../services/api', () => ({
  api: { get: mockApiGet },
}));

vi.mock('../../../components/slr/QualityChecklistEditor', () => ({
  default: ({ studyId }: { studyId: number }) => (
    <div data-testid="quality-checklist-editor" data-study-id={studyId} />
  ),
}));

vi.mock('../../../components/slr/QualityScoreForm', () => ({
  default: (props: Record<string, unknown>) => {
    mockScoreFormProps.push(props);
    return (
      <div
        data-testid="quality-score-form"
        data-candidate-paper-id={String(props.candidatePaperId)}
        data-study-id={String(props.studyId)}
      />
    );
  },
}));

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function acceptedCandidate(id: number, title: string) {
  return {
    id,
    study_id: 42,
    paper_id: id * 100,
    phase_tag: 'phase3',
    current_status: 'accepted' as const,
    duplicate_of_id: null,
    conflict_flag: false,
    paper: {
      id: id * 100,
      title,
      abstract: null,
      doi: null,
      authors: null,
      year: 2024,
      venue: null,
    },
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Renders the page with no `reviewerId` — that prop no longer exists on
 * {@link QualityAssessmentPage} per TFIX5. `QualityAssessmentPageProps` in
 * the component still declares it as required today, so this call is
 * expected to produce a `tsc` error until the prop is deleted; that error is
 * part of this task's RED evidence, not a mistake to work around.
 */
function renderPage(studyId = 42) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={qc}>
      <QualityAssessmentPage studyId={studyId} />
    </QueryClientProvider>,
  );
}

function openScorePapersTab() {
  fireEvent.click(screen.getByRole('tab', { name: /score papers/i }));
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('QualityAssessmentPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockScoreFormProps.length = 0;
    mockApiGet.mockResolvedValue([]);
  });

  it('renders the Quality Assessment heading', () => {
    // Arrange / Act
    renderPage();

    // Assert
    expect(screen.getByText(/quality assessment/i)).toBeInTheDocument();
  });

  it('renders the Checklist Setup tab', () => {
    // Arrange / Act
    renderPage();

    // Assert
    expect(screen.getByRole('tab', { name: /checklist setup/i })).toBeInTheDocument();
  });

  it('renders the Score Papers tab', () => {
    // Arrange / Act
    renderPage();

    // Assert
    expect(screen.getByRole('tab', { name: /score papers/i })).toBeInTheDocument();
  });

  it('renders QualityChecklistEditor in the first tab by default', () => {
    // Arrange / Act
    renderPage(77);

    // Assert
    expect(screen.getByTestId('quality-checklist-editor')).toBeInTheDocument();
    expect(screen.getByTestId('quality-checklist-editor').getAttribute('data-study-id')).toBe('77');
  });

  it('no longer renders the old "select an accepted paper" placeholder string', () => {
    // Arrange
    mockApiGet.mockResolvedValue([acceptedCandidate(5, 'Paper Five')]);
    renderPage();

    // Act
    openScorePapersTab();

    // Assert: the exact placeholder string this defect names must be gone
    // from the rendered output entirely, not merely conditionally hidden.
    expect(screen.queryByText('Select an accepted paper to score it.')).not.toBeInTheDocument();
  });

  it("lists the study's accepted candidate papers in the Score Papers tab", async () => {
    // Arrange
    mockApiGet.mockResolvedValue([
      acceptedCandidate(5, 'Paper Five'),
      acceptedCandidate(6, 'Paper Six'),
    ]);
    renderPage(42);

    // Act
    openScorePapersTab();

    // Assert
    expect(await screen.findByText('Paper Five')).toBeInTheDocument();
    expect(await screen.findByText('Paper Six')).toBeInTheDocument();
  });

  it('requests only accepted candidates for the current study', async () => {
    // Arrange
    mockApiGet.mockResolvedValue([acceptedCandidate(5, 'Paper Five')]);
    renderPage(42);

    // Act
    openScorePapersTab();

    // Assert
    await waitFor(() => expect(mockApiGet).toHaveBeenCalled());
    const [url] = mockApiGet.mock.calls[0] as [string];
    expect(url).toContain('/studies/42/');
    expect(url).toContain('status=accepted');
  });

  it('mounts QualityScoreForm for the selected accepted paper, with no reviewerId prop', async () => {
    // Arrange
    mockApiGet.mockResolvedValue([
      acceptedCandidate(5, 'Paper Five'),
      acceptedCandidate(6, 'Paper Six'),
    ]);
    renderPage(42);
    openScorePapersTab();
    const option = await screen.findByRole('button', { name: 'Paper Five' });

    // Act
    fireEvent.click(option);

    // Assert
    const form = screen.getByTestId('quality-score-form');
    expect(form.getAttribute('data-candidate-paper-id')).toBe('5');
    expect(form.getAttribute('data-study-id')).toBe('42');
    expect(mockScoreFormProps.at(-1)).not.toHaveProperty('reviewerId');
  });
});
