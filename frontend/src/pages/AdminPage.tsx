/**
 * AdminPage: health dashboard and job retry UI for system administrators.
 *
 * Composes ServiceHealthPanel and JobRetryPanel. Redirects non-admins
 * (users who receive HTTP 403 from the health endpoint) to /groups with
 * an access-denied message.
 */

import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api, ApiError } from '../services/api';
import ServiceHealthPanel from '../components/admin/ServiceHealthPanel';
import JobRetryPanel from '../components/admin/JobRetryPanel';

/** Probes admin access by attempting to fetch the health endpoint. */
function useAdminAccess() {
  return useQuery<unknown>({
    queryKey: ['admin', 'access-check'],
    queryFn: () => api.get('/api/v1/admin/health'),
    retry: false,
  });
}

/** Full-page admin dashboard with health and job management panels. */
export default function AdminPage() {
  const navigate = useNavigate();
  const { isLoading, error } = useAdminAccess();

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', color: '#64748b' }}>
        Checking access…
      </div>
    );
  }

  if (error instanceof ApiError && error.status === 403) {
    return (
      <div style={{ padding: '2rem' }}>
        <h2 style={{ color: '#dc2626', marginBottom: '0.5rem' }}>403 Forbidden</h2>
        <p style={{ color: '#4b5563' }}>
          You do not have admin access. Only group administrators may view this page.
        </p>
        <button
          onClick={() => navigate('/groups')}
          style={{
            marginTop: '1rem',
            padding: '0.5rem 1rem',
            background: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer',
          }}
        >
          Back to Groups
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '1.5rem' }}>
      <h2 style={{ marginTop: 0, marginBottom: '1.5rem', fontSize: '1.375rem', color: '#111827' }}>
        Admin Dashboard
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <ServiceHealthPanel />
        <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0' }} />
        <JobRetryPanel />
      </div>
    </div>
  );
}
