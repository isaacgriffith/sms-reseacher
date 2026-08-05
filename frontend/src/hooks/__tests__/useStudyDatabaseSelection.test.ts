import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { databaseSelectionKey, useStudyDatabaseSelection } from '../useStudyDatabaseSelection';

vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ study_id: 1, selections: [], snowball_enabled: false, scihub_enabled: false, scihub_acknowledged: false }),
    put: vi.fn().mockResolvedValue({ study_id: 1, selections: [], snowball_enabled: true, scihub_enabled: false, scihub_acknowledged: false }),
  },
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('databaseSelectionKey', () => {
  it('returns stable key', () => {
    expect(databaseSelectionKey(42)).toEqual(['database-selection', 42]);
  });
});

describe('useStudyDatabaseSelection', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => useStudyDatabaseSelection(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.data).toBeDefined();
  });

  it('executes update mutation', async () => {
    const { result } = renderHook(() => useStudyDatabaseSelection(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    await act(async () => {
      result.current.updateSelection.mutate({
        selections: [],
        snowball_enabled: true,
        scihub_enabled: false,
        scihub_acknowledged: false,
      });
    });
    await waitFor(() => expect(result.current.updateSelection.isSuccess).toBe(true));
  });
});
