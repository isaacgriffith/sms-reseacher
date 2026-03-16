/**
 * ReviewerPanel: submit accept/reject/duplicate decisions with reason selector
 * from the study's criteria list and override annotation.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';

interface Criterion {
  id: number;
  description: string;
  order_index: number;
}

interface ReviewerPanelProps {
  studyId: number;
  candidateId: number;
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
  onDecisionSubmitted,
}: ReviewerPanelProps) {
  const qc = useQueryClient();

  const [selectedDecision, setSelectedDecision] = useState<DecisionType | null>(null);
  const [selectedReasons, setSelectedReasons] = useState<number[]>([]);
  const [annotationText, setAnnotationText] = useState('');
  const [reviewerId, setReviewerId] = useState<number | null>(null);

  const { data: inclusion = [] } = useQuery<Criterion[]>({
    queryKey: ['criteria', studyId, 'inclusion'],
    queryFn: () =>
      api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/inclusion`),
  });

  const { data: exclusion = [] } = useQuery<Criterion[]>({
    queryKey: ['criteria', studyId, 'exclusion'],
    queryFn: () =>
      api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/exclusion`),
  });

  const submitDecision = useMutation({
    mutationFn: (body: {
      reviewer_id: number;
      decision: string;
      reasons: object[];
    }) =>
      api.post(
        `/api/v1/studies/${studyId}/papers/${candidateId}/decisions`,
        body
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['decisions', studyId, candidateId] });
      qc.invalidateQueries({ queryKey: ['papers', studyId] });
      setSelectedDecision(null);
      setSelectedReasons([]);
      setAnnotationText('');
      onDecisionSubmitted?.();
    },
  });

  const handleSubmit = () => {
    if (!selectedDecision || reviewerId === null) return;

    const reasons: object[] = [
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

    submitDecision.mutate({ reviewer_id: reviewerId, decision: selectedDecision, reasons });
  };

  const toggleReason = (id: number) => {
    setSelectedReasons((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const canSubmit =
    selectedDecision !== null &&
    reviewerId !== null &&
    !submitDecision.isPending;

  return (
    <Box
      sx={{
        border: '1px solid #e2e8f0',
        borderRadius: '0.5rem',
        padding: '1rem',
        background: '#f8fafc',
      }}
    >
      <Typography variant="subtitle2" sx={{ margin: '0 0 0.875rem', fontSize: '0.9375rem', color: '#111827' }}>
        Submit Decision
      </Typography>

      {/* Reviewer ID input (simplified — in real use would be populated from auth context) */}
      <Box sx={{ marginBottom: '0.875rem' }}>
        <Typography component="label" sx={{ display: 'block', fontSize: '0.8125rem', fontWeight: 600, color: '#374151', marginBottom: '0.375rem' }}>
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
        <Typography component="label" sx={{ display: 'block', fontSize: '0.8125rem', fontWeight: 600, color: '#374151', marginBottom: '0.375rem' }}>
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
          <Typography component="label" sx={{ display: 'block', fontSize: '0.8125rem', fontWeight: 600, color: '#374151', marginBottom: '0.375rem' }}>
            Reasons (select criteria)
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', maxHeight: '160px', overflowY: 'auto' }}>
            {inclusion.length > 0 && (
              <Box>
                <Typography sx={{ fontSize: '0.6875rem', fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', padding: '0.25rem 0' }}>Inclusion Criteria</Typography>
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
                <Typography sx={{ fontSize: '0.6875rem', fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', padding: '0.25rem 0' }}>Exclusion Criteria</Typography>
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

      {/* Override annotation */}
      <Box sx={{ marginBottom: '0.875rem' }}>
        <Typography component="label" sx={{ display: 'block', fontSize: '0.8125rem', fontWeight: 600, color: '#374151', marginBottom: '0.375rem' }}>
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

      {submitDecision.isError && (
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
