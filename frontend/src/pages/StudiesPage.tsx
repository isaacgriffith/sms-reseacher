/**
 * Studies page: lists studies for a research group with actions.
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import NewStudyWizard from '../components/studies/NewStudyWizard';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

interface StudySummary {
  id: number;
  name: string;
  topic: string | null;
  study_type: string;
  status: string;
  current_phase: number;
  created_at: string;
}

const PHASE_LABELS: Record<number, string> = {
  1: 'Scoping',
  2: 'Search',
  3: 'Screening',
  4: 'Extraction',
  5: 'Reporting',
};

const STATUS_COLOR: Record<string, string> = {
  active: '#16a34a',
  draft: '#64748b',
  completed: '#2563eb',
  archived: '#9ca3af',
};

export default function StudiesPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showWizard, setShowWizard] = useState(false);

  const { data: studies, isLoading, error } = useQuery<StudySummary[]>({
    queryKey: ['studies', groupId],
    queryFn: () => api.get<StudySummary[]>(`/api/v1/groups/${groupId}/studies`),
    enabled: !!groupId,
  });

  const archiveMutation = useMutation({
    mutationFn: (studyId: number) =>
      api.post<{ status: string }>(`/api/v1/studies/${studyId}/archive`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['studies', groupId] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (studyId: number) => api.delete<void>(`/api/v1/studies/${studyId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['studies', groupId] }),
  });

  if (isLoading) return <Typography>Loading studies…</Typography>;
  if (error) return <Typography sx={{ color: 'red' }}>Failed to load studies.</Typography>;

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.5rem',
        }}
      >
        <Typography variant="h5" sx={{ margin: 0 }}>Studies</Typography>
        <Button
          variant="contained"
          onClick={() => setShowWizard(true)}
          sx={{ padding: '0.5rem 1rem' }}
        >
          New Study
        </Button>
      </Box>

      {showWizard && groupId && (
        <NewStudyWizard
          groupId={parseInt(groupId)}
          onClose={() => setShowWizard(false)}
          onCreated={(studyId) => {
            setShowWizard(false);
            queryClient.invalidateQueries({ queryKey: ['studies', groupId] });
            navigate(`/studies/${studyId}`);
          }}
        />
      )}

      {(!studies || studies.length === 0) ? (
        <Typography sx={{ color: '#475569' }}>No studies yet. Create one to get started.</Typography>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {studies.map((s) => (
            <Box
              key={s.id}
              sx={{
                padding: '1rem 1.25rem',
                border: '1px solid #e2e8f0',
                borderRadius: '0.5rem',
                background: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
              }}
              onClick={() => navigate(`/studies/${s.id}`)}
            >
              <Box>
                <Typography variant="subtitle1" sx={{ margin: '0 0 0.25rem', fontSize: '1rem' }}>{s.name}</Typography>
                {s.topic && (
                  <Typography sx={{ margin: '0 0 0.25rem', color: '#64748b', fontSize: '0.875rem' }}>
                    {s.topic}
                  </Typography>
                )}
                <Box sx={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#64748b' }}>{s.study_type}</Typography>
                  <Typography component="span" sx={{ color: '#cbd5e1' }}>·</Typography>
                  <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#64748b' }}>
                    Phase {s.current_phase}: {PHASE_LABELS[s.current_phase] ?? ''}
                  </Typography>
                  <Typography component="span" sx={{ color: '#cbd5e1' }}>·</Typography>
                  <Typography
                    component="span"
                    sx={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: STATUS_COLOR[s.status] ?? '#64748b',
                      textTransform: 'capitalize',
                    }}
                  >
                    {s.status}
                  </Typography>
                </Box>
              </Box>

              <Box
                sx={{ display: 'flex', gap: '0.5rem' }}
                onClick={(e) => e.stopPropagation()}
              >
                {s.status !== 'archived' && (
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => archiveMutation.mutate(s.id)}
                    sx={{
                      padding: '0.25rem 0.75rem',
                      fontSize: '0.8125rem',
                      color: '#64748b',
                      borderColor: '#cbd5e1',
                    }}
                  >
                    Archive
                  </Button>
                )}
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    if (confirm(`Delete "${s.name}"? This cannot be undone.`)) {
                      deleteMutation.mutate(s.id);
                    }
                  }}
                  sx={{
                    padding: '0.25rem 0.75rem',
                    fontSize: '0.8125rem',
                    color: '#dc2626',
                    borderColor: '#fca5a5',
                  }}
                >
                  Delete
                </Button>
              </Box>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
}
