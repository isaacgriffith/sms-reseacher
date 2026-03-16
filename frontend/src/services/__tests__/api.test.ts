/**
 * Tests for the api service module.
 *
 * Uses vi.stubGlobal to mock the fetch API.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api, ApiError } from '../api';

/**
 * Creates a mock Response object.
 *
 * @param status - HTTP status code.
 * @param body - Response body object.
 * @returns A mock Response.
 */
function mockResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    json: () => Promise.resolve(body),
    headers: new Headers(),
  } as unknown as Response;
}

describe('api service', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
    localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('api.get makes a GET request and returns JSON', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, { id: 1, name: 'Test' }));
    const result = await api.get<{ id: number; name: string }>('/api/v1/test');
    expect(result.name).toBe('Test');
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/test'),
      expect.objectContaining({ method: 'GET' }),
    );
  });

  it('api.post makes a POST request with JSON body', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(201, { id: 1 }));
    await api.post('/api/v1/items', { name: 'New Item' });
    const call = vi.mocked(fetch).mock.calls[0];
    expect(call[1]?.method).toBe('POST');
    expect(call[1]?.body).toBe(JSON.stringify({ name: 'New Item' }));
  });

  it('api.put makes a PUT request', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, {}));
    await api.put('/api/v1/items/1', { name: 'Updated' });
    expect(vi.mocked(fetch).mock.calls[0][1]?.method).toBe('PUT');
  });

  it('api.patch makes a PATCH request', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, {}));
    await api.patch('/api/v1/items/1', { status: 'active' });
    expect(vi.mocked(fetch).mock.calls[0][1]?.method).toBe('PATCH');
  });

  it('api.delete makes a DELETE request', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, {}));
    await api.delete('/api/v1/items/1');
    expect(vi.mocked(fetch).mock.calls[0][1]?.method).toBe('DELETE');
  });

  it('throws ApiError on non-ok response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(404, { detail: 'Not found' }));
    await expect(api.get('/api/v1/missing')).rejects.toThrow(ApiError);
  });

  it('ApiError has correct status and detail', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(403, { detail: 'Forbidden' }));
    try {
      await api.get('/api/v1/secret');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect((err as ApiError).status).toBe(403);
      expect((err as ApiError).detail).toBe('Forbidden');
    }
  });

  it('returns undefined for 204 No Content', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      status: 204,
      statusText: 'No Content',
      json: () => Promise.resolve(null),
    } as unknown as Response);
    const result = await api.delete('/api/v1/items/1');
    expect(result).toBeUndefined();
  });

  it('includes Authorization header when token is in localStorage', async () => {
    localStorage.setItem('sms-auth-token', 'test-jwt-token');
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, {}));
    await api.get('/api/v1/protected');
    const headers = vi.mocked(fetch).mock.calls[0][1]?.headers as Record<string, string>;
    expect(headers['Authorization']).toBe('Bearer test-jwt-token');
  });

  it('does not include Authorization header when no token', async () => {
    localStorage.removeItem('sms-auth-token');
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, {}));
    await api.get('/api/v1/public');
    const headers = vi.mocked(fetch).mock.calls[0][1]?.headers as Record<string, string>;
    expect(headers['Authorization']).toBeUndefined();
  });

  it('falls back to statusText when response has no detail field', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.resolve({}),
    } as unknown as Response);
    try {
      await api.get('/api/v1/broken');
    } catch (err) {
      expect((err as ApiError).detail).toBe('Internal Server Error');
    }
  });

  it('includes Content-Type: application/json header on POST', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(201, { id: 1 }));
    await api.post('/api/v1/items', { name: 'Test' });
    const call = vi.mocked(fetch).mock.calls[0];
    const headers = call[1]?.headers as Record<string, string>;
    expect(headers['Content-Type']).toBe('application/json');
  });

  it('includes Content-Type: application/json header on GET', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, {}));
    await api.get('/api/v1/items');
    const headers = vi.mocked(fetch).mock.calls[0][1]?.headers as Record<string, string>;
    expect(headers['Content-Type']).toBe('application/json');
  });

  it('does not include Authorization header when authRequired=false even if token exists', async () => {
    localStorage.setItem('sms-auth-token', 'some-token');
    vi.mocked(fetch).mockResolvedValue(mockResponse(201, {}));
    await api.post('/api/v1/public', { data: 1 }, false);
    const headers = vi.mocked(fetch).mock.calls[0][1]?.headers as Record<string, string>;
    expect(headers['Authorization']).toBeUndefined();
  });

  it('api.get does not send a body', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, {}));
    await api.get('/api/v1/test');
    const call = vi.mocked(fetch).mock.calls[0];
    expect(call[1]?.body).toBeUndefined();
  });

  it('api.post default authRequired includes auth header when token exists', async () => {
    localStorage.setItem('sms-auth-token', 'default-auth-token');
    vi.mocked(fetch).mockResolvedValue(mockResponse(201, {}));
    await api.post('/api/v1/items', { name: 'Test' });
    const headers = vi.mocked(fetch).mock.calls[0][1]?.headers as Record<string, string>;
    expect(headers['Authorization']).toBe('Bearer default-auth-token');
  });

  it('uses statusText when error json() returns null', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 503,
      statusText: 'Service Unavailable',
      json: () => Promise.resolve(null),
    } as unknown as Response);
    try {
      await api.get('/api/v1/down');
      expect.fail('should have thrown');
    } catch (err) {
      expect((err as ApiError).detail).toBe('Service Unavailable');
    }
  });
});

describe('ApiError', () => {
  it('creates with correct name', () => {
    const err = new ApiError(422, 'Validation error');
    expect(err.name).toBe('ApiError');
    expect(err.status).toBe(422);
    expect(err.detail).toBe('Validation error');
  });
});
