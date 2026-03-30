/**
 * Unit tests for tertiary seedImportApi.ts (feature 009).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { listSeedImports, createSeedImport, listGroupStudies } from '../seedImportApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockApi = vi.mocked(api);

const IMPORT_FIXTURE = {
  id: 1,
  target_study_id: 10,
  source_study_id: 5,
  source_study_title: 'Source SLR',
  source_study_type: 'SLR',
  imported_at: '2026-01-15T12:00:00Z',
  records_added: 7,
  records_skipped: 2,
  imported_by_user_id: null,
};

const STUDY_FIXTURE = {
  id: 5,
  name: 'Source SLR Study',
  topic: 'TDD',
  study_type: 'SLR',
  status: 'active',
  current_phase: 3,
  created_at: '2026-01-01T00:00:00Z',
};

describe('listSeedImports', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and parses the seed import list', async () => {
    mockApi.get.mockResolvedValue([IMPORT_FIXTURE]);
    const result = await listSeedImports(10);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/tertiary/studies/10/seed-imports');
    expect(result).toHaveLength(1);
    expect(result[0].records_added).toBe(7);
  });
});

describe('createSeedImport', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST with source_study_id and parses the response', async () => {
    mockApi.post.mockResolvedValue({
      id: 2,
      records_added: 5,
      records_skipped: 0,
      imported_at: '2026-01-20T00:00:00Z',
    });
    const result = await createSeedImport(10, 5);
    expect(mockApi.post).toHaveBeenCalledWith('/api/v1/tertiary/studies/10/seed-imports', {
      source_study_id: 5,
    });
    expect(result.records_added).toBe(5);
  });
});

describe('listGroupStudies', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET /api/v1/groups/{id}/studies and parses studies', async () => {
    mockApi.get.mockResolvedValue([STUDY_FIXTURE]);
    const result = await listGroupStudies(3);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/groups/3/studies');
    expect(result).toHaveLength(1);
    expect(result[0].study_type).toBe('SLR');
  });
});
