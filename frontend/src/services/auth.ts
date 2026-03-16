/**
 * Session management: store/read/clear JWT and current user state.
 * Backed by localStorage with a React context-compatible hook.
 */

import { useSyncExternalStore } from 'react';

const TOKEN_KEY = 'sms-auth-token';
const USER_KEY = 'sms-auth-user';

export interface AuthUser {
  id: number;
  email: string;
  displayName: string;
  themePreference?: 'light' | 'dark' | 'system';
}

// ---------------------------------------------------------------------------
// Raw localStorage helpers (usable outside React)
// ---------------------------------------------------------------------------

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getCurrentUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function setSession(token: string, user: AuthUser): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  window.dispatchEvent(new Event('sms-auth-change'));
}

export function updateUserFields(updates: Partial<AuthUser>): void {
  const current = getCurrentUser();
  if (!current) return;
  localStorage.setItem(USER_KEY, JSON.stringify({ ...current, ...updates }));
  window.dispatchEvent(new Event('sms-auth-change'));
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  window.dispatchEvent(new Event('sms-auth-change'));
}

// ---------------------------------------------------------------------------
// React hook: re-renders on auth changes
// ---------------------------------------------------------------------------

function subscribe(cb: () => void): () => void {
  window.addEventListener('sms-auth-change', cb);
  return () => window.removeEventListener('sms-auth-change', cb);
}

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  setSession: (token: string, user: AuthUser) => void;
  clearSession: () => void;
}

// Cached snapshot — returned by reference so useSyncExternalStore can use
// Object.is() equality checks without triggering spurious re-renders.
let _snapshot: AuthState = {
  token: null,
  user: null,
  setSession,
  clearSession,
};

function getAuthSnapshot(): AuthState {
  const token = localStorage.getItem(TOKEN_KEY);
  const userRaw = localStorage.getItem(USER_KEY);
  const tokenChanged = token !== _snapshot.token;
  const userChanged = userRaw !== (_snapshot.user ? JSON.stringify(_snapshot.user) : null);
  if (!tokenChanged && !userChanged) return _snapshot;
  let user: AuthUser | null = null;
  if (userRaw) {
    try { user = JSON.parse(userRaw) as AuthUser; } catch { /* ignore */ }
  }
  _snapshot = { token, user, setSession, clearSession };
  return _snapshot;
}

export function useAuthStore<T>(selector: (state: AuthState) => T): T {
  return useSyncExternalStore(
    subscribe,
    () => selector(getAuthSnapshot()),
    () => selector({ token: null, user: null, setSession, clearSession }),
  );
}
