import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  searchIntegrationKey,
  useSearchIntegrations,
  useSearchIntegration,
  useUpsertCredential,
  useTestIntegration,
} from '../useSearchIntegrations';

vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue([]),
    put: vi.fn().mockResolvedValue({ integration_type: 'ieee', status: 'ok' }),
    post: vi.fn().mockResolvedValue({
      integration_type: 'ieee',
      status: 'ok',
      message: 'ok',
      tested_at: '2026-01-01',
    }),
  },
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useSearchIntegrations hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('searchIntegrationKey returns correct key', () => {
    expect(searchIntegrationKey('ieee_xplore')).toEqual(['search-integration', 'ieee_xplore']);
  });

  it('useSearchIntegrations fetches data', async () => {
    const { result } = renderHook(() => useSearchIntegrations(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.data).toEqual([]);
  });

  it('useSearchIntegration fetches data', async () => {
    const { result } = renderHook(() => useSearchIntegration('ieee'), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
  });

  it('useUpsertCredential executes mutation', async () => {
    const { result } = renderHook(() => useUpsertCredential(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ integrationType: 'ieee', body: { api_key: 'key123' } });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('useTestIntegration executes mutation', async () => {
    const { result } = renderHook(() => useTestIntegration(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate('ieee');
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
