/**
 * JobRetryPanel: lists failed background jobs across all studies and provides
 * a retry button for each. Calls POST /admin/jobs/{id}/retry on click.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';

interface AdminJob {
  id: string;
  study_id: number;
  job_type: string;
  status: string;
  error_message: string | null;
  queued_at: string;
  completed_at: string | null;
}

interface AdminJobPage {
  items: AdminJob[];
  total: number;
  page: number;
  page_size: number;
}

interface RetryResponse {
  new_job_id: string;
  original_job_id: string;
}

interface RetryResultBannerProps {
  originalId: string;
  newId: string;
  onDismiss: () => void;
}

/** Confirmation banner displayed after a successful retry. */
function RetryResultBanner({ originalId, newId, onDismiss }: RetryResultBannerProps) {
  return (
    <Box
      sx={{
        padding: '0.75rem 1rem',
        background: '#f0fdf4',
        border: '1px solid #bbf7d0',
        borderRadius: '0.375rem',
        fontSize: '0.875rem',
        color: '#15803d',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}
    >
      <Typography component="span" sx={{ fontSize: '0.875rem', color: '#15803d' }}>
        Retried job <code>{originalId.slice(-8)}</code>. New job ID:{' '}
        <code>{newId.slice(-8)}</code>
      </Typography>
      <Button
        onClick={onDismiss}
        sx={{ background: 'none', border: 'none', cursor: 'pointer', color: '#15803d', fontSize: '1rem', minWidth: 'auto', padding: 0 }}
      >
        ✕
      </Button>
    </Box>
  );
}

interface JobRowProps {
  job: AdminJob;
  onRetry: (id: string) => void;
  isRetrying: boolean;
}

/** Single failed job row. */
function JobRow({ job, onRetry, isRetrying }: JobRowProps) {
  return (
    <Paper
      variant="outlined"
      sx={{
        padding: '0.875rem 1rem',
        border: '1px solid #fecaca',
        borderRadius: '0.5rem',
        background: '#fff',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: '1rem',
      }}
    >
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Box sx={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.25rem' }}>
          <Typography component="span" sx={{ fontWeight: 600, fontSize: '0.875rem', color: '#111827' }}>
            {job.job_type}
          </Typography>
          <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#6b7280' }}>
            Study #{job.study_id}
          </Typography>
          <Typography component="span" sx={{ fontSize: '0.75rem', color: '#9ca3af' }}>
            ID: …{job.id.slice(-8)}
          </Typography>
        </Box>
        {job.error_message && (
          <Typography sx={{ margin: 0, fontSize: '0.8125rem', color: '#dc2626', wordBreak: 'break-word' }}>
            {job.error_message}
          </Typography>
        )}
        <Typography sx={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: '#9ca3af' }}>
          Queued: {new Date(job.queued_at).toLocaleString()}
        </Typography>
      </Box>
      <Button
        variant="contained"
        size="small"
        onClick={() => onRetry(job.id)}
        disabled={isRetrying}
        sx={{
          padding: '0.375rem 0.75rem',
          background: isRetrying ? '#f1f5f9' : '#2563eb',
          color: isRetrying ? '#94a3b8' : '#fff',
          fontSize: '0.8125rem',
          whiteSpace: 'nowrap',
        }}
      >
        {isRetrying ? 'Retrying…' : 'Retry'}
      </Button>
    </Paper>
  );
}

/** Lists failed jobs and allows admins to re-enqueue them. */
export default function JobRetryPanel() {
  const queryClient = useQueryClient();
  const [retryResult, setRetryResult] = useState<RetryResponse | null>(null);
  const [retryingId, setRetryingId] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery<AdminJobPage>({
    queryKey: ['admin', 'jobs', 'failed'],
    queryFn: () => api.get<AdminJobPage>('/api/v1/admin/jobs?status=failed&page_size=50'),
  });

  const retryMutation = useMutation({
    mutationFn: (jobId: string) =>
      api.post<RetryResponse>(`/api/v1/admin/jobs/${jobId}/retry`, {}),
    onSuccess: (result) => {
      setRetryResult(result);
      setRetryingId(null);
      queryClient.invalidateQueries({ queryKey: ['admin', 'jobs'] });
    },
    onError: () => setRetryingId(null),
  });

  const handleRetry = (jobId: string) => {
    setRetryingId(jobId);
    retryMutation.mutate(jobId);
  };

  if (isLoading) return <Typography sx={{ color: '#64748b' }}>Loading failed jobs…</Typography>;
  if (error) return <Typography sx={{ color: '#dc2626' }}>Failed to load jobs.</Typography>;

  const jobs = data?.items ?? [];

  return (
    <Box component="section">
      <Typography variant="subtitle1" sx={{ margin: '0 0 0.75rem', fontSize: '1.0625rem' }}>
        Failed Jobs {data && `(${data.total})`}
      </Typography>

      {retryResult && (
        <Box sx={{ marginBottom: '0.75rem' }}>
          <RetryResultBanner
            originalId={retryResult.original_job_id}
            newId={retryResult.new_job_id}
            onDismiss={() => setRetryResult(null)}
          />
        </Box>
      )}

      {jobs.length === 0 ? (
        <Typography sx={{ color: '#16a34a', fontSize: '0.9375rem' }}>No failed jobs. All systems running.</Typography>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {jobs.map((job) => (
            <JobRow
              key={job.id}
              job={job}
              onRetry={handleRetry}
              isRetrying={retryingId === job.id && retryMutation.isPending}
            />
          ))}
        </Box>
      )}
    </Box>
  );
}
