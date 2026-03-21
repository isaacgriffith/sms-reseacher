/**
 * DiscussionFlowPanel — Think-Aloud discussion workflow for disagreed papers.
 *
 * Renders when a Kappa record has `threshold_met === false`. Lists disagreed
 * papers one at a time, showing each reviewer's decision side-by-side.
 * Tracks resolved papers with useReducer. Shows "Re-compute Kappa" after all
 * disagreements are resolved.
 */

import React, { memo, useReducer } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';
import type { InterRaterRecord } from '../../services/slr/interRaterApi';
import { usePostDiscussionKappa } from '../../hooks/slr/useInterRater';

// ---------------------------------------------------------------------------
// State management
// ---------------------------------------------------------------------------

interface DisagreementItem {
  paperId: number;
  paperTitle: string;
  decisionA: string;
  decisionB: string;
}

interface FlowState {
  resolved: Set<number>;
}

type FlowAction = { type: 'RESOLVE'; paperId: number } | { type: 'RESET' };

function flowReducer(state: FlowState, action: FlowAction): FlowState {
  switch (action.type) {
    case 'RESOLVE':
      return { resolved: new Set([...state.resolved, action.paperId]) };
    case 'RESET':
      return { resolved: new Set() };
    default:
      return state;
  }
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface DiscussionFlowPanelProps {
  /** The integer study ID. */
  studyId: number;
  /**
   * The Kappa record that triggered this discussion flow
   * (must have `threshold_met === false`).
   */
  record: InterRaterRecord;
  /**
   * List of papers with disagreements to resolve.
   * Callers are responsible for fetching and passing these.
   */
  disagreements: DisagreementItem[];
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface DecisionCellProps {
  label: string;
  decision: string;
}

function DecisionCell({ label, decision }: DecisionCellProps) {
  const color = decision === 'accepted' ? 'success' : 'error';
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Chip label={decision} color={color} size="small" />
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Think-Aloud discussion panel for resolving inter-rater disagreements.
 *
 * @param props - {@link DiscussionFlowPanelProps}
 */
function DiscussionFlowPanel({ studyId, record, disagreements }: DiscussionFlowPanelProps) {
  const [state, dispatch] = useReducer(flowReducer, { resolved: new Set<number>() });
  const postDiscussion = usePostDiscussionKappa(studyId);

  if (!record || record.threshold_met) return null;

  const total = disagreements.length;
  const resolvedCount = state.resolved.size;
  const allResolved = resolvedCount >= total && total > 0;
  const pending = disagreements.filter((d) => !state.resolved.has(d.paperId));

  const handleRecompute = () => {
    postDiscussion.mutate({
      reviewer_a_id: record.reviewer_a_id,
      reviewer_b_id: record.reviewer_b_id,
      round_type: record.round_type,
    });
    dispatch({ type: 'RESET' });
  };

  return (
    <Box
      data-testid="discussion-flow-panel"
      sx={{ border: '1px solid', borderColor: 'warning.main', borderRadius: 1, p: 2 }}
    >
      <Typography variant="subtitle2" color="warning.main" gutterBottom>
        κ below threshold — discuss disagreements
      </Typography>

      <Box sx={{ mb: 1 }}>
        <LinearProgress
          variant="determinate"
          value={total > 0 ? (resolvedCount / total) * 100 : 0}
          aria-label="Resolution progress"
        />
        <Typography variant="caption" color="text.secondary">
          {resolvedCount} of {total} disagreements resolved
        </Typography>
      </Box>

      {pending.map((item) => (
        <Box
          key={item.paperId}
          data-testid={`disagreement-item-${item.paperId}`}
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            py: 1,
            borderBottom: '1px solid',
            borderColor: 'divider',
            gap: 2,
          }}
        >
          <Typography variant="body2" sx={{ flex: 1 }}>
            {item.paperTitle}
          </Typography>
          <DecisionCell label={`Reviewer ${record.reviewer_a_id}`} decision={item.decisionA} />
          <DecisionCell label={`Reviewer ${record.reviewer_b_id}`} decision={item.decisionB} />
          <Button
            size="small"
            variant="outlined"
            onClick={() => dispatch({ type: 'RESOLVE', paperId: item.paperId })}
            data-testid={`resolve-btn-${item.paperId}`}
          >
            Mark resolved
          </Button>
        </Box>
      ))}

      {allResolved && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
          <Alert severity="success" sx={{ flex: 1 }}>
            All disagreements resolved — re-compute Kappa to update the record.
          </Alert>
          <Button
            variant="contained"
            size="small"
            disabled={postDiscussion.isPending}
            onClick={handleRecompute}
            data-testid="recompute-kappa-btn"
          >
            {postDiscussion.isPending ? 'Computing…' : 'Re-compute Kappa'}
          </Button>
        </Box>
      )}
    </Box>
  );
}

export default memo(DiscussionFlowPanel);
