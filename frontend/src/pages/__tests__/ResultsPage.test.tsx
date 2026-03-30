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
        { id: 1, chart_type: 'venue', version: 1, chart_data: {}, svg_content: '<svg/>', generated_at: '' },
      ],
    });
    vi.mocked(api.post).mockResolvedValue({ job_id: 'j1', study_id: 42 });
    renderResultsPage();
    expect(await screen.findByTestId('chart-gallery')).toBeInTheDocument();
  });

  it('renders domain model tab when clicked', async () => {
    vi.mocked(api.get).mockResolvedValue({
      domain_model: { id: 1, version: 1, concepts: [], relationships: [], svg_content: null, generated_at: '' },
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
