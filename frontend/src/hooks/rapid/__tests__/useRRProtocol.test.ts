/**
 * Unit tests for useRRProtocol hooks (feature 008).
 *
 * Covers rrProtocolKey, rrThreatsKey, useRRProtocol, useRRThreats,
 * useUpdateRRProtocol, and useValidateRRProtocol.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  rrProtocolKey,
  rrThreatsKey,
  useRRProtocol,
  useRRThreats,
  useUpdateRRProtocol,
  useValidateRRProtocol,
} from '../useRRProtocol';

vi.mock('../../../services/rapid/protocolApi', () => ({
  getProtocol: vi.fn().mockRejectedValue(new Error('network')),
  getThreats: vi.fn().mockRejectedValue(new Error('network')),
  updateProtocol: vi.fn().mockResolvedValue({ id: 1, status: 'draft' }),
  validateProtocol: vi.fn().mockResolvedValue({ id: 1, status: 'validated' }),
}));

vi.mock('../../../services/api', () => ({
  ApiError: class ApiError extends Error {
    status: number;
    detail: string;
    constructor(status: number, detail: string) {
      super(detail);
      this.status = status;
      this.detail = detail;
    }
  },
}));

import * as protocolApiModule from '../../../services/rapid/protocolApi';

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('Query keys', () => {
  it('rrProtocolKey returns stable tuple', () => {
    expect(rrProtocolKey(42)).toEqual(['rr-protocol', 42]);
  });

  it('rrThreatsKey returns stable tuple', () => {
    expect(rrThreatsKey(42)).toEqual(['rr-threats', 42]);
  });
});

describe('useRRProtocol', () => {
  it('returns a query result with data property', async () => {
    const { result } = renderHook(() => useRRProtocol(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useRRProtocol(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useRRThreats', () => {
  it('returns a query result with data property', async () => {
    const { result } = renderHook(() => useRRThreats(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useRRThreats(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useUpdateRRProtocol', () => {
  it('returns mutation object and helpers', () => {
    const { result } = renderHook(() => useUpdateRRProtocol(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutation.mutate).toBe('function');
    expect(typeof result.current.confirmInvalidation).toBe('function');
    expect(typeof result.current.cancelInvalidation).toBe('function');
    expect(result.current.invalidationPending).toBeNull();
  });

  it('calls updateProtocol with studyId and data', async () => {
    const { result } = renderHook(() => useUpdateRRProtocol(42), { wrapper: makeWrapper() });
    result.current.mutation.mutate({ practical_problem: 'A problem' });
    await waitFor(() => result.current.mutation.isSuccess);
    expect(protocolApiModule.updateProtocol).toHaveBeenCalledWith(42, { practical_problem: 'A problem' }, false);
  });

  it('cancelInvalidation resets invalidationPending to null', () => {
    const { result } = renderHook(() => useUpdateRRProtocol(42), { wrapper: makeWrapper() });
    result.current.cancelInvalidation();
    expect(result.current.invalidationPending).toBeNull();
  });
});

describe('useValidateRRProtocol', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useValidateRRProtocol(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls validateProtocol with studyId', async () => {
    const { result } = renderHook(() => useValidateRRProtocol(42), { wrapper: makeWrapper() });
    result.current.mutate();
    await waitFor(() => result.current.isSuccess);
    expect(protocolApiModule.validateProtocol).toHaveBeenCalledWith(42);
  });
});
