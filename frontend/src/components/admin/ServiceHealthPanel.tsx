/**
 * ServiceHealthPanel: polls GET /admin/health every 30 s and displays
 * color-coded status cards for each system service.
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

interface ServiceHealth {
  name: string;
  status: string;
  latency_ms?: number;
  detail?: string;
}

interface HealthResponse {
  status: string;
  services: ServiceHealth[];
  checked_at: string;
}

/** Colour mapping from status string to a CSS colour token. */
const STATUS_COLOR: Record<string, string> = {
  healthy: '#16a34a',
  degraded: '#d97706',
  unhealthy: '#dc2626',
};

interface StatusBadgeProps {
  status: string;
}

/** Inline badge showing a service health status. */
function StatusBadge({ status }: StatusBadgeProps) {
  const color = STATUS_COLOR[status] ?? '#64748b';
  return (
    <Typography
      component="span"
      sx={{
        display: 'inline-block',
        padding: '0.125rem 0.5rem',
        borderRadius: '9999px',
        background: `${color}20`,
        color,
        fontSize: '0.75rem',
        fontWeight: 700,
        textTransform: 'uppercase',
      }}
    >
      {status}
    </Typography>
  );
}

interface ServiceCardProps {
  service: ServiceHealth;
}

/** Single service health card. */
function ServiceCard({ service }: ServiceCardProps) {
  return (
    <Paper
      variant="outlined"
      sx={{
        padding: '0.875rem 1rem',
        border: `1px solid ${STATUS_COLOR[service.status] ?? '#e2e8f0'}40`,
        borderLeft: `4px solid ${STATUS_COLOR[service.status] ?? '#94a3b8'}`,
        borderRadius: '0.5rem',
        background: '#fff',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography component="span" sx={{ fontWeight: 600, fontSize: '0.9375rem', color: '#111827' }}>
          {service.name}
        </Typography>
        <StatusBadge status={service.status} />
      </Box>
      {service.latency_ms != null && (
        <Typography sx={{ margin: '0.25rem 0 0', fontSize: '0.8125rem', color: '#6b7280' }}>
          Latency: {service.latency_ms} ms
        </Typography>
      )}
      {service.detail && (
        <Typography sx={{ margin: '0.25rem 0 0', fontSize: '0.8125rem', color: '#6b7280' }}>
          {service.detail}
        </Typography>
      )}
    </Paper>
  );
}

/** Polls /admin/health every 30 s and renders per-service status cards. */
export default function ServiceHealthPanel() {
  const { data, isLoading, error, dataUpdatedAt } = useQuery<HealthResponse>({
    queryKey: ['admin', 'health'],
    queryFn: () => api.get<HealthResponse>('/api/v1/admin/health'),
    refetchInterval: 30_000,
  });

  if (isLoading) {
    return <Typography sx={{ color: '#64748b' }}>Probing services…</Typography>;
  }

  if (error) {
    return (
      <Typography sx={{ color: '#dc2626' }}>
        Failed to load health data. Check that you have admin access.
      </Typography>
    );
  }

  const lastChecked = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString()
    : '—';

  return (
    <Box component="section">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.75rem' }}>
        <Typography variant="subtitle1" sx={{ margin: 0, fontSize: '1.0625rem' }}>Service Health</Typography>
        <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#64748b' }}>
          Last checked: {lastChecked}
          {data && <> · Overall: <StatusBadge status={data.status} /></>}
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {data?.services.map((svc) => (
          <ServiceCard key={svc.name} service={svc} />
        ))}
      </Box>
    </Box>
  );
}
