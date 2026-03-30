/**
 * Unit tests for tertiary extractionApi.ts (feature 009).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { listExtractions, updateExtraction, triggerAiAssist } from '../extractionApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: {
    get: vi.fn(),
    put: vi.fn(),
    post: vi.fn(),
  },
}));

const mockApi = vi.mocked(api);

const EXTRACTION_FIXTURE = {
  id: 1,
  candidate_paper_id: 42,
  paper_title: 'A Mapping Study on TDD',
  secondary_study_type: 'SLR',
  research_questions_addressed: ['RQ1'],
  databases_searched: ['ACM DL'],
  study_period_start: 2010,
  study_period_end: 2020,
  primary_study_count: 25,
  synthesis_approach_used: 'narrative',
  key_findings: 'TDD improves quality.',
  research_gaps: 'Long-term data missing.',
  reviewer_quality_rating: 0.75,
  extraction_status: 'pending',
  extracted_by_agent: null,
  validated_by_reviewer_id: null,
  version_id: 0,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('listExtractions', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET /extractions and parses response', async () => {
    mockApi.get.mockResolvedValue([EXTRACTION_FIXTURE]);
    const result = await listExtractions(10);
    expect(mockApi.get).toHaveBeenCalledWith(
      '/api/v1/tertiary/studies/10/extractions',
    );
    expect(result).toHaveLength(1);
    expect(result[0].extraction_status).toBe('pending');
  });

  it('appends status filter when provided', async () => {
    mockApi.get.mockResolvedValue([]);
    await listExtractions(10, 'validated');
    expect(mockApi.get).toHaveBeenCalledWith(
      '/api/v1/tertiary/studies/10/extractions?status=validated',
    );
  });
});

describe('updateExtraction', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls PUT with update data and parses response', async () => {
    mockApi.put.mockResolvedValue({ ...EXTRACTION_FIXTURE, extraction_status: 'human_reviewed' });
    const result = await updateExtraction(10, 1, { extraction_status: 'human_reviewed' });
    expect(mockApi.put).toHaveBeenCalledWith(
      '/api/v1/tertiary/studies/10/extractions/1',
      { extraction_status: 'human_reviewed' },
    );
    expect(result.extraction_status).toBe('human_reviewed');
  });
});

describe('triggerAiAssist', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST /extractions/ai-assist and parses response', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'ai-job-1', status: 'queued', paper_count: 3 });
    const result = await triggerAiAssist(10);
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/tertiary/studies/10/extractions/ai-assist',
      {},
    );
    expect(result.job_id).toBe('ai-job-1');
    expect(result.paper_count).toBe(3);
  });
});
