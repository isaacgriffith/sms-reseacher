/**
 * SearchConfigPage: Phase 2 of the Rapid Review workflow.
 *
 * Wraps DatabaseSelectionPanel (from 006), SearchRestrictionPanel, and
 * SingleReviewerWarningBanner. Provides a single view for configuring
 * search sources, restrictions, and reviewer mode.
 */

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

import DatabaseSelectionPanel from '../../components/studies/DatabaseSelectionPanel';
import SearchRestrictionPanel from '../../components/rapid/SearchRestrictionPanel';
import SingleReviewerWarningBanner from '../../components/rapid/SingleReviewerWarningBanner';
import { useRRProtocol } from '../../hooks/rapid/useRRProtocol';

interface SearchConfigPageProps {
  studyId: number;
}

export default function SearchConfigPage({ studyId }: SearchConfigPageProps) {
  const { data: protocol } = useRRProtocol(studyId);

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 0.5, fontWeight: 600 }}>
        Search Configuration
      </Typography>
      <Typography variant="body2" sx={{ mb: 3, color: '#64748b' }}>
        Select databases, configure restrictions, and set reviewer mode. Each restriction is
        automatically recorded as a threat to validity.
      </Typography>

      <SingleReviewerWarningBanner
        studyId={studyId}
        singleReviewerMode={protocol?.single_reviewer_mode ?? false}
      />

      <Box sx={{ mb: 3 }}>
        <DatabaseSelectionPanel studyId={studyId} />
      </Box>

      <Box
        sx={{
          p: 2,
          border: '1px solid #e2e8f0',
          borderRadius: '0.5rem',
          background: '#f8fafc',
        }}
      >
        <SearchRestrictionPanel studyId={studyId} />
      </Box>
    </Box>
  );
}
