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
  api: { get: vi.fn() },
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
});
