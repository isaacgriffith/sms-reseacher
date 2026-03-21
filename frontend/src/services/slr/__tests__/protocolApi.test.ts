/**
 * Unit tests for protocolApi.ts (feature 007).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  getProtocol,
  upsertProtocol,
  submitForReview,
  validateProtocol,
  getPhases,
} from '../protocolApi';
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
  background: 'bg',
  rationale: 'rat',
  research_questions: ['RQ1'],
  pico_population: null,
  pico_intervention: null,
  pico_comparison: null,
  pico_outcome: null,
  pico_context: null,
  search_strategy: null,
  inclusion_criteria: ['include'],
  exclusion_criteria: ['exclude'],
  data_extraction_strategy: null,
  synthesis_approach: null,
  dissemination_strategy: null,
  timetable: null,
  status: 'draft',
  review_report: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const PHASES_FIXTURE = {
  study_id: 42,
  unlocked_phases: [1],
  protocol_status: 'draft',
  quality_complete: false,
  synthesis_complete: false,
};

describe('getProtocol', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and parses the response', async () => {
    mockApi.get.mockResolvedValue(PROTOCOL_FIXTURE);
    const result = await getProtocol(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/slr/studies/42/protocol');
    expect(result.id).toBe(1);
  });
});

describe('upsertProtocol', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls PUT and parses the response', async () => {
    mockApi.put.mockResolvedValue(PROTOCOL_FIXTURE);
    const result = await upsertProtocol(42, { background: 'bg', rationale: 'rat' });
    expect(mockApi.put).toHaveBeenCalledWith(
      '/api/v1/slr/studies/42/protocol',
      { background: 'bg', rationale: 'rat' },
    );
    expect(result.status).toBe('draft');
  });
});

describe('submitForReview', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST and returns job info', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'job-1', status: 'queued' });
    const result = await submitForReview(42);
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/slr/studies/42/protocol/submit-for-review',
      {},
    );
    expect(result.job_id).toBe('job-1');
  });
});

describe('validateProtocol', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST and returns status', async () => {
    mockApi.post.mockResolvedValue({ status: 'validated' });
    const result = await validateProtocol(42);
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/slr/studies/42/protocol/validate',
      {},
    );
    expect(result.status).toBe('validated');
  });
});

describe('getPhases', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and parses phases response', async () => {
    mockApi.get.mockResolvedValue(PHASES_FIXTURE);
    const result = await getPhases(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/slr/studies/42/phases');
    expect(result.unlocked_phases).toEqual([1]);
  });
});
