/**
 * TestRetest: trigger test search, show iteration results, approve/reject.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';

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

  if (isLoading) return <Typography sx={{ color: '#64748b', fontSize: '0.875rem' }}>Loading…</Typography>;

  if (strings.length === 0) {
    return (
      <Box sx={{ color: '#64748b', fontSize: '0.875rem' }}>
        No search strings yet. Create one in the Search String Editor above.
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="subtitle1" sx={{ margin: '0 0 1rem', fontSize: '1rem', color: '#111827' }}>Test &amp; Evaluate</Typography>

      {/* String selector */}
      <Box sx={{ marginBottom: '1rem' }}>
        <Typography component="label" sx={{ fontSize: '0.875rem', color: '#374151', marginRight: '0.5rem' }}>
          Search string:
        </Typography>
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
      </Box>

      {/* Databases input */}
      <Box sx={{ marginBottom: '1rem' }}>
        <Typography component="label" sx={{ fontSize: '0.875rem', color: '#374151', display: 'block', marginBottom: '0.25rem' }}>
          Databases (comma-separated, e.g. acm,ieee,scopus):
        </Typography>
        <TextField
          value={databases}
          onChange={(e) => setDatabases(e.target.value)}
          placeholder="acm,ieee,scopus"
          size="small"
          fullWidth
        />
      </Box>

      {/* Run test button */}
      <Button
        variant="contained"
        onClick={() => activeOrFirst && runTest.mutate(activeOrFirst.id)}
        disabled={runTest.isPending || !activeOrFirst}
        sx={{
          background: '#0891b2',
          '&:hover': { background: '#0e7490' },
          fontSize: '0.875rem',
          marginBottom: '1rem',
          opacity: runTest.isPending || !activeOrFirst ? 0.6 : 1,
        }}
      >
        {runTest.isPending ? 'Queuing…' : '▶ Run Test Search'}
      </Button>

      {runTest.isSuccess && (
        <Typography sx={{ fontSize: '0.875rem', color: '#16a34a', marginBottom: '0.75rem' }}>
          Test search queued. Refresh to see new iteration results.
        </Typography>
      )}

      {testError && (
        <Typography sx={{ color: '#ef4444', fontSize: '0.875rem', margin: '0 0 0.75rem' }}>{testError}</Typography>
      )}

      {/* Iterations table */}
      {activeOrFirst && activeOrFirst.iterations.length > 0 && (
        <Box>
          <Typography variant="subtitle2" sx={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}>
            Iterations for v{activeOrFirst.version}
          </Typography>
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
                    <Typography
                      component="span"
                      sx={{
                        color: it.test_set_recall >= 0.8 ? '#16a34a' : it.test_set_recall >= 0.5 ? '#d97706' : '#dc2626',
                        fontWeight: 600,
                      }}
                    >
                      {(it.test_set_recall * 100).toFixed(1)}%
                    </Typography>
                  </td>
                  <td style={{ ...tdStyle, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {it.ai_adequacy_judgment ?? '—'}
                  </td>
                  <td style={tdStyle}>
                    {it.human_approved === true && (
                      <Typography component="span" sx={{ color: '#16a34a', fontWeight: 600 }}>Approved</Typography>
                    )}
                    {it.human_approved === false && (
                      <Typography component="span" sx={{ color: '#dc2626', fontWeight: 600 }}>Rejected</Typography>
                    )}
                    {it.human_approved === null && (
                      <Typography component="span" sx={{ color: '#64748b' }}>Pending</Typography>
                    )}
                  </td>
                  <td style={tdStyle}>
                    {it.human_approved !== true && (
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() =>
                          approveIteration.mutate({
                            ssId: activeOrFirst.id,
                            iterId: it.id,
                            approved: true,
                          })
                        }
                        sx={{ color: '#16a34a', borderColor: '#16a34a', fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                      >
                        Approve
                      </Button>
                    )}
                    {it.human_approved !== false && (
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() =>
                          approveIteration.mutate({
                            ssId: activeOrFirst.id,
                            iterId: it.id,
                            approved: false,
                          })
                        }
                        sx={{ color: '#dc2626', borderColor: '#dc2626', fontSize: '0.75rem', padding: '0.25rem 0.5rem', marginLeft: '0.25rem' }}
                      >
                        Reject
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      )}

      {activeOrFirst && activeOrFirst.iterations.length === 0 && (
        <Typography sx={{ color: '#64748b', fontSize: '0.875rem' }}>
          No test iterations yet. Run a test search to evaluate recall.
        </Typography>
      )}
    </Box>
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
