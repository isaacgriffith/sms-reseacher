/**
 * Unit tests for rapid/protocolApi.ts (feature 008).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getProtocol, updateProtocol, validateProtocol, getThreats } from '../protocolApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: { get: vi.fn(), put: vi.fn(), post: vi.fn() },
}));

const mockApi = vi.mocked(api);

const PROTOCOL_FIXTURE = {
  id: 1,
  study_id: 42,
  status: 'draft' as const,
  practical_problem: 'problem',
  research_questions: ['RQ1'],
  time_budget_days: 14,
  effort_budget_hours: 40,
  context_restrictions: [],
  dissemination_medium: 'report',
  problem_scoping_notes: 'notes',
  search_strategy_notes: 'strategy',
  inclusion_criteria: ['ic'],
  exclusion_criteria: ['ec'],
  single_reviewer_mode: false,
  single_source_acknowledged: false,
  quality_appraisal_mode: 'full' as const,
  version_id: 1,
  research_gap_warnings: [],
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('getProtocol', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls GET and returns parsed protocol', async () => {
    mockApi.get.mockResolvedValue(PROTOCOL_FIXTURE);
    const result = await getProtocol(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/rapid/studies/42/protocol');
    expect(result.id).toBe(1);
  });
});

describe('updateProtocol', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls PUT without acknowledge param by default', async () => {
    mockApi.put.mockResolvedValue(PROTOCOL_FIXTURE);
    await updateProtocol(42, { practical_problem: 'up' });
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/rapid/studies/42/protocol', {
      practical_problem: 'up',
    });
  });
  it('calls PUT with acknowledge param when true', async () => {
    mockApi.put.mockResolvedValue(PROTOCOL_FIXTURE);
    await updateProtocol(42, {}, true);
    expect(mockApi.put).toHaveBeenCalledWith(
      '/api/v1/rapid/studies/42/protocol?acknowledge_invalidation=true',
      {},
    );
  });
});

describe('validateProtocol', () => {
  beforeEach(() => vi.clearAllMocks());
  it('POSTs to validate endpoint', async () => {
    mockApi.post.mockResolvedValue({ ...PROTOCOL_FIXTURE, status: 'validated' });
    const result = await validateProtocol(42);
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/rapid/studies/42/protocol/validate',
      {},
    );
    expect(result.status).toBe('validated');
  });
});

describe('getThreats', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls GET and returns threats array', async () => {
    const threats = [
      {
        id: 1,
        study_id: 42,
        threat_type: 'bias',
        description: 'd',
        source_detail: null,
        created_at: '2026-01-01T00:00:00Z',
      },
    ];
    mockApi.get.mockResolvedValue(threats);
    const result = await getThreats(42);
    expect(result).toHaveLength(1);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/rapid/studies/42/threats');
  });
});
