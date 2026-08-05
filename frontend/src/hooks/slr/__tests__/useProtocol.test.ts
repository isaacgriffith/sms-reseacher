import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
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

vi.mock('../../../services/slr/protocolApi', () => ({
  getProtocol: vi.fn().mockResolvedValue({ id: 1, status: 'draft' }),
  getPhases: vi.fn().mockResolvedValue({ unlocked: [1, 2] }),
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
  it('fetches protocol data', async () => {
    const { result } = renderHook(() => useProtocol(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
  });
});

describe('usePhases', () => {
  it('fetches phases data', async () => {
    const { result } = renderHook(() => usePhases(42), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
  });
});

describe('useUpsertProtocol', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useUpsertProtocol(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ background: 'Updated background' });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useSubmitForReview', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useSubmitForReview(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate();
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useValidateProtocol', () => {
  it('executes mutation', async () => {
    const { result } = renderHook(() => useValidateProtocol(42), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate();
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
