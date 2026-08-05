/**
 * Unit tests for rapid/qualityApi.ts (feature 008).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getQualityConfig, setQualityConfig } from '../qualityApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: { get: vi.fn(), put: vi.fn() },
}));

const mockApi = vi.mocked(api);

const CONFIG_FIXTURE = {
  quality_appraisal_mode: 'full' as const,
  threats: [],
};

describe('getQualityConfig', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls GET and returns parsed config', async () => {
    mockApi.get.mockResolvedValue(CONFIG_FIXTURE);
    const result = await getQualityConfig(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/rapid/studies/42/quality-config');
    expect(result.quality_appraisal_mode).toBe('full');
  });
});

describe('setQualityConfig', () => {
  beforeEach(() => vi.clearAllMocks());
  it('calls PUT with mode payload', async () => {
    mockApi.put.mockResolvedValue({ ...CONFIG_FIXTURE, quality_appraisal_mode: 'skipped' });
    const result = await setQualityConfig(42, 'skipped');
    expect(mockApi.put).toHaveBeenCalledWith('/api/v1/rapid/studies/42/quality-config', {
      mode: 'skipped',
    });
    expect(result.quality_appraisal_mode).toBe('skipped');
  });
});
