/**
 * InterRaterPanel — displays Cohen's Kappa values per reviewer pair per round.
 *
 * Shows a threshold status badge and a "Compute Kappa" button when both
 * reviewers have completed their independent assessments.
 */

import React, { memo } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Collapse from '@mui/material/Collapse';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import type { InterRaterRecord } from '../../services/slr/interRaterApi';
import { useComputeKappa, useInterRaterRecords } from '../../hooks/slr/useInterRater';

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface ThresholdBadgeProps {
  /** Whether the kappa threshold was met. */
  met: boolean;
}

/** Status badge showing ✓/✗ for threshold. */
function ThresholdBadge({ met }: ThresholdBadgeProps) {
  return (
    <Chip
      label={met ? '✓ Threshold met' : '✗ Below threshold'}
      color={met ? 'success' : 'error'}
      size="small"
      aria-label={met ? 'Threshold met' : 'Below threshold'}
    />
  );
}

interface RecordRowProps {
  record: InterRaterRecord;
}

/** A single table row for an agreement record. */
function RecordRow({ record }: RecordRowProps) {
  const kappaDisplay =
    record.kappa_value !== null
      ? record.kappa_value.toFixed(3)
      : record.kappa_undefined_reason ?? 'Undefined';

  return (
    <TableRow>
      <TableCell>{record.round_type}</TableCell>
      <TableCell>{record.phase}</TableCell>
      <TableCell>
        {record.reviewer_a_id} / {record.reviewer_b_id}
      </TableCell>
      <TableCell>{kappaDisplay}</TableCell>
      <TableCell>{record.n_papers}</TableCell>
      <TableCell>
        <ThresholdBadge met={record.threshold_met} />
      </TableCell>
    </TableRow>
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface InterRaterPanelProps {
  /** The integer study ID. */
  studyId: number;
  /**
   * Pre-filled compute request body (reviewer IDs + round_type) for the
   * "Compute Kappa" button. When provided the button is visible.
   */
  computeBody?: {
    reviewer_a_id: number;
    reviewer_b_id: number;
    round_type: string;
  };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Displays all inter-rater agreement records for a study in a collapsible table.
 *
 * @param props - {@link InterRaterPanelProps}
 */
function InterRaterPanel({ studyId, computeBody }: InterRaterPanelProps) {
  const { data, isLoading, error } = useInterRaterRecords(studyId);
  const compute = useComputeKappa(studyId);

  if (isLoading) return <CircularProgress size={20} aria-label="Loading inter-rater records" />;
  if (error) {
    return (
      <Alert severity="error" data-testid="irr-error">
        Failed to load inter-rater records.
      </Alert>
    );
  }

  const records = data?.records ?? [];

  return (
    <Box data-testid="inter-rater-panel">
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <Typography variant="subtitle2">Inter-Rater Agreement (Cohen's κ)</Typography>
        {computeBody && (
          <Button
            size="small"
            variant="outlined"
            disabled={compute.isPending}
            onClick={() => compute.mutate(computeBody)}
            data-testid="compute-kappa-btn"
          >
            {compute.isPending ? 'Computing…' : 'Compute Kappa'}
          </Button>
        )}
      </Box>

      {compute.isError && (
        <Alert severity="warning" sx={{ mb: 1 }} data-testid="compute-error">
          {(compute.error as Error).message}
        </Alert>
      )}

      <Collapse in={records.length > 0}>
        <Table size="small" aria-label="Inter-rater agreement records">
          <TableHead>
            <TableRow>
              <TableCell>Round</TableCell>
              <TableCell>Phase</TableCell>
              <TableCell>Reviewers</TableCell>
              <TableCell>κ</TableCell>
              <TableCell>Papers</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {records.map((r) => (
              <RecordRow key={r.id} record={r} />
            ))}
          </TableBody>
        </Table>
      </Collapse>

      {records.length === 0 && (
        <Typography variant="body2" color="text.secondary" data-testid="irr-empty">
          No Kappa values computed yet. Use "Compute Kappa" after both reviewers
          have completed their independent assessments.
        </Typography>
      )}
    </Box>
  );
}

export default memo(InterRaterPanel);
