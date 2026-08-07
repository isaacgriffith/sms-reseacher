/**
 * Controls for starting a snowball sampling run.
 *
 * Closes the frontend half of G22. `run_snowball` was a complete, registered
 * ARQ job that nothing could start: no endpoint enqueued it and no control
 * reached it, so backward and forward snowballing had never run for a user
 * even though `Study.snowball_threshold` was a setting they could change.
 *
 * Refusals are shown rather than swallowed. A 409 (another automated pass is
 * running) and a 422 (nothing accepted to snowball from) are both ordinary
 * outcomes here, and hiding them leaves a button that appears to do nothing.
 */

import { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

import { api, ApiError } from '../../services/api';

type Direction = 'backward' | 'forward';

interface SnowballResponse {
  job_id: string;
  search_execution_id: number;
  seed_count: number;
}

interface SnowballControlsProps {
  /** The study to snowball for. */
  studyId: number;
  /** Called with the new job id so the progress panel can poll it. */
  onJobStarted: (jobId: string) => void;
}

const DIRECTIONS: { value: Direction; label: string; hint: string }[] = [
  { value: 'backward', label: 'Backward (references)', hint: 'Papers cited by your accepted set' },
  { value: 'forward', label: 'Forward (citations)', hint: 'Papers citing your accepted set' },
];

/**
 * Renders a button per snowball direction, plus the outcome of the last run.
 *
 * @param props - The study id and the job-started callback.
 * @returns The snowball control group.
 */
export default function SnowballControls({ studyId, onJobStarted }: SnowballControlsProps) {
  const [pending, setPending] = useState<Direction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [seedCount, setSeedCount] = useState<number | null>(null);

  const start = async (direction: Direction) => {
    setPending(direction);
    setError(null);
    setSeedCount(null);
    try {
      const res = (await api.post(`/api/v1/studies/${studyId}/snowball`, {
        direction,
      })) as SnowballResponse;
      setSeedCount(res.seed_count);
      onJobStarted(res.job_id);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.detail : 'Could not start the snowball run. Try again.',
      );
    } finally {
      setPending(null);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {DIRECTIONS.map(({ value, label, hint }) => (
          <Button
            key={value}
            variant="outlined"
            size="small"
            disabled={pending !== null}
            title={hint}
            onClick={() => start(value)}
            sx={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
          >
            {pending === value ? `Starting ${value}…` : label}
          </Button>
        ))}
      </Box>
      {seedCount !== null && (
        <Typography variant="body2" sx={{ marginTop: '0.5rem', color: '#64748b' }}>
          Snowballing from {seedCount} seed papers.
        </Typography>
      )}
      {error && (
        <Alert severity="warning" sx={{ marginTop: '0.5rem' }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}
