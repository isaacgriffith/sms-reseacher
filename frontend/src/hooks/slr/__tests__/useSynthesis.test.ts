/**
 * Unit tests for useSynthesis hooks (feature 007).
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  synthesisListKey,
  synthesisResultKey,
  useSynthesisResults,
  useStartSynthesis,
  useSynthesisResult,
} from '../useSynthesis';

vi.mock('../../../services/slr/synthesisApi', () => ({
  listSynthesisResults: vi.fn().mockResolvedValue({ results: [] }),
  startSynthesis: vi.fn().mockResolvedValue({ id: 1, status: 'pending' }),
  getSynthesisResult: vi.fn().mockResolvedValue({ id: 1, status: 'completed' }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('synthesisListKey', () => {
  it('returns stable key', () => {
    expect(synthesisListKey(5)).toEqual(['slr-synthesis-list', 5]);
  });
});

describe('synthesisResultKey', () => {
  it('returns stable key', () => {
    expect(synthesisResultKey(10)).toEqual(['slr-synthesis-result', 10]);
  });
});

describe('useSynthesisResults', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => useSynthesisResults(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useSynthesisResults(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useStartSynthesis', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useStartSynthesis(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ approach: 'meta_analysis', parameters: {} });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useSynthesisResult', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => useSynthesisResult(1), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
  });

  it('is disabled when synthesisId is 0', () => {
    const { result } = renderHook(() => useSynthesisResult(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});
