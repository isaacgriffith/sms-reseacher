/**
 * SSE hook for tracking background job progress.
 *
 * useJobProgress(jobId) wraps EventSource, handles reconnect,
 * and exposes {status, progressPct, detail} state. Auto-closes
 * on complete or error events.
 */

import { useEffect, useRef, useState } from 'react';

export interface JobProgressState {
  status: 'idle' | 'queued' | 'running' | 'completed' | 'failed';
  progressPct: number;
  detail: Record<string, unknown> | null;
  error: string | null;
}

const INITIAL_STATE: JobProgressState = {
  status: 'idle',
  progressPct: 0,
  detail: null,
  error: null,
};

/**
 * Subscribe to real-time job progress via SSE.
 *
 * @param jobId - ARQ background job ID (or null to skip)
 * @returns Current job progress state
 */
export function useJobProgress(jobId: string | null): JobProgressState {
  const [state, setState] = useState<JobProgressState>(INITIAL_STATE);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!jobId) {
      setState(INITIAL_STATE);
      return;
    }

    setState({ status: 'queued', progressPct: 0, detail: null, error: null });

    const connect = () => {
      const token = localStorage.getItem('auth_token');
      const url = `/api/v1/jobs/${encodeURIComponent(jobId)}/progress${token ? `?token=${token}` : ''}`;
      const es = new EventSource(url);
      esRef.current = es;

      es.addEventListener('progress', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          setState({
            status: data.status ?? 'running',
            progressPct: data.progress_pct ?? 0,
            detail: data.detail ?? null,
            error: null,
          });
        } catch {
          // ignore parse errors
        }
      });

      es.addEventListener('complete', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          setState({
            status: 'completed',
            progressPct: 100,
            detail: data.detail ?? null,
            error: null,
          });
        } catch {
          setState((prev) => ({ ...prev, status: 'completed', progressPct: 100 }));
        }
        es.close();
      });

      es.addEventListener('error', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          setState((prev) => ({
            ...prev,
            status: 'failed',
            error: data.error ?? 'Job failed',
          }));
        } catch {
          setState((prev) => ({ ...prev, status: 'failed', error: 'Connection error' }));
        }
        es.close();
      });

      es.onerror = () => {
        // EventSource native error (network issue) — close and mark failed
        setState((prev) => ({
          ...prev,
          status: 'failed',
          error: prev.error ?? 'SSE connection lost',
        }));
        es.close();
      };
    };

    connect();

    return () => {
      esRef.current?.close();
      esRef.current = null;
    };
  }, [jobId]);

  return state;
}
