/**
 * Unit tests for agentsApi.ts hooks and query functions.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useAgents, useAgent, useAgentTaskTypes } from '../agentsApi';
import { api } from '../api';

vi.mock('../api', () => ({ api: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() } }));

const mockApi = vi.mocked(api);

const AGENT_SUMMARY = {
  id: '00000000-0000-0000-0000-000000000001',
  task_type: 'screener',
  role_name: 'Reviewer',
  persona_name: 'Alice',
  model_id: '00000000-0000-0000-0000-000000000002',
  provider_id: '00000000-0000-0000-0000-000000000003',
  model_display_name: 'GPT-4',
  provider_display_name: 'OpenAI',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const AGENT_FULL = {
  ...AGENT_SUMMARY,
  role_description: 'Reviews papers.',
  persona_description: 'A diligent reviewer.',
  persona_svg: null,
  system_message_template: 'You are a reviewer.',
  system_message_undo_buffer: null,
  version_id: 1,
};

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('useAgents', () => {
  beforeEach(() => vi.clearAllMocks());

  it('fetches agents without params', async () => {
    mockApi.get.mockResolvedValue([AGENT_SUMMARY]);
    const { result } = renderHook(() => useAgents(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/agents');
    expect(result.current.data).toHaveLength(1);
  });

  it('includes task_type query param when provided', async () => {
    mockApi.get.mockResolvedValue([AGENT_SUMMARY]);
    const { result } = renderHook(() => useAgents({ task_type: 'screener' }), {
      wrapper: makeWrapper(),
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/agents?task_type=screener');
  });

  it('includes is_active query param when provided', async () => {
    mockApi.get.mockResolvedValue([AGENT_SUMMARY]);
    const { result } = renderHook(() => useAgents({ is_active: false }), {
      wrapper: makeWrapper(),
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/agents?is_active=false');
  });
});

describe('useAgent', () => {
  beforeEach(() => vi.clearAllMocks());

  it('fetches agent when id is provided', async () => {
    mockApi.get.mockResolvedValue(AGENT_FULL);
    const { result } = renderHook(
      () => useAgent('00000000-0000-0000-0000-000000000001'),
      { wrapper: makeWrapper() },
    );
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.id).toBe('00000000-0000-0000-0000-000000000001');
  });

  it('is disabled when id is null', () => {
    const { result } = renderHook(() => useAgent(null), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
    expect(mockApi.get).not.toHaveBeenCalled();
  });
});

describe('useAgentTaskTypes', () => {
  beforeEach(() => vi.clearAllMocks());

  it('fetches task types', async () => {
    mockApi.get.mockResolvedValue(['screener', 'extractor']);
    const { result } = renderHook(() => useAgentTaskTypes(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(['screener', 'extractor']);
  });
});
