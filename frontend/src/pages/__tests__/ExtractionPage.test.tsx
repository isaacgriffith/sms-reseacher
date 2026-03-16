/**
 * Tests for ExtractionPage component.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import ExtractionPage from '../ExtractionPage';

vi.mock('../../services/api', () => ({
  api: { get: vi.fn(), patch: vi.fn() },
}));

vi.mock('../../components/phase3/ExtractionView', () => ({
  default: ({ extractionId }: { extractionId: number }) => (
    <div data-testid="extraction-view">Extraction: {extractionId}</div>
  ),
}));

vi.mock('../../components/shared/DiffViewer', () => ({
  default: ({ onDismiss }: { onDismiss: () => void }) => (
    <div data-testid="diff-viewer">
      <button onClick={onDismiss}>Dismiss</button>
    </div>
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
 * Renders ExtractionPage with required router context.
 *
 * @param studyId - The study ID to route to.
 * @returns The rendered component.
 */
function renderExtractionPage(studyId = '7') {
  const qc = makeQueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/studies/${studyId}/extraction`]}>
        <Routes>
          <Route path="/studies/:studyId/extraction" element={<ExtractionPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ExtractionPage', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(api.get).mockReturnValue(new Promise(() => {}));
    renderExtractionPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows error when fetch fails', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('fail'));
    renderExtractionPage();
    expect(await screen.findByText(/failed/i)).toBeInTheDocument();
  });

  it('shows empty list message when no extractions', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderExtractionPage();
    expect(await screen.findByText(/no extractions yet/i)).toBeInTheDocument();
  });

  it('renders extraction list items', async () => {
    vi.mocked(api.get).mockResolvedValue([
      { id: 1, candidate_paper_id: 10, extraction_status: 'pending', research_type: 'evaluation', version_id: 1 },
      { id: 2, candidate_paper_id: 11, extraction_status: 'complete', research_type: 'validation', version_id: 2 },
    ]);
    renderExtractionPage();
    // Should render 2 items — check for extraction status labels
    await screen.findByText(/pending/i);
    expect(screen.getAllByText(/paper/i).length).toBeGreaterThan(0);
  });
});
