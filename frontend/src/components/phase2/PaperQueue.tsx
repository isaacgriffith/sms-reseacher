/**
 * PaperQueue: paginated list of candidate papers with status badges,
 * phase tags, and AI decision summaries. Filters by status and phase.
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';

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
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
        }}
      >
        <Typography variant="subtitle1" sx={{ margin: 0, fontSize: '1rem', color: '#111827' }}>Paper Queue</Typography>
        <Button
          variant="outlined"
          onClick={() => refetch()}
          size="small"
          sx={{ fontSize: '0.8125rem', color: '#374151' }}
        >
          Refresh
        </Button>
      </Box>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
          style={{
            padding: '0.375rem 0.625rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
            background: '#fff',
            cursor: 'pointer',
          }}
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
          <option value="duplicate">Duplicate</option>
        </select>

        <TextField
          value={phaseFilter}
          onChange={(e) => { setPhaseFilter(e.target.value); setPage(0); }}
          placeholder="Filter by phase tag…"
          size="small"
          sx={{ minWidth: '180px' }}
        />

        {(statusFilter || phaseFilter) && (
          <Button variant="outlined" size="small" onClick={handleResetFilters} sx={{ fontSize: '0.8125rem', color: '#374151' }}>
            Clear filters
          </Button>
        )}
      </Box>

      {/* Paper list */}
      {isLoading && <Typography style={{ color: 'rgb(107, 114, 128)' }} sx={{ fontSize: '0.875rem' }}>Loading papers…</Typography>}
      {error && <Typography style={{ color: 'rgb(239, 68, 68)' }} sx={{ fontSize: '0.875rem' }}>Failed to load papers.</Typography>}

      {!isLoading && papers.length === 0 && (
        <Typography sx={{ color: '#9ca3af', fontSize: '0.875rem' }}>
          {statusFilter || phaseFilter
            ? 'No candidate papers found. Try adjusting your filters.'
            : 'No candidate papers found. Run a full search to populate the paper queue.'}
        </Typography>
      )}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {papers.map((cp) => (
          <Box
            key={cp.id}
            sx={{
              border: '1px solid #e2e8f0',
              borderRadius: '0.5rem',
              padding: '0.875rem',
              background: '#fff',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                gap: '0.75rem',
                marginBottom: '0.375rem',
              }}
            >
              <Typography
                component="span"
                sx={{
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  color: '#111827',
                  flex: 1,
                }}
              >
                {cp.paper.title}
              </Typography>
              <Typography
                component="span"
                sx={{
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
              </Typography>
            </Box>

            <Box
              sx={{
                display: 'flex',
                gap: '1rem',
                fontSize: '0.75rem',
                color: '#6b7280',
                flexWrap: 'wrap',
              }}
            >
              {cp.paper.year && <Typography component="span" sx={{ fontSize: '0.75rem', color: '#6b7280' }}>{cp.paper.year}</Typography>}
              {cp.paper.venue && <Typography component="span" sx={{ fontSize: '0.75rem', color: '#6b7280' }}>{cp.paper.venue}</Typography>}
              {cp.paper.doi && <Typography component="span" sx={{ fontSize: '0.75rem', color: '#6b7280' }}>DOI: {cp.paper.doi}</Typography>}
              <Typography
                component="span"
                sx={{
                  padding: '0.0625rem 0.375rem',
                  background: '#f1f5f9',
                  borderRadius: '0.25rem',
                  fontSize: '0.6875rem',
                }}
              >
                {cp.phase_tag}
              </Typography>
            </Box>

            {cp.paper.abstract && (
              <Typography
                sx={{
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
              </Typography>
            )}
          </Box>
        ))}
      </Box>

      {/* Pagination */}
      {(papers.length === PAGE_SIZE || page > 0) && (
        <Box
          sx={{
            display: 'flex',
            gap: '0.5rem',
            justifyContent: 'center',
            marginTop: '1rem',
          }}
        >
          <Button
            variant="outlined"
            size="small"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            style={{ cursor: page === 0 ? 'not-allowed' : 'pointer', opacity: page === 0 ? 0.6 : 1 }}
            sx={{ fontSize: '0.875rem', color: page === 0 ? '#9ca3af' : '#374151' }}
          >
            ← Previous
          </Button>
          <Typography component="span" sx={{ padding: '0.375rem 0.625rem', fontSize: '0.875rem', color: '#374151' }}>
            Page {page + 1}
          </Typography>
          <Button
            variant="outlined"
            size="small"
            onClick={() => setPage((p) => p + 1)}
            disabled={papers.length < PAGE_SIZE}
            style={{ cursor: papers.length < PAGE_SIZE ? 'not-allowed' : 'pointer', opacity: papers.length < PAGE_SIZE ? 0.6 : 1 }}
            sx={{ fontSize: '0.875rem', color: papers.length < PAGE_SIZE ? '#9ca3af' : '#374151' }}
          >
            Next →
          </Button>
        </Box>
      )}
    </Box>
  );
}
