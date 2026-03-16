/**
 * Authenticated API documentation page using Swagger UI.
 * Fetches the OpenAPI schema from the backend (requires valid JWT).
 */

import { useQuery } from '@tanstack/react-query';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';

import { api } from '../../services/api';

async function fetchOpenApiSpec(): Promise<object> {
  return api.get<object>('/api/v1/openapi.json');
}

export default function APIDocsPage() {
  const { data: spec, isLoading, isError, error } = useQuery({
    queryKey: ['openapi-spec'],
    queryFn: fetchOpenApiSpec,
    staleTime: 60_000,
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 4 }}>
        <CircularProgress size={24} />
        <Typography>Loading API documentation…</Typography>
      </Box>
    );
  }

  if (isError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Failed to load API documentation: {(error as Error).message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 0 }}>
      <SwaggerUI spec={spec} />
    </Box>
  );
}
