/**
 * Unit tests for useProtocol hooks (feature 007).
 *
 * Covers:
 * - Hook exports are functions.
 * - Query keys are stable.
 * - Hook instantiation without throwing.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  protocolKey,
  phasesKey,
  useProtocol,
  usePhases,
  useUpsertProtocol,
  useSubmitForReview,
  useValidateProtocol,
} from '../useProtocol';

// Mock the API layer so no real HTTP calls are made
vi.mock('../../../services/slr/protocolApi', () => ({
  getProtocol: vi.fn().mockRejectedValue({ status: 404 }),
  getPhases: vi.fn().mockRejectedValue(new Error('not found')),
  upsertProtocol: vi.fn().mockResolvedValue({ id: 1 }),
  submitForReview: vi.fn().mockResolvedValue({ job_id: 'j1', status: 'queued' }),
  validateProtocol: vi.fn().mockResolvedValue({ status: 'validated' }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('Query keys', () => {
  it('protocolKey returns stable array', () => {
    expect(protocolKey(42)).toEqual(['slr-protocol', 42]);
  });

  it('phasesKey returns stable array', () => {
    expect(phasesKey(42)).toEqual(['slr-phases', 42]);
  });
});

describe('useProtocol', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => useProtocol(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });
});

describe('usePhases', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => usePhases(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });
});

describe('useUpsertProtocol', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useUpsertProtocol(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('useSubmitForReview', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useSubmitForReview(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('useValidateProtocol', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useValidateProtocol(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });
});
