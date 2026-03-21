/**
 * Unit tests for greyLiteratureApi.ts (feature 007).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { listGreyLiterature, addGreyLiteratureSource, deleteGreyLiteratureSource } from '../greyLiteratureApi';
import { api } from '../../api';

vi.mock('../../api', () => ({ api: { get: vi.fn(), post: vi.fn(), delete: vi.fn() } }));

const mockApi = vi.mocked(api);

const SOURCE = {
  id: 1,
  study_id: 42,
  source_type: 'dissertation',
  title: 'A dissertation',
  authors: null,
  year: 2023,
  url: null,
  description: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('listGreyLiterature', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET and parses list', async () => {
    mockApi.get.mockResolvedValue({ sources: [SOURCE] });
    const result = await listGreyLiterature(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/slr/studies/42/grey-literature');
    expect(result.sources).toHaveLength(1);
  });
});

describe('addGreyLiteratureSource', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls POST and returns new source', async () => {
    mockApi.post.mockResolvedValue(SOURCE);
    const result = await addGreyLiteratureSource(42, {
      source_type: 'dissertation',
      title: 'A dissertation',
    });
    expect(mockApi.post).toHaveBeenCalledWith('/api/v1/slr/studies/42/grey-literature', expect.any(Object));
    expect(result.source_type).toBe('dissertation');
  });
});

describe('deleteGreyLiteratureSource', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls DELETE endpoint', async () => {
    mockApi.delete.mockResolvedValue(undefined);
    await deleteGreyLiteratureSource(42, 1);
    expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/slr/studies/42/grey-literature/1');
  });
});
