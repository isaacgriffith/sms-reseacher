/**
 * EvidenceBriefingPage — Phase 6 page for Rapid Review evidence briefing
 * generation, preview, and export (feature 008).
 *
 * @module EvidenceBriefingPage
 */

import React from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import BriefingVersionPanel from '../../components/rapid/BriefingVersionPanel';
import BriefingPreview from '../../components/rapid/BriefingPreview';
import { useBriefings, useGenerateBriefing } from '../../hooks/rapid/useBriefingVersions';
import { getBriefing, ApiError } from '../../services/rapid/briefingApi';
import type { BriefingDetail } from '../../services/rapid/briefingApi';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link EvidenceBriefingPage}. */
interface EvidenceBriefingPageProps {
  /** Integer study ID from the parent page. */
  studyId: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * EvidenceBriefingPage renders the evidence briefing management UI.
 *
 * Layout:
 * - Page header with "Generate New Version" CTA.
 * - Error alert when synthesis is not complete (422).
 * - {@link BriefingVersionPanel} listing all versions.
 * - {@link BriefingPreview} for the currently selected briefing.
 *
 * @param studyId - The study whose evidence briefings to manage.
 */
export default function EvidenceBriefingPage({
  studyId,
}: EvidenceBriefingPageProps): React.ReactElement {
  const { data: briefings } = useBriefings(studyId);
  const generateMutation = useGenerateBriefing(studyId);

  const [selectedBriefingId, setSelectedBriefingId] = React.useState<number | null>(null);
  const [selectedBriefing, setSelectedBriefing] = React.useState<BriefingDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = React.useState(false);
  const [generateError, setGenerateError] = React.useState<string | null>(null);

  // Determine if any briefing is still generating (used to disable the button)
  const anyGenerating = briefings?.some((b) => !b.pdf_available) ?? false;

  const handleSelectBriefing = async (briefingId: number) => {
    setSelectedBriefingId(briefingId);
    setLoadingDetail(true);
    try {
      const detail = await getBriefing(studyId, briefingId);
      setSelectedBriefing(detail);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleGenerate = () => {
    setGenerateError(null);
    generateMutation.mutate(undefined, {
      onError: (err) => {
        if (err instanceof ApiError && err.status === 422) {
          setGenerateError(
            'Cannot generate a briefing until narrative synthesis is complete. ' +
              'Please finalise all synthesis sections first.',
          );
        } else {
          setGenerateError(err.message ?? 'Failed to start briefing generation.');
        }
      },
    });
  };

  const noBriefings = !briefings || briefings.length === 0;

  return (
    <Box>
      {/* Page header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Evidence Briefing</Typography>
        <Button
          variant="contained"
          color="primary"
          disabled={generateMutation.isPending || anyGenerating}
          onClick={handleGenerate}
          startIcon={generateMutation.isPending ? <CircularProgress size={16} /> : undefined}
        >
          {generateMutation.isPending ? 'Queuing…' : 'Generate New Version'}
        </Button>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Phase 6 · Evidence Briefing — Generate practitioner-ready briefings from the completed
        narrative synthesis.
      </Typography>

      {/* Generation error */}
      {generateError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setGenerateError(null)}>
          {generateError}
        </Alert>
      )}

      {/* Empty state */}
      {noBriefings && !generateMutation.isPending && (
        <Alert severity="info" sx={{ mb: 2 }}>
          No briefings yet. Complete the narrative synthesis and click Generate.
        </Alert>
      )}

      {/* Version list */}
      {!noBriefings && (
        <BriefingVersionPanel
          studyId={studyId}
          onSelectBriefing={(id) => void handleSelectBriefing(id)}
          selectedBriefingId={selectedBriefingId}
        />
      )}

      {/* Preview */}
      {selectedBriefingId && (
        <>
          <Divider sx={{ my: 3 }} />
          {loadingDetail ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={20} />
              <Typography>Loading briefing…</Typography>
            </Box>
          ) : selectedBriefing ? (
            <BriefingPreview briefing={selectedBriefing} />
          ) : null}
        </>
      )}
    </Box>
  );
}
