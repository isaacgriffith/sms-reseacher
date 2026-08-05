import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  checklistKey,
  qualityScoresKey,
  useChecklist,
  useQualityScores,
  useUpsertChecklist,
  useSubmitScores,
} from '../useQualityAssessment';

vi.mock('../../../services/slr/qualityApi', () => ({
  getChecklist: vi.fn().mockResolvedValue({ id: 1, items: [] }),
  getQualityScores: vi.fn().mockResolvedValue([]),
  upsertChecklist: vi.fn().mockResolvedValue({ id: 1 }),
  submitQualityScores: vi.fn().mockResolvedValue([]),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('checklistKey', () => {
  it('returns stable key', () => {
    expect(checklistKey(42)).toEqual(['slr-quality-checklist', 42]);
  });
});

describe('qualityScoresKey', () => {
  it('returns stable key', () => {
    expect(qualityScoresKey(7)).toEqual(['slr-quality-scores', 7]);
  });
});

describe('useChecklist', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => useChecklist(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
  });
});

describe('useQualityScores', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => useQualityScores(7), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
  });
});

describe('useUpsertChecklist', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useUpsertChecklist(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ items: [] });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useSubmitScores', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useSubmitScores(7), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate([]);
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
