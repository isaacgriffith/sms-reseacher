/**
 * Tests for StudiesPage component.
 *
 * Mocks React Query and react-router-dom so no real HTTP calls are made.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import StudiesPage from '../StudiesPage';

// Mock the api module
vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    constructor(
      public status: number,
      public detail: string,
    ) {
      super(detail);
      this.name = 'ApiError';
    }
  },
}));

// Mock NewStudyWizard to avoid rendering it in page tests
vi.mock('../../components/studies/NewStudyWizard', () => ({
  default: ({ onSuccess }: { onSuccess: () => void }) => (
    <div data-testid="new-study-wizard">
      <button onClick={onSuccess}>Submit Wizard</button>
    </div>
  ),
}));

import { api } from '../../services/api';

/**
 * Creates a new QueryClient configured for testing with retries disabled.
 *
 * @returns A QueryClient instance with default retries set to false.
 */
function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
}

/**
 * Wraps component with MemoryRouter and QueryClientProvider.
 *
 * @param groupId - The group ID to use in the route.
 * @returns The wrapped component tree.
 */
function renderStudiesPage(groupId = '1') {
  const qc = makeQueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[`/groups/${groupId}/studies`]}>
        <Routes>
          <Route path="/groups/:groupId/studies" element={<StudiesPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('StudiesPage', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(api.get).mockReturnValue(new Promise(() => {}));
    renderStudiesPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows error when fetch fails', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('Network error'));
    renderStudiesPage();
    const error = await screen.findByText(/failed to load studies/i);
    expect(error).toBeInTheDocument();
  });

  it('renders studies list when data is loaded', async () => {
    vi.mocked(api.get).mockResolvedValue([
      {
        id: 1,
        name: 'TDD Study',
        topic: 'Test-driven development',
        study_type: 'SMS',
        status: 'active',
        current_phase: 2,
        created_at: '2024-01-01T00:00:00Z',
      },
    ]);
    renderStudiesPage();
    expect(await screen.findByText('TDD Study')).toBeInTheDocument();
  });

  it('shows new study wizard when button is clicked', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderStudiesPage();
    // Wait for loading to complete
    await screen.findByText(/new study/i);
    fireEvent.click(screen.getByText(/new study/i));
    expect(await screen.findByTestId('new-study-wizard')).toBeInTheDocument();
  });

  it('renders phase label for study', async () => {
    vi.mocked(api.get).mockResolvedValue([
      {
        id: 2,
        name: 'Phase 3 Study',
        topic: null,
        study_type: 'SMS',
        status: 'active',
        current_phase: 3,
        created_at: '2024-06-01T00:00:00Z',
      },
    ]);
    renderStudiesPage();
    expect(await screen.findByText(/Screening/)).toBeInTheDocument();
  });

  it('renders multiple studies', async () => {
    vi.mocked(api.get).mockResolvedValue([
      { id: 1, name: 'Study A', topic: null, study_type: 'SMS', status: 'active', current_phase: 1, created_at: '' },
      { id: 2, name: 'Study B', topic: null, study_type: 'SMS', status: 'draft', current_phase: 2, created_at: '' },
    ]);
    renderStudiesPage();
    expect(await screen.findByText('Study A')).toBeInTheDocument();
    expect(await screen.findByText('Study B')).toBeInTheDocument();
  });
});
