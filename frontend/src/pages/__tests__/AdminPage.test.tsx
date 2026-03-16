/**
 * Tests for AdminPage component.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import AdminPage from '../AdminPage';

vi.mock('../../services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../services/api')>();
  return {
    ...actual,
    api: {
      get: vi.fn(),
      post: vi.fn(),
      delete: vi.fn(),
    },
  };
});

// Mock child panels to avoid their own API calls
vi.mock('../../components/admin/ServiceHealthPanel', () => ({
  default: () => <div data-testid="service-health-panel">Service Health Panel</div>,
}));
vi.mock('../../components/admin/JobRetryPanel', () => ({
  default: () => <div data-testid="job-retry-panel">Job Retry Panel</div>,
}));

import { api, ApiError } from '../../services/api';

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
 * Renders AdminPage with required context providers.
 *
 * @returns The rendered component.
 */
function renderAdminPage() {
  const qc = makeQueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <AdminPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AdminPage', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('shows checking access state initially', () => {
    vi.mocked(api.get).mockReturnValue(new Promise(() => {}));
    renderAdminPage();
    expect(screen.getByText(/checking access/i)).toBeInTheDocument();
  });

  it('shows admin dashboard heading when access check succeeds', async () => {
    vi.mocked(api.get).mockResolvedValue({});
    renderAdminPage();
    expect(await screen.findByRole('heading')).toBeInTheDocument();
    expect(screen.getByText(/admin dashboard/i)).toBeInTheDocument();
  });

  it('renders ServiceHealthPanel when access check succeeds', async () => {
    vi.mocked(api.get).mockResolvedValue({});
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    expect(screen.getByTestId('service-health-panel')).toBeInTheDocument();
  });

  it('renders JobRetryPanel when access check succeeds', async () => {
    vi.mocked(api.get).mockResolvedValue({});
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    expect(screen.getByTestId('job-retry-panel')).toBeInTheDocument();
  });

  it('shows 403 forbidden message when access is denied', async () => {
    vi.mocked(api.get).mockRejectedValue(new ApiError(403, 'Forbidden'));
    renderAdminPage();
    expect(await screen.findByText(/403 Forbidden/i)).toBeInTheDocument();
  });

  it('shows back to groups button on 403', async () => {
    vi.mocked(api.get).mockRejectedValue(new ApiError(403, 'Forbidden'));
    renderAdminPage();
    expect(await screen.findByRole('button', { name: /back to groups/i })).toBeInTheDocument();
  });
});
