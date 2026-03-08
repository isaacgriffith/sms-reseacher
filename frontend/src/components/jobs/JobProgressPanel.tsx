/**
 * JobProgressPanel: live dashboard for a background job.
 *
 * Shows phase name, progress bar, papers-found counter,
 * current database label, and complete/error state.
 */

import { useJobProgress } from '../../services/jobs';

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
    <div
      style={{
        border: '1px solid #e2e8f0',
        borderRadius: '0.5rem',
        padding: '1rem',
        background: '#f8fafc',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '0.75rem',
        }}
      >
        <h4 style={{ margin: 0, fontSize: '0.9375rem', color: '#111827' }}>
          {isComplete ? 'Search Complete' : isFailed ? 'Search Failed' : 'Search Running'}
        </h4>
        <span
          style={{
            fontSize: '0.75rem',
            fontWeight: 600,
            color: barColor,
            textTransform: 'uppercase',
          }}
        >
          {status}
        </span>
      </div>

      {/* Progress bar */}
      <div
        style={{
          background: '#e2e8f0',
          borderRadius: '9999px',
          height: '0.5rem',
          overflow: 'hidden',
          marginBottom: '0.75rem',
        }}
      >
        <div
          style={{
            background: barColor,
            height: '100%',
            width: `${progressPct}%`,
            transition: 'width 0.3s ease',
          }}
        />
      </div>

      {/* Details */}
      {isRunning && (
        <div style={{ fontSize: '0.8125rem', color: '#4b5563', display: 'flex', gap: '1rem' }}>
          {phase && <span>Phase: <strong>{phase}</strong></span>}
          {currentDb && <span>Database: <strong>{currentDb}</strong></span>}
          {papersFound > 0 && <span>Papers found: <strong>{papersFound}</strong></span>}
        </div>
      )}

      {isComplete && detail && (
        <div style={{ fontSize: '0.8125rem', color: '#374151', display: 'flex', gap: '1.5rem' }}>
          {typeof (detail as Record<string, number>).total_identified === 'number' && (
            <span>Identified: <strong>{(detail as Record<string, number>).total_identified}</strong></span>
          )}
          {typeof (detail as Record<string, number>).accepted === 'number' && (
            <span style={{ color: '#16a34a' }}>Accepted: <strong>{(detail as Record<string, number>).accepted}</strong></span>
          )}
          {typeof (detail as Record<string, number>).rejected === 'number' && (
            <span style={{ color: '#dc2626' }}>Rejected: <strong>{(detail as Record<string, number>).rejected}</strong></span>
          )}
          {typeof (detail as Record<string, number>).duplicates === 'number' && (
            <span style={{ color: '#d97706' }}>Duplicates: <strong>{(detail as Record<string, number>).duplicates}</strong></span>
          )}
        </div>
      )}

      {isFailed && (
        <p style={{ margin: 0, fontSize: '0.8125rem', color: '#ef4444' }}>
          {error ?? 'An error occurred'}
        </p>
      )}
    </div>
  );
}
