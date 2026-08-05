/**
 * Unit tests for rapid/synthesisApi.ts (feature 008).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { listSections, updateSection, requestAIDraft, completeSynthesis } from '../synthesisApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: { get: vi.fn(), put: vi.fn(), post: vi.fn() },
  ApiError: class extends Error {},
}));

const mockApi = vi.mocked(api);

const SECTION_FIXTURE = {
  id: 1,
  study_id: 42,
  rq_index: 0,
  research_question: 'RQ1',
  narrative_text: null,
  ai_draft_text: null,
  is_complete: false,
  ai_draft_job_id: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('listSections', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls GET and returns sections', async () => {
    mockApi.get.mockResolvedValue([SECTION_FIXTURE]);
    const result = await listSections(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/rapid/studies/42/synthesis');
    expect(result).toHaveLength(1);
  });
});

describe('updateSection', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls PUT with data', async () => {
    mockApi.put.mockResolvedValue({ ...SECTION_FIXTURE, narrative_text: 'text' });
    const result = await updateSection(42, 1, { narrative_text: 'text' });
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/rapid/studies/42/synthesis/1', { narrative_text: 'text' });
    expect(result.narrative_text).toBe('text');
  });
});

describe('requestAIDraft', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls POST and returns job info', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'j1', section_id: 1, status: 'enqueued' });
    const result = await requestAIDraft(42, 1);
    expect(mockApi.post).toHaveBeenCalledWith('/api/v1/rapid/studies/42/synthesis/1/ai-draft', {});
    expect(result.job_id).toBe('j1');
  });
});

describe('completeSynthesis', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls POST and returns completion status', async () => {
    mockApi.post.mockResolvedValue({ synthesis_complete: true });
    const result = await completeSynthesis(42);
    expect(mockApi.post).toHaveBeenCalledWith('/api/v1/rapid/studies/42/synthesis/complete', {});
    expect(result.synthesis_complete).toBe(true);
  });
});
