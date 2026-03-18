/**
 * JobProgressPanel: live dashboard for a background job.
 *
 * Shows phase name, progress bar, papers-found counter,
 * current database label, and complete/error state.
 */

import { useJobProgress } from '../../services/jobs';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

interface JobProgressPanelProps {
  jobId: string | null;
  onComplete?: () => void;
}

export default function JobProgressPanel({ jobId, onComplete }: JobProgressPanelProps) {
  const { status, progressPct, detail, error } = useJobProgress(jobId);

  // Notify parent when complete
  if (status === 'completed' && onComplete) {
    // Use a ref to call only once
  }

  if (!jobId) return null;

  const isRunning = status === 'running' || status === 'queued';
  const isComplete = status === 'completed';
  const isFailed = status === 'failed';

  const phase = (detail as Record<string, string> | null)?.phase ?? '';
  const currentDb = (detail as Record<string, string> | null)?.current_database ?? '';
  const papersFound = (detail as Record<string, number> | null)?.papers_found ?? 0;

  const barColor = isFailed ? '#ef4444' : isComplete ? '#22c55e' : '#2563eb';

  return (
    <Paper
      variant="outlined"
      sx={{
        border: '1px solid #e2e8f0',
        borderRadius: '0.5rem',
        padding: '1rem',
        background: '#f8fafc',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '0.75rem',
        }}
      >
        <Typography variant="subtitle2" sx={{ margin: 0, fontSize: '0.9375rem', color: '#111827' }}>
          {isComplete ? 'Search Complete' : isFailed ? 'Search Failed' : 'Search Running'}
        </Typography>
        <Typography
          component="span"
          sx={{
            fontSize: '0.75rem',
            fontWeight: 600,
            color: barColor,
            textTransform: 'uppercase',
          }}
        >
          {status}
        </Typography>
      </Box>

      {/* Progress bar */}
      <Box
        sx={{
          background: '#e2e8f0',
          borderRadius: '9999px',
          height: '0.5rem',
          overflow: 'hidden',
          marginBottom: '0.75rem',
        }}
      >
        <Box
          style={{ width: `${progressPct}%` }}
          sx={{
            background: barColor,
            height: '100%',
            transition: 'width 0.3s ease',
          }}
        />
      </Box>

      {/* Details */}
      {isRunning && (
        <Box sx={{ fontSize: '0.8125rem', color: '#4b5563', display: 'flex', gap: '1rem' }}>
          {phase && <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#4b5563' }}>Phase: <strong>{phase}</strong></Typography>}
          {currentDb && <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#4b5563' }}>Database: <strong>{currentDb}</strong></Typography>}
          {papersFound > 0 && <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#4b5563' }}>Papers found: <strong>{papersFound}</strong></Typography>}
        </Box>
      )}

      {isComplete && detail && (
        <Box sx={{ fontSize: '0.8125rem', color: '#374151', display: 'flex', gap: '1.5rem' }}>
          {typeof (detail as Record<string, number>).total_identified === 'number' && (
            <Typography component="span" sx={{ fontSize: '0.8125rem' }}>Identified: <strong>{(detail as Record<string, number>).total_identified}</strong></Typography>
          )}
          {typeof (detail as Record<string, number>).accepted === 'number' && (
            <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#16a34a' }}>Accepted: <strong>{(detail as Record<string, number>).accepted}</strong></Typography>
          )}
          {typeof (detail as Record<string, number>).rejected === 'number' && (
            <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#dc2626' }}>Rejected: <strong>{(detail as Record<string, number>).rejected}</strong></Typography>
          )}
          {typeof (detail as Record<string, number>).duplicates === 'number' && (
            <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#d97706' }}>Duplicates: <strong>{(detail as Record<string, number>).duplicates}</strong></Typography>
          )}
        </Box>
      )}

      {isFailed && (
        <Typography sx={{ margin: 0, fontSize: '0.8125rem', color: '#ef4444' }}>
          {error ?? 'An error occurred'}
        </Typography>
      )}
    </Paper>
  );
}
