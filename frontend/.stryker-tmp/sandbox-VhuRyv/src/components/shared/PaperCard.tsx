/**
 * PaperCard: displays paper metadata, abstract, decision history timeline,
 * and conflict resolution UI when conflict_flag is true.
 */
// @ts-nocheck


import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';

interface Paper {
  id: number;
  title: string;
  abstract: string | null;
  doi: string | null;
  authors: Array<{ name: string; institution?: string }> | null;
  year: number | null;
  venue: string | null;
}

interface Decision {
  id: number;
  candidate_paper_id: number;
  reviewer_id: number;
  decision: 'accepted' | 'rejected' | 'duplicate';
  reasons: Array<{ criterion_id?: number; criterion_type?: string; text: string }> | null;
  is_override: boolean;
  overrides_decision_id: number | null;
  decided_at: string | null;
}

interface PaperCardProps {
  studyId: number;
  candidateId: number;
  paperId: number;
  paper: Paper;
  currentStatus: string;
  conflictFlag: boolean;
  phaseTag: string;
  onDecisionChange?: () => void;
}

const DECISION_COLORS: Record<string, string> = {
  accepted: '#16a34a',
  rejected: '#dc2626',
  duplicate: '#6b7280',
};

const STATUS_BG: Record<string, string> = {
  accepted: '#dcfce7',
  rejected: '#fee2e2',
  duplicate: '#f3f4f6',
  pending: '#fef3c7',
};

export default function PaperCard({
  studyId,
  candidateId,
  paper,
  currentStatus,
  conflictFlag,
  phaseTag,
  onDecisionChange,
}: PaperCardProps) {
  const qc = useQueryClient();

  const { data: decisions = [] } = useQuery<Decision[]>({
    queryKey: ['decisions', studyId, candidateId],
    queryFn: () =>
      api.get<Decision[]>(
        `/api/v1/studies/${studyId}/papers/${candidateId}/decisions`
      ),
  });

  const resolveConflict = useMutation({
    mutationFn: (body: { reviewer_id: number; decision: string; reasons: object[] }) =>
      api.post(
        `/api/v1/studies/${studyId}/papers/${candidateId}/resolve-conflict`,
        body
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['decisions', studyId, candidateId] });
      qc.invalidateQueries({ queryKey: ['papers', studyId] });
      onDecisionChange?.();
    },
  });

  const authorList = paper.authors?.map((a) => a.name).join(', ') ?? '';

  return (
    <div
      style={{
        border: `1px solid ${conflictFlag ? '#fbbf24' : '#e2e8f0'}`,
        borderRadius: '0.5rem',
        background: '#fff',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '0.875rem 1rem',
          background: STATUS_BG[currentStatus] ?? '#f8fafc',
          borderBottom: '1px solid #e2e8f0',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem' }}>
          <h4 style={{ margin: 0, fontSize: '0.9375rem', color: '#111827', flex: 1 }}>
            {paper.title}
          </h4>
          <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0, alignItems: 'center' }}>
            {conflictFlag && (
              <span
                style={{
                  padding: '0.125rem 0.5rem',
                  background: '#fef3c7',
                  border: '1px solid #fbbf24',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: '#92400e',
                }}
              >
                ⚠ CONFLICT
              </span>
            )}
            <span
              style={{
                padding: '0.125rem 0.5rem',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                fontWeight: 600,
                background: `${DECISION_COLORS[currentStatus] ?? '#6b7280'}20`,
                color: DECISION_COLORS[currentStatus] ?? '#6b7280',
                textTransform: 'capitalize',
              }}
            >
              {currentStatus}
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: '#6b7280', marginTop: '0.375rem', flexWrap: 'wrap' }}>
          {paper.year && <span>{paper.year}</span>}
          {paper.venue && <span>{paper.venue}</span>}
          {paper.doi && <span>DOI: {paper.doi}</span>}
          {authorList && <span>{authorList}</span>}
          <span
            style={{
              padding: '0.0625rem 0.375rem',
              background: '#f1f5f9',
              borderRadius: '0.25rem',
              fontSize: '0.6875rem',
            }}
          >
            {phaseTag}
          </span>
        </div>
      </div>

      {/* Abstract */}
      {paper.abstract && (
        <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #f1f5f9' }}>
          <p style={{ margin: 0, fontSize: '0.8125rem', color: '#374151', lineHeight: 1.6 }}>
            {paper.abstract}
          </p>
        </div>
      )}

      {/* Decision history timeline */}
      {decisions.length > 0 && (
        <div style={{ padding: '0.75rem 1rem', borderBottom: conflictFlag ? '1px solid #fbbf24' : undefined }}>
          <h5 style={{ margin: '0 0 0.625rem', fontSize: '0.8125rem', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Audit Trail
          </h5>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {decisions.map((d) => (
              <DecisionEntry key={d.id} decision={d} />
            ))}
          </div>
        </div>
      )}

      {/* Conflict resolution panel */}
      {conflictFlag && decisions.length >= 2 && (
        <ConflictResolutionPanel
          decisions={decisions}
          studyId={studyId}
          onResolve={(reviewerId, decision) =>
            resolveConflict.mutate({ reviewer_id: reviewerId, decision, reasons: [] })
          }
          isResolving={resolveConflict.isPending}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function DecisionEntry({ decision }: { decision: Decision }) {
  const color = DECISION_COLORS[decision.decision] ?? '#6b7280';
  const timestamp = decision.decided_at
    ? new Date(decision.decided_at).toLocaleString(undefined, {
        dateStyle: 'short',
        timeStyle: 'short',
      })
    : null;

  return (
    <div style={{ display: 'flex', gap: '0.625rem', alignItems: 'flex-start' }}>
      <span
        style={{
          width: '0.5rem',
          height: '0.5rem',
          borderRadius: '50%',
          background: color,
          flexShrink: 0,
          marginTop: '0.3125rem',
        }}
      />
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <span
            style={{ fontSize: '0.8125rem', fontWeight: 600, color, textTransform: 'capitalize' }}
          >
            {decision.decision}
          </span>
          {decision.is_override && (
            <span style={{ fontSize: '0.6875rem', color: '#b45309', fontStyle: 'italic', background: '#fef3c7', padding: '0.0625rem 0.3rem', borderRadius: '0.25rem' }}>
              override
            </span>
          )}
          {decision.overrides_decision_id != null && (
            <span style={{ fontSize: '0.6875rem', color: '#6b7280' }}>
              ↳ overrides #{decision.overrides_decision_id}
            </span>
          )}
          <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
            Reviewer #{decision.reviewer_id}
          </span>
          {timestamp && (
            <span style={{ fontSize: '0.6875rem', color: '#9ca3af', marginLeft: 'auto' }}>
              {timestamp}
            </span>
          )}
        </div>
        {decision.reasons && decision.reasons.length > 0 && (
          <ul style={{ margin: '0.25rem 0 0', paddingLeft: '1rem' }}>
            {decision.reasons.map((r, i) => (
              <li key={i} style={{ fontSize: '0.75rem', color: '#4b5563' }}>
                {r.text}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function ConflictResolutionPanel({
  decisions,
  studyId,
  onResolve,
  isResolving,
}: {
  decisions: Decision[];
  studyId: number;
  onResolve: (reviewerId: number, decision: string) => void;
  isResolving: boolean;
}) {
  // Show the two most recent conflicting human decisions side-by-side
  const lastTwo = decisions.slice(-2);

  return (
    <div style={{ padding: '0.875rem 1rem', background: '#fffbeb' }}>
      <h5
        style={{
          margin: '0 0 0.75rem',
          fontSize: '0.8125rem',
          color: '#92400e',
          fontWeight: 700,
        }}
      >
        Conflict Resolution Required
      </h5>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.875rem' }}>
        {lastTwo.map((d) => (
          <div
            key={d.id}
            style={{
              padding: '0.625rem',
              border: `2px solid ${DECISION_COLORS[d.decision] ?? '#6b7280'}`,
              borderRadius: '0.375rem',
              background: '#fff',
            }}
          >
            <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: DECISION_COLORS[d.decision], textTransform: 'capitalize', marginBottom: '0.25rem' }}>
              {d.decision}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
              Reviewer #{d.reviewer_id}
            </div>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        {(['accepted', 'rejected'] as const).map((decision) => (
          <button
            key={decision}
            onClick={() => onResolve(lastTwo[0]?.reviewer_id ?? 0, decision)}
            disabled={isResolving}
            style={{
              padding: '0.375rem 0.875rem',
              background: DECISION_COLORS[decision],
              color: '#fff',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: isResolving ? 'not-allowed' : 'pointer',
              fontSize: '0.8125rem',
              fontWeight: 600,
              opacity: isResolving ? 0.6 : 1,
              textTransform: 'capitalize',
            }}
          >
            Resolve as {decision}
          </button>
        ))}
      </div>
    </div>
  );
}
