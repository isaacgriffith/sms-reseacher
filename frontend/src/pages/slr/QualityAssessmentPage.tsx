/**
 * QualityAssessmentPage — Phase 5 quality assessment page for SLR studies.
 *
 * Presents two tabs:
 * - "Checklist Setup": lets the lead reviewer define the quality checklist.
 * - "Score Papers": placeholder directing users to select an accepted paper.
 *
 * @module QualityAssessmentPage
 */

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import QualityChecklistEditor from '../../components/slr/QualityChecklistEditor';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface QualityAssessmentPageProps {
  /** Integer study ID from the parent page. */
  studyId: number;
  /** Integer reviewer ID for the current user. */
  reviewerId: number;
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
// Page component
// ---------------------------------------------------------------------------

/**
 * QualityAssessmentPage provides a tabbed interface for quality assessment.
 *
 * @param studyId - The study whose quality assessment to manage.
 * @param reviewerId - The current reviewer's ID.
 */
export default function QualityAssessmentPage({
  studyId,
  reviewerId: _reviewerId, // eslint-disable-line @typescript-eslint/no-unused-vars
}: QualityAssessmentPageProps) {
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
        <Typography sx={{ color: '#6b7280' }}>
          Select an accepted paper to score it.
        </Typography>
      </TabPanel>
    </Box>
  );
}
