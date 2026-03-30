/**
 * Unit tests for useExtractions hooks (feature 009).
 *
 * Covers:
 * - Query key stability.
 * - Hook instantiation without throwing.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  extractionsKey,
  useExtractions,
  useUpdateExtraction,
  useAiAssist,
} from '../useExtractions';

vi.mock('../../../services/tertiary/extractionApi', () => ({
  listExtractions: vi.fn().mockRejectedValue(new Error('not found')),
  updateExtraction: vi.fn().mockResolvedValue({ id: 1, extraction_status: 'human_reviewed' }),
  triggerAiAssist: vi.fn().mockResolvedValue({ job_id: 'ai-1', status: 'queued', paper_count: 2 }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('extractionsKey', () => {
  it('returns stable array with study id', () => {
    expect(extractionsKey(10)).toEqual(['tertiary-extractions', 10]);
  });
});

describe('useExtractions', () => {
  it('returns a query result with data property', async () => {
    const { result } = renderHook(() => useExtractions(10), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useExtractions(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useUpdateExtraction', () => {
  it('returns a mutation with mutate function', () => {
    const { result } = renderHook(() => useUpdateExtraction(10), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('useAiAssist', () => {
  it('returns a mutation with mutate function', () => {
    const { result } = renderHook(() => useAiAssist(10), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});
