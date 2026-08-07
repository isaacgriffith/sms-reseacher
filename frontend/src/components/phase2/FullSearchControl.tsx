/**
 * Control for starting a full database search.
 *
 * Lifted out of `renderSearchAndScreen`, whose click handler caught every error
 * and discarded it. That was survivable while the endpoint only failed on a
 * missing search string; it is not now that the in-flight guard makes 409 an
 * ordinary answer. A refusal the user cannot see is a button that does nothing.
 *
 * Deliberately not merged with `SnowballControls`: the two share a shape but
 * not a payload, and one component taking a request body as a prop would be an
 * abstraction over two cases.
 */

import { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

import { api, ApiError } from '../../services/api';

/** Databases queried when no per-study selection is in play. */
const DEFAULT_DATABASES = ['acm', 'ieee', 'scopus'];

interface FullSearchResponse {
  job_id: string;
  search_execution_id: number;
}

interface FullSearchControlProps {
  /** The study to search for. */
  studyId: number;
  /** Called with the new job id so the progress panel can poll it. */
  onJobStarted: (jobId: string) => void;
}

/**
 * Renders the search trigger and the reason the last attempt was refused.
 *
 * @param props - The study id and the job-started callback.
 * @returns The full-search control.
 */
export default function FullSearchControl({ studyId, onJobStarted }: FullSearchControlProps) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = async () => {
    setPending(true);
    setError(null);
    try {
      const res = (await api.post(`/api/v1/studies/${studyId}/searches`, {
        databases: DEFAULT_DATABASES,
        phase_tag: 'initial-search',
      })) as FullSearchResponse;
      onJobStarted(res.job_id);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Could not start the search. Try again.');
    } finally {
      setPending(false);
    }
  };

  return (
    <Box>
      <Button
        variant="contained"
        size="small"
        disabled={pending}
        onClick={start}
        sx={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
      >
        {pending ? 'Starting…' : 'Run Full Search'}
      </Button>
      {error && (
        <Alert severity="warning" sx={{ marginTop: '0.5rem' }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}
