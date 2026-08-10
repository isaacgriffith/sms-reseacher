/**
 * Unit tests for TertiaryQualityPanel (TFIX7 part 3, extended by TFIX13).
 *
 * The component had no test file at all, which is how it came to carry
 * user-visible methodological claims that nothing pinned. These tests pin the
 * claims, not the layout: every assertion below corresponds to a sentence in
 * `07-quality-assessment.md`, so a rewrite that quietly drops or alters one
 * fails here rather than shipping.
 *
 * TFIX13 deleted `TertiaryQAGuidancePanel`, which taught six fabricated
 * "mandatory" dimensions. Its nine tests passed against the fabrication. That
 * is the failure mode these tests exist to avoid repeating: assert the
 * sourced claim, not merely that some text rendered.
 */

import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TertiaryQualityPanel from '../TertiaryQualityPanel';

vi.mock('../../../hooks/slr/useQualityAssessment', () => ({
  useChecklist: vi.fn(),
}));

vi.mock('../../../services/slr/qualityApi', () => ({
  seedDareChecklist: vi.fn(),
}));

// QualityScoreForm has its own suite, including the DARE anchor rendering
// added by TFIX7. Stubbing it keeps these tests about the panel's prose.
vi.mock('../../slr/QualityScoreForm', () => ({
  default: () => <div data-testid="quality-score-form" />,
}));

import { useChecklist } from '../../../hooks/slr/useQualityAssessment';

const mockUseChecklist = useChecklist as unknown as ReturnType<typeof vi.fn>;

const PAPERS = [{ id: 1, title: 'A systematic review of X' }];

function renderPanel(papers = PAPERS) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <TertiaryQualityPanel studyId={7} papers={papers} />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe('TertiaryQualityPanel — setup state', () => {
  beforeEach(() => {
    mockUseChecklist.mockReturnValue({ data: undefined, isLoading: false, error: null });
  });

  it('names DARE as the instrument for tertiary studies', () => {
    // 07-quality-assessment.md:146 assigns tertiary studies DARE. Matched on
    // the sentence rather than the bare word, which also appears on the button.
    renderPanel();

    expect(screen.getByText(/DARE — four anchored questions/)).toBeInTheDocument();
  });

  it('states the four-question Yes/Partly/No scoring', () => {
    // Four questions scored Y = 1, P = 0.5, N = 0 (04-tertiary.md 2.3).
    renderPanel();

    expect(screen.getByText(/four anchored questions/)).toBeInTheDocument();
    expect(screen.getByText(/Partly \(0\.5\)/)).toBeInTheDocument();
  });

  it('says omission is legitimate but must be justified', () => {
    // 07-quality-assessment.md:150 — "omission is reasonable … but it must be
    // stated, not silent". The panel must not imply the instrument is
    // mandatory, which is precisely the claim TFIX13 deleted.
    renderPanel();

    expect(screen.getByText(/legitimate choice/)).toBeInTheDocument();
    expect(screen.getByText(/stated and justified/)).toBeInTheDocument();
  });

  it('offers to set DARE up rather than seeding it silently', () => {
    renderPanel();

    expect(screen.getByRole('button', { name: /Set up DARE/ })).toBeInTheDocument();
  });
});

describe('TertiaryQualityPanel — scoring state', () => {
  beforeEach(() => {
    mockUseChecklist.mockReturnValue({
      data: { id: 1, name: 'DARE', items: [] },
      isLoading: false,
      error: null,
    });
  });

  it('warns that collecting scores and ignoring them is worse than not collecting them', () => {
    // TFIX13. 07-quality-assessment.md:151-152: DARE Q3 scores N for "quality
    // data extracted but not used". This is the one DARE rule the UI did not
    // state, and it is counter-intuitive — a reviewer who scores diligently
    // and then ignores the result scores *worse* than one who never scored.
    renderPanel();

    expect(
      screen.getByText(/collecting scores and ignoring them is worse than not collecting them/i),
    ).toBeInTheDocument();
  });

  it('attributes the warning to DARE Q3 rather than stating it unsourced', () => {
    // An unsourced methodological claim in the UI is what TFIX13 removed.
    renderPanel();

    expect(screen.getByText(/Q3/)).toBeInTheDocument();
  });

  it('requires a justification for every answer', () => {
    renderPanel();

    expect(screen.getByText(/Every answer needs a justification/)).toBeInTheDocument();
  });

  it('tells the user nothing to assess yet when no papers are included', () => {
    renderPanel([]);

    expect(screen.getByText(/No included secondary studies to assess yet/)).toBeInTheDocument();
  });
});
