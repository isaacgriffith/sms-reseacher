/**
 * Unit tests for useProtocol hooks (feature 009).
 *
 * Covers:
 * - Query key stability.
 * - Hook instantiation without throwing.
 * - Hook returns expected TanStack Query shapes.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  tertiaryProtocolKey,
  useTertiaryProtocol,
  useUpdateTertiaryProtocol,
  useValidateTertiaryProtocol,
} from '../useProtocol';

vi.mock('../../../services/tertiary/protocolApi', () => ({
  getProtocol: vi.fn().mockRejectedValue(new Error('not found')),
  updateProtocol: vi.fn().mockResolvedValue({ id: 1, status: 'draft' }),
  validateProtocol: vi.fn().mockResolvedValue({ job_id: 'j1', status: 'queued' }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('tertiaryProtocolKey', () => {
  it('returns stable array with study id', () => {
    expect(tertiaryProtocolKey(42)).toEqual(['tertiary-protocol', 42]);
  });
});

describe('useTertiaryProtocol', () => {
  it('returns a query result with data property', async () => {
    const { result } = renderHook(() => useTertiaryProtocol(42), {
      wrapper: makeWrapper(),
    });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useTertiaryProtocol(0), {
      wrapper: makeWrapper(),
    });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useUpdateTertiaryProtocol', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useUpdateTertiaryProtocol(42), {
      wrapper: makeWrapper(),
    });
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('useValidateTertiaryProtocol', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useValidateTertiaryProtocol(42), {
      wrapper: makeWrapper(),
    });
    expect(typeof result.current.mutate).toBe('function');
  });
});
