import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useColorMode } from './useColorMode';

// ---------------------------------------------------------------------------
// matchMedia mock helpers
// ---------------------------------------------------------------------------

function mockMatchMedia(matches: boolean) {
  const listeners: ((e: MediaQueryListEvent) => void)[] = [];

  const mq = {
    matches,
    addEventListener: vi.fn((_: string, fn: (e: MediaQueryListEvent) => void) => {
      listeners.push(fn);
    }),
    removeEventListener: vi.fn((_: string, fn: (e: MediaQueryListEvent) => void) => {
      const i = listeners.indexOf(fn);
      if (i !== -1) listeners.splice(i, 1);
    }),
    dispatchChange: (newMatches: boolean) => {
      listeners.forEach((fn) => fn({ matches: newMatches } as MediaQueryListEvent));
    },
  };

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockReturnValue(mq),
  });

  return mq;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('useColorMode', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('returns "light" for preference "light" regardless of OS setting', () => {
    mockMatchMedia(true); // OS is dark — but preference overrides
    const { result } = renderHook(() => useColorMode('light'));
    expect(result.current).toBe('light');
  });

  it('returns "dark" for preference "dark" regardless of OS setting', () => {
    mockMatchMedia(false); // OS is light — but preference overrides
    const { result } = renderHook(() => useColorMode('dark'));
    expect(result.current).toBe('dark');
  });

  it('returns "dark" for "system" when OS prefers dark', () => {
    mockMatchMedia(true);
    const { result } = renderHook(() => useColorMode('system'));
    expect(result.current).toBe('dark');
  });

  it('returns "light" for "system" when OS prefers light', () => {
    mockMatchMedia(false);
    const { result } = renderHook(() => useColorMode('system'));
    expect(result.current).toBe('light');
  });

  it('subscribes to matchMedia change events when preference is "system"', () => {
    const mq = mockMatchMedia(false);
    renderHook(() => useColorMode('system'));
    expect(mq.addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
  });

  it('does NOT subscribe to matchMedia when preference is "light"', () => {
    const mq = mockMatchMedia(false);
    renderHook(() => useColorMode('light'));
    expect(mq.addEventListener).not.toHaveBeenCalled();
  });

  it('updates mode reactively when OS dark-mode changes while preference is "system"', () => {
    const mq = mockMatchMedia(false); // starts light
    const { result } = renderHook(() => useColorMode('system'));
    expect(result.current).toBe('light');

    act(() => {
      mq.dispatchChange(true); // OS switches to dark
    });

    expect(result.current).toBe('dark');
  });

  it('removes matchMedia listener on unmount', () => {
    const mq = mockMatchMedia(false);
    const { unmount } = renderHook(() => useColorMode('system'));
    unmount();
    expect(mq.removeEventListener).toHaveBeenCalledWith('change', expect.any(Function));
  });
});
