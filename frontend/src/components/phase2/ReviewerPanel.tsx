/**
 * ReviewerPanel: submit accept/reject/duplicate decisions with reason selector
 * from the study's criteria list and override annotation.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';

interface Criterion {
  id: number;
  description: string;
  order_index: number;
}

interface Reviewer {
  id: number;
  reviewer_type: string;
  user_id: number | null;
  agent_name: string | null;
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
    <div
      style={{
        border: '1px solid #e2e8f0',
        borderRadius: '0.5rem',
        padding: '1rem',
        background: '#f8fafc',
      }}
    >
      <h4 style={{ margin: '0 0 0.875rem', fontSize: '0.9375rem', color: '#111827' }}>
        Submit Decision
      </h4>

      {/* Reviewer ID input (simplified — in real use would be populated from auth context) */}
      <div style={{ marginBottom: '0.875rem' }}>
        <label style={labelStyle}>Reviewer ID</label>
        <input
          type="number"
          value={reviewerId ?? ''}
          onChange={(e) => setReviewerId(e.target.value ? Number(e.target.value) : null)}
          placeholder="Enter reviewer ID…"
          style={inputStyle}
        />
      </div>

      {/* Decision buttons */}
      <div style={{ marginBottom: '0.875rem' }}>
        <label style={labelStyle}>Decision</label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {(['accepted', 'rejected', 'duplicate'] as DecisionType[]).map((d) => {
            const style = DECISION_STYLES[d];
            const isSelected = selectedDecision === d;
            return (
              <button
                key={d}
                onClick={() => setSelectedDecision(isSelected ? null : d)}
                style={{
                  padding: '0.5rem 1rem',
                  background: isSelected ? style.text : '#fff',
                  color: isSelected ? '#fff' : style.text,
                  border: `2px solid ${style.border}`,
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  textTransform: 'capitalize',
                  transition: 'all 0.1s',
                }}
              >
                {d}
              </button>
            );
          })}
        </div>
      </div>

      {/* Criteria reason selector */}
      {selectedDecision && (inclusion.length > 0 || exclusion.length > 0) && (
        <div style={{ marginBottom: '0.875rem' }}>
          <label style={labelStyle}>Reasons (select criteria)</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', maxHeight: '160px', overflowY: 'auto' }}>
            {inclusion.length > 0 && (
              <div>
                <div style={groupLabelStyle}>Inclusion Criteria</div>
                {inclusion.map((c) => (
                  <CriterionCheckbox
                    key={c.id}
                    criterion={c}
                    checked={selectedReasons.includes(c.id)}
                    onChange={() => toggleReason(c.id)}
                  />
                ))}
              </div>
            )}
            {exclusion.length > 0 && (
              <div>
                <div style={groupLabelStyle}>Exclusion Criteria</div>
                {exclusion.map((c) => (
                  <CriterionCheckbox
                    key={c.id}
                    criterion={c}
                    checked={selectedReasons.includes(c.id)}
                    onChange={() => toggleReason(c.id)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Override annotation */}
      <div style={{ marginBottom: '0.875rem' }}>
        <label style={labelStyle}>Additional notes / override annotation</label>
        <textarea
          value={annotationText}
          onChange={(e) => setAnnotationText(e.target.value)}
          placeholder="Optional annotation…"
          rows={2}
          style={{
            ...inputStyle,
            resize: 'vertical',
            fontFamily: 'inherit',
          }}
        />
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        style={{
          padding: '0.5rem 1.25rem',
          background: canSubmit ? '#2563eb' : '#93c5fd',
          color: '#fff',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: canSubmit ? 'pointer' : 'not-allowed',
          fontSize: '0.875rem',
          fontWeight: 600,
        }}
      >
        {submitDecision.isPending ? 'Submitting…' : 'Submit Decision'}
      </button>

      {submitDecision.isError && (
        <p style={{ margin: '0.5rem 0 0', color: '#ef4444', fontSize: '0.8125rem' }}>
          Failed to submit decision. Please try again.
        </p>
      )}

      {submitDecision.isSuccess && (
        <p style={{ margin: '0.5rem 0 0', color: '#16a34a', fontSize: '0.8125rem' }}>
          Decision submitted.
        </p>
      )}
    </div>
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
      <span style={{ fontSize: '0.8125rem', color: '#374151' }}>
        {criterion.description}
      </span>
    </label>
  );
}

// ---------------------------------------------------------------------------
// Shared styles
// ---------------------------------------------------------------------------

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.8125rem',
  fontWeight: 600,
  color: '#374151',
  marginBottom: '0.375rem',
};

const groupLabelStyle: React.CSSProperties = {
  fontSize: '0.6875rem',
  fontWeight: 700,
  color: '#9ca3af',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  padding: '0.25rem 0',
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.375rem 0.625rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  background: '#fff',
  boxSizing: 'border-box',
};
