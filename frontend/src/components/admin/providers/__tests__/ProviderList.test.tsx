/**
 * Unit tests for ProviderList component.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import ProviderList from '../ProviderList';
import type { Provider } from '../../../../types/provider';

const PROVIDER: Provider = {
  id: '00000000-0000-0000-0000-000000000001',
  provider_type: 'openai',
  display_name: 'OpenAI',
  has_api_key: true,
  base_url: null,
  is_enabled: true,
  version_id: 1,
};

describe('ProviderList', () => {
  it('renders table headers', () => {
    render(
      <ProviderList providers={[]} onEdit={vi.fn()} onDelete={vi.fn()} onRefresh={vi.fn()} />,
    );
    expect(screen.getByText(/type/i)).toBeInTheDocument();
    expect(screen.getByText(/display name/i)).toBeInTheDocument();
  });

  it('shows empty state when no providers', () => {
    render(
      <ProviderList providers={[]} onEdit={vi.fn()} onDelete={vi.fn()} onRefresh={vi.fn()} />,
    );
    expect(screen.getByText(/no providers/i)).toBeInTheDocument();
  });

  it('renders a provider row', () => {
    render(
      <ProviderList
        providers={[PROVIDER]}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );
    expect(screen.getByText('OpenAI')).toBeInTheDocument();
    expect(screen.getByText('openai')).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', () => {
    const onEdit = vi.fn();
    render(
      <ProviderList
        providers={[PROVIDER]}
        onEdit={onEdit}
        onDelete={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith(PROVIDER);
  });

  it('calls onDelete when delete button clicked', () => {
    const onDelete = vi.fn();
    render(
      <ProviderList
        providers={[PROVIDER]}
        onEdit={vi.fn()}
        onDelete={onDelete}
        onRefresh={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /delete/i }));
    expect(onDelete).toHaveBeenCalledWith(PROVIDER.id);
  });

  it('shows Disabled chip for disabled provider', () => {
    render(
      <ProviderList
        providers={[{ ...PROVIDER, is_enabled: false }]}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );
    expect(screen.getByText('Disabled')).toBeInTheDocument();
  });

  it('shows Not set chip when no API key', () => {
    render(
      <ProviderList
        providers={[{ ...PROVIDER, has_api_key: false }]}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );
    expect(screen.getByText('Not set')).toBeInTheDocument();
  });

  it('uses default color for unknown provider type', () => {
    render(
      <ProviderList
        providers={[{ ...PROVIDER, provider_type: 'custom' }]}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );
    expect(screen.getByText('custom')).toBeInTheDocument();
  });

  it('calls onRefresh when refresh button clicked', () => {
    const onRefresh = vi.fn();
    render(
      <ProviderList
        providers={[PROVIDER]}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        onRefresh={onRefresh}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /refresh/i }));
    expect(onRefresh).toHaveBeenCalledWith(PROVIDER.id);
  });
});
