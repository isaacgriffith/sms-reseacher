/**
 * Unit tests for useInterRater hooks (feature 007).
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  useInterRaterRecords,
  useComputeKappa,
  usePostDiscussionKappa,
} from '../useInterRater';

vi.mock('../../../services/slr/interRaterApi', () => ({
  getInterRaterRecords: vi.fn().mockRejectedValue(new Error('network')),
  computeKappa: vi.fn().mockResolvedValue({ id: 1 }),
  recordPostDiscussionKappa: vi.fn().mockResolvedValue({ id: 2 }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useInterRaterRecords', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => useInterRaterRecords(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('error');
  });
});

describe('useComputeKappa', () => {
  it('returns a mutation object', () => {
    const { result } = renderHook(() => useComputeKappa(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('usePostDiscussionKappa', () => {
  it('returns a mutation object', () => {
    const { result } = renderHook(() => usePostDiscussionKappa(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});
