/**
 * Unit tests for useSynthesis hooks (feature 007).
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  useSynthesisResults,
  useStartSynthesis,
  useSynthesisResult,
} from '../useSynthesis';

vi.mock('../../../services/slr/synthesisApi', () => ({
  listSynthesisResults: vi.fn().mockRejectedValue(new Error('network')),
  startSynthesis: vi.fn().mockResolvedValue({ id: 1, status: 'pending' }),
  getSynthesisResult: vi.fn().mockRejectedValue(new Error('not found')),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useSynthesisResults', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => useSynthesisResults(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('error');
  });
});

describe('useStartSynthesis', () => {
  it('returns a mutation object', () => {
    const { result } = renderHook(() => useStartSynthesis(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('useSynthesisResult', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => useSynthesisResult(1), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });
});
