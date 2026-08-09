/**
 * Characterisation tests for StudyPage's study-type dispatch.
 *
 * StudyPage currently selects phase content through eleven paired `isSLR` /
 * `isRapid` boolean checks. Task TREF2 replaces that chain with a study-type →
 * renderer map (plan.md, C1). This file pins the *entire* dispatch surface
 * first, so the refactor is provably behaviour-preserving rather than
 * apparently so: every (study type × phase) cell is asserted, including the
 * cells no existing test touches.
 *
 * Two properties matter more than the individual assertions:
 *
 * 1. Locked tabs are never silently skipped. `openPhase` throws when a tab is
 *    absent or disabled, rather than leaving a `fireEvent.click` unexecuted and
 *    letting the assertion pass for the wrong reason (Principle VI).
 * 2. Negative cells are asserted. Rapid at phase 7 renders nothing at all — a
 *    real consequence of the boolean chain that a dispatch map must reproduce.
 *
 * The Tertiary case pins the *intended* behaviour instead (research.md R7,
 * closing G19): StudyPage renders its header and then delegates wholesale to
 * `TertiaryStudyPage` rather than dispatching per phase — no per-phase body of
 * its own, and no second "Phase N:" tab strip alongside the tertiary
 * workspace's own. These tests fail against today's boolean-chain
 * implementation, which still falls through to the mapping-study workspace,
 * until Task T024 wires the delegation in.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import StudyPage from '../StudyPage';

vi.mock('../../services/api', () => ({
  api: { get: vi.fn(), post: vi.fn() },
}));

vi.mock('../TertiaryStudyPage', () => ({
  default: () => <div data-testid="tertiary-workspace">Tertiary Workspace</div>,
}));

vi.mock('../../components/phase1/PICOForm', () => ({
  default: () => <div data-testid="pico-form">PICO Form</div>,
}));
vi.mock('../../components/phase1/SeedPapers', () => ({
  default: () => <div data-testid="seed-papers">Seed Papers</div>,
}));
vi.mock('../../components/phase2/CriteriaForm', () => ({
  default: () => <div data-testid="criteria-form">Criteria Form</div>,
}));
vi.mock('../../components/phase2/SearchStringEditor', () => ({
  default: () => <div data-testid="search-editor">Search Editor</div>,
}));
vi.mock('../../components/phase2/TestRetest', () => ({
  default: () => <div data-testid="test-retest">Test Retest</div>,
}));
vi.mock('../../components/jobs/JobProgressPanel', () => ({
  default: () => <div data-testid="job-progress">Job Progress</div>,
}));
vi.mock('../../components/phase2/PaperQueue', () => ({
  default: () => <div data-testid="paper-queue">Paper Queue</div>,
}));
vi.mock('../../components/studies/DatabaseSelectionPanel', () => ({
  default: () => <div data-testid="db-selection">Database Selection</div>,
}));
vi.mock('../slr/ProtocolEditorPage', () => ({
  default: () => <div data-testid="slr-protocol-editor">SLR Protocol</div>,
}));
vi.mock('../slr/QualityAssessmentPage', () => ({
  default: () => <div data-testid="slr-qa">SLR QA</div>,
}));
vi.mock('../slr/SynthesisPage', () => ({
  default: () => <div data-testid="slr-synthesis">SLR Synthesis</div>,
}));
vi.mock('../slr/ReportPage', () => ({
  default: () => <div data-testid="slr-report">SLR Report</div>,
}));
vi.mock('../slr/GreyLiteraturePage', () => ({
  default: () => <div data-testid="slr-grey">Grey Literature</div>,
}));
vi.mock('../rapid/ProtocolEditorPage', () => ({
  default: () => <div data-testid="rr-protocol-editor">RR Protocol</div>,
}));
vi.mock('../rapid/SearchConfigPage', () => ({
  default: () => <div data-testid="rr-search-config">RR Search Config</div>,
}));
vi.mock('../rapid/QualityConfigPage', () => ({
  default: () => <div data-testid="rr-qa-config">RR QA Config</div>,
}));
vi.mock('../rapid/NarrativeSynthesisPage', () => ({
  default: () => <div data-testid="rr-narrative">RR Narrative</div>,
}));
vi.mock('../rapid/EvidenceBriefingPage', () => ({
  default: () => <div data-testid="rr-briefing">RR Briefing</div>,
}));
vi.mock('../../components/protocols/ProtocolGraph', () => ({
  default: () => <div data-testid="protocol-graph">Protocol Graph</div>,
}));
vi.mock('../../components/protocols/ProtocolNodePanel', () => ({
  default: () => <div data-testid="protocol-node-panel">Node Panel</div>,
}));
vi.mock('../../components/protocols/ExecutionStateView', () => ({
  default: () => <div data-testid="execution-state">Execution State</div>,
}));
vi.mock('../../components/slr/InterRaterPanel', () => ({
  default: () => <div data-testid="irr-panel">IRR Panel</div>,
}));
vi.mock('../../components/slr/DiscussionFlowPanel', () => ({
  default: () => <div data-testid="discussion-flow">Discussion Flow</div>,
}));
vi.mock('../../hooks/slr/useProtocol', () => ({
  usePhases: vi.fn(() => ({ data: null })),
}));
vi.mock('../../hooks/slr/useInterRater', () => ({
  useInterRaterRecords: vi.fn(() => ({ data: null })),
}));
vi.mock('../../hooks/protocols/useProtocol', () => ({
  useProtocolAssignment: vi.fn(() => ({ data: null })),
  useProtocolDetail: vi.fn(() => ({ data: null })),
  useResetProtocol: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

import { api } from '../../services/api';

/** Every phase-body test id the page can render, for negative assertions. */
const ALL_PHASE_BODIES = [
  'pico-form',
  'seed-papers',
  'criteria-form',
  'search-editor',
  'test-retest',
  'db-selection',
  'job-progress',
  'paper-queue',
  'irr-panel',
  'slr-protocol-editor',
  'slr-qa',
  'slr-synthesis',
  'slr-report',
  'slr-grey',
  'rr-protocol-editor',
  'rr-search-config',
  'rr-qa-config',
  'rr-narrative',
  'rr-briefing',
] as const;

const BASE_STUDY = {
  id: 5,
  name: 'Agile Mapping Study',
  topic: 'Agile practices in distributed teams',
  study_type: 'SMS',
  status: 'active',
  current_phase: 2,
  motivation: 'To understand agile adoption',
  research_objectives: ['Map agile practices'],
  research_questions: ['RQ1: How widely is Scrum adopted?'],
  snowball_threshold: 3,
  // Every phase unlocked, so the matrix exercises dispatch rather than gating.
  unlocked_phases: [1, 2, 3, 4, 5, 6, 7],
  viewer_role: 'lead',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-06-01T00:00:00Z',
};

/**
 * Renders StudyPage for a study of the given type.
 *
 * @param studyType - Value for the study's `study_type` field.
 * @param overrides - Additional fields to merge into the fetched study, for
 *   cases (e.g. Tertiary) that need fields `BASE_STUDY` does not carry.
 */
async function renderStudyOfType(
  studyType: string,
  overrides: Record<string, unknown> = {},
): Promise<void> {
  vi.mocked(api.get).mockResolvedValue({ ...BASE_STUDY, study_type: studyType, ...overrides });
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/studies/5']}>
        <Routes>
          <Route path="/studies/:studyId" element={<StudyPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  await screen.findByText(BASE_STUDY.name);
}

/**
 * Switches to a phase tab, failing loudly if it is absent or locked.
 *
 * The existing suite writes `if (tab) fireEvent.click(tab)`, which turns a
 * missing tab into a silent no-op and lets the following assertion pass against
 * whatever phase happened to be showing. This throws instead.
 *
 * @param phase - Phase number whose tab should be activated.
 */
function openPhase(phase: number): void {
  const tab = screen.getAllByRole('button').find((b) => b.textContent?.includes(`Phase ${phase}:`));

  if (!tab) {
    throw new Error(`No tab found for phase ${phase} — dispatch matrix is stale`);
  }
  if (tab.hasAttribute('disabled')) {
    throw new Error(`Phase ${phase} tab is locked; the fixture must unlock it`);
  }
  fireEvent.click(tab);
}

/** One cell of the dispatch matrix. */
interface Cell {
  /** Test ids that must be present. */
  present?: string[];
  /** Literal text that must be present. */
  text?: string;
  /** True when the phase renders no body at all. */
  empty?: boolean;
}

/**
 * The complete dispatch surface as of the boolean-chain implementation.
 *
 * Read down a column for one study type's workspace; read across a row to see
 * how a phase varies by type. Anything TREF2 changes here is a regression.
 */
const MATRIX: Record<string, Record<number, Cell>> = {
  SMS: {
    1: { present: ['pico-form', 'seed-papers'] },
    2: { present: ['db-selection', 'criteria-form', 'search-editor', 'test-retest'] },
    3: { present: ['job-progress', 'paper-queue'] },
    4: { text: 'Phase 4 content will be available in a future sprint.' },
    5: { text: 'Phase 5 content will be available in a future sprint.' },
    6: { text: 'This feature is only available for SLR studies.' },
    7: { text: 'This feature is only available for SLR studies.' },
  },
  SLR: {
    1: { present: ['slr-protocol-editor'] },
    2: { present: ['db-selection', 'criteria-form', 'search-editor', 'test-retest'] },
    3: { present: ['paper-queue', 'irr-panel'] },
    4: { present: ['slr-qa'] },
    5: { present: ['slr-synthesis'] },
    6: { present: ['slr-report'] },
    7: { present: ['slr-grey'] },
  },
  Rapid: {
    1: { present: ['rr-protocol-editor'] },
    2: { present: ['rr-search-config'] },
    3: { present: ['job-progress', 'paper-queue'] },
    4: { present: ['rr-qa-config'] },
    5: { present: ['rr-narrative'] },
    6: { present: ['rr-briefing'] },
    // Falls through every branch: phase 7 is SLR-only, and the "SLR studies
    // only" message excludes Rapid. Nothing renders.
    7: { empty: true },
  },
};

describe('StudyPage study-type dispatch (characterisation)', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  for (const [studyType, phases] of Object.entries(MATRIX)) {
    describe(studyType, () => {
      for (const [phase, cell] of Object.entries(phases)) {
        const label = cell.empty
          ? `phase ${phase} renders no body`
          : `phase ${phase} renders ${cell.present?.join(', ') ?? `"${cell.text}"`}`;

        it(label, async () => {
          // Arrange
          await renderStudyOfType(studyType);

          // Act
          openPhase(Number(phase));

          // Assert
          for (const testId of cell.present ?? []) {
            expect(screen.getByTestId(testId)).toBeInTheDocument();
          }
          if (cell.text) {
            expect(screen.getByText(cell.text)).toBeInTheDocument();
          }
          if (cell.empty) {
            for (const testId of ALL_PHASE_BODIES) {
              expect(screen.queryByTestId(testId)).not.toBeInTheDocument();
            }
          }
        });
      }
    });
  }

  it.each(Object.keys(MATRIX))('renders the protocol tab at phase 0 for %s', async (studyType) => {
    // Arrange — phase 0 is unlocked unconditionally, for every study type
    await renderStudyOfType(studyType);

    // Act
    openPhase(0);

    // Assert
    expect(screen.getByRole('button', { name: 'Graph' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Execution' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reset to Default' })).toBeInTheDocument();
  });

  // ---------------------------------------------------------------------------
  // Tertiary — the intended behaviour (FR-007 / research.md R7): StudyPage
  // delegates wholesale to TertiaryStudyPage instead of dispatching per phase.
  // ---------------------------------------------------------------------------

  describe('Tertiary', () => {
    it('renders the tertiary workspace, not any SMS phase body', async () => {
      // Arrange
      await renderStudyOfType('Tertiary', { research_group_id: 10 });

      // Act — StudyPage delegates wholesale (R7); there is no per-phase tab
      // of its own to open for a Tertiary study.

      // Assert
      expect(screen.getByTestId('tertiary-workspace')).toBeInTheDocument();
      for (const testId of ALL_PHASE_BODIES) {
        expect(screen.queryByTestId(testId)).not.toBeInTheDocument();
      }
    });

    it("does not render StudyPage's own phase tab strip alongside the tertiary workspace", async () => {
      // Arrange
      await renderStudyOfType('Tertiary', { research_group_id: 10 });

      // Act — none; the absence of the tab strip is itself what's under test.

      // Assert — R7 explicitly rejects "rendering two phase bars": once a
      // Tertiary study takes over, none of StudyPage's own "Phase N: ..."
      // tabs (from PHASE_META) should be present.
      const phaseTabs = screen
        .getAllByRole('button')
        .filter((button) => /Phase \d+:/.test(button.textContent ?? ''));
      expect(phaseTabs).toHaveLength(0);
    });
  });
});
