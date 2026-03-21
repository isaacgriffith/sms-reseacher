/**
 * Unit tests for useGreyLiterature hooks (feature 007).
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  useGreyLiterature,
  useAddSource,
  useDeleteSource,
} from '../useGreyLiterature';

vi.mock('../../../services/slr/greyLiteratureApi', () => ({
  listGreyLiterature: vi.fn().mockRejectedValue(new Error('network')),
  addGreyLiteratureSource: vi.fn().mockResolvedValue({ id: 1 }),
  deleteGreyLiteratureSource: vi.fn().mockResolvedValue(undefined),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useGreyLiterature', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => useGreyLiterature(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('error');
  });
});

describe('useAddSource', () => {
  it('returns a mutation object', () => {
    const { result } = renderHook(() => useAddSource(42), {
      wrapper: makeWrapper(),
    });
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('useDeleteSource', () => {
  it('returns a mutation object', () => {
    const { result } = renderHook(() => useDeleteSource(42), {
      wrapper: makeWrapper(),
    });
    expect(typeof result.current.mutate).toBe('function');
  });
});
