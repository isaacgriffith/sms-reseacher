/**
 * TestRetest: trigger test search, show iteration results, approve/reject.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';

interface Iteration {
  id: number;
  iteration_number: number;
  result_set_count: number;
  test_set_recall: number;
  ai_adequacy_judgment: string | null;
  human_approved: boolean | null;
}

interface SearchString {
  id: number;
  version: number;
  string_text: string;
  is_active: boolean;
  created_by_agent: string | null;
  iterations: Iteration[];
}

interface TestRetestProps {
  studyId: number;
}

export default function TestRetest({ studyId }: TestRetestProps) {
  const qc = useQueryClient();
  const [testError, setTestError] = useState<string | null>(null);
  const [selectedStringId, setSelectedStringId] = useState<number | null>(null);
  const [databases, setDatabases] = useState('');

  const { data: strings = [], isLoading } = useQuery<SearchString[]>({
    queryKey: ['search-strings', studyId],
    queryFn: () => api.get<SearchString[]>(`/api/v1/studies/${studyId}/search-strings`),
  });

  const activeOrFirst = selectedStringId
    ? strings.find((s) => s.id === selectedStringId)
    : strings.find((s) => s.is_active) ?? strings[0];

  const runTest = useMutation({
    mutationFn: (ssId: number) =>
      api.post<{ job_id: string | null; search_string_id: number }>(
        `/api/v1/studies/${studyId}/search-strings/${ssId}/test`,
        { databases: databases.split(',').map((d) => d.trim()).filter(Boolean) }
      ),
    onSuccess: () => {
      setTestError(null);
      // After job completes, user can refresh to see new iteration
      qc.invalidateQueries({ queryKey: ['search-strings', studyId] });
    },
    onError: (err) => {
      setTestError(err instanceof ApiError ? err.detail : 'Test search failed');
    },
  });

  const approveIteration = useMutation({
    mutationFn: ({ ssId, iterId, approved }: { ssId: number; iterId: number; approved: boolean }) =>
      api.patch<Iteration>(
        `/api/v1/studies/${studyId}/search-strings/${ssId}/iterations/${iterId}`,
        { human_approved: approved }
      ),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['search-strings', studyId] }),
  });

  if (isLoading) return <p style={{ color: '#64748b', fontSize: '0.875rem' }}>Loading…</p>;

  if (strings.length === 0) {
    return (
      <div style={{ color: '#64748b', fontSize: '0.875rem' }}>
        No search strings yet. Create one in the Search String Editor above.
      </div>
    );
  }

  return (
    <div>
      <h3 style={{ margin: '0 0 1rem', fontSize: '1rem', color: '#111827' }}>Test &amp; Evaluate</h3>

      {/* String selector */}
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ fontSize: '0.875rem', color: '#374151', marginRight: '0.5rem' }}>
          Search string:
        </label>
        <select
          value={activeOrFirst?.id ?? ''}
          onChange={(e) => setSelectedStringId(Number(e.target.value))}
          style={{
            padding: '0.375rem 0.5rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
          }}
        >
          {strings.map((ss) => (
            <option key={ss.id} value={ss.id}>
              v{ss.version}{ss.is_active ? ' (active)' : ''}{ss.created_by_agent ? ' [AI]' : ''}
            </option>
          ))}
        </select>
      </div>

      {/* Databases input */}
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ fontSize: '0.875rem', color: '#374151', display: 'block', marginBottom: '0.25rem' }}>
          Databases (comma-separated, e.g. acm,ieee,scopus):
        </label>
        <input
          value={databases}
          onChange={(e) => setDatabases(e.target.value)}
          placeholder="acm,ieee,scopus"
          style={{
            width: '100%',
            padding: '0.375rem 0.625rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
            boxSizing: 'border-box',
          }}
        />
      </div>

      {/* Run test button */}
      <button
        onClick={() => activeOrFirst && runTest.mutate(activeOrFirst.id)}
        disabled={runTest.isPending || !activeOrFirst}
        style={{
          padding: '0.5rem 1rem',
          background: '#0891b2',
          color: '#fff',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: runTest.isPending || !activeOrFirst ? 'not-allowed' : 'pointer',
          fontSize: '0.875rem',
          marginBottom: '1rem',
          opacity: runTest.isPending || !activeOrFirst ? 0.6 : 1,
        }}
      >
        {runTest.isPending ? 'Queuing…' : '▶ Run Test Search'}
      </button>

      {runTest.isSuccess && (
        <p style={{ fontSize: '0.875rem', color: '#16a34a', marginBottom: '0.75rem' }}>
          Test search queued. Refresh to see new iteration results.
        </p>
      )}

      {testError && (
        <p style={{ color: '#ef4444', fontSize: '0.875rem', margin: '0 0 0.75rem' }}>{testError}</p>
      )}

      {/* Iterations table */}
      {activeOrFirst && activeOrFirst.iterations.length > 0 && (
        <div>
          <h4 style={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}>
            Iterations for v{activeOrFirst.version}
          </h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ background: '#f1f5f9' }}>
                <th style={thStyle}>#</th>
                <th style={thStyle}>Results</th>
                <th style={thStyle}>Recall</th>
                <th style={thStyle}>AI Judgment</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {activeOrFirst.iterations.map((it) => (
                <tr key={it.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <td style={tdStyle}>{it.iteration_number}</td>
                  <td style={tdStyle}>{it.result_set_count.toLocaleString()}</td>
                  <td style={tdStyle}>
                    <span
                      style={{
                        color: it.test_set_recall >= 0.8 ? '#16a34a' : it.test_set_recall >= 0.5 ? '#d97706' : '#dc2626',
                        fontWeight: 600,
                      }}
                    >
                      {(it.test_set_recall * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td style={{ ...tdStyle, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {it.ai_adequacy_judgment ?? '—'}
                  </td>
                  <td style={tdStyle}>
                    {it.human_approved === true && (
                      <span style={{ color: '#16a34a', fontWeight: 600 }}>Approved</span>
                    )}
                    {it.human_approved === false && (
                      <span style={{ color: '#dc2626', fontWeight: 600 }}>Rejected</span>
                    )}
                    {it.human_approved === null && (
                      <span style={{ color: '#64748b' }}>Pending</span>
                    )}
                  </td>
                  <td style={tdStyle}>
                    {it.human_approved !== true && (
                      <button
                        onClick={() =>
                          approveIteration.mutate({
                            ssId: activeOrFirst.id,
                            iterId: it.id,
                            approved: true,
                          })
                        }
                        style={actionBtnStyle('#16a34a')}
                      >
                        Approve
                      </button>
                    )}
                    {it.human_approved !== false && (
                      <button
                        onClick={() =>
                          approveIteration.mutate({
                            ssId: activeOrFirst.id,
                            iterId: it.id,
                            approved: false,
                          })
                        }
                        style={{ ...actionBtnStyle('#dc2626'), marginLeft: '0.25rem' }}
                      >
                        Reject
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeOrFirst && activeOrFirst.iterations.length === 0 && (
        <p style={{ color: '#64748b', fontSize: '0.875rem' }}>
          No test iterations yet. Run a test search to evaluate recall.
        </p>
      )}
    </div>
  );
}

const thStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  textAlign: 'left',
  fontWeight: 600,
  color: '#374151',
  fontSize: '0.8125rem',
  borderBottom: '2px solid #e2e8f0',
};

const tdStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  color: '#374151',
};

function actionBtnStyle(color: string): React.CSSProperties {
  return {
    padding: '0.25rem 0.5rem',
    background: 'transparent',
    border: `1px solid ${color}`,
    borderRadius: '0.25rem',
    color,
    cursor: 'pointer',
    fontSize: '0.75rem',
  };
}
