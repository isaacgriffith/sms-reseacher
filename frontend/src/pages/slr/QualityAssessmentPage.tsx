/**
 * QualityAssessmentPage — Phase 5 quality assessment page for SLR studies.
 *
 * Presents two tabs:
 * - "Checklist Setup": lets the lead reviewer define the quality checklist.
 * - "Score Papers": lists the study's accepted candidate papers and mounts
 *   {@link QualityScoreForm} for the one selected.
 *
 * @module QualityAssessmentPage
 */

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import QualityChecklistEditor from '../../components/slr/QualityChecklistEditor';
import QualityScoreForm from '../../components/slr/QualityScoreForm';
import type { CandidatePaper } from '../../components/phase2/PaperQueue';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface QualityAssessmentPageProps {
  /** Integer study ID from the parent page. */
  studyId: number;
}

// ---------------------------------------------------------------------------
// Tab panel helper
// ---------------------------------------------------------------------------

interface TabPanelProps {
  children: React.ReactNode;
  value: number;
  index: number;
}

/**
 * TabPanel renders children only when the tab is active.
 *
 * @param value - Currently selected tab index.
 * @param index - This panel's tab index.
 * @param children - Content to render inside the panel.
 */
function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <Box role="tabpanel" hidden={value !== index} sx={{ pt: 2 }}>
      {value === index && children}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Score Papers tab
// ---------------------------------------------------------------------------

/**
 * Fetches the study's accepted candidate papers.
 *
 * Mirrors the query shape used by {@link PaperQueue} — same endpoint, same
 * `status` query param — and namespaces its query key explicitly rather than
 * distinguishing it from other paper queries by argument absence.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the accepted {@link CandidatePaper} list.
 */
function useAcceptedPapers(studyId: number) {
  const params = new URLSearchParams();
  params.set('status', 'accepted');

  return useQuery<CandidatePaper[]>({
    queryKey: ['slr-accepted-papers', studyId],
    queryFn: () =>
      api.get<CandidatePaper[]>(`/api/v1/studies/${studyId}/papers?${params.toString()}`),
  });
}

interface ScorePapersTabProps {
  studyId: number;
}

/**
 * Lists the study's accepted candidate papers and mounts
 * {@link QualityScoreForm} for the one selected.
 *
 * @param studyId - The study whose accepted papers to list.
 */
function ScorePapersTab({ studyId }: ScorePapersTabProps) {
  const [selectedPaperId, setSelectedPaperId] = useState<number | null>(null);
  const { data: papers = [], isLoading } = useAcceptedPapers(studyId);

  if (isLoading) return <CircularProgress size={24} />;

  if (papers.length === 0) {
    return (
      <Typography sx={{ color: '#6b7280' }}>
        No accepted papers yet. Papers appear here once screening accepts them.
      </Typography>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
        {papers.map((candidate) => (
          <Button
            key={candidate.id}
            variant={selectedPaperId === candidate.id ? 'contained' : 'outlined'}
            onClick={() => setSelectedPaperId(candidate.id)}
          >
            {candidate.paper.title}
          </Button>
        ))}
      </Box>
      {selectedPaperId !== null && (
        <QualityScoreForm candidatePaperId={selectedPaperId} studyId={studyId} />
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

/**
 * QualityAssessmentPage provides a tabbed interface for quality assessment.
 *
 * @param studyId - The study whose quality assessment to manage.
 */
export default function QualityAssessmentPage({ studyId }: QualityAssessmentPageProps) {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Quality Assessment
      </Typography>

      <Tabs
        value={activeTab}
        onChange={(_, newValue: number) => setActiveTab(newValue)}
        aria-label="Quality assessment tabs"
      >
        <Tab label="Checklist Setup" />
        <Tab label="Score Papers" />
      </Tabs>

      <TabPanel value={activeTab} index={0}>
        <QualityChecklistEditor studyId={studyId} />
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <ScorePapersTab studyId={studyId} />
      </TabPanel>
    </Box>
  );
}
