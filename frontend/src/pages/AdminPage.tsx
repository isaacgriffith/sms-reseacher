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
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';

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
      <Box sx={{ padding: '2rem', color: '#64748b' }}>
        Checking access…
      </Box>
    );
  }

  if (error instanceof ApiError && error.status === 403) {
    return (
      <Box sx={{ padding: '2rem' }}>
        <Typography variant="h5" sx={{ color: '#dc2626', marginBottom: '0.5rem' }}>403 Forbidden</Typography>
        <Typography sx={{ color: '#4b5563' }}>
          You do not have admin access. Only group administrators may view this page.
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate('/groups')}
          sx={{ marginTop: '1rem', padding: '0.5rem 1rem' }}
        >
          Back to Groups
        </Button>
      </Box>
    );
  }

  return (
    <Container maxWidth="md" sx={{ padding: '1.5rem' }}>
      <Typography variant="h5" sx={{ marginTop: 0, marginBottom: '1.5rem', fontSize: '1.375rem', color: '#111827' }}>
        Admin Dashboard
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <ServiceHealthPanel />
        <Divider />
        <JobRetryPanel />
      </Box>
    </Container>
  );
}
