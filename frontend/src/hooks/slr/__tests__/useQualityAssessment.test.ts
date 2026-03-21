/**
 * Unit tests for useQualityAssessment hooks (feature 007).
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  useChecklist,
  useQualityScores,
  useUpsertChecklist,
  useSubmitScores,
} from '../useQualityAssessment';

vi.mock('../../../services/slr/qualityApi', () => ({
  getChecklist: vi.fn().mockRejectedValue(new Error('not found')),
  getQualityScores: vi.fn().mockRejectedValue(new Error('not found')),
  upsertChecklist: vi.fn().mockResolvedValue({ id: 1 }),
  submitQualityScores: vi.fn().mockResolvedValue([]),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useChecklist', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => useChecklist(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('error');
  });
});

describe('useQualityScores', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => useQualityScores(7), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('error');
  });
});

describe('useUpsertChecklist', () => {
  it('returns a mutation object', () => {
    const { result } = renderHook(() => useUpsertChecklist(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('useSubmitScores', () => {
  it('returns a mutation object', () => {
    const { result } = renderHook(() => useSubmitScores(7), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});
