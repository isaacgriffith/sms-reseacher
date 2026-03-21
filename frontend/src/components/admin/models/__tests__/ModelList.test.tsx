/**
 * Unit tests for ModelList component.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import ModelList from '../ModelList';
import { useProviderModels, useToggleModel } from '../../../../services/providersApi';

vi.mock('../../../../services/providersApi', () => ({
  useProviderModels: vi.fn(),
  useToggleModel: vi.fn(),
}));

const PROVIDER_ID = '00000000-0000-0000-0000-000000000001';

const MODEL = {
  id: '00000000-0000-0000-0000-000000000002',
  model_identifier: 'gpt-4',
  display_name: 'GPT-4',
  is_enabled: true,
  provider_id: PROVIDER_ID,
};

const mockMutate = vi.fn();

function setupMocks(overrides: Partial<ReturnType<typeof useProviderModels>> = {}) {
  vi.mocked(useProviderModels).mockReturnValue({
    data: undefined,
    isLoading: false,
    error: null,
    ...overrides,
  } as ReturnType<typeof useProviderModels>);
  vi.mocked(useToggleModel).mockReturnValue({
    mutate: mockMutate,
    isPending: false,
  } as unknown as ReturnType<typeof useToggleModel>);
}

describe('ModelList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMocks();
  });

  it('shows loading spinner while fetching', () => {
    setupMocks({ isLoading: true });
    render(<ModelList providerId={PROVIDER_ID} />);
    expect(document.querySelector('circle')).toBeInTheDocument();
  });

  it('shows error message on failure', () => {
    setupMocks({ error: new Error('Network error') } as Parameters<typeof setupMocks>[0]);
    render(<ModelList providerId={PROVIDER_ID} />);
    expect(screen.getByText(/failed to load models/i)).toBeInTheDocument();
  });

  it('shows empty state when no models', () => {
    setupMocks({ data: [] });
    render(<ModelList providerId={PROVIDER_ID} />);
    expect(screen.getByText(/no models found/i)).toBeInTheDocument();
  });

  it('renders table headers', () => {
    setupMocks({ data: [] });
    render(<ModelList providerId={PROVIDER_ID} />);
    expect(screen.getByText('Model Identifier')).toBeInTheDocument();
    expect(screen.getByText('Display Name')).toBeInTheDocument();
    expect(screen.getByText('Enabled')).toBeInTheDocument();
  });

  it('renders a model row with identifier and display name', () => {
    setupMocks({ data: [MODEL] });
    render(<ModelList providerId={PROVIDER_ID} />);
    expect(screen.getByText('gpt-4')).toBeInTheDocument();
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  it('calls toggleMutation when switch clicked', () => {
    setupMocks({ data: [MODEL] });
    render(<ModelList providerId={PROVIDER_ID} />);
    const toggle = screen.getByRole('checkbox', { name: /toggle gpt-4/i });
    fireEvent.click(toggle);
    expect(mockMutate).toHaveBeenCalledWith({
      providerId: PROVIDER_ID,
      modelId: MODEL.id,
      is_enabled: false,
    });
  });
});
