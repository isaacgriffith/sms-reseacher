/**
 * ReviewerPanel: submit accept/reject/duplicate decisions with reason selector
 * from the study's criteria list and override annotation.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';

interface Criterion {
  id: number;
  description: string;
  order_index: number;
}

interface PriorDecision {
  id: number;
  decision: string;
  reasons?: Array<{ criterion_id?: number; criterion_type?: string; text: string }>;
  decided_at?: string | null;
}

type ConflictState =
  | { kind: 'stale_state'; observedStatus: string; currentStatus: string }
  | { kind: 'unacknowledged_prior_decision'; priorDecision: PriorDecision }
  | null;

interface DecisionRequestBody {
  reviewer_id: number;
  decision: string;
  reasons: object[];
  observed_status: string;
  overrides_decision_id?: number;
}

interface ReviewerPanelProps {
  studyId: number;
  candidateId: number;
  /** The candidate's current_status as shown to the reviewer; sent as observed_status. */
  observedStatus: string;
  /** Set when this submission supersedes the reviewer's own earlier decision. */
  overridesDecisionId?: number | null;
  onDecisionSubmitted?: () => void;
}

type DecisionType = 'accepted' | 'rejected' | 'duplicate';

const DECISION_STYLES: Record<DecisionType, { bg: string; text: string; border: string }> = {
  accepted: { bg: '#dcfce7', text: '#16a34a', border: '#16a34a' },
  rejected: { bg: '#fee2e2', text: '#dc2626', border: '#dc2626' },
  duplicate: { bg: '#f3f4f6', text: '#6b7280', border: '#6b7280' },
};

export default function ReviewerPanel({
  studyId,
  candidateId,
  observedStatus,
  overridesDecisionId,
  onDecisionSubmitted,
}: ReviewerPanelProps) {
  const qc = useQueryClient();

  const [selectedDecision, setSelectedDecision] = useState<DecisionType | null>(null);
  const [selectedReasons, setSelectedReasons] = useState<number[]>([]);
  const [annotationText, setAnnotationText] = useState('');
  const [reviewerId, setReviewerId] = useState<number | null>(null);
  const [conflict, setConflict] = useState<ConflictState>(null);

  const { data: inclusion = [] } = useQuery<Criterion[]>({
    queryKey: ['criteria', studyId, 'inclusion'],
    queryFn: () => api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/inclusion`),
  });

  const { data: exclusion = [] } = useQuery<Criterion[]>({
    queryKey: ['criteria', studyId, 'exclusion'],
    queryFn: () => api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/exclusion`),
  });

  const submitDecision = useMutation({
    mutationFn: (body: DecisionRequestBody) =>
      api.post(`/api/v1/studies/${studyId}/papers/${candidateId}/decisions`, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['decisions', studyId, candidateId] });
      qc.invalidateQueries({ queryKey: ['papers', studyId] });
      setSelectedDecision(null);
      setSelectedReasons([]);
      setAnnotationText('');
      setConflict(null);
      onDecisionSubmitted?.();
    },
    onError: (err: unknown) => {
      if (!(err instanceof ApiError) || err.status !== 409) return;
      const detail = err.detail as unknown as
        | { error: 'stale_state'; observed_status: string; current_status: string }
        | { error: 'unacknowledged_prior_decision'; prior_decision: PriorDecision }
        | undefined;
      if (detail?.error === 'stale_state') {
        setConflict({
          kind: 'stale_state',
          observedStatus: detail.observed_status,
          currentStatus: detail.current_status,
        });
      } else if (detail?.error === 'unacknowledged_prior_decision') {
        setConflict({
          kind: 'unacknowledged_prior_decision',
          priorDecision: detail.prior_decision,
        });
      }
    },
  });

  const buildReasons = (): object[] => [
    ...selectedReasons.map((id) => {
      const inc = inclusion.find((c) => c.id === id);
      const exc = exclusion.find((c) => c.id === id);
      return {
        criterion_id: id,
        criterion_type: inc ? 'inclusion' : 'exclusion',
        text: (inc ?? exc)?.description ?? '',
      };
    }),
    ...(annotationText.trim()
      ? [{ criterion_type: 'annotation', text: annotationText.trim() }]
      : []),
  ];

  const performSubmit = (opts?: {
    observedStatusOverride?: string;
    overridesDecisionIdOverride?: number;
  }) => {
    if (!selectedDecision || reviewerId === null) return;

    const effectiveOverrideId = opts?.overridesDecisionIdOverride ?? overridesDecisionId;

    const body: DecisionRequestBody = {
      reviewer_id: reviewerId,
      decision: selectedDecision,
      reasons: buildReasons(),
      observed_status: opts?.observedStatusOverride ?? observedStatus,
      ...(effectiveOverrideId != null ? { overrides_decision_id: effectiveOverrideId } : {}),
    };

    submitDecision.mutate(body);
  };

  const handleSubmit = () => performSubmit();

  const handleConfirmStale = () => {
    if (conflict?.kind !== 'stale_state') return;
    performSubmit({ observedStatusOverride: conflict.currentStatus });
  };

  const handleConfirmOverride = () => {
    if (conflict?.kind !== 'unacknowledged_prior_decision') return;
    performSubmit({ overridesDecisionIdOverride: conflict.priorDecision.id });
  };

  const toggleReason = (id: number) => {
    setSelectedReasons((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const canSubmit = selectedDecision !== null && reviewerId !== null && !submitDecision.isPending;

  return (
    <Box
      data-testid="reviewer-panel"
      sx={{
        border: '1px solid #e2e8f0',
        borderRadius: '0.5rem',
        padding: '1rem',
        background: '#f8fafc',
      }}
    >
      <Typography
        variant="subtitle2"
        sx={{ margin: '0 0 0.875rem', fontSize: '0.9375rem', color: '#111827' }}
      >
        Submit Decision
      </Typography>

      {/* Reviewer ID input (simplified — in real use would be populated from auth context) */}
      <Box sx={{ marginBottom: '0.875rem' }}>
        <Typography
          component="label"
          sx={{
            display: 'block',
            fontSize: '0.8125rem',
            fontWeight: 600,
            color: '#374151',
            marginBottom: '0.375rem',
          }}
        >
          Reviewer ID
        </Typography>
        <TextField
          type="number"
          value={reviewerId ?? ''}
          onChange={(e) => setReviewerId(e.target.value ? Number(e.target.value) : null)}
          placeholder="Enter reviewer ID…"
          size="small"
          fullWidth
        />
      </Box>

      {/* Decision buttons */}
      <Box sx={{ marginBottom: '0.875rem' }}>
        <Typography
          component="label"
          sx={{
            display: 'block',
            fontSize: '0.8125rem',
            fontWeight: 600,
            color: '#374151',
            marginBottom: '0.375rem',
          }}
        >
          Decision
        </Typography>
        <Box sx={{ display: 'flex', gap: '0.5rem' }}>
          {(['accepted', 'rejected', 'duplicate'] as DecisionType[]).map((d) => {
            const style = DECISION_STYLES[d];
            const isSelected = selectedDecision === d;
            return (
              <Button
                key={d}
                onClick={() => setSelectedDecision(isSelected ? null : d)}
                variant="outlined"
                sx={{
                  padding: '0.5rem 1rem',
                  background: isSelected ? style.text : '#fff',
                  color: isSelected ? '#fff' : style.text,
                  border: `2px solid ${style.border}`,
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  textTransform: 'capitalize',
                  '&:hover': {
                    background: isSelected ? style.text : style.bg,
                    border: `2px solid ${style.border}`,
                  },
                }}
              >
                {d}
              </Button>
            );
          })}
        </Box>
      </Box>

      {/* Criteria reason selector */}
      {selectedDecision && (inclusion.length > 0 || exclusion.length > 0) && (
        <Box sx={{ marginBottom: '0.875rem' }}>
          <Typography
            component="label"
            sx={{
              display: 'block',
              fontSize: '0.8125rem',
              fontWeight: 600,
              color: '#374151',
              marginBottom: '0.375rem',
            }}
          >
            Reasons (select criteria)
          </Typography>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              gap: '0.375rem',
              maxHeight: '160px',
              overflowY: 'auto',
            }}
          >
            {inclusion.length > 0 && (
              <Box>
                <Typography
                  sx={{
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    color: '#9ca3af',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    padding: '0.25rem 0',
                  }}
                >
                  Inclusion Criteria
                </Typography>
                {inclusion.map((c) => (
                  <CriterionCheckbox
                    key={c.id}
                    criterion={c}
                    checked={selectedReasons.includes(c.id)}
                    onChange={() => toggleReason(c.id)}
                  />
                ))}
              </Box>
            )}
            {exclusion.length > 0 && (
              <Box>
                <Typography
                  sx={{
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    color: '#9ca3af',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    padding: '0.25rem 0',
                  }}
                >
                  Exclusion Criteria
                </Typography>
                {exclusion.map((c) => (
                  <CriterionCheckbox
                    key={c.id}
                    criterion={c}
                    checked={selectedReasons.includes(c.id)}
                    onChange={() => toggleReason(c.id)}
                  />
                ))}
              </Box>
            )}
          </Box>
        </Box>
      )}

      {/* Re-confirmation prompts (FR-025 / FR-022) — entered state above is preserved */}
      {conflict?.kind === 'stale_state' && (
        <Box
          data-testid="stale-state-prompt"
          sx={{
            marginBottom: '0.875rem',
            padding: '0.75rem',
            background: '#fef3c7',
            border: '1px solid #fbbf24',
            borderRadius: '0.375rem',
          }}
        >
          <Typography sx={{ fontSize: '0.8125rem', color: '#92400e', marginBottom: '0.5rem' }}>
            This paper changed since you loaded it — its status is now &quot;
            {conflict.currentStatus}
            &quot; (you saw &quot;{conflict.observedStatus}&quot;). Your entered decision and notes
            are kept; confirm to resubmit against the current state.
          </Typography>
          <Button
            variant="contained"
            size="small"
            onClick={handleConfirmStale}
            sx={{ fontSize: '0.8125rem' }}
          >
            Confirm and resubmit
          </Button>
        </Box>
      )}

      {conflict?.kind === 'unacknowledged_prior_decision' && (
        <Box
          data-testid="prior-decision-prompt"
          sx={{
            marginBottom: '0.875rem',
            padding: '0.75rem',
            background: '#fef3c7',
            border: '1px solid #fbbf24',
            borderRadius: '0.375rem',
          }}
        >
          <Typography sx={{ fontSize: '0.8125rem', color: '#92400e', marginBottom: '0.5rem' }}>
            You already recorded &quot;{conflict.priorDecision.decision}&quot; for this paper. Your
            entered decision and notes are kept; confirm to override your earlier decision.
          </Typography>
          <Button
            variant="contained"
            size="small"
            onClick={handleConfirmOverride}
            sx={{ fontSize: '0.8125rem' }}
          >
            Confirm override
          </Button>
        </Box>
      )}

      {/* Override annotation */}
      <Box sx={{ marginBottom: '0.875rem' }}>
        <Typography
          component="label"
          sx={{
            display: 'block',
            fontSize: '0.8125rem',
            fontWeight: 600,
            color: '#374151',
            marginBottom: '0.375rem',
          }}
        >
          Additional notes / override annotation
        </Typography>
        <TextField
          value={annotationText}
          onChange={(e) => setAnnotationText(e.target.value)}
          placeholder="Optional annotation…"
          multiline
          rows={2}
          fullWidth
          size="small"
        />
      </Box>

      {/* Submit */}
      <Button
        variant="contained"
        onClick={handleSubmit}
        disabled={!canSubmit}
        sx={{
          padding: '0.5rem 1.25rem',
          background: canSubmit ? '#2563eb' : '#93c5fd',
          fontSize: '0.875rem',
          fontWeight: 600,
        }}
      >
        {submitDecision.isPending ? 'Submitting…' : 'Submit Decision'}
      </Button>

      {submitDecision.isError && !conflict && (
        <Typography sx={{ margin: '0.5rem 0 0', color: '#ef4444', fontSize: '0.8125rem' }}>
          Failed to submit decision. Please try again.
        </Typography>
      )}

      {submitDecision.isSuccess && (
        <Typography sx={{ margin: '0.5rem 0 0', color: '#16a34a', fontSize: '0.8125rem' }}>
          Decision submitted.
        </Typography>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function CriterionCheckbox({
  criterion,
  checked,
  onChange,
}: {
  criterion: Criterion;
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <label
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.375rem',
        cursor: 'pointer',
        padding: '0.1875rem 0',
      }}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        style={{ flexShrink: 0, marginTop: '2px' }}
      />
      <Typography component="span" sx={{ fontSize: '0.8125rem', color: '#374151' }}>
        {criterion.description}
      </Typography>
    </label>
  );
}
