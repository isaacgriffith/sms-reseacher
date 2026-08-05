import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  greyLiteratureKey,
  useGreyLiterature,
  useAddSource,
  useDeleteSource,
} from '../useGreyLiterature';

vi.mock('../../../services/slr/greyLiteratureApi', () => ({
  listGreyLiterature: vi.fn().mockResolvedValue([]),
  addGreyLiteratureSource: vi.fn().mockResolvedValue({ id: 1 }),
  deleteGreyLiteratureSource: vi.fn().mockResolvedValue(undefined),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('greyLiteratureKey', () => {
  it('returns stable key', () => {
    expect(greyLiteratureKey(42)).toEqual(['slr-grey-literature', 42]);
  });
});

describe('useGreyLiterature', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => useGreyLiterature(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
  });
});

describe('useAddSource', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useAddSource(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ title: 'Test', url: 'http://test.com', source_type: 'report' });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useDeleteSource', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useDeleteSource(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate(1);
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
