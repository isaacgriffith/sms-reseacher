/**
 * Seed papers management: add/remove by DOI or manual entry,
 * trigger Librarian agent or Expert agent, display suggestions.
 */

import { useEffect, useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import JobProgressPanel from '../jobs/JobProgressPanel';
import { useJobProgress } from '../../services/jobs';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';

interface PaperRef {
  id: number;
  title: string;
  doi: string | null;
  authors: unknown[] | null;
  year: number | null;
  venue: string | null;
}

interface SeedPaperItem {
  id: number;
  paper: PaperRef;
  added_by: string;
}

interface SuggestedPaper {
  title: string;
  authors: string[];
  year: number | null;
  venue: string | null;
  doi: string | null;
  rationale: string;
}

interface Props {
  studyId: number;
}

/** Inner component that subscribes to a job's SSE stream and notifies on completion. */
function ExpertJobWatcher({
  jobId,
  onComplete,
}: {
  jobId: string;
  onComplete: (papers: SuggestedPaper[]) => void;
}) {
  const { status, detail } = useJobProgress(jobId);
  const notified = useRef(false);

  useEffect(() => {
    if (status === 'completed' && !notified.current) {
      notified.current = true;
      const papers = (detail as { papers?: SuggestedPaper[] } | null)?.papers ?? [];
      onComplete(papers);
    }
  }, [status, detail, onComplete]);

  return null;
}

export default function SeedPapers({ studyId }: Props) {
  const queryClient = useQueryClient();
  const [doi, setDoi] = useState('');
  const [manualTitle, setManualTitle] = useState('');
  const [suggestions, setSuggestions] = useState<SuggestedPaper[] | null>(null);
  const [librarianLoading, setLibrarianLoading] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);
  const [expertJobId, setExpertJobId] = useState<string | null>(null);
  const [expertSuggestions, setExpertSuggestions] = useState<SuggestedPaper[] | null>(null);

  const { data: seeds, isLoading } = useQuery<SeedPaperItem[]>({
    queryKey: ['seeds', studyId],
    queryFn: () => api.get<SeedPaperItem[]>(`/api/v1/studies/${studyId}/seeds/papers`),
  });

  const addMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api.post<SeedPaperItem>(`/api/v1/studies/${studyId}/seeds/papers`, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seeds', studyId] });
      setDoi('');
      setManualTitle('');
      setAddError(null);
    },
    onError: () => setAddError('Failed to add paper'),
  });

  const deleteMutation = useMutation({
    mutationFn: (seedId: number) =>
      api.delete<void>(`/api/v1/studies/${studyId}/seeds/papers/${seedId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['seeds', studyId] }),
  });

  const handleAddDoi = () => {
    if (!doi.trim()) return;
    addMutation.mutate({ doi: doi.trim() });
  };

  const handleAddManual = () => {
    if (!manualTitle.trim()) return;
    addMutation.mutate({ title: manualTitle.trim() });
  };

  const handleLibrarian = async () => {
    setLibrarianLoading(true);
    setSuggestions(null);
    try {
      const result = await api.post<{ suggestions: { papers: SuggestedPaper[] } }>(
        `/api/v1/studies/${studyId}/seeds/librarian`,
        {},
      );
      setSuggestions(result.suggestions.papers);
    } catch {
      setSuggestions([]);
    } finally {
      setLibrarianLoading(false);
    }
  };

  const handleExpert = async () => {
    setExpertJobId(null);
    setExpertSuggestions(null);
    try {
      const result = await api.post<{ job_id: string }>(
        `/api/v1/studies/${studyId}/seeds/expert`,
        {},
      );
      setExpertJobId(result.job_id);
    } catch {
      setExpertSuggestions([]);
    }
  };

  return (
    <Box>
      <Typography variant="h6" sx={{ margin: '0 0 1rem' }}>Seed Papers</Typography>

      {/* Add by DOI */}
      <Box sx={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <TextField
          value={doi}
          onChange={(e) => setDoi(e.target.value)}
          placeholder="DOI (e.g. 10.1145/1234)"
          size="small"
          sx={{ flex: 1 }}
          onKeyDown={(e) => e.key === 'Enter' && handleAddDoi()}
        />
        <Button
          variant="contained"
          onClick={handleAddDoi}
          disabled={addMutation.isPending}
          sx={{ whiteSpace: 'nowrap' }}
        >
          Add by DOI
        </Button>
      </Box>

      {/* Add manually */}
      <Box sx={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <TextField
          value={manualTitle}
          onChange={(e) => setManualTitle(e.target.value)}
          placeholder="Paper title (manual entry)"
          size="small"
          sx={{ flex: 1 }}
          onKeyDown={(e) => e.key === 'Enter' && handleAddManual()}
        />
        <Button
          variant="contained"
          onClick={handleAddManual}
          disabled={addMutation.isPending}
          sx={{ background: '#475569', '&:hover': { background: '#334155' }, whiteSpace: 'nowrap' }}
        >
          Add Manually
        </Button>
      </Box>

      {addError && <Typography sx={{ color: 'red', fontSize: '0.875rem', marginBottom: '0.75rem' }}>{addError}</Typography>}

      {/* AI agent buttons */}
      <Box sx={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          onClick={handleLibrarian}
          disabled={librarianLoading}
          sx={{
            background: librarianLoading ? '#94a3b8' : '#7c3aed',
            '&:hover': { background: '#6d28d9' },
          }}
        >
          {librarianLoading ? 'Searching…' : 'Suggest with Librarian AI'}
        </Button>
        <Button
          variant="contained"
          onClick={handleExpert}
          disabled={expertJobId !== null && expertSuggestions === null}
          sx={{
            background: (expertJobId !== null && expertSuggestions === null) ? '#94a3b8' : '#0f766e',
            '&:hover': { background: '#0d6561' },
          }}
        >
          Find with Expert AI
        </Button>
      </Box>

      {/* Expert job progress */}
      {expertJobId !== null && expertSuggestions === null && (
        <>
          <ExpertJobWatcher jobId={expertJobId} onComplete={setExpertSuggestions} />
          <Box sx={{ marginBottom: '1.5rem' }}>
            <JobProgressPanel jobId={expertJobId} />
          </Box>
        </>
      )}

      {/* Librarian suggestions */}
      {suggestions !== null && (
        <Box sx={{ marginBottom: '1.5rem', padding: '1rem', background: '#f5f3ff', borderRadius: '0.5rem' }}>
          <Typography variant="subtitle2" sx={{ margin: '0 0 0.75rem', color: '#6d28d9' }}>Librarian Suggestions</Typography>
          {suggestions.length === 0 ? (
            <Typography sx={{ color: '#64748b', fontSize: '0.875rem' }}>No suggestions available.</Typography>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {suggestions.map((p, i) => (
                <li key={i} style={{ marginBottom: '0.75rem', paddingBottom: '0.75rem', borderBottom: i < suggestions.length - 1 ? '1px solid #ddd6fe' : 'none' }}>
                  <Typography sx={{ margin: '0 0 0.25rem', fontWeight: 500, fontSize: '0.875rem' }}>{p.title}</Typography>
                  <Typography sx={{ margin: '0 0 0.125rem', color: '#64748b', fontSize: '0.8125rem' }}>
                    {p.authors.join(', ')} {p.year ? `(${p.year})` : ''} {p.venue ? `— ${p.venue}` : ''}
                  </Typography>
                  <Typography sx={{ margin: '0 0 0.25rem', color: '#4b5563', fontSize: '0.8125rem', fontStyle: 'italic' }}>{p.rationale}</Typography>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => addMutation.mutate(p.doi ? { doi: p.doi } : { title: p.title, authors: p.authors, year: p.year, venue: p.venue })}
                    sx={{ background: '#7c3aed', '&:hover': { background: '#6d28d9' }, fontSize: '0.75rem' }}
                  >
                    + Add as Seed
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </Box>
      )}

      {/* Expert suggestions */}
      {expertSuggestions !== null && (
        <Box sx={{ marginBottom: '1.5rem', padding: '1rem', background: '#f0fdfa', borderRadius: '0.5rem' }}>
          <Typography variant="subtitle2" sx={{ margin: '0 0 0.75rem', color: '#0f766e' }}>Expert AI Suggestions</Typography>
          {expertSuggestions.length === 0 ? (
            <Typography sx={{ color: '#64748b', fontSize: '0.875rem' }}>No suggestions available.</Typography>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {expertSuggestions.map((p, i) => (
                <li key={i} style={{ marginBottom: '0.75rem', paddingBottom: '0.75rem', borderBottom: i < expertSuggestions.length - 1 ? '1px solid #99f6e4' : 'none' }}>
                  <Typography sx={{ margin: '0 0 0.25rem', fontWeight: 500, fontSize: '0.875rem' }}>{p.title}</Typography>
                  <Typography sx={{ margin: '0 0 0.125rem', color: '#64748b', fontSize: '0.8125rem' }}>
                    {p.authors.join(', ')} {p.year ? `(${p.year})` : ''} {p.venue ? `— ${p.venue}` : ''}
                  </Typography>
                  <Typography sx={{ margin: '0 0 0.25rem', color: '#4b5563', fontSize: '0.8125rem', fontStyle: 'italic' }}>{p.rationale}</Typography>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => addMutation.mutate(p.doi ? { doi: p.doi } : { title: p.title, authors: p.authors, year: p.year, venue: p.venue })}
                    sx={{ background: '#0f766e', '&:hover': { background: '#0d6561' }, fontSize: '0.75rem' }}
                  >
                    + Add as Seed
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </Box>
      )}

      {/* Current seeds list */}
      <Typography variant="subtitle2" sx={{ margin: '0 0 0.75rem' }}>Added Seeds ({seeds?.length ?? 0})</Typography>
      {isLoading ? (
        <Typography>Loading…</Typography>
      ) : !seeds || seeds.length === 0 ? (
        <Typography sx={{ color: '#64748b', fontSize: '0.875rem' }}>No seed papers yet.</Typography>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {seeds.map((s) => (
            <li
              key={s.id}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                padding: '0.625rem 0',
                borderBottom: '1px solid #e2e8f0',
              }}
            >
              <Box>
                <Typography sx={{ margin: '0 0 0.125rem', fontWeight: 500, fontSize: '0.875rem' }}>{s.paper.title}</Typography>
                <Typography sx={{ margin: 0, color: '#64748b', fontSize: '0.8125rem' }}>
                  {s.paper.doi ?? 'No DOI'} · Added by {s.added_by}
                </Typography>
              </Box>
              <Button
                onClick={() => deleteMutation.mutate(s.id)}
                sx={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer', flexShrink: 0, marginLeft: '0.5rem', minWidth: 'auto', padding: 0 }}
              >
                ✕
              </Button>
            </li>
          ))}
        </ul>
      )}
    </Box>
  );
}
