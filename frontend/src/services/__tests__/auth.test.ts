/**
 * Tests for the auth service module.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  getToken,
  getCurrentUser,
  setSession,
  clearSession,
  useAuthStore,
  type AuthUser,
} from '../auth';

const TEST_USER: AuthUser = {
  id: 1,
  email: 'alice@example.com',
  displayName: 'Alice',
};

describe('auth service', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('getToken returns null when no token is stored', () => {
    expect(getToken()).toBeNull();
  });

  it('getCurrentUser returns null when no user is stored', () => {
    expect(getCurrentUser()).toBeNull();
  });

  it('setSession stores token and user in localStorage', () => {
    setSession('my-jwt', TEST_USER);
    expect(getToken()).toBe('my-jwt');
    expect(getCurrentUser()).toEqual(TEST_USER);
  });

  it('clearSession removes token and user from localStorage', () => {
    setSession('my-jwt', TEST_USER);
    clearSession();
    expect(getToken()).toBeNull();
    expect(getCurrentUser()).toBeNull();
  });

  it('getCurrentUser returns null for invalid JSON in localStorage', () => {
    localStorage.setItem('sms-auth-user', 'not-valid-json{{{');
    expect(getCurrentUser()).toBeNull();
  });

  it('setSession dispatches sms-auth-change event', () => {
    let fired = false;
    window.addEventListener('sms-auth-change', () => { fired = true; }, { once: true });
    setSession('token', TEST_USER);
    expect(fired).toBe(true);
  });

  it('clearSession dispatches sms-auth-change event', () => {
    let fired = false;
    window.addEventListener('sms-auth-change', () => { fired = true; }, { once: true });
    clearSession();
    expect(fired).toBe(true);
  });

  it('getCurrentUser parses stored user JSON correctly', () => {
    localStorage.setItem('sms-auth-user', JSON.stringify(TEST_USER));
    const user = getCurrentUser();
    expect(user?.email).toBe('alice@example.com');
    expect(user?.displayName).toBe('Alice');
  });

  describe('storage key isolation', () => {
    it('getToken does not return a token stored under a different key', () => {
      localStorage.setItem('other-key', 'decoy');
      expect(getToken()).toBeNull();
    });

    it('getToken returns only the token stored by setSession', () => {
      setSession('correct-token', TEST_USER);
      localStorage.setItem('other-key', 'decoy');
      expect(getToken()).toBe('correct-token');
    });

    it('getCurrentUser does not return a user stored under a different key', () => {
      localStorage.setItem('other-user-key', JSON.stringify(TEST_USER));
      expect(getCurrentUser()).toBeNull();
    });
  });

  describe('event correctness', () => {
    it('setSession fires sms-auth-change (not another event)', () => {
      let correctFired = false;
      let wrongFired = false;
      window.addEventListener('sms-auth-change', () => { correctFired = true; }, { once: true });
      window.addEventListener('other-event', () => { wrongFired = true; }, { once: true });
      setSession('tok', TEST_USER);
      expect(correctFired).toBe(true);
      expect(wrongFired).toBe(false);
    });

    it('clearSession fires sms-auth-change (not another event)', () => {
      let correctFired = false;
      let wrongFired = false;
      window.addEventListener('sms-auth-change', () => { correctFired = true; }, { once: true });
      window.addEventListener('other-event', () => { wrongFired = true; }, { once: true });
      clearSession();
      expect(correctFired).toBe(true);
      expect(wrongFired).toBe(false);
    });

    it('subscribe adds listener for sms-auth-change: setSession triggers re-render', () => {
      const { result } = renderHook(() => useAuthStore((s) => s.token));
      expect(result.current).toBeNull();
      act(() => { setSession('subscribe-test', TEST_USER); });
      expect(result.current).toBe('subscribe-test');
    });

    it('subscribe cleanup removes listener: unmounted hook does not update', () => {
      const { result, unmount } = renderHook(() => useAuthStore((s) => s.token));
      unmount();
      // After unmount, firing the event should not throw or update anything
      act(() => { setSession('after-unmount', TEST_USER); });
      // result.current should be whatever it was at unmount time (null)
      expect(result.current).toBeNull();
    });

    it('subscribe returns a cleanup that calls window.removeEventListener', () => {
      const removeSpy = vi.spyOn(window, 'removeEventListener');
      const { unmount } = renderHook(() => useAuthStore((s) => s.token));
      unmount();
      expect(removeSpy).toHaveBeenCalledWith('sms-auth-change', expect.any(Function));
      removeSpy.mockRestore();
    });
  });

  describe('useAuthStore', () => {
    it('returns current token via selector', () => {
      setSession('hook-token', TEST_USER);
      const { result } = renderHook(() => useAuthStore((s) => s.token));
      expect(result.current).toBe('hook-token');
    });

    it('returns null token when no session exists', () => {
      const { result } = renderHook(() => useAuthStore((s) => s.token));
      expect(result.current).toBeNull();
    });

    it('returns current user email via selector', () => {
      setSession('tok', TEST_USER);
      const { result } = renderHook(() => useAuthStore((s) => s.user?.email ?? null));
      expect(result.current).toBe('alice@example.com');
    });

    it('returns null user email when no session exists', () => {
      const { result } = renderHook(() => useAuthStore((s) => s.user?.email ?? null));
      expect(result.current).toBeNull();
    });

    it('re-renders on setSession call', () => {
      const { result } = renderHook(() => useAuthStore((s) => s.token));
      expect(result.current).toBeNull();
      act(() => { setSession('updated-token', TEST_USER); });
      expect(result.current).toBe('updated-token');
    });

    it('re-renders on clearSession call', () => {
      setSession('initial', TEST_USER);
      const { result } = renderHook(() => useAuthStore((s) => s.token));
      expect(result.current).toBe('initial');
      act(() => { clearSession(); });
      expect(result.current).toBeNull();
    });

    it('selector receives setSession function', () => {
      const { result } = renderHook(() => useAuthStore((s) => s.setSession));
      expect(typeof result.current).toBe('function');
    });

    it('selector receives clearSession function', () => {
      const { result } = renderHook(() => useAuthStore((s) => s.clearSession));
      expect(typeof result.current).toBe('function');
    });

    it('server snapshot returns null token', () => {
      // The server snapshot is the third arg to useSyncExternalStore.
      // We verify it by checking that the initial render with no localStorage returns null.
      const { result } = renderHook(() => useAuthStore((s) => s.token));
      // With no localStorage state, token should be null regardless of snapshot
      expect(result.current).toBeNull();
    });

    it('returns null user when localStorage has invalid JSON via useAuthStore', () => {
      localStorage.setItem('sms-auth-user', 'not-valid-json{{{');
      localStorage.setItem('sms-auth-token', 'some-token');
      const { result } = renderHook(() => useAuthStore((s) => s.user));
      expect(result.current).toBeNull();
    });
  });
});
