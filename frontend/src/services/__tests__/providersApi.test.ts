/**
 * Unit tests for providersApi.ts hooks (feature 005).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  useProviders,
  useProvider,
  useProviderModels,
  useCreateProvider,
  useUpdateProvider,
  useDeleteProvider,
  useRefreshModels,
  useToggleModel,
} from '../providersApi';
import { api } from '../api';

vi.mock('../api', () => ({
  api: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}));

const mockApi = vi.mocked(api);

const PROVIDER = {
  id: '00000000-0000-0000-0000-000000000001',
  display_name: 'OpenAI',
  provider_type: 'openai',
  base_url: null,
  has_api_key: true,
  is_enabled: true,
  version_id: 1,
};

const MODEL = {
  id: '00000000-0000-0000-0000-000000000010',
  provider_id: '00000000-0000-0000-0000-000000000001',
  model_identifier: 'gpt-4',
  display_name: 'GPT-4',
  is_enabled: true,
  version_id: 1,
};

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useProviders', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('fetches providers list', async () => {
    mockApi.get.mockResolvedValue([PROVIDER]);
    const { result } = renderHook(() => useProviders(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
  });
});

describe('useProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('fetches single provider', async () => {
    mockApi.get.mockResolvedValue(PROVIDER);
    const { result } = renderHook(() => useProvider('00000000-0000-0000-0000-000000000001'), {
      wrapper: makeWrapper(),
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.display_name).toBe('OpenAI');
  });
});

describe('useProviderModels', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('fetches models for provider', async () => {
    mockApi.get.mockResolvedValue([MODEL]);
    const { result } = renderHook(() => useProviderModels('00000000-0000-0000-0000-000000000001'), {
      wrapper: makeWrapper(),
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
  });
});

describe('useCreateProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('creates provider', async () => {
    mockApi.post.mockResolvedValue(PROVIDER);
    const { result } = renderHook(() => useCreateProvider(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({
        display_name: 'OpenAI',
        provider_type: 'openai',
        api_key: 'sk-123',
        is_enabled: true,
      });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockApi.post).toHaveBeenCalled();
  });
});

describe('useUpdateProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('updates provider', async () => {
    mockApi.patch.mockResolvedValue(PROVIDER);
    const { result } = renderHook(() => useUpdateProvider(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({
        id: '00000000-0000-0000-0000-000000000001',
        data: { display_name: 'Updated' },
      });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useDeleteProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('deletes provider', async () => {
    mockApi.delete.mockResolvedValue(undefined);
    const { result } = renderHook(() => useDeleteProvider(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate('00000000-0000-0000-0000-000000000001');
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useRefreshModels', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('refreshes models', async () => {
    mockApi.post.mockResolvedValue({ models_added: 1, models_removed: 0, models_total: 5 });
    const { result } = renderHook(() => useRefreshModels(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate('00000000-0000-0000-0000-000000000001');
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useToggleModel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('toggles model', async () => {
    mockApi.patch.mockResolvedValue({ ...MODEL, is_enabled: false });
    const { result } = renderHook(() => useToggleModel(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({
        providerId: '00000000-0000-0000-0000-000000000001',
        modelId: '00000000-0000-0000-0000-000000000010',
        is_enabled: false,
      });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
