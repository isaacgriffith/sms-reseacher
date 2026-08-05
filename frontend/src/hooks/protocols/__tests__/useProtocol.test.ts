import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  protocolListKey,
  protocolDetailKey,
  protocolAssignmentKey,
  useProtocolList,
  useProtocolDetail,
  useProtocolAssignment,
  useCopyProtocol,
  useCreateProtocol,
  useUpdateProtocol,
  useDeleteProtocol,
  useImportProtocol,
  useResetProtocol,
  useAssignProtocol,
} from '../useProtocol';

vi.mock('../../../services/protocols/protocolsApi', () => ({
  listProtocols: vi.fn().mockResolvedValue([]),
  getProtocol: vi.fn().mockResolvedValue({ id: 1, name: 'Test' }),
  getProtocolAssignment: vi.fn().mockResolvedValue(null),
  copyProtocol: vi.fn().mockResolvedValue({ id: 2, name: 'Copy' }),
  createProtocol: vi.fn().mockResolvedValue({ id: 3, name: 'New' }),
  updateProtocol: vi.fn().mockResolvedValue({ id: 1, name: 'Updated' }),
  deleteProtocol: vi.fn().mockResolvedValue(undefined),
  importProtocol: vi.fn().mockResolvedValue({ id: 4, name: 'Imported' }),
  resetProtocol: vi.fn().mockResolvedValue(undefined),
  assignProtocol: vi.fn().mockResolvedValue(undefined),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useProtocol hooks', () => {
  beforeEach(() => vi.clearAllMocks());

  it('protocolListKey returns correct key', () => {
    expect(protocolListKey()).toEqual(['protocols', undefined]);
    expect(protocolListKey('sms')).toEqual(['protocols', 'sms']);
  });

  it('protocolDetailKey returns correct key', () => {
    expect(protocolDetailKey(5)).toEqual(['protocol', 5]);
  });

  it('protocolAssignmentKey returns correct key', () => {
    expect(protocolAssignmentKey(3)).toEqual(['protocol-assignment', 3]);
  });

  it('useProtocolList fetches data', async () => {
    const { result } = renderHook(() => useProtocolList(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.data).toEqual([]);
  });

  it('useProtocolDetail fetches data', async () => {
    const { result } = renderHook(() => useProtocolDetail(1), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
  });

  it('useProtocolAssignment fetches data', async () => {
    const { result } = renderHook(() => useProtocolAssignment(1), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isLoading).toBe(false));
  });

  it('useCopyProtocol executes mutation', async () => {
    const { result } = renderHook(() => useCopyProtocol(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ name: 'Copy', copy_from_protocol_id: 1 });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('useCreateProtocol executes mutation', async () => {
    const { result } = renderHook(() => useCreateProtocol(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ name: 'New', study_type: 'sms', nodes: [], edges: [] });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('useUpdateProtocol executes mutation', async () => {
    const { result } = renderHook(() => useUpdateProtocol(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ id: 1, version_id: 1, name: 'Updated', nodes: [], edges: [] });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('useDeleteProtocol executes mutation', async () => {
    const { result } = renderHook(() => useDeleteProtocol(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate(1);
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('useImportProtocol executes mutation', async () => {
    const { result } = renderHook(() => useImportProtocol(), { wrapper: makeWrapper() });
    const file = new File(['test'], 'test.yaml', { type: 'text/yaml' });
    await act(async () => {
      result.current.mutate(file);
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('useResetProtocol executes mutation', async () => {
    const { result } = renderHook(() => useResetProtocol(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate(1);
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('useAssignProtocol executes mutation', async () => {
    const { result } = renderHook(() => useAssignProtocol(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ studyId: 1, protocolId: 2 });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
