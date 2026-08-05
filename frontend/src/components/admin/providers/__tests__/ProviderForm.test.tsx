import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import ProviderForm from '../ProviderForm';

vi.mock('../../../../services/providersApi', () => ({
  useCreateProvider: vi.fn().mockReturnValue({ mutateAsync: vi.fn(), isPending: false, error: null }),
  useUpdateProvider: vi.fn().mockReturnValue({ mutateAsync: vi.fn(), isPending: false, error: null }),
}));

const mockProvider = {
  id: '00000000-0000-0000-0000-000000000001',
  display_name: 'OpenAI',
  provider_type: 'openai' as const,
  base_url: null,
  has_api_key: true,
  is_enabled: true,
  version_id: 1,
};

describe('ProviderForm', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders create mode when no provider', () => {
    render(React.createElement(ProviderForm, { onSuccess: vi.fn(), onCancel: vi.fn() }));
    expect(screen.getByText('Add Provider')).toBeInTheDocument();
  });

  it('renders edit mode with provider data', () => {
    render(
      React.createElement(ProviderForm, {
        provider: mockProvider,
        onSuccess: vi.fn(),
        onCancel: vi.fn(),
      }),
    );
    expect(screen.getByDisplayValue('OpenAI')).toBeInTheDocument();
  });
});
