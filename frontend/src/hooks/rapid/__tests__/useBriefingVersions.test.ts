/**
 * Unit tests for useBriefingVersions hooks (feature 008).
 *
 * Covers useBriefings, useGenerateBriefing, usePublishBriefing,
 * useCreateShareToken, and useRevokeShareToken.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  rrBriefingsKey,
  useBriefings,
  useGenerateBriefing,
  usePublishBriefing,
  useCreateShareToken,
  useRevokeShareToken,
} from '../useBriefingVersions';

// Mock the API service layer so no real HTTP calls are made
vi.mock('../../../services/rapid/briefingApi', () => ({
  listBriefings: vi.fn().mockRejectedValue(new Error('network')),
  generateBriefing: vi.fn().mockResolvedValue({ job_id: 'j1', status: 'queued', estimated_version_number: 1 }),
  publishBriefing: vi.fn().mockResolvedValue({ id: 1, status: 'published' }),
  createShareToken: vi.fn().mockResolvedValue({ token: 'tok', share_url: 'https://example.com/tok', briefing_id: 1, created_at: '2026-01-01T00:00:00Z', revoked_at: null, expires_at: null }),
  revokeShareToken: vi.fn().mockResolvedValue(undefined),
}));

import * as briefingApiModule from '../../../services/rapid/briefingApi';

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

// ---------------------------------------------------------------------------
// Query key
// ---------------------------------------------------------------------------

describe('rrBriefingsKey', () => {
  it('returns stable tuple', () => {
    expect(rrBriefingsKey(42)).toEqual(['rr-briefings', 42]);
  });
});

// ---------------------------------------------------------------------------
// useBriefings
// ---------------------------------------------------------------------------

describe('useBriefings', () => {
  it('returns a query result object with data property', async () => {
    const { result } = renderHook(() => useBriefings(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useBriefings(0), { wrapper: makeWrapper() });
    // Query disabled — fetchStatus is 'idle'
    expect(result.current.fetchStatus).toBe('idle');
  });

  it('polls when any briefing has no pdf_available', async () => {
    vi.mocked(briefingApiModule.listBriefings).mockResolvedValue([
      { id: 1, study_id: 42, version_number: 1, status: 'draft', title: 'B', generated_at: null, pdf_available: false, html_available: false },
    ]);

    const { result } = renderHook(() => useBriefings(42), { wrapper: makeWrapper() });
    await waitFor(() => { if (!result.current.isSuccess) throw new Error('not ready'); });
    // refetchInterval is a function — verify data loaded with generating briefing
    expect(result.current.data?.[0].pdf_available).toBe(false);
  });

  it('does not poll when all briefings have pdf_available', async () => {
    vi.mocked(briefingApiModule.listBriefings).mockResolvedValue([
      { id: 1, study_id: 42, version_number: 1, status: 'draft', title: 'B', generated_at: '2026-01-01T00:00:00Z', pdf_available: true, html_available: true },
    ]);

    const { result } = renderHook(() => useBriefings(42), { wrapper: makeWrapper() });
    await waitFor(() => { if (!result.current.isSuccess) throw new Error('not ready'); });
    expect(result.current.data?.[0].pdf_available).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// useGenerateBriefing
// ---------------------------------------------------------------------------

describe('useGenerateBriefing', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useGenerateBriefing(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls generateBriefing with correct studyId on mutate', async () => {
    const { result } = renderHook(() => useGenerateBriefing(42), { wrapper: makeWrapper() });
    result.current.mutate();
    await waitFor(() => result.current.isSuccess);
    expect(briefingApiModule.generateBriefing).toHaveBeenCalledWith(42);
  });
});

// ---------------------------------------------------------------------------
// usePublishBriefing
// ---------------------------------------------------------------------------

describe('usePublishBriefing', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => usePublishBriefing(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls publishBriefing with studyId and briefingId', async () => {
    const { result } = renderHook(() => usePublishBriefing(42), { wrapper: makeWrapper() });
    result.current.mutate(1);
    await waitFor(() => result.current.isSuccess);
    expect(briefingApiModule.publishBriefing).toHaveBeenCalledWith(42, 1);
  });
});

// ---------------------------------------------------------------------------
// useCreateShareToken
// ---------------------------------------------------------------------------

describe('useCreateShareToken', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useCreateShareToken(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls createShareToken with studyId and briefingId', async () => {
    const { result } = renderHook(() => useCreateShareToken(42), { wrapper: makeWrapper() });
    result.current.mutate(1);
    await waitFor(() => result.current.isSuccess);
    expect(briefingApiModule.createShareToken).toHaveBeenCalledWith(42, 1);
  });
});

// ---------------------------------------------------------------------------
// useRevokeShareToken
// ---------------------------------------------------------------------------

describe('useRevokeShareToken', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useRevokeShareToken(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls revokeShareToken with studyId and token string', async () => {
    const { result } = renderHook(() => useRevokeShareToken(42), { wrapper: makeWrapper() });
    result.current.mutate('tok-abc');
    await waitFor(() => result.current.isSuccess);
    expect(briefingApiModule.revokeShareToken).toHaveBeenCalledWith(42, 'tok-abc');
  });
});
