/**
 * PaperCard: displays paper metadata, abstract, decision history timeline,
 * and conflict resolution UI when conflict_flag is true.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

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
    <Box
      sx={{
        border: `1px solid ${conflictFlag ? '#fbbf24' : '#e2e8f0'}`,
        borderRadius: '0.5rem',
        background: '#fff',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          padding: '0.875rem 1rem',
          background: STATUS_BG[currentStatus] ?? '#f8fafc',
          borderBottom: '1px solid #e2e8f0',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem' }}>
          <Typography sx={{ margin: 0, fontSize: '0.9375rem', color: '#111827', flex: 1, fontWeight: 600 }}>
            {paper.title}
          </Typography>
          <Box sx={{ display: 'flex', gap: '0.5rem', flexShrink: 0, alignItems: 'center' }}>
            {conflictFlag && (
              <Typography
                component="span"
                sx={{
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
              </Typography>
            )}
            <Typography
              component="span"
              sx={{
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
            </Typography>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: '#6b7280', marginTop: '0.375rem', flexWrap: 'wrap' }}>
          {paper.year && <Typography component="span" sx={{ fontSize: '0.75rem', color: '#6b7280' }}>{paper.year}</Typography>}
          {paper.venue && <Typography component="span" sx={{ fontSize: '0.75rem', color: '#6b7280' }}>{paper.venue}</Typography>}
          {paper.doi && <Typography component="span" sx={{ fontSize: '0.75rem', color: '#6b7280' }}>DOI: {paper.doi}</Typography>}
          {authorList && <Typography component="span" sx={{ fontSize: '0.75rem', color: '#6b7280' }}>{authorList}</Typography>}
          <Typography
            component="span"
            sx={{
              padding: '0.0625rem 0.375rem',
              background: '#f1f5f9',
              borderRadius: '0.25rem',
              fontSize: '0.6875rem',
            }}
          >
            {phaseTag}
          </Typography>
        </Box>
      </Box>

      {/* Abstract */}
      {paper.abstract && (
        <Box sx={{ padding: '0.75rem 1rem', borderBottom: '1px solid #f1f5f9' }}>
          <Typography sx={{ margin: 0, fontSize: '0.8125rem', color: '#374151', lineHeight: 1.6 }}>
            {paper.abstract}
          </Typography>
        </Box>
      )}

      {/* Decision history timeline */}
      {decisions.length > 0 && (
        <Box sx={{ padding: '0.75rem 1rem', borderBottom: conflictFlag ? '1px solid #fbbf24' : undefined }}>
          <Typography
            sx={{
              margin: '0 0 0.625rem',
              fontSize: '0.8125rem',
              color: '#6b7280',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontWeight: 600,
            }}
          >
            Audit Trail
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {decisions.map((d) => (
              <DecisionEntry key={d.id} decision={d} />
            ))}
          </Box>
        </Box>
      )}

      {/* Conflict resolution panel */}
      {conflictFlag && decisions.length >= 2 && (
        <ConflictResolutionPanel
          decisions={decisions}
          onResolve={(reviewerId, decision) =>
            resolveConflict.mutate({ reviewer_id: reviewerId, decision, reasons: [] })
          }
          isResolving={resolveConflict.isPending}
        />
      )}
    </Box>
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
    <Box sx={{ display: 'flex', gap: '0.625rem', alignItems: 'flex-start' }}>
      <Box
        component="span"
        sx={{
          width: '0.5rem',
          height: '0.5rem',
          borderRadius: '50%',
          background: color,
          flexShrink: 0,
          marginTop: '0.3125rem',
          display: 'inline-block',
        }}
      />
      <Box sx={{ flex: 1 }}>
        <Box sx={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <Typography
            component="span"
            sx={{ fontSize: '0.8125rem', fontWeight: 600, color, textTransform: 'capitalize' }}
          >
            {decision.decision}
          </Typography>
          {decision.is_override && (
            <Typography component="span" sx={{ fontSize: '0.6875rem', color: '#b45309', fontStyle: 'italic', background: '#fef3c7', padding: '0.0625rem 0.3rem', borderRadius: '0.25rem' }}>
              override
            </Typography>
          )}
          {decision.overrides_decision_id != null && (
            <Typography component="span" sx={{ fontSize: '0.6875rem', color: '#6b7280' }}>
              ↳ overrides #{decision.overrides_decision_id}
            </Typography>
          )}
          <Typography component="span" sx={{ fontSize: '0.75rem', color: '#9ca3af' }}>
            Reviewer #{decision.reviewer_id}
          </Typography>
          {timestamp && (
            <Typography component="span" sx={{ fontSize: '0.6875rem', color: '#9ca3af', marginLeft: 'auto' }}>
              {timestamp}
            </Typography>
          )}
        </Box>
        {decision.reasons && decision.reasons.length > 0 && (
          <Box component="ul" sx={{ margin: '0.25rem 0 0', paddingLeft: '1rem' }}>
            {decision.reasons.map((r, i) => (
              <Box component="li" key={i} sx={{ fontSize: '0.75rem', color: '#4b5563' }}>
                {r.text}
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
}

function ConflictResolutionPanel({
  decisions,
  onResolve,
  isResolving,
}: {
  decisions: Decision[];
  onResolve: (reviewerId: number, decision: string) => void;
  isResolving: boolean;
}) {
  // Show the two most recent conflicting human decisions side-by-side
  const lastTwo = decisions.slice(-2);

  return (
    <Box sx={{ padding: '0.875rem 1rem', background: '#fffbeb' }}>
      <Typography
        sx={{
          margin: '0 0 0.75rem',
          fontSize: '0.8125rem',
          color: '#92400e',
          fontWeight: 700,
        }}
      >
        Conflict Resolution Required
      </Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.875rem' }}>
        {lastTwo.map((d) => (
          <Box
            key={d.id}
            sx={{
              padding: '0.625rem',
              border: `2px solid ${DECISION_COLORS[d.decision] ?? '#6b7280'}`,
              borderRadius: '0.375rem',
              background: '#fff',
            }}
          >
            <Typography sx={{ fontSize: '0.8125rem', fontWeight: 600, color: DECISION_COLORS[d.decision], textTransform: 'capitalize', marginBottom: '0.25rem' }}>
              {d.decision}
            </Typography>
            <Typography sx={{ fontSize: '0.75rem', color: '#6b7280' }}>
              Reviewer #{d.reviewer_id}
            </Typography>
          </Box>
        ))}
      </Box>
      <Box sx={{ display: 'flex', gap: '0.5rem' }}>
        {(['accepted', 'rejected'] as const).map((decision) => (
          <Button
            key={decision}
            onClick={() => onResolve(lastTwo[0]?.reviewer_id ?? 0, decision)}
            disabled={isResolving}
            variant="contained"
            sx={{
              padding: '0.375rem 0.875rem',
              background: DECISION_COLORS[decision],
              color: '#fff',
              fontSize: '0.8125rem',
              fontWeight: 600,
              textTransform: 'capitalize',
              opacity: isResolving ? 0.6 : 1,
              '&:hover': { background: DECISION_COLORS[decision] },
            }}
          >
            Resolve as {decision}
          </Button>
        ))}
      </Box>
    </Box>
  );
}
