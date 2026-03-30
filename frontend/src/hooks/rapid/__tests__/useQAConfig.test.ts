/**
 * Unit tests for useQAConfig hooks (feature 008).
 *
 * Covers rrQualityConfigKey, useQualityConfig, and useSetQAMode.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { rrQualityConfigKey, useQualityConfig, useSetQAMode } from '../useQAConfig';

vi.mock('../../../services/rapid/qualityApi', () => ({
  getQualityConfig: vi.fn().mockRejectedValue(new Error('network')),
  setQualityConfig: vi.fn().mockResolvedValue({
    mode: 'full',
    threats: [],
  }),
}));

vi.mock('../useRRProtocol', () => ({
  rrThreatsKey: vi.fn((studyId: number) => ['rr-threats', studyId]),
}));

import * as qualityApiModule from '../../../services/rapid/qualityApi';

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('rrQualityConfigKey', () => {
  it('returns stable tuple', () => {
    expect(rrQualityConfigKey(42)).toEqual(['rr-quality-config', 42]);
  });
});

describe('useQualityConfig', () => {
  it('returns a query result with data property', async () => {
    const { result } = renderHook(() => useQualityConfig(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useQualityConfig(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });

  it('fetches config when studyId > 0', async () => {
    vi.mocked(qualityApiModule.getQualityConfig).mockResolvedValue({ mode: 'full', threats: [] });
    const { result } = renderHook(() => useQualityConfig(42), { wrapper: makeWrapper() });
    await waitFor(() => { if (!result.current.isSuccess) throw new Error('not ready'); });
    expect(result.current.data?.mode).toBe('full');
  });
});

describe('useSetQAMode', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useSetQAMode(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls setQualityConfig with studyId and mode', async () => {
    const { result } = renderHook(() => useSetQAMode(42), { wrapper: makeWrapper() });
    result.current.mutate({ mode: 'skipped' });
    await waitFor(() => result.current.isSuccess);
    expect(qualityApiModule.setQualityConfig).toHaveBeenCalledWith(42, 'skipped');
  });
});
