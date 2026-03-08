/**
 * Tests for useJobProgress hook.
 *
 * Principle IX: resource-acquiring effects MUST return a cleanup function.
 * This file verifies the EventSource is closed when the hook unmounts.
 */

import { renderHook, cleanup, act } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useJobProgress } from '../jobs';

// ---------------------------------------------------------------------------
// Mock EventSource
// ---------------------------------------------------------------------------

interface MockEventSource {
  url: string;
  close: ReturnType<typeof vi.fn>;
  addEventListener: ReturnType<typeof vi.fn>;
  removeEventListener: ReturnType<typeof vi.fn>;
  onerror: ((e: Event) => void) | null;
  listeners: Record<string, ((e: MessageEvent) => void)[]>;
  emit: (eventType: string, data: unknown) => void;
}

let mockEventSource: MockEventSource;

const MockEventSourceClass = vi.fn().mockImplementation((url: string): MockEventSource => {
  mockEventSource = {
    url,
    close: vi.fn(),
    onerror: null,
    listeners: {},
    addEventListener: vi.fn((type: string, fn: (e: MessageEvent) => void) => {
      mockEventSource.listeners[type] = mockEventSource.listeners[type] ?? [];
      mockEventSource.listeners[type].push(fn);
    }),
    removeEventListener: vi.fn(),
    emit(eventType: string, data: unknown) {
      const fns = mockEventSource.listeners[eventType] ?? [];
      const event = { data: JSON.stringify(data) } as MessageEvent;
      fns.forEach((fn) => fn(event));
    },
  };
  return mockEventSource;
});

beforeEach(() => {
  vi.stubGlobal('EventSource', MockEventSourceClass);
  vi.stubGlobal('localStorage', {
    getItem: vi.fn().mockReturnValue(null),
  });
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('useJobProgress', () => {
  it('returns idle state when jobId is null', () => {
    const { result } = renderHook(() => useJobProgress(null));
    expect(result.current.status).toBe('idle');
    expect(result.current.progressPct).toBe(0);
    expect(result.current.error).toBeNull();
  });

  it('creates an EventSource when jobId is provided', () => {
    renderHook(() => useJobProgress('job-123'));
    expect(MockEventSourceClass).toHaveBeenCalledWith(
      expect.stringContaining('job-123')
    );
  });

  it('closes EventSource on unmount (Principle IX cleanup)', () => {
    const { unmount } = renderHook(() => useJobProgress('job-abc'));
    // EventSource must have been created
    expect(mockEventSource.close).not.toHaveBeenCalled();
    // Unmount triggers cleanup
    unmount();
    expect(mockEventSource.close).toHaveBeenCalledTimes(1);
  });

  it('closes EventSource when jobId changes to null', () => {
    const { rerender } = renderHook(({ jobId }) => useJobProgress(jobId), {
      initialProps: { jobId: 'job-xyz' as string | null },
    });
    const firstSource = mockEventSource;
    expect(firstSource.close).not.toHaveBeenCalled();

    rerender({ jobId: null });
    expect(firstSource.close).toHaveBeenCalledTimes(1);
  });

  it('closes old EventSource when jobId changes to a new value', () => {
    const { rerender } = renderHook(({ jobId }) => useJobProgress(jobId), {
      initialProps: { jobId: 'job-1' as string | null },
    });
    const firstSource = mockEventSource;

    rerender({ jobId: 'job-2' });
    expect(firstSource.close).toHaveBeenCalledTimes(1);
  });

  it('sets status to queued initially when jobId is provided', () => {
    const { result } = renderHook(() => useJobProgress('job-queued'));
    expect(result.current.status).toBe('queued');
  });

  it('updates state on progress event', async () => {
    const { result } = renderHook(() => useJobProgress('job-progress'));

    act(() => {
      mockEventSource.emit('progress', {
        status: 'running',
        progress_pct: 42,
        detail: { phase: 'searching' },
      });
    });

    expect(result.current.status).toBe('running');
    expect(result.current.progressPct).toBe(42);
    expect(result.current.detail).toEqual({ phase: 'searching' });
  });

  it('sets status to completed and closes EventSource on complete event', async () => {
    const { result } = renderHook(() => useJobProgress('job-complete'));

    act(() => {
      mockEventSource.emit('complete', { detail: { total: 10 } });
    });

    expect(result.current.status).toBe('completed');
    expect(result.current.progressPct).toBe(100);
    expect(mockEventSource.close).toHaveBeenCalledTimes(1);
  });

  it('sets status to failed and closes EventSource on error event', async () => {
    const { result } = renderHook(() => useJobProgress('job-fail'));

    act(() => {
      mockEventSource.emit('error', { error: 'Job failed with timeout' });
    });

    expect(result.current.status).toBe('failed');
    expect(result.current.error).toBe('Job failed with timeout');
    expect(mockEventSource.close).toHaveBeenCalledTimes(1);
  });

  it('includes auth token in EventSource URL when localStorage returns one', () => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn().mockReturnValue('my-auth-token'),
    });
    renderHook(() => useJobProgress('job-auth'));
    const url: string = MockEventSourceClass.mock.calls.at(-1)?.[0] ?? '';
    expect(url).toContain('token=my-auth-token');
  });

  it('omits token param from EventSource URL when localStorage returns null', () => {
    // localStorage already mocked to return null in beforeEach
    renderHook(() => useJobProgress('job-no-auth'));
    const url: string = MockEventSourceClass.mock.calls.at(-1)?.[0] ?? '';
    expect(url).not.toContain('token=');
  });

  it('defaults status to "running" when progress event has no status field', () => {
    const { result } = renderHook(() => useJobProgress('job-default-status'));

    act(() => {
      mockEventSource.emit('progress', { progress_pct: 50, detail: null });
    });

    expect(result.current.status).toBe('running');
  });

  it('defaults progressPct to 0 when progress event has no progress_pct field', () => {
    const { result } = renderHook(() => useJobProgress('job-default-pct'));

    act(() => {
      mockEventSource.emit('progress', { status: 'running' });
    });

    expect(result.current.progressPct).toBe(0);
  });

  it('sets detail to null when progress event has no detail field', () => {
    const { result } = renderHook(() => useJobProgress('job-no-detail'));

    act(() => {
      mockEventSource.emit('progress', { status: 'running', progress_pct: 10 });
    });

    expect(result.current.detail).toBeNull();
  });

  it('preserves detail from complete event payload', () => {
    const { result } = renderHook(() => useJobProgress('job-complete-detail'));

    act(() => {
      mockEventSource.emit('complete', { detail: { download_url: '/exports/file.zip', size_bytes: 1024 } });
    });

    expect(result.current.status).toBe('completed');
    expect(result.current.progressPct).toBe(100);
    expect(result.current.detail).toEqual({ download_url: '/exports/file.zip', size_bytes: 1024 });
  });

  it('sets detail to null when complete event has no detail field', () => {
    const { result } = renderHook(() => useJobProgress('job-complete-no-detail'));

    act(() => {
      mockEventSource.emit('complete', {});
    });

    expect(result.current.detail).toBeNull();
  });

  it('handles malformed JSON in progress event without throwing', () => {
    const { result } = renderHook(() => useJobProgress('job-bad-json-progress'));

    act(() => {
      // Emit raw malformed JSON via listeners directly
      const listeners = mockEventSource.listeners['progress'] ?? [];
      const event = { data: 'not-json' } as MessageEvent;
      listeners.forEach((fn) => fn(event));
    });

    // State should remain as 'queued' (no update on parse error)
    expect(result.current.status).toBe('queued');
  });

  it('handles malformed JSON in complete event — falls back to completed state', () => {
    const { result } = renderHook(() => useJobProgress('job-bad-json-complete'));

    act(() => {
      const listeners = mockEventSource.listeners['complete'] ?? [];
      const event = { data: 'not-json' } as MessageEvent;
      listeners.forEach((fn) => fn(event));
    });

    expect(result.current.status).toBe('completed');
    expect(result.current.progressPct).toBe(100);
  });

  it('handles malformed JSON in error event — falls back to failed with connection error', () => {
    const { result } = renderHook(() => useJobProgress('job-bad-json-error'));

    act(() => {
      const listeners = mockEventSource.listeners['error'] ?? [];
      const event = { data: 'not-json' } as MessageEvent;
      listeners.forEach((fn) => fn(event));
    });

    expect(result.current.status).toBe('failed');
    expect(result.current.error).toBe('Connection error');
  });

  it('sets status to failed and closes EventSource when native onerror fires', () => {
    const { result } = renderHook(() => useJobProgress('job-onerror'));

    act(() => {
      // Trigger the native EventSource onerror handler
      if (mockEventSource.onerror) {
        mockEventSource.onerror(new Event('error'));
      }
    });

    expect(result.current.status).toBe('failed');
    expect(mockEventSource.close).toHaveBeenCalledTimes(1);
  });

  it('sets error to "SSE connection lost" on native onerror when no prior error', () => {
    const { result } = renderHook(() => useJobProgress('job-onerror-msg'));

    act(() => {
      if (mockEventSource.onerror) {
        mockEventSource.onerror(new Event('error'));
      }
    });

    expect(result.current.error).toBe('SSE connection lost');
  });
});
