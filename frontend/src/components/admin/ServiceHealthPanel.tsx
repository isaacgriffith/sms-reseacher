/**
 * ServiceHealthPanel: polls GET /admin/health every 30 s and displays
 * color-coded status cards for each system service.
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';

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
    <span
      style={{
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
    </span>
  );
}

interface ServiceCardProps {
  service: ServiceHealth;
}

/** Single service health card. */
function ServiceCard({ service }: ServiceCardProps) {
  return (
    <div
      style={{
        padding: '0.875rem 1rem',
        border: `1px solid ${STATUS_COLOR[service.status] ?? '#e2e8f0'}40`,
        borderLeft: `4px solid ${STATUS_COLOR[service.status] ?? '#94a3b8'}`,
        borderRadius: '0.5rem',
        background: '#fff',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontWeight: 600, fontSize: '0.9375rem', color: '#111827' }}>
          {service.name}
        </span>
        <StatusBadge status={service.status} />
      </div>
      {service.latency_ms != null && (
        <p style={{ margin: '0.25rem 0 0', fontSize: '0.8125rem', color: '#6b7280' }}>
          Latency: {service.latency_ms} ms
        </p>
      )}
      {service.detail && (
        <p style={{ margin: '0.25rem 0 0', fontSize: '0.8125rem', color: '#6b7280' }}>
          {service.detail}
        </p>
      )}
    </div>
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
    return <p style={{ color: '#64748b' }}>Probing services…</p>;
  }

  if (error) {
    return (
      <p style={{ color: '#dc2626' }}>
        Failed to load health data. Check that you have admin access.
      </p>
    );
  }

  const lastChecked = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString()
    : '—';

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.75rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.0625rem' }}>Service Health</h3>
        <span style={{ fontSize: '0.8125rem', color: '#64748b' }}>
          Last checked: {lastChecked}
          {data && <> · Overall: <StatusBadge status={data.status} /></>}
        </span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {data?.services.map((svc) => (
          <ServiceCard key={svc.name} service={svc} />
        ))}
      </div>
    </section>
  );
}
