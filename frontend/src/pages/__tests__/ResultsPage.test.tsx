/**
 * Tests for ResultsPage component.
 *
 * Mocks React Query and child components so no real HTTP calls are made.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import ResultsPage from '../ResultsPage';

vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

vi.mock('../../components/results/ChartGallery', () => ({
  default: ({ charts }: { charts: unknown[] }) => (
    <div data-testid="chart-gallery">Charts: {charts.length}</div>
  ),
}));

vi.mock('../../components/results/DomainModelViewer', () => ({
  default: ({ domainModel: _domainModel }: { domainModel: unknown }) => (
    <div data-testid="domain-model-viewer">Domain Model</div>
  ),
}));

vi.mock('../../components/results/ExportPanel', () => ({
  default: ({ studyId }: { studyId: number }) => (
    <div data-testid="export-panel">Export: {studyId}</div>
  ),
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
 * Renders ResultsPage with required router and query client context.
 *
 * @param studyId - The study ID to route to.
 * @returns The rendered component.
 */
function renderResultsPage(studyId = '42') {
  const qc = makeQueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/studies/${studyId}/results`]}>
        <Routes>
          <Route path="/studies/:studyId/results" element={<ResultsPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ResultsPage', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(api.get).mockReturnValue(new Promise(() => {}));
    renderResultsPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows error state when query fails', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('Network error'));
    renderResultsPage();
    const error = await screen.findByText(/failed/i);
    expect(error).toBeInTheDocument();
  });

  it('renders charts tab with data', async () => {
    vi.mocked(api.get).mockResolvedValue({
      domain_model: null,
      charts: [
        {
          id: 1,
          chart_type: 'venue',
          version: 1,
          chart_data: {},
          svg_content: '<svg/>',
          generated_at: '',
        },
      ],
    });
    vi.mocked(api.post).mockResolvedValue({ job_id: 'j1', study_id: 42 });
    renderResultsPage();
    expect(await screen.findByTestId('chart-gallery')).toBeInTheDocument();
  });

  it('renders domain model tab when clicked', async () => {
    vi.mocked(api.get).mockResolvedValue({
      domain_model: {
        id: 1,
        version: 1,
        concepts: [],
        relationships: [],
        svg_content: null,
        generated_at: '',
      },
      charts: [],
    });
    vi.mocked(api.post).mockResolvedValue({ job_id: 'j1', study_id: 42 });
    renderResultsPage();
    await screen.findByTestId('chart-gallery');
    // Click domain model tab
    const dmTab = screen.getByText(/domain model/i);
    fireEvent.click(dmTab);
    expect(screen.getByTestId('domain-model-viewer')).toBeInTheDocument();
  });

  it('renders export tab when clicked', async () => {
    vi.mocked(api.get).mockResolvedValue({ domain_model: null, charts: [] });
    vi.mocked(api.post).mockResolvedValue({ job_id: 'j1', study_id: 42 });
    renderResultsPage();
    await screen.findByTestId('chart-gallery');
    const exportTab = screen.getByText(/export/i);
    fireEvent.click(exportTab);
    expect(screen.getByTestId('export-panel')).toBeInTheDocument();
  });

  it('renders generate results button', async () => {
    vi.mocked(api.get).mockResolvedValue({ domain_model: null, charts: [] });
    vi.mocked(api.post).mockResolvedValue({ job_id: 'j1', study_id: 42 });
    renderResultsPage();
    await screen.findByTestId('chart-gallery');
    expect(screen.getByText(/generate results/i)).toBeInTheDocument();
  });
});

/**
 * TFIX14 — appraisal provenance.
 *
 * A study that AI-extracted 200 papers and had 12 checked rendered
 * indistinguishably from one that checked all 200. These tests pin the counts
 * to the page, because the number is the whole point: `01-slr.md` 269-270
 * forbids extraction decoupled from appraisal, and a denominator nobody can see
 * is still decoupled.
 */
describe('ResultsPage — extraction provenance (TFIX14)', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('states both denominators when some extractions are unappraised', async () => {
    vi.mocked(api.get).mockResolvedValue({
      domain_model: null,
      charts: [],
      extraction_provenance: {
        total: 200,
        appraised: 12,
        unappraised: 188,
        is_fully_appraised: false,
      },
    });
    renderResultsPage();

    // ChartGallery is mocked and renders during loading too, so awaiting it
    // proves nothing about the query. Await the banner itself.
    expect(await screen.findByText('200')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('188')).toBeInTheDocument();
  });

  it('warns that unappraised results may be wrong', async () => {
    // The corpus's sharpest warning for a platform like this one
    // (`01-slr.md` 266-270): extraction without quality appraisal yields
    // results "very quickly but will be wrong".
    vi.mocked(api.get).mockResolvedValue({
      domain_model: null,
      charts: [],
      extraction_provenance: {
        total: 10,
        appraised: 1,
        unappraised: 9,
        is_fully_appraised: false,
      },
    });
    renderResultsPage();

    expect(await screen.findByText(/may be\s+wrong/i)).toBeInTheDocument();
  });

  it('confirms full appraisal rather than staying silent', async () => {
    // Absence of a warning is ambiguous — it reads as "no data" just as easily
    // as "all checked". The fully-appraised case earns its own statement.
    vi.mocked(api.get).mockResolvedValue({
      domain_model: null,
      charts: [],
      extraction_provenance: {
        total: 7,
        appraised: 7,
        unappraised: 0,
        is_fully_appraised: true,
      },
    });
    renderResultsPage();

    expect(await screen.findByText(/were appraised by a reviewer/i)).toBeInTheDocument();
    expect(screen.queryByText(/remain AI-extracted/i)).not.toBeInTheDocument();
  });

  it('shows no provenance banner when nothing has been extracted', async () => {
    vi.mocked(api.get).mockResolvedValue({
      domain_model: null,
      // One chart, so "Charts: 1" proves the query resolved. With an empty
      // array this assertion would pass while still loading — a negative test
      // that cannot tell absence from not-yet-arrived asserts nothing.
      charts: [
        {
          id: 1,
          chart_type: 'venue',
          version: 1,
          chart_data: {},
          svg_content: '<svg/>',
          generated_at: '',
        },
      ],
      extraction_provenance: {
        total: 0,
        appraised: 0,
        unappraised: 0,
        is_fully_appraised: false,
      },
    });
    renderResultsPage();
    await screen.findByText('Charts: 1');

    expect(screen.queryByText(/appraised by a reviewer/i)).not.toBeInTheDocument();
  });
});
