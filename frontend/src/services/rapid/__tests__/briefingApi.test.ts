/**
 * Unit tests for briefingApi.ts (feature 008).
 *
 * Covers listBriefings, generateBriefing, getBriefing, publishBriefing,
 * exportBriefing, createShareToken, revokeShareToken, getPublicBriefing,
 * and exportPublicBriefing.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  listBriefings,
  generateBriefing,
  getBriefing,
  publishBriefing,
  exportBriefing,
  createShareToken,
  revokeShareToken,
  getPublicBriefing,
  exportPublicBriefing,
  ApiError,
} from '../briefingApi';
import { api } from '../../api';

vi.mock('../../api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    status: number;
    detail: string;
    constructor(status: number, detail: string) {
      super(detail);
      this.status = status;
      this.detail = detail;
    }
  },
}));

vi.mock('../../auth', () => ({
  getToken: vi.fn().mockReturnValue('test-token'),
}));

const mockApi = vi.mocked(api);

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const SUMMARY_FIXTURE = {
  id: 1,
  study_id: 42,
  version_number: 1,
  status: 'draft' as const,
  title: 'Test Briefing',
  generated_at: '2026-01-01T00:00:00Z',
  pdf_available: true,
  html_available: false,
};

const DETAIL_FIXTURE = {
  ...SUMMARY_FIXTURE,
  summary: 'Summary text',
  findings: { '0': 'Finding for RQ0', '1': 'Finding for RQ1' },
  target_audience: 'Practitioners',
  reference_complementary: 'See full paper',
  institution_logos: [],
};

const SHARE_TOKEN_FIXTURE = {
  token: 'abc123',
  share_url: 'https://example.com/briefings/abc123',
  briefing_id: 1,
  created_at: '2026-01-01T00:00:00Z',
  revoked_at: null,
  expires_at: null,
};

const GENERATE_RESPONSE_FIXTURE = {
  job_id: 'job-abc',
  status: 'queued',
  estimated_version_number: 2,
};

// ---------------------------------------------------------------------------
// listBriefings
// ---------------------------------------------------------------------------

describe('listBriefings', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET with the correct endpoint and returns parsed summaries', async () => {
    mockApi.get.mockResolvedValue([SUMMARY_FIXTURE]);
    const result = await listBriefings(42);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/rapid/studies/42/briefings');
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe(1);
    expect(result[0].title).toBe('Test Briefing');
  });

  it('returns an empty array when the response is empty', async () => {
    mockApi.get.mockResolvedValue([]);
    const result = await listBriefings(42);
    expect(result).toEqual([]);
  });

  it('throws when the API call rejects', async () => {
    mockApi.get.mockRejectedValue(new Error('network error'));
    await expect(listBriefings(42)).rejects.toThrow('network error');
  });
});

// ---------------------------------------------------------------------------
// generateBriefing
// ---------------------------------------------------------------------------

describe('generateBriefing', () => {
  beforeEach(() => vi.clearAllMocks());

  it('POSTs to the correct endpoint and returns parsed response', async () => {
    mockApi.post.mockResolvedValue(GENERATE_RESPONSE_FIXTURE);
    const result = await generateBriefing(42);
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/rapid/studies/42/briefings/generate',
      {},
    );
    expect(result.job_id).toBe('job-abc');
    expect(result.estimated_version_number).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// getBriefing
// ---------------------------------------------------------------------------

describe('getBriefing', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls GET with the correct endpoint and returns full detail', async () => {
    mockApi.get.mockResolvedValue(DETAIL_FIXTURE);
    const result = await getBriefing(42, 1);
    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/rapid/studies/42/briefings/1');
    expect(result.summary).toBe('Summary text');
    expect(result.findings['0']).toBe('Finding for RQ0');
  });
});

// ---------------------------------------------------------------------------
// publishBriefing
// ---------------------------------------------------------------------------

describe('publishBriefing', () => {
  beforeEach(() => vi.clearAllMocks());

  it('POSTs to the publish endpoint and returns updated briefing', async () => {
    const published = { ...DETAIL_FIXTURE, status: 'published' as const };
    mockApi.post.mockResolvedValue(published);
    const result = await publishBriefing(42, 1);
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/rapid/studies/42/briefings/1/publish',
      {},
    );
    expect(result.status).toBe('published');
  });
});

// ---------------------------------------------------------------------------
// exportBriefing (uses fetch, not api wrapper)
// ---------------------------------------------------------------------------

describe('exportBriefing', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('fetches with Authorization header and returns blob for pdf', async () => {
    const fakeBlob = new Blob(['%PDF'], { type: 'application/pdf' });
    const fakeFetch = vi.fn().mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(fakeBlob),
    });
    vi.stubGlobal('fetch', fakeFetch);

    const result = await exportBriefing(42, 1, 'pdf');
    expect(fakeFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/rapid/studies/42/briefings/1/export?format=pdf'),
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: expect.stringMatching(/^Bearer /) }) }),
    );
    expect(result).toBe(fakeBlob);
    vi.unstubAllGlobals();
  });

  it('throws ApiError when response is not ok', async () => {
    const fakeFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      statusText: 'Forbidden',
    });
    vi.stubGlobal('fetch', fakeFetch);

    await expect(exportBriefing(42, 1, 'html')).rejects.toBeInstanceOf(ApiError);
    vi.unstubAllGlobals();
  });
});

// ---------------------------------------------------------------------------
// createShareToken
// ---------------------------------------------------------------------------

describe('createShareToken', () => {
  beforeEach(() => vi.clearAllMocks());

  it('POSTs to share endpoint and returns parsed token', async () => {
    mockApi.post.mockResolvedValue(SHARE_TOKEN_FIXTURE);
    const result = await createShareToken(42, 1);
    expect(mockApi.post).toHaveBeenCalledWith(
      '/api/v1/rapid/studies/42/briefings/1/share',
      {},
    );
    expect(result.token).toBe('abc123');
    expect(result.share_url).toBe('https://example.com/briefings/abc123');
  });
});

// ---------------------------------------------------------------------------
// revokeShareToken
// ---------------------------------------------------------------------------

describe('revokeShareToken', () => {
  beforeEach(() => vi.clearAllMocks());

  it('calls DELETE on the correct revoke endpoint', async () => {
    mockApi.delete.mockResolvedValue(undefined);
    await revokeShareToken(42, 'abc123');
    expect(mockApi.delete).toHaveBeenCalledWith(
      '/api/v1/rapid/studies/42/briefings/share/abc123/revoke',
    );
  });
});

// ---------------------------------------------------------------------------
// getPublicBriefing (uses fetch, no auth)
// ---------------------------------------------------------------------------

describe('getPublicBriefing', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('fetches from public endpoint and returns parsed public briefing', async () => {
    const publicBriefing = {
      ...DETAIL_FIXTURE,
      threats: [{ threat_type: 'Selection', description: 'Bias', source_detail: null }],
    };
    const fakeFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(publicBriefing),
    });
    vi.stubGlobal('fetch', fakeFetch);

    const result = await getPublicBriefing('abc123');
    expect(fakeFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/public/briefings/abc123'),
    );
    expect(result.threats[0].threat_type).toBe('Selection');
    vi.unstubAllGlobals();
  });

  it('throws ApiError when response is not ok', async () => {
    const fakeFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
    });
    vi.stubGlobal('fetch', fakeFetch);

    await expect(getPublicBriefing('bad-token')).rejects.toBeInstanceOf(ApiError);
    vi.unstubAllGlobals();
  });
});

// ---------------------------------------------------------------------------
// exportPublicBriefing (uses fetch, no auth)
// ---------------------------------------------------------------------------

describe('exportPublicBriefing', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('fetches public export endpoint and returns blob', async () => {
    const fakeBlob = new Blob(['%PDF'], { type: 'application/pdf' });
    const fakeFetch = vi.fn().mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(fakeBlob),
    });
    vi.stubGlobal('fetch', fakeFetch);

    const result = await exportPublicBriefing('abc123', 'pdf');
    expect(fakeFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/public/briefings/abc123/export?format=pdf'),
    );
    expect(result).toBe(fakeBlob);
    vi.unstubAllGlobals();
  });

  it('throws ApiError when response is not ok for public export', async () => {
    const fakeFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 410,
      statusText: 'Gone',
    });
    vi.stubGlobal('fetch', fakeFetch);

    await expect(exportPublicBriefing('revoked-token', 'html')).rejects.toBeInstanceOf(ApiError);
    vi.unstubAllGlobals();
  });
});
