/**
 * Unit tests for rapid/searchConfigApi.ts (feature 008).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { updateSearchConfig } from '../searchConfigApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: { put: vi.fn() },
}));

const mockApi = vi.mocked(api);

describe('updateSearchConfig', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls PUT and returns threats', async () => {
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
    mockApi.put.mockResolvedValue(threats);
    const result = await updateSearchConfig(42, { restrictions: [], single_reviewer_mode: true });
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/rapid/studies/42/search-config', {
      restrictions: [],
      single_reviewer_mode: true,
    });
    expect(result).toHaveLength(1);
  });

  it('handles empty response', async () => {
    mockApi.put.mockResolvedValue([]);
    const result = await updateSearchConfig(42, { restrictions: [] });
    expect(result).toEqual([]);
  });
});
