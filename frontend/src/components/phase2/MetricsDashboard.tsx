/**
 * MetricsDashboard: displays per-phase and total search metrics funnel
 * (identified → accepted → rejected → duplicates) for a study.
 *
 * Consumes GET /studies/{study_id}/metrics
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

interface PhaseMetrics {
  phase_tag: string;
  search_execution_id: number;
  total_identified: number;
  accepted: number;
  rejected: number;
  duplicates: number;
}

interface StudyMetricsResponse {
  study_id: number;
  phases: PhaseMetrics[];
  totals: PhaseMetrics;
}

interface MetricsDashboardProps {
  studyId: number;
}

const BAR_COLORS: Record<string, string> = {
  total_identified: '#3b82f6',
  accepted: '#16a34a',
  rejected: '#dc2626',
  duplicates: '#6b7280',
};

const BAR_LABELS: Record<string, string> = {
  total_identified: 'Identified',
  accepted: 'Accepted',
  rejected: 'Rejected',
  duplicates: 'Duplicates',
};

function FunnelBar({
  label,
  value,
  max,
  color,
}: {
  label: string;
  value: number;
  max: number;
  color: string;
}) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <Box sx={{ marginBottom: '0.5rem' }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.8125rem',
          color: '#374151',
          marginBottom: '0.2rem',
        }}
      >
        <Typography component="span" sx={{ fontSize: '0.8125rem' }}>{label}</Typography>
        <Typography component="span" sx={{ fontWeight: 600, color, fontSize: '0.8125rem' }}>
          {value.toLocaleString()}
          {max > 0 && (
            <Typography component="span" sx={{ fontWeight: 400, color: '#9ca3af', marginLeft: '0.25rem', fontSize: '0.8125rem' }}>
              ({pct}%)
            </Typography>
          )}
        </Typography>
      </Box>
      <Box
        sx={{
          height: '0.5rem',
          background: '#f1f5f9',
          borderRadius: '9999px',
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            width: `${pct}%`,
            height: '100%',
            background: color,
            borderRadius: '9999px',
            transition: 'width 0.3s ease',
          }}
        />
      </Box>
    </Box>
  );
}

function PhaseCard({ phase }: { phase: PhaseMetrics }) {
  const max = phase.total_identified;
  return (
    <Paper
      variant="outlined"
      sx={{
        border: '1px solid #e2e8f0',
        borderRadius: '0.5rem',
        padding: '1rem',
        background: '#fff',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '0.875rem',
        }}
      >
        <Typography variant="subtitle2" sx={{ margin: 0, fontSize: '0.9375rem', color: '#111827' }}>
          {phase.phase_tag === 'all' ? 'All Phases (Totals)' : phase.phase_tag}
        </Typography>
        {phase.phase_tag !== 'all' && (
          <Typography
            component="span"
            sx={{
              fontSize: '0.6875rem',
              color: '#6b7280',
              background: '#f1f5f9',
              padding: '0.125rem 0.375rem',
              borderRadius: '0.25rem',
            }}
          >
            exec #{phase.search_execution_id}
          </Typography>
        )}
      </Box>

      {(['total_identified', 'accepted', 'rejected', 'duplicates'] as const).map((key) => (
        <FunnelBar
          key={key}
          label={BAR_LABELS[key]}
          value={phase[key]}
          max={max}
          color={BAR_COLORS[key]}
        />
      ))}
    </Paper>
  );
}

export default function MetricsDashboard({ studyId }: MetricsDashboardProps) {
  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery<StudyMetricsResponse>({
    queryKey: ['metrics', studyId],
    queryFn: () => api.get<StudyMetricsResponse>(`/api/v1/studies/${studyId}/metrics`),
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <Box sx={{ padding: '1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
        Loading metrics…
      </Box>
    );
  }

  if (isError) {
    return (
      <Box
        sx={{
          padding: '1rem',
          border: '1px solid #fecaca',
          borderRadius: '0.5rem',
          background: '#fef2f2',
          color: '#dc2626',
          fontSize: '0.875rem',
        }}
      >
        Failed to load metrics: {(error as Error)?.message ?? 'Unknown error'}
      </Box>
    );
  }

  if (!data || data.phases.length === 0) {
    return (
      <Box
        sx={{
          padding: '2rem',
          textAlign: 'center',
          color: '#6b7280',
          fontSize: '0.875rem',
          background: '#f8fafc',
          borderRadius: '0.5rem',
          border: '1px solid #e2e8f0',
        }}
      >
        No search metrics yet. Run a search to see the funnel.
      </Box>
    );
  }

  return (
    <Box component="section">
      <Typography variant="subtitle1" sx={{ margin: '0 0 1rem', fontSize: '1rem', color: '#111827', fontWeight: 700 }}>
        Search Metrics
      </Typography>

      {/* Per-phase cards */}
      {data.phases.length > 0 && (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '0.75rem',
            marginBottom: '0.75rem',
          }}
        >
          {data.phases.map((phase) => (
            <PhaseCard key={phase.phase_tag} phase={phase} />
          ))}
        </Box>
      )}

      {/* Totals card (only shown when >1 phase) */}
      {data.phases.length > 1 && (
        <PhaseCard phase={data.totals} />
      )}
    </Box>
  );
}
