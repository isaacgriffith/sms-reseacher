import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useExecutionState, useCompleteTask, useApproveTask } from '../useExecutionState';

vi.mock('../../../services/protocols/protocolsApi', () => ({
  getExecutionState: vi.fn().mockResolvedValue({ tasks: [{ status: 'active', task_id: 't1' }] }),
  completeTask: vi.fn().mockResolvedValue({ success: true }),
  approveTask: vi.fn().mockResolvedValue({ success: true }),
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useExecutionState hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('useExecutionState fetches data', async () => {
    const { result } = renderHook(() => useExecutionState(1), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.data?.tasks).toHaveLength(1);
  });

  it('useExecutionState disabled when studyId is 0', () => {
    const { result } = renderHook(() => useExecutionState(0), { wrapper: makeWrapper() });
    expect(result.current.data).toBeUndefined();
  });

  it('useCompleteTask executes mutation', async () => {
    const { result } = renderHook(() => useCompleteTask(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ studyId: 1, taskId: 't1' });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('useApproveTask executes mutation', async () => {
    const { result } = renderHook(() => useApproveTask(), { wrapper: makeWrapper() });
    await act(async () => {
      result.current.mutate({ studyId: 1, taskId: 't1' });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
