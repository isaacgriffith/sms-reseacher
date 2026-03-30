/**
 * QualityConfigPage: Phase 4 of the Rapid Review workflow.
 *
 * Allows the researcher to choose between full quality appraisal,
 * peer-reviewed-only filtering, or skipping quality appraisal entirely.
 * The chosen approach is recorded as a threat to validity where applicable.
 */

import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';

import QAModeSelector from '../../components/rapid/QAModeSelector';
import { useQualityConfig } from '../../hooks/rapid/useQAConfig';

/** Props for {@link QualityConfigPage}. */
interface QualityConfigPageProps {
  /** The Rapid Review study ID. */
  studyId: number;
}

/**
 * Renders the quality appraisal configuration step for a Rapid Review study.
 *
 * Loads the current quality appraisal mode from the API and delegates
 * selection and saving to {@link QAModeSelector}.
 */
export default function QualityConfigPage({ studyId }: QualityConfigPageProps) {
  const { data: config, isLoading } = useQualityConfig(studyId);

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 0.5, fontWeight: 600 }}>
        Quality Appraisal
      </Typography>
      <Typography variant="body2" sx={{ mb: 3, color: '#64748b' }}>
        Choose how quality appraisal is handled for this Rapid Review. Skipping or simplifying is
        common in practitioner-focused reviews; the chosen approach is transparently recorded in the
        Evidence Briefing.
      </Typography>

      {isLoading ? (
        <CircularProgress size={24} />
      ) : (
        <Box
          sx={{
            p: 2,
            border: '1px solid #e2e8f0',
            borderRadius: '0.5rem',
            background: '#f8fafc',
          }}
        >
          <QAModeSelector
            studyId={studyId}
            currentMode={config?.quality_appraisal_mode ?? 'full'}
          />
        </Box>
      )}
    </Box>
  );
}
