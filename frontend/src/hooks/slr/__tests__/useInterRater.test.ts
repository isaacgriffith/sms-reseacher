import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { interRaterKey, useInterRaterRecords, useComputeKappa, usePostDiscussionKappa } from '../useInterRater';

vi.mock('../../../services/slr/interRaterApi', () => ({
  getInterRaterRecords: vi.fn().mockResolvedValue([]),
  computeKappa: vi.fn().mockResolvedValue({ kappa: 0.8 }),
  recordPostDiscussionKappa: vi.fn().mockResolvedValue({ kappa: 0.9 }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('interRaterKey', () => {
  it('returns stable key', () => {
    expect(interRaterKey(42)).toEqual(['slr-inter-rater', 42]);
  });
});

describe('useInterRaterRecords', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => useInterRaterRecords(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
  });
});

describe('useComputeKappa', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useComputeKappa(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate();
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('usePostDiscussionKappa', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => usePostDiscussionKappa(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ kappa: 0.9 });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
