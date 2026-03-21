/**
 * Unit tests for qualityApi.ts (feature 007).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getChecklist, upsertChecklist, getQualityScores, submitQualityScores } from '../qualityApi';
import { api } from '../../api';

vi.mock('../../api', () => ({ api: { get: vi.fn(), put: vi.fn(), post: vi.fn() } }));

const mockApi = vi.mocked(api);

const CHECKLIST = {
  id: 1,
  study_id: 42,
  name: 'Standard QA',
  description: null,
  items: [
    { id: 1, order: 1, question: 'Q1', scoring_method: 'binary', weight: 1.0 },
  ],
};

const QUALITY_SCORES = {
  candidate_paper_id: 7,
  reviewer_scores: [
    {
      reviewer_id: 3,
      items: [{ checklist_item_id: 1, score_value: 1.0, notes: null }],
      aggregate_quality_score: 1.0,
    },
  ],
};

describe('getChecklist', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and returns parsed checklist', async () => {
    mockApi.get.mockResolvedValue(CHECKLIST);
    const result = await getChecklist(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/slr/studies/42/quality-checklist');
    expect(result.name).toBe('Standard QA');
  });
});

describe('upsertChecklist', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls PUT and returns updated checklist', async () => {
    mockApi.put.mockResolvedValue(CHECKLIST);
    const result = await upsertChecklist(42, {
      name: 'Standard QA',
      description: null,
      items: [{ question: 'Q1', scoring_method: 'binary', weight: 1.0, order: 1 }],
    });
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/slr/studies/42/quality-checklist', expect.any(Object));
    expect(result.name).toBe('Standard QA');
  });
});

describe('getQualityScores', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and returns parsed scores', async () => {
    mockApi.get.mockResolvedValue(QUALITY_SCORES);
    const result = await getQualityScores(7);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/slr/papers/7/quality-scores');
    expect(result.candidate_paper_id).toBe(7);
  });
});

describe('submitQualityScores', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls PUT and returns scores', async () => {
    mockApi.put.mockResolvedValue(QUALITY_SCORES);
    const result = await submitQualityScores(7, {
      reviewer_id: 3,
      scores: [{ checklist_item_id: 1, score_value: 1.0, notes: null }],
    });
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/slr/papers/7/quality-scores', expect.any(Object));
    expect(result.candidate_paper_id).toBe(7);
  });
});
