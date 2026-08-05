/**
 * Tests for StudyPage component.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import StudyPage from '../StudyPage';

vi.mock('../../services/api', () => ({
  api: { get: vi.fn(), post: vi.fn() },
}));

// Mock all child components to avoid rendering complexity
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

/**
 * Creates a QueryClient suitable for testing.
 *
 * @returns A QueryClient with retries disabled.
 */
function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
}

/**
 * Renders StudyPage with required router context.
 *
 * @param studyId - The study ID to route to.
 * @returns The rendered component.
 */
function renderStudyPage(studyId = '5') {
  const qc = makeQueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/studies/${studyId}`]}>
        <Routes>
          <Route path="/studies/:studyId" element={<StudyPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

const TEST_STUDY = {
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
  unlocked_phases: [1, 2],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-06-01T00:00:00Z',
};

describe('StudyPage', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(api.get).mockReturnValue(new Promise(() => {}));
    renderStudyPage();
    expect(screen.getByText(/loading study/i)).toBeInTheDocument();
  });

  it('shows error when fetch fails', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('Not found'));
    renderStudyPage();
    expect(await screen.findByText(/failed to load study/i)).toBeInTheDocument();
  });

  it('renders study name when loaded', async () => {
    vi.mocked(api.get).mockResolvedValue(TEST_STUDY);
    renderStudyPage();
    expect(await screen.findByText('Agile Mapping Study')).toBeInTheDocument();
  });

  it('renders study topic when present', async () => {
    vi.mocked(api.get).mockResolvedValue(TEST_STUDY);
    renderStudyPage();
    expect(await screen.findByText('Agile practices in distributed teams')).toBeInTheDocument();
  });

  it('renders phase tabs', async () => {
    vi.mocked(api.get).mockResolvedValue(TEST_STUDY);
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    expect(screen.getByText(/Scoping/)).toBeInTheDocument();
    expect(screen.getByText(/Search/)).toBeInTheDocument();
  });

  it('shows PICO form and Seed Papers for SMS Phase 1', async () => {
    vi.mocked(api.get).mockResolvedValue(TEST_STUDY);
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    // Default active phase is 1 for SMS study
    expect(screen.getByTestId('pico-form')).toBeInTheDocument();
    expect(screen.getByTestId('seed-papers')).toBeInTheDocument();
  });

  it('switches to Phase 2 and shows search components', async () => {
    vi.mocked(api.get).mockResolvedValue(TEST_STUDY);
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    // Click Phase 2: Search
    const searchTab = screen.getAllByText(/Search/).find(el => el.textContent?.includes('Phase 2'));
    if (searchTab) fireEvent.click(searchTab);
    expect(screen.getByTestId('criteria-form')).toBeInTheDocument();
    expect(screen.getByTestId('search-editor')).toBeInTheDocument();
  });

  it('renders research objectives and questions for SMS study', async () => {
    vi.mocked(api.get).mockResolvedValue(TEST_STUDY);
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    expect(screen.getByText('Map agile practices')).toBeInTheDocument();
    expect(screen.getByText('RQ1: How widely is Scrum adopted?')).toBeInTheDocument();
  });

  it('renders Protocol tab (Phase 0)', async () => {
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      unlocked_phases: [0, 1, 2],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    // Click Phase 0: Protocol
    const protocolTab = screen.getAllByText(/Protocol/).find(el => el.textContent?.includes('Phase 0'));
    if (protocolTab) fireEvent.click(protocolTab);
    // Should show Graph/Execution toggle buttons
    expect(screen.getByRole('button', { name: /Graph/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Execution/ })).toBeInTheDocument();
  });

  it('shows snowball threshold in header', async () => {
    vi.mocked(api.get).mockResolvedValue(TEST_STUDY);
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    expect(screen.getByText(/Snowball threshold: 3/)).toBeInTheDocument();
  });

  it('renders SLR protocol editor for SLR study phase 1', async () => {
    const { usePhases } = await import('../../hooks/slr/useProtocol');
    vi.mocked(usePhases).mockReturnValue({ data: { unlocked_phases: [1, 2, 3, 4, 5] } } as ReturnType<typeof usePhases>);
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      study_type: 'SLR',
      unlocked_phases: [1, 2, 3, 4, 5],
    });
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    expect(screen.getByTestId('slr-protocol-editor')).toBeInTheDocument();
  });

  it('renders Rapid protocol editor for Rapid study phase 1', async () => {
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      study_type: 'Rapid',
      unlocked_phases: [1, 2, 3, 4, 5],
    });
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    expect(screen.getByTestId('rr-protocol-editor')).toBeInTheDocument();
  });

  it('renders phase 3 screening for non-SLR SMS study', async () => {
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      unlocked_phases: [1, 2, 3],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    const screeningTab = screen.getAllByText(/Screening/).find(el => el.textContent?.includes('Phase 3'));
    if (screeningTab) fireEvent.click(screeningTab);
    expect(screen.getByTestId('paper-queue')).toBeInTheDocument();
  });

  it('renders SLR screening view with IRR panel for SLR phase 3', async () => {
    const { usePhases } = await import('../../hooks/slr/useProtocol');
    vi.mocked(usePhases).mockReturnValue({ data: { unlocked_phases: [1, 2, 3, 4, 5] } } as ReturnType<typeof usePhases>);
    const { useInterRaterRecords } = await import('../../hooks/slr/useInterRater');
    vi.mocked(useInterRaterRecords).mockReturnValue({ data: { records: [] } } as ReturnType<typeof useInterRaterRecords>);
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      study_type: 'SLR',
      unlocked_phases: [1, 2, 3, 4, 5],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    const screeningTab = screen.getAllByText(/Screening/).find(el => el.textContent?.includes('Phase 3'));
    if (screeningTab) fireEvent.click(screeningTab);
    expect(screen.getByTestId('paper-queue')).toBeInTheDocument();
    expect(screen.getByTestId('irr-panel')).toBeInTheDocument();
  });

  it('renders SLR synthesis for phase 5', async () => {
    const { usePhases } = await import('../../hooks/slr/useProtocol');
    vi.mocked(usePhases).mockReturnValue({ data: { unlocked_phases: [1, 2, 3, 4, 5] } } as ReturnType<typeof usePhases>);
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      study_type: 'SLR',
      unlocked_phases: [1, 2, 3, 4, 5],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    const synthesisTab = screen.getAllByText(/Reporting/).find(el => el.textContent?.includes('Phase 5'));
    if (synthesisTab) fireEvent.click(synthesisTab);
    expect(screen.getByTestId('slr-synthesis')).toBeInTheDocument();
  });

  it('renders Rapid search config for phase 2', async () => {
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      study_type: 'Rapid',
      unlocked_phases: [1, 2, 3, 4, 5],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    const searchTab = screen.getAllByText(/Search/).find(el => el.textContent?.includes('Phase 2'));
    if (searchTab) fireEvent.click(searchTab);
    expect(screen.getByTestId('rr-search-config')).toBeInTheDocument();
  });

  it('renders SLR QA for phase 4', async () => {
    const { usePhases } = await import('../../hooks/slr/useProtocol');
    vi.mocked(usePhases).mockReturnValue({ data: { unlocked_phases: [1, 2, 3, 4, 5] } } as ReturnType<typeof usePhases>);
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      study_type: 'SLR',
      unlocked_phases: [1, 2, 3, 4, 5],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    const qaTab = screen.getAllByText(/Extraction/).find(el => el.textContent?.includes('Phase 4'));
    if (qaTab) fireEvent.click(qaTab);
    expect(screen.getByTestId('slr-qa')).toBeInTheDocument();
  });

  it('renders Rapid QA config for phase 4', async () => {
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      study_type: 'Rapid',
      unlocked_phases: [1, 2, 3, 4, 5],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    const qaTab = screen.getAllByText(/Extraction/).find(el => el.textContent?.includes('Phase 4'));
    if (qaTab) fireEvent.click(qaTab);
    expect(screen.getByTestId('rr-qa-config')).toBeInTheDocument();
  });

  it('renders Rapid narrative synthesis for phase 5', async () => {
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      study_type: 'Rapid',
      unlocked_phases: [1, 2, 3, 4, 5],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    const reportingTab = screen.getAllByText(/Reporting/).find(el => el.textContent?.includes('Phase 5'));
    if (reportingTab) fireEvent.click(reportingTab);
    expect(screen.getByTestId('rr-narrative')).toBeInTheDocument();
  });

  it('shows protocol graph when assignment exists', async () => {
    const { useProtocolAssignment, useProtocolDetail } = await import('../../hooks/protocols/useProtocol');
    vi.mocked(useProtocolAssignment).mockReturnValue({ data: { protocol_id: 1 } } as ReturnType<typeof useProtocolAssignment>);
    vi.mocked(useProtocolDetail).mockReturnValue({
      data: { id: 1, name: 'Test', nodes: [], edges: [] },
    } as ReturnType<typeof useProtocolDetail>);
    vi.mocked(api.get).mockResolvedValue({
      ...TEST_STUDY,
      unlocked_phases: [0, 1, 2],
    });
    const { fireEvent } = await import('@testing-library/react');
    renderStudyPage();
    await screen.findByText('Agile Mapping Study');
    const protocolTab = screen.getAllByText(/Protocol/).find(el => el.textContent?.includes('Phase 0'));
    if (protocolTab) fireEvent.click(protocolTab);
    expect(screen.getByTestId('protocol-graph')).toBeInTheDocument();
  });
});
