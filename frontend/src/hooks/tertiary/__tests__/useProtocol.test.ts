import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  tertiaryProtocolKey,
  useTertiaryProtocol,
  useUpdateTertiaryProtocol,
  useValidateTertiaryProtocol,
} from '../useProtocol';

vi.mock('../../../services/tertiary/protocolApi', () => ({
  getProtocol: vi.fn().mockResolvedValue({ id: 1, status: 'draft' }),
  updateProtocol: vi.fn().mockResolvedValue({ id: 1, status: 'draft' }),
  validateProtocol: vi.fn().mockResolvedValue({ status: 'validated' }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('tertiaryProtocolKey', () => {
  it('returns stable array', () => {
    expect(tertiaryProtocolKey(42)).toEqual(['tertiary-protocol', 42]);
  });
});

describe('useTertiaryProtocol', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => useTertiaryProtocol(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useTertiaryProtocol(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useUpdateTertiaryProtocol', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useUpdateTertiaryProtocol(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ status: 'draft' });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useValidateTertiaryProtocol', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useValidateTertiaryProtocol(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate();
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
