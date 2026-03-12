/**
 * PaperQueue: paginated list of candidate papers with status badges,
 * phase tags, and AI decision summaries. Filters by status and phase.
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';

interface Paper {
  id: number;
  title: string;
  abstract: string | null;
  doi: string | null;
  authors: Array<{ name: string }> | null;
  year: number | null;
  venue: string | null;
}

interface CandidatePaper {
  id: number;
  study_id: number;
  paper_id: number;
  phase_tag: string;
  current_status: 'pending' | 'accepted' | 'rejected' | 'duplicate';
  duplicate_of_id: number | null;
  paper: Paper;
}

interface PaperQueueProps {
  studyId: number;
}

const STATUS_COLORS: Record<string, string> = {
  pending: '#d97706',
  accepted: '#16a34a',
  rejected: '#dc2626',
  duplicate: '#6b7280',
};

const PAGE_SIZE = 20;

export default function PaperQueue({ studyId }: PaperQueueProps) {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [phaseFilter, setPhaseFilter] = useState<string>('');
  const [page, setPage] = useState(0);

  const offset = page * PAGE_SIZE;

  const params = new URLSearchParams();
  if (statusFilter) params.set('status', statusFilter);
  if (phaseFilter) params.set('phase_tag', phaseFilter);
  params.set('offset', String(offset));
  params.set('limit', String(PAGE_SIZE));

  const { data: papers = [], isLoading, error, refetch } = useQuery<CandidatePaper[]>({
    queryKey: ['papers', studyId, statusFilter, phaseFilter, page],
    queryFn: () =>
      api.get<CandidatePaper[]>(`/api/v1/studies/${studyId}/papers?${params.toString()}`),
  });

  const handleResetFilters = () => {
    setStatusFilter('');
    setPhaseFilter('');
    setPage(0);
  };

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
        }}
      >
        <h3 style={{ margin: 0, fontSize: '1rem', color: '#111827' }}>Paper Queue</h3>
        <button
          onClick={() => refetch()}
          style={{
            padding: '0.25rem 0.75rem',
            background: 'transparent',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            cursor: 'pointer',
            fontSize: '0.8125rem',
            color: '#374151',
          }}
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
          style={selectStyle}
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
          <option value="duplicate">Duplicate</option>
        </select>

        <input
          value={phaseFilter}
          onChange={(e) => { setPhaseFilter(e.target.value); setPage(0); }}
          placeholder="Filter by phase tag…"
          style={{
            padding: '0.375rem 0.625rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
            minWidth: '180px',
          }}
        />

        {(statusFilter || phaseFilter) && (
          <button onClick={handleResetFilters} style={clearBtnStyle}>
            Clear filters
          </button>
        )}
      </div>

      {/* Paper list */}
      {isLoading && <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Loading papers…</p>}
      {error && <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>Failed to load papers.</p>}

      {!isLoading && papers.length === 0 && (
        <p style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
          No candidate papers found.{' '}
          {statusFilter || phaseFilter
            ? 'Try adjusting your filters.'
            : 'Run a full search to populate the paper queue.'}
        </p>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {papers.map((cp) => (
          <div
            key={cp.id}
            style={{
              border: '1px solid #e2e8f0',
              borderRadius: '0.5rem',
              padding: '0.875rem',
              background: '#fff',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                gap: '0.75rem',
                marginBottom: '0.375rem',
              }}
            >
              <span
                style={{
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  color: '#111827',
                  flex: 1,
                }}
              >
                {cp.paper.title}
              </span>
              <span
                style={{
                  flexShrink: 0,
                  padding: '0.125rem 0.5rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  background: `${STATUS_COLORS[cp.current_status]}20`,
                  color: STATUS_COLORS[cp.current_status],
                  textTransform: 'capitalize',
                }}
              >
                {cp.current_status}
              </span>
            </div>

            <div
              style={{
                display: 'flex',
                gap: '1rem',
                fontSize: '0.75rem',
                color: '#6b7280',
                flexWrap: 'wrap',
              }}
            >
              {cp.paper.year && <span>{cp.paper.year}</span>}
              {cp.paper.venue && <span>{cp.paper.venue}</span>}
              {cp.paper.doi && <span>DOI: {cp.paper.doi}</span>}
              <span
                style={{
                  padding: '0.0625rem 0.375rem',
                  background: '#f1f5f9',
                  borderRadius: '0.25rem',
                  fontSize: '0.6875rem',
                }}
              >
                {cp.phase_tag}
              </span>
            </div>

            {cp.paper.abstract && (
              <p
                style={{
                  margin: '0.5rem 0 0',
                  fontSize: '0.8125rem',
                  color: '#4b5563',
                  lineHeight: 1.5,
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}
              >
                {cp.paper.abstract}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      {(papers.length === PAGE_SIZE || page > 0) && (
        <div
          style={{
            display: 'flex',
            gap: '0.5rem',
            justifyContent: 'center',
            marginTop: '1rem',
          }}
        >
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            style={paginationBtnStyle(page === 0)}
          >
            ← Previous
          </button>
          <span style={{ padding: '0.375rem 0.625rem', fontSize: '0.875rem', color: '#374151' }}>
            Page {page + 1}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={papers.length < PAGE_SIZE}
            style={paginationBtnStyle(papers.length < PAGE_SIZE)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}

const selectStyle: React.CSSProperties = {
  padding: '0.375rem 0.625rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  background: '#fff',
  cursor: 'pointer',
};

const clearBtnStyle: React.CSSProperties = {
  padding: '0.375rem 0.625rem',
  background: 'transparent',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.8125rem',
  color: '#374151',
};

function paginationBtnStyle(disabled: boolean): React.CSSProperties {
  return {
    padding: '0.375rem 0.75rem',
    background: disabled ? '#f9fafb' : '#fff',
    border: '1px solid #d1d5db',
    borderRadius: '0.375rem',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontSize: '0.875rem',
    color: disabled ? '#9ca3af' : '#374151',
    opacity: disabled ? 0.6 : 1,
  };
}
