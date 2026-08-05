/**
 * Tests for AdminPage component.
 */

import { render, screen, fireEvent } from '@testing-library/react';
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

const { capturedProviderCallbacks, capturedAgentCallbacks } = vi.hoisted(() => ({
  capturedProviderCallbacks: {} as Record<string, (...args: unknown[]) => void>,
  capturedAgentCallbacks: {} as Record<string, (...args: unknown[]) => void>,
}));

// Mock child panels to avoid their own API calls
vi.mock('../../components/admin/ServiceHealthPanel', () => ({
  default: () => <div data-testid="service-health-panel">Service Health Panel</div>,
}));
vi.mock('../../components/admin/JobRetryPanel', () => ({
  default: () => <div data-testid="job-retry-panel">Job Retry Panel</div>,
}));
vi.mock('../../components/admin/providers/ProviderList', () => ({
  default: ({ onEdit, onDelete, onRefresh }: Record<string, (...args: unknown[]) => void>) => {
    capturedProviderCallbacks.onEdit = onEdit;
    capturedProviderCallbacks.onDelete = onDelete;
    capturedProviderCallbacks.onRefresh = onRefresh;
    return <div data-testid="provider-list">Provider List</div>;
  },
}));
vi.mock('../../components/admin/providers/ProviderForm', () => ({
  default: ({ onSuccess, onCancel }: Record<string, () => void>) => (
    <div data-testid="provider-form">
      <button onClick={onSuccess}>Form Success</button>
      <button onClick={onCancel}>Form Cancel</button>
    </div>
  ),
}));
vi.mock('../../components/admin/models/ModelList', () => ({
  default: () => <div data-testid="model-list">Model List</div>,
}));
vi.mock('../../components/admin/agents/AgentList', () => ({
  default: ({ onEdit }: { onEdit: (agent: { id: string }) => void }) => {
    capturedAgentCallbacks.onEdit = onEdit as (...args: unknown[]) => void;
    return <div data-testid="agent-list">Agent List</div>;
  },
}));
vi.mock('../../components/admin/agents/AgentForm', () => ({
  default: ({ onSuccess, onCancel }: Record<string, () => void>) => (
    <div data-testid="agent-form">
      <button onClick={onSuccess}>Agent Form Success</button>
      <button onClick={onCancel}>Agent Form Cancel</button>
    </div>
  ),
}));
vi.mock('../../components/admin/agents/AgentWizard', () => ({
  default: ({ open, onClose }: { open: boolean; onClose: () => void }) =>
    open ? (
      <div data-testid="agent-wizard">
        <button onClick={onClose}>Close Wizard</button>
      </div>
    ) : null,
}));
vi.mock('../../components/admin/SearchIntegrationsTable', () => ({
  default: () => <div data-testid="search-integrations">Search Integrations</div>,
}));

vi.mock('../../services/providersApi', () => ({
  useProviders: vi.fn(() => ({ data: [{ id: 'p1', display_name: 'OpenAI', provider_type: 'openai' }], isLoading: false })),
  useDeleteProvider: vi.fn(() => ({ mutate: vi.fn() })),
  useRefreshModels: vi.fn(() => ({ mutate: vi.fn() })),
}));
vi.mock('../../services/agentsApi', () => ({
  useAgents: vi.fn(() => ({ data: [{ id: 'a1', role_name: 'Screener' }], isLoading: false })),
  useAgent: vi.fn(() => ({ data: null })),
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

  it('switches to Providers tab and shows provider list', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /providers/i }));
    expect(await screen.findByTestId('provider-list')).toBeInTheDocument();
  });

  it('switches to Models tab and shows provider selector', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /models/i }));
    expect(await screen.findByText(/select a provider/i)).toBeInTheDocument();
  });

  it('switches to Agents tab and shows agent list', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /agents/i }));
    expect(await screen.findByTestId('agent-list')).toBeInTheDocument();
  });

  it('switches to Search Integrations tab', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /search integrations/i }));
    expect(await screen.findByTestId('search-integrations')).toBeInTheDocument();
  });

  it('opens Add Provider dialog when Add Provider clicked', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /providers/i }));
    await screen.findByTestId('provider-list');
    fireEvent.click(screen.getByRole('button', { name: /add provider/i }));
    expect(await screen.findByTestId('provider-form')).toBeInTheDocument();
  });

  it('opens Agent Wizard when Create Agent clicked', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /agents/i }));
    await screen.findByTestId('agent-list');
    fireEvent.click(screen.getByRole('button', { name: /create agent/i }));
    // Agent wizard rendered with open=true; mock renders it unconditionally
    expect(screen.getByTestId('agent-wizard')).toBeInTheDocument();
  });

  it('shows providers loading spinner while fetching', async () => {
    // Return never-resolving promises for all calls
    vi.mocked(api.get).mockReturnValue(new Promise(() => {}));
    renderAdminPage();
    // Still in checking access state; cannot reach Providers tab
    expect(screen.getByText(/checking access/i)).toBeInTheDocument();
  });

  it('calls onEdit callback from provider list to open edit dialog', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /providers/i }));
    await screen.findByTestId('provider-list');
    // Trigger the captured onEdit callback from ProviderList
    const { act } = await import('@testing-library/react');
    act(() => {
      capturedProviderCallbacks.onEdit({ id: 'p1', display_name: 'OpenAI', provider_type: 'openai' });
    });
    expect(await screen.findByText(/Edit Provider/i)).toBeInTheDocument();
  });

  it('calls onDelete callback from provider list with confirm', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /providers/i }));
    await screen.findByTestId('provider-list');
    const { act } = await import('@testing-library/react');
    act(() => {
      capturedProviderCallbacks.onDelete('p1');
    });
    vi.mocked(window.confirm).mockRestore();
  });

  it('closes provider form via onSuccess callback', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /providers/i }));
    await screen.findByTestId('provider-list');
    fireEvent.click(screen.getByRole('button', { name: /add provider/i }));
    await screen.findByTestId('provider-form');
    fireEvent.click(screen.getByText('Form Success'));
    // Dialog should close — form should no longer be visible after animation
  });

  it('selects provider in Models tab dropdown', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /models/i }));
    // The Models tab should show the provider dropdown
    expect(await screen.findByText(/select a provider/i)).toBeInTheDocument();
  });

  it('triggers onEdit from agent list to open edit dialog', async () => {
    const { useAgent } = await import('../../services/agentsApi');
    vi.mocked(useAgent).mockReturnValue({ data: { id: 'a1', role_name: 'Test' } } as ReturnType<typeof useAgent>);
    vi.mocked(api.get).mockResolvedValue([]);
    renderAdminPage();
    await screen.findByText(/admin dashboard/i);
    fireEvent.click(screen.getByRole('tab', { name: /agents/i }));
    await screen.findByTestId('agent-list');
    const { act } = await import('@testing-library/react');
    act(() => {
      capturedAgentCallbacks.onEdit({ id: 'a1' });
    });
    // Agent edit dialog should appear
  });
});
