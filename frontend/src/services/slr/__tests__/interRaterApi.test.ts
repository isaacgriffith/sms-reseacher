/**
 * Unit tests for interRaterApi.ts (feature 007).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getInterRaterRecords, computeKappa, recordPostDiscussionKappa } from '../interRaterApi';
import { api } from '../../api';

vi.mock('../../api', () => ({ api: { get: vi.fn(), post: vi.fn() } }));

const mockApi = vi.mocked(api);

const RECORD = {
  id: 1,
  study_id: 42,
  reviewer_a_id: 3,
  reviewer_b_id: 4,
  round_type: 'title_abstract',
  phase: 'pre_discussion',
  kappa_value: 0.75,
  kappa_undefined_reason: null,
  n_papers: 10,
  threshold_met: true,
  created_at: '2026-01-01T00:00:00Z',
};

describe('getInterRaterRecords', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and returns parsed list', async () => {
    mockApi.get.mockResolvedValue({ records: [RECORD] });
    const result = await getInterRaterRecords(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/slr/studies/42/inter-rater');
    expect(result.records).toHaveLength(1);
  });
});

describe('computeKappa', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST and returns a parsed record', async () => {
    mockApi.post.mockResolvedValue(RECORD);
    const result = await computeKappa(42, { reviewer_a_id: 3, reviewer_b_id: 4, round_type: 'title_abstract' });
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/slr/studies/42/inter-rater/compute',
      { reviewer_a_id: 3, reviewer_b_id: 4, round_type: 'title_abstract' },
    );
    expect(result.kappa_value).toBe(0.75);
  });
});

describe('recordPostDiscussionKappa', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST to post-discussion endpoint', async () => {
    mockApi.post.mockResolvedValue({ ...RECORD, phase: 'post_discussion' });
    const result = await recordPostDiscussionKappa(42, { reviewer_a_id: 3, reviewer_b_id: 4, round_type: 'title_abstract' });
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/slr/studies/42/inter-rater/post-discussion',
      expect.any(Object),
    );
    expect(result.phase).toBe('post_discussion');
  });
});
