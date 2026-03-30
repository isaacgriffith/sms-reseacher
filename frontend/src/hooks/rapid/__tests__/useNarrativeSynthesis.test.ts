/**
 * Unit tests for useNarrativeSynthesis hooks (feature 008).
 *
 * Covers useNarrativeSections, useUpdateSection, useRequestAIDraft,
 * and useCompleteSynthesis.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import {
  rrSynthesisSectionsKey,
  useNarrativeSections,
  useUpdateSection,
  useRequestAIDraft,
  useCompleteSynthesis,
} from '../useNarrativeSynthesis';

vi.mock('../../../services/rapid/synthesisApi', () => ({
  listSections: vi.fn().mockRejectedValue(new Error('network')),
  updateSection: vi.fn().mockResolvedValue({ id: 1, is_complete: true }),
  requestAIDraft: vi.fn().mockResolvedValue({ job_id: 'draft-job' }),
  completeSynthesis: vi.fn().mockResolvedValue({ status: 'complete' }),
}));

import * as synthesisApiModule from '../../../services/rapid/synthesisApi';

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('rrSynthesisSectionsKey', () => {
  it('returns stable tuple', () => {
    expect(rrSynthesisSectionsKey(42)).toEqual(['rr-synthesis-sections', 42]);
  });
});

describe('useNarrativeSections', () => {
  it('returns a query result object', async () => {
    const { result } = renderHook(() => useNarrativeSections(42), { wrapper: makeWrapper() });
    await waitFor(() => !result.current.isLoading);
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when studyId is 0', () => {
    const { result } = renderHook(() => useNarrativeSections(0), { wrapper: makeWrapper() });
    expect(result.current.fetchStatus).toBe('idle');
  });

  it('succeeds and data is accessible when API resolves', async () => {
    vi.mocked(synthesisApiModule.listSections).mockResolvedValue([
      { id: 1, study_id: 42, rq_index: 0, rq_text: 'RQ1', narrative_text: null, is_complete: false, ai_draft_job_id: null, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
    ]);
    const { result } = renderHook(() => useNarrativeSections(42), { wrapper: makeWrapper() });
    await waitFor(() => { if (!result.current.isSuccess) throw new Error('not ready'); });
    expect(result.current.data?.[0].rq_index).toBe(0);
  });
});

describe('useUpdateSection', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useUpdateSection(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls updateSection with studyId, sectionId, and data', async () => {
    const { result } = renderHook(() => useUpdateSection(42), { wrapper: makeWrapper() });
    result.current.mutate({ sectionId: 1, data: { narrative_text: 'text', is_complete: true } });
    await waitFor(() => result.current.isSuccess);
    expect(synthesisApiModule.updateSection).toHaveBeenCalledWith(42, 1, { narrative_text: 'text', is_complete: true });
  });
});

describe('useRequestAIDraft', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useRequestAIDraft(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls requestAIDraft with studyId and sectionId', async () => {
    const { result } = renderHook(() => useRequestAIDraft(42), { wrapper: makeWrapper() });
    result.current.mutate(1);
    await waitFor(() => result.current.isSuccess);
    expect(synthesisApiModule.requestAIDraft).toHaveBeenCalledWith(42, 1);
  });
});

describe('useCompleteSynthesis', () => {
  it('returns a mutation object with mutate function', () => {
    const { result } = renderHook(() => useCompleteSynthesis(42), { wrapper: makeWrapper() });
    expect(typeof result.current.mutate).toBe('function');
  });

  it('calls completeSynthesis with studyId', async () => {
    const { result } = renderHook(() => useCompleteSynthesis(42), { wrapper: makeWrapper() });
    result.current.mutate();
    await waitFor(() => result.current.isSuccess);
    expect(synthesisApiModule.completeSynthesis).toHaveBeenCalledWith(42);
  });
});
