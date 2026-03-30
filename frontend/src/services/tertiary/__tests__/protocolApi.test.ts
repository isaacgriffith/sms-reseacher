/**
 * Unit tests for tertiary protocolApi.ts (feature 009).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getProtocol, updateProtocol, validateProtocol } from '../protocolApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: {
    get: vi.fn(),
    put: vi.fn(),
    post: vi.fn(),
  },
}));

const mockApi = vi.mocked(api);

const PROTOCOL_FIXTURE = {
  id: 1,
  study_id: 42,
  status: 'draft',
  background: 'Background text',
  research_questions: ['RQ1'],
  secondary_study_types: ['SLR'],
  inclusion_criteria: ['IC1'],
  exclusion_criteria: ['EC1'],
  recency_cutoff_year: 2015,
  search_strategy: 'strategy',
  quality_threshold: 0.6,
  synthesis_approach: 'narrative',
  dissemination_strategy: 'publish',
  version_id: 0,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('getProtocol', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET /api/v1/tertiary/studies/{id}/protocol', async () => {
    mockApi.get.mockResolvedValue(PROTOCOL_FIXTURE);
    const result = await getProtocol(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/tertiary/studies/42/protocol');
    expect(result.id).toBe(1);
    expect(result.status).toBe('draft');
  });
});

describe('updateProtocol', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls PUT /api/v1/tertiary/studies/{id}/protocol with data', async () => {
    mockApi.put.mockResolvedValue({ ...PROTOCOL_FIXTURE, background: 'updated' });
    const result = await updateProtocol(42, { background: 'updated' });
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/tertiary/studies/42/protocol', {
      background: 'updated',
    });
    expect(result.background).toBe('updated');
  });
});

describe('validateProtocol', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST /api/v1/tertiary/studies/{id}/protocol/validate', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'job-abc', status: 'queued' });
    const result = await validateProtocol(42);
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/tertiary/studies/42/protocol/validate',
      {},
    );
    expect(result.job_id).toBe('job-abc');
    expect(result.status).toBe('queued');
  });
});
