/**
 * NarrativeSynthesisPage — Phase 5 page for Rapid Review narrative synthesis (feature 008).
 *
 * Renders one NarrativeSectionEditor per research question, plus a
 * "Finalize Synthesis" CTA that gates Evidence Briefing generation.
 *
 * @module NarrativeSynthesisPage
 */

import React from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import NarrativeSectionEditor from '../../components/rapid/NarrativeSectionEditor';
import {
  useNarrativeSections,
  useUpdateSection,
  useRequestAIDraft,
  useCompleteSynthesis,
} from '../../hooks/rapid/useNarrativeSynthesis';
import { ApiError } from '../../services/rapid/synthesisApi';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link NarrativeSynthesisPage}. */
interface NarrativeSynthesisPageProps {
  /** Integer study ID from the parent page. */
  studyId: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * NarrativeSynthesisPage renders the full narrative synthesis editor.
 *
 * Layout:
 * - Page header.
 * - One {@link NarrativeSectionEditor} per research question section.
 * - "Mark All Complete" shortcut button.
 * - "Finalize Synthesis" CTA (shows 422 error list if any sections incomplete).
 *
 * @param studyId - The study whose synthesis sections to render.
 */
export default function NarrativeSynthesisPage({
  studyId,
}: NarrativeSynthesisPageProps): React.ReactElement {
  const { data: sections, isLoading, error: loadError } = useNarrativeSections(studyId);
  const updateMutation = useUpdateSection(studyId);
  const draftMutation = useRequestAIDraft(studyId);
  const completeMutation = useCompleteSynthesis(studyId);

  const [completedSuccessfully, setCompletedSuccessfully] = React.useState(false);
  const [finalizeError, setFinalizeError] = React.useState<string | null>(null);
  const [incompleteSections, setIncompleteSections] = React.useState<number[]>([]);

  const handleUpdate = (sectionId: number, narrativeText: string, isComplete: boolean) => {
    updateMutation.mutate({
      sectionId,
      data: { narrative_text: narrativeText, is_complete: isComplete },
    });
  };

  const handleRequestDraft = (sectionId: number) => {
    draftMutation.mutate(sectionId, {
      onError: () => {
        // errors surfaced per-section via draftMutation.error
      },
    });
  };

  const handleMarkAllComplete = () => {
    if (!sections) return;
    sections.forEach((s) => {
      if (!s.is_complete) {
        updateMutation.mutate({
          sectionId: s.id,
          data: { is_complete: true },
        });
      }
    });
  };

  const handleFinalize = () => {
    setFinalizeError(null);
    setIncompleteSections([]);
    completeMutation.mutate(undefined, {
      onSuccess: () => {
        setCompletedSuccessfully(true);
      },
      onError: (err) => {
        if (err instanceof ApiError && err.status === 422) {
          try {
            const detail = JSON.parse(err.detail) as {
              detail?: string;
              incomplete_sections?: number[];
            };
            setFinalizeError(detail.detail ?? 'Some sections are incomplete.');
            setIncompleteSections(detail.incomplete_sections ?? []);
          } catch {
            setFinalizeError('Some sections must be completed before finalising.');
          }
        } else {
          setFinalizeError(err.message ?? 'Failed to finalise synthesis.');
        }
      },
    });
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CircularProgress size={20} />
        <Typography>Loading synthesis sections…</Typography>
      </Box>
    );
  }

  if (loadError || !sections) {
    return (
      <Alert severity="error">Failed to load synthesis sections. Please refresh the page.</Alert>
    );
  }

  if (sections.length === 0) {
    return (
      <Alert severity="info">
        No synthesis sections yet. Validate the protocol to auto-create sections.
      </Alert>
    );
  }

  const allComplete = sections.every((s) => s.is_complete);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Narrative Synthesis
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Write a practitioner-friendly narrative for each research question. Use the AI draft as a
        starting point, then edit and mark each section complete.
      </Typography>

      {/* Section editors */}
      {sections.map((section) => (
        <NarrativeSectionEditor
          key={section.id}
          section={section}
          onUpdate={handleUpdate}
          onRequestDraft={handleRequestDraft}
          isSaving={
            updateMutation.isPending &&
            (updateMutation.variables as { sectionId: number } | undefined)?.sectionId ===
              section.id
          }
          isRequestingDraft={draftMutation.isPending && draftMutation.variables === section.id}
          draftError={
            draftMutation.isError && draftMutation.variables === section.id
              ? (draftMutation.error?.message ?? 'Failed to request AI draft.')
              : null
          }
        />
      ))}

      {/* Mark all complete shortcut */}
      {!allComplete && (
        <Box sx={{ mb: 2 }}>
          <Button
            size="small"
            variant="outlined"
            onClick={handleMarkAllComplete}
            disabled={updateMutation.isPending}
          >
            Mark All Sections Complete
          </Button>
        </Box>
      )}

      {/* Finalize error */}
      {finalizeError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {finalizeError}
          {incompleteSections.length > 0 && (
            <> Incomplete RQ indices: {incompleteSections.map((i) => i + 1).join(', ')}.</>
          )}
        </Alert>
      )}

      {/* Success banner */}
      {completedSuccessfully && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Synthesis finalised. You can now generate an Evidence Briefing.
        </Alert>
      )}

      {/* Finalize CTA */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          color="success"
          disabled={completeMutation.isPending || completedSuccessfully}
          onClick={handleFinalize}
          startIcon={completeMutation.isPending ? <CircularProgress size={16} /> : undefined}
        >
          {completeMutation.isPending ? 'Finalising…' : 'Finalize Synthesis'}
        </Button>
      </Box>
    </Box>
  );
}
