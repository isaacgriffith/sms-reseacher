/**
 * SSE hook for tracking background job progress.
 *
 * useJobProgress(jobId) wraps EventSource, handles reconnect,
 * and exposes {status, progressPct, detail} state. Auto-closes
 * on complete or error events.
 */
// @ts-nocheck
function stryNS_9fa48() {
  var g = typeof globalThis === 'object' && globalThis && globalThis.Math === Math && globalThis || new Function("return this")();
  var ns = g.__stryker__ || (g.__stryker__ = {});
  if (ns.activeMutant === undefined && g.process && g.process.env && g.process.env.__STRYKER_ACTIVE_MUTANT__) {
    ns.activeMutant = g.process.env.__STRYKER_ACTIVE_MUTANT__;
  }
  function retrieveNS() {
    return ns;
  }
  stryNS_9fa48 = retrieveNS;
  return retrieveNS();
}
stryNS_9fa48();
function stryCov_9fa48() {
  var ns = stryNS_9fa48();
  var cov = ns.mutantCoverage || (ns.mutantCoverage = {
    static: {},
    perTest: {}
  });
  function cover() {
    var c = cov.static;
    if (ns.currentTestId) {
      c = cov.perTest[ns.currentTestId] = cov.perTest[ns.currentTestId] || {};
    }
    var a = arguments;
    for (var i = 0; i < a.length; i++) {
      c[a[i]] = (c[a[i]] || 0) + 1;
    }
  }
  stryCov_9fa48 = cover;
  cover.apply(null, arguments);
}
function stryMutAct_9fa48(id) {
  var ns = stryNS_9fa48();
  function isActive(id) {
    if (ns.activeMutant === id) {
      if (ns.hitCount !== void 0 && ++ns.hitCount > ns.hitLimit) {
        throw new Error('Stryker: Hit count limit reached (' + ns.hitCount + ')');
      }
      return true;
    }
    return false;
  }
  stryMutAct_9fa48 = isActive;
  return isActive(id);
}
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
  error: null
};

/**
 * Subscribe to real-time job progress via SSE.
 *
 * @param jobId - ARQ background job ID (or null to skip)
 * @returns Current job progress state
 */
export function useJobProgress(jobId: string | null): JobProgressState {
  if (stryMutAct_9fa48("1850")) {
    {}
  } else {
    stryCov_9fa48("1850");
    const [state, setState] = useState<JobProgressState>(INITIAL_STATE);
    const esRef = useRef<EventSource | null>(null);
    useEffect(() => {
      if (stryMutAct_9fa48("1851")) {
        {}
      } else {
        stryCov_9fa48("1851");
        if (stryMutAct_9fa48("1854") ? false : stryMutAct_9fa48("1853") ? true : stryMutAct_9fa48("1852") ? jobId : (stryCov_9fa48("1852", "1853", "1854"), !jobId)) {
          if (stryMutAct_9fa48("1855")) {
            {}
          } else {
            stryCov_9fa48("1855");
            setState(INITIAL_STATE);
            return;
          }
        }
        setState({
          status: 'queued',
          progressPct: 0,
          detail: null,
          error: null
        });
        const connect = () => {
          if (stryMutAct_9fa48("1858")) {
            {}
          } else {
            stryCov_9fa48("1858");
            const token = localStorage.getItem('auth_token');
            const url = `/api/v1/jobs/${encodeURIComponent(jobId)}/progress${token ? `?token=${token}` : ''}`;
            const es = new EventSource(url);
            esRef.current = es;
            es.addEventListener('progress', (e: MessageEvent) => {
              if (stryMutAct_9fa48("1864")) {
                {}
              } else {
                stryCov_9fa48("1864");
                try {
                  if (stryMutAct_9fa48("1865")) {
                    {}
                  } else {
                    stryCov_9fa48("1865");
                    const data = JSON.parse(e.data);
                    setState({
                      status: stryMutAct_9fa48("1867") ? data.status && 'running' : (stryCov_9fa48("1867"), data.status ?? 'running'),
                      progressPct: stryMutAct_9fa48("1869") ? data.progress_pct && 0 : (stryCov_9fa48("1869"), data.progress_pct ?? 0),
                      detail: stryMutAct_9fa48("1870") ? data.detail && null : (stryCov_9fa48("1870"), data.detail ?? null),
                      error: null
                    });
                  }
                } catch {
                  // ignore parse errors
                }
              }
            });
            es.addEventListener('complete', (e: MessageEvent) => {
              if (stryMutAct_9fa48("1872")) {
                {}
              } else {
                stryCov_9fa48("1872");
                try {
                  if (stryMutAct_9fa48("1873")) {
                    {}
                  } else {
                    stryCov_9fa48("1873");
                    const data = JSON.parse(e.data);
                    setState({
                      status: 'completed',
                      progressPct: 100,
                      detail: stryMutAct_9fa48("1876") ? data.detail && null : (stryCov_9fa48("1876"), data.detail ?? null),
                      error: null
                    });
                  }
                } catch {
                  if (stryMutAct_9fa48("1877")) {
                    {}
                  } else {
                    stryCov_9fa48("1877");
                    setState(stryMutAct_9fa48("1878") ? () => undefined : (stryCov_9fa48("1878"), prev => ({
                      ...prev,
                      status: 'completed',
                      progressPct: 100
                    })));
                  }
                }
                es.close();
              }
            });
            es.addEventListener('error', (e: MessageEvent) => {
              if (stryMutAct_9fa48("1882")) {
                {}
              } else {
                stryCov_9fa48("1882");
                try {
                  if (stryMutAct_9fa48("1883")) {
                    {}
                  } else {
                    stryCov_9fa48("1883");
                    const data = JSON.parse(e.data);
                    setState(stryMutAct_9fa48("1884") ? () => undefined : (stryCov_9fa48("1884"), prev => ({
                      ...prev,
                      status: 'failed',
                      error: stryMutAct_9fa48("1887") ? data.error && 'Job failed' : (stryCov_9fa48("1887"), data.error ?? 'Job failed')
                    })));
                  }
                } catch {
                  if (stryMutAct_9fa48("1889")) {
                    {}
                  } else {
                    stryCov_9fa48("1889");
                    setState(stryMutAct_9fa48("1890") ? () => undefined : (stryCov_9fa48("1890"), prev => ({
                      ...prev,
                      status: 'failed',
                      error: 'Connection error'
                    })));
                  }
                }
                es.close();
              }
            });
            es.onerror = () => {
              if (stryMutAct_9fa48("1894")) {
                {}
              } else {
                stryCov_9fa48("1894");
                // EventSource native error (network issue) — close and mark failed
                setState(stryMutAct_9fa48("1895") ? () => undefined : (stryCov_9fa48("1895"), prev => ({
                  ...prev,
                  status: 'failed',
                  error: stryMutAct_9fa48("1898") ? prev.error && 'SSE connection lost' : (stryCov_9fa48("1898"), prev.error ?? 'SSE connection lost')
                })));
                es.close();
              }
            };
          }
        };
        connect();
        return () => {
          if (stryMutAct_9fa48("1900")) {
            {}
          } else {
            stryCov_9fa48("1900");
            stryMutAct_9fa48("1901") ? esRef.current.close() : (stryCov_9fa48("1901"), esRef.current?.close());
            esRef.current = null;
          }
        };
      }
    }, stryMutAct_9fa48("1902") ? [] : (stryCov_9fa48("1902"), [jobId]));
    return state;
  }
}