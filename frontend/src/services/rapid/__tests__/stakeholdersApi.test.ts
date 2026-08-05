/**
 * Unit tests for rapid/stakeholdersApi.ts (feature 008).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  listStakeholders,
  createStakeholder,
  updateStakeholder,
  deleteStakeholder,
} from '../stakeholdersApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() },
}));

const mockApi = vi.mocked(api);

const SH_FIXTURE = {
  id: 1,
  study_id: 42,
  name: 'Alice',
  role_title: 'PM',
  organisation: 'Acme',
  involvement_type: 'advisor' as const,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('listStakeholders', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('calls GET and returns list', async () => {
    mockApi.get.mockResolvedValue([SH_FIXTURE]);
    const result = await listStakeholders(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/rapid/studies/42/stakeholders');
    expect(result).toHaveLength(1);
  });
});

describe('createStakeholder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('calls POST with data', async () => {
    mockApi.post.mockResolvedValue(SH_FIXTURE);
    const data = {
      name: 'Alice',
      role_title: 'PM',
      organisation: 'Acme',
      involvement_type: 'advisor' as const,
    };
    const result = await createStakeholder(42, data);
    expect(mockApi.post).toHaveBeenCalledWith('/api/v1/rapid/studies/42/stakeholders', data);
    expect(result.name).toBe('Alice');
  });
});

describe('updateStakeholder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('calls PUT with data', async () => {
    mockApi.put.mockResolvedValue({ ...SH_FIXTURE, name: 'Bob' });
    const result = await updateStakeholder(42, 1, { name: 'Bob' });
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/rapid/studies/42/stakeholders/1', {
      name: 'Bob',
    });
    expect(result.name).toBe('Bob');
  });
});

describe('deleteStakeholder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('calls DELETE', async () => {
    mockApi.delete.mockResolvedValue(undefined);
    await deleteStakeholder(42, 1);
    expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/rapid/studies/42/stakeholders/1');
  });
});
