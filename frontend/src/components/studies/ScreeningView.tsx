/**
 * ScreeningView: composes the Phase 2 screening workflow into one screen.
 *
 * The queue lists candidate papers; selecting one shows its PaperCard (prior
 * decisions, disagreement warning) and ReviewerPanel (record a decision) beside
 * it, with MetricsDashboard summarising the funnel below.
 */

import { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import PaperQueue, { type CandidatePaper } from '../phase2/PaperQueue';
import ReviewerPanel from '../phase2/ReviewerPanel';
import PaperCard from '../shared/PaperCard';
import MetricsDashboard from '../phase2/MetricsDashboard';

interface ScreeningViewProps {
  studyId: number;
}

export default function ScreeningView({ studyId }: ScreeningViewProps) {
  const [selected, setSelected] = useState<CandidatePaper | null>(null);

  return (
    <Box data-testid="screening-view">
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          gap: '1.25rem',
          alignItems: 'start',
        }}
      >
        <PaperQueue studyId={studyId} onSelect={setSelected} selectedId={selected?.id ?? null} />

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {selected ? (
            <>
              <PaperCard
                studyId={studyId}
                candidateId={selected.id}
                paperId={selected.paper_id}
                paper={selected.paper}
                currentStatus={selected.current_status}
                conflictFlag={selected.conflict_flag}
                phaseTag={selected.phase_tag}
              />
              <ReviewerPanel
                key={selected.id}
                studyId={studyId}
                candidateId={selected.id}
                observedStatus={selected.current_status}
              />
            </>
          ) : (
            <Typography sx={{ color: '#9ca3af', fontSize: '0.875rem', padding: '1rem' }}>
              Select a paper from the queue to begin screening.
            </Typography>
          )}
        </Box>
      </Box>

      <Box sx={{ marginTop: '1.5rem' }}>
        <MetricsDashboard studyId={studyId} />
      </Box>
    </Box>
  );
}
