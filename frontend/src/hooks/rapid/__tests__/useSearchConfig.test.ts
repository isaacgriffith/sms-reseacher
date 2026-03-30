/**
 * Unit tests for useSearchConfig hooks (feature 008).
 *
 * Covers useUpdateSearchConfig.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useUpdateSearchConfig } from '../useSearchConfig';

vi.mock('../../../services/rapid/searchConfigApi', () => ({
  updateSearchConfig: vi.fn().mockResolvedValue([]),
}));

vi.mock('../useRRProtocol', () => ({
  rrThreatsKey: vi.fn((studyId: number) => ['rr-threats', studyId]),
}));

import * as searchConfigApiModule from '../../../services/rapid/searchConfigApi';

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useUpdateSearchConfig', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useUpdateSearchConfig(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls updateSearchConfig with studyId and data', async () => {
    const { result } = renderHook(() => useUpdateSearchConfig(42), { wrapper: makeWrapper() });
    result.current.mutate({ restrictions: [], single_reviewer_mode: false });
    await waitFor(() => result.current.isSuccess);
    expect(searchConfigApiModule.updateSearchConfig).toHaveBeenCalledWith(42, {
      restrictions: [],
      single_reviewer_mode: false,
    });
  });
});
