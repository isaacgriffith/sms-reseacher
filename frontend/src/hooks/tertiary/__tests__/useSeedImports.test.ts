/**
 * Unit tests for useSeedImports hooks (feature 009).
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
  seedImportsKey,
  groupStudiesKey,
  useSeedImports,
  useGroupStudies,
  useCreateSeedImport,
} from '../useSeedImports';

vi.mock('../../../services/tertiary/seedImportApi', () => ({
  listSeedImports: vi.fn().mockRejectedValue(new Error('not found')),
  listGroupStudies: vi.fn().mockRejectedValue(new Error('not found')),
  createSeedImport: vi.fn().mockResolvedValue({ id: 1, records_added: 3, records_skipped: 0, imported_at: '2026-01-01T00:00:00Z' }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('seedImportsKey', () => {
  it('returns stable array with study id', () => {
    expect(seedImportsKey(10)).toEqual(['tertiary-seed-imports', 10]);
  });
});

describe('groupStudiesKey', () => {
  it('returns stable array with group id', () => {
    expect(groupStudiesKey(3)).toEqual(['group-studies', 3]);
  });
});

describe('useSeedImports', () => {
  it('returns a query result with data property', async () => {
    const { result } = renderHook(() => useSeedImports(10), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useSeedImports(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useGroupStudies', () => {
  it('returns a query result with data property', async () => {
    const { result } = renderHook(() => useGroupStudies(3), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when groupId is 0', () => {
    const { result } = renderHook(() => useGroupStudies(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useCreateSeedImport', () => {
  it('returns a mutation with mutate function', () => {
    const { result } = renderHook(() => useCreateSeedImport(10), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});
