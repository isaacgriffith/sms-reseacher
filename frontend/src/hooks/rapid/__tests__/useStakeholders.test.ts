/**
 * Unit tests for useStakeholders hooks (feature 008).
 *
 * Covers stakeholdersKey, useStakeholders, useCreateStakeholder,
 * useUpdateStakeholder, and useDeleteStakeholder.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  stakeholdersKey,
  useStakeholders,
  useCreateStakeholder,
  useUpdateStakeholder,
  useDeleteStakeholder,
} from '../useStakeholders';

vi.mock('../../../services/rapid/stakeholdersApi', () => ({
  listStakeholders: vi.fn().mockRejectedValue(new Error('network')),
  createStakeholder: vi.fn().mockResolvedValue({ id: 1, study_id: 42, name: 'Alice', role: 'Reviewer', email: null, created_at: '2026-01-01T00:00:00Z' }),
  updateStakeholder: vi.fn().mockResolvedValue({ id: 1, study_id: 42, name: 'Alice Updated', role: 'Reviewer', email: null, created_at: '2026-01-01T00:00:00Z' }),
  deleteStakeholder: vi.fn().mockResolvedValue(undefined),
}));

vi.mock('../useRRProtocol', () => ({
  rrProtocolKey: vi.fn((studyId: number) => ['rr-protocol', studyId]),
}));

import * as stakeholdersApiModule from '../../../services/rapid/stakeholdersApi';

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('stakeholdersKey', () => {
  it('returns stable tuple', () => {
    expect(stakeholdersKey(42)).toEqual(['rr-stakeholders', 42]);
  });
});

describe('useStakeholders', () => {
  it('returns a query result with data property', async () => {
    const { result } = renderHook(() => useStakeholders(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useStakeholders(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useCreateStakeholder', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useCreateStakeholder(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls createStakeholder with studyId and data', async () => {
    const { result } = renderHook(() => useCreateStakeholder(42), { wrapper: makeWrapper() });
    result.current.mutate({ name: 'Alice', role: 'Reviewer', email: null });
    await waitFor(() => result.current.isSuccess);
    expect(stakeholdersApiModule.createStakeholder).toHaveBeenCalledWith(42, { name: 'Alice', role: 'Reviewer', email: null });
  });
});

describe('useUpdateStakeholder', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useUpdateStakeholder(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls updateStakeholder with studyId, id, and data', async () => {
    const { result } = renderHook(() => useUpdateStakeholder(42), { wrapper: makeWrapper() });
    result.current.mutate({ id: 1, data: { name: 'Alice Updated' } });
    await waitFor(() => result.current.isSuccess);
    expect(stakeholdersApiModule.updateStakeholder).toHaveBeenCalledWith(42, 1, { name: 'Alice Updated' });
  });
});

describe('useDeleteStakeholder', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useDeleteStakeholder(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls deleteStakeholder with studyId and id', async () => {
    const { result } = renderHook(() => useDeleteStakeholder(42), { wrapper: makeWrapper() });
    result.current.mutate(1);
    await waitFor(() => result.current.isSuccess);
    expect(stakeholdersApiModule.deleteStakeholder).toHaveBeenCalledWith(42, 1);
  });
});
