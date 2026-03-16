/**
 * Typed fetch wrapper with Bearer token injection and JSON error handling.
 */

import { z } from 'zod';

import { getToken } from './auth';

// ---------------------------------------------------------------------------
// Login response — discriminated union with Zod schemas
// ---------------------------------------------------------------------------

export const LoginSuccessSchema = z.object({
  type: z.literal('success').default('success'),
  access_token: z.string(),
  token_type: z.string(),
  user_id: z.number(),
  display_name: z.string(),
});
export type LoginSuccess = z.infer<typeof LoginSuccessSchema>;

export const LoginTotpRequiredSchema = z.object({
  type: z.literal('totp_required').default('totp_required'),
  requires_totp: z.literal(true),
  partial_token: z.string(),
});
export type LoginTotpRequired = z.infer<typeof LoginTotpRequiredSchema>;

export type LoginResult = LoginSuccess | LoginTotpRequired;

/** Post credentials and return a typed discriminated union. */
export async function loginUser(email: string, password: string): Promise<LoginResult> {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = data?.detail ?? detail;
    } catch { /* ignore */ }
    throw new ApiError(response.status, detail);
  }

  const raw = await response.json();
  if (raw?.requires_totp === true) {
    return LoginTotpRequiredSchema.parse(raw);
  }
  return LoginSuccessSchema.parse(raw);
}

const BASE_URL = import.meta.env.VITE_API_URL ?? '';

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  authRequired = true,
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (authRequired) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = data?.detail ?? detail;
    } catch {
      // ignore parse error
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body: unknown, authRequired = true) =>
    request<T>('POST', path, body, authRequired),
  put: <T>(path: string, body: unknown) => request<T>('PUT', path, body),
  patch: <T>(path: string, body: unknown) => request<T>('PATCH', path, body),
  delete: <T>(path: string) => request<T>('DELETE', path),
};
