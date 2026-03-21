/**
 * Unit tests for synthesisApi.ts (feature 007).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { listSynthesisResults, startSynthesis, getSynthesisResult } from '../synthesisApi';
import { api } from '../../api';

vi.mock('../../api', () => ({ api: { get: vi.fn(), post: vi.fn() } }));

const mockApi = vi.mocked(api);

const RESULT = {
  id: 1,
  study_id: 42,
  approach: 'descriptive',
  status: 'completed',
  model_type: null,
  parameters: null,
  computed_statistics: null,
  forest_plot_svg: null,
  funnel_plot_svg: null,
  qualitative_themes: null,
  sensitivity_analysis: null,
  error_message: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('listSynthesisResults', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and parses list response', async () => {
    mockApi.get.mockResolvedValue({ results: [RESULT] });
    const result = await listSynthesisResults(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/slr/studies/42/synthesis');
    expect(result.results).toHaveLength(1);
  });
});

describe('startSynthesis', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST and returns a synthesis result', async () => {
    mockApi.post.mockResolvedValue({ ...RESULT, status: 'pending' });
    const result = await startSynthesis(42, { approach: 'descriptive', parameters: {} });
    expect(mockApi.post).toHaveBeenCalledWith('/api/v1/slr/studies/42/synthesis', expect.any(Object));
    expect(result.status).toBe('pending');
  });
});

describe('getSynthesisResult', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and parses individual result', async () => {
    mockApi.get.mockResolvedValue(RESULT);
    const result = await getSynthesisResult(1);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/slr/synthesis/1');
    expect(result.id).toBe(1);
  });
});
