/**
 * Unit tests for APIDocsPage component.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import APIDocsPage from '../APIDocsPage';
import { api } from '../../../services/api';

vi.mock('../../../services/api', () => ({ api: { get: vi.fn() } }));
vi.mock('swagger-ui-react', () => ({
  default: ({ spec }: { spec: unknown }) => (
    <div data-testid="swagger-ui">{spec ? 'Swagger loaded' : 'No spec'}</div>
  ),
}));

const mockApi = vi.mocked(api);

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe('APIDocsPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('shows loading state initially', () => {
    mockApi.get.mockReturnValue(new Promise(() => {}));
    render(<APIDocsPage />, { wrapper });
    expect(screen.getByText(/loading api documentation/i)).toBeInTheDocument();
  });

  it('renders swagger ui when spec loads', async () => {
    mockApi.get.mockResolvedValue({ openapi: '3.0.0' });
    render(<APIDocsPage />, { wrapper });
    expect(await screen.findByTestId('swagger-ui')).toBeInTheDocument();
  });

  it('shows error when fetch fails', async () => {
    mockApi.get.mockRejectedValue(new Error('Unauthorized'));
    render(<APIDocsPage />, { wrapper });
    expect(await screen.findByText(/failed to load api documentation/i)).toBeInTheDocument();
  });
});
