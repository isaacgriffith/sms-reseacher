/**
 * GreyLiteraturePage — page for managing grey literature sources (feature 007, Phase 8).
 *
 * Hosts the {@link GreyLiteraturePanel} within a standard page header/description
 * layout so users can track technical reports, dissertations, rejected publications,
 * and works-in-progress that are not available through standard academic databases.
 */

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import GreyLiteraturePanel from '../../components/slr/GreyLiteraturePanel';

interface GreyLiteraturePageProps {
  /** The integer study ID. */
  studyId: number;
}

/**
 * Page component for managing grey literature sources for an SLR study.
 *
 * @param props - {@link GreyLiteraturePageProps}
 */
export default function GreyLiteraturePage({ studyId }: GreyLiteraturePageProps) {
  return (
    <Box data-testid="grey-literature-page">
      <Typography variant="h6" sx={{ mb: 1 }}>
        Grey Literature Sources
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Track technical reports, dissertations, rejected publications, and works-in-progress
        that are not available through standard academic databases.
      </Typography>
      <GreyLiteraturePanel studyId={studyId} />
    </Box>
  );
}
