/**
 * NarrativeSectionEditor — editor for a single narrative synthesis section (feature 008).
 *
 * Displays the research question, an AI draft panel, and an editable narrative
 * textarea. The researcher can request an AI draft, accept it into the narrative
 * field, and mark the section complete.
 */

import React from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import FormControlLabel from '@mui/material/FormControlLabel';
import Paper from '@mui/material/Paper';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import type { NarrativeSection } from '../../services/rapid/synthesisApi';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link NarrativeSectionEditor}. */
export interface NarrativeSectionEditorProps {
  /** The synthesis section to render. */
  section: NarrativeSection;
  /** Called when the researcher updates narrative text or completion status. */
  onUpdate: (sectionId: number, narrativeText: string, isComplete: boolean) => void;
  /** Called when the researcher requests an AI draft for this section. */
  onRequestDraft: (sectionId: number) => void;
  /** Whether the update mutation is currently pending for this section. */
  isSaving?: boolean;
  /** Whether the AI draft request mutation is pending for this section. */
  isRequestingDraft?: boolean;
  /** Error message from the AI draft request, if any. */
  draftError?: string | null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * NarrativeSectionEditor renders a single synthesis section editor.
 *
 * Layout:
 * - Research question header.
 * - Two-pane area: AI draft preview (left) | editable textarea (right).
 * - "Request AI Draft" button (disabled while a job is running).
 * - "Accept Draft" button copies ai_draft_text → narrative textarea.
 * - "Mark Complete" checkbox.
 *
 * @param section - The synthesis section data.
 * @param onUpdate - Callback on text/completion change.
 * @param onRequestDraft - Callback to enqueue an AI draft job.
 * @param isSaving - Whether a save is in progress.
 * @param isRequestingDraft - Whether a draft request is in progress.
 * @param draftError - Error message from the last draft request, if any.
 */
export default function NarrativeSectionEditor({
  section,
  onUpdate,
  onRequestDraft,
  isSaving = false,
  isRequestingDraft = false,
  draftError = null,
}: NarrativeSectionEditorProps): React.ReactElement {
  const [localText, setLocalText] = React.useState(section.narrative_text ?? '');
  const [localComplete, setLocalComplete] = React.useState(section.is_complete);

  // Sync local state when section prop changes (e.g. after polling)
  React.useEffect(() => {
    setLocalText(section.narrative_text ?? '');
    setLocalComplete(section.is_complete);
  }, [section.narrative_text, section.is_complete]);

  const isDraftActive = section.ai_draft_job_id !== null || isRequestingDraft;

  const handleAcceptDraft = () => {
    if (section.ai_draft_text) {
      setLocalText(section.ai_draft_text);
    }
  };

  const handleSave = () => {
    onUpdate(section.id, localText, localComplete);
  };

  return (
    <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
      {/* Research question header */}
      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
        RQ {section.rq_index + 1}: {section.research_question}
      </Typography>

      <Divider sx={{ mb: 2 }} />

      {/* Draft error */}
      {draftError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {draftError}
        </Alert>
      )}

      {/* Two-pane layout */}
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
        {/* Left pane: AI draft */}
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Typography variant="caption" color="text.secondary" fontWeight="bold">
              AI DRAFT
            </Typography>
            {isDraftActive && <CircularProgress size={14} />}
          </Box>

          <Paper
            variant="outlined"
            sx={{
              p: 1.5,
              minHeight: 120,
              bgcolor: 'grey.50',
              fontSize: '0.875rem',
              whiteSpace: 'pre-wrap',
            }}
          >
            {section.ai_draft_text ? (
              <Typography variant="body2">{section.ai_draft_text}</Typography>
            ) : (
              <Typography variant="body2" color="text.disabled" fontStyle="italic">
                {isDraftActive ? 'Generating draft…' : 'No AI draft yet.'}
              </Typography>
            )}
          </Paper>

          <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
            <Button
              size="small"
              variant="outlined"
              disabled={isDraftActive}
              onClick={() => onRequestDraft(section.id)}
              startIcon={isDraftActive ? <CircularProgress size={12} /> : undefined}
            >
              {isDraftActive ? 'Generating…' : 'Request AI Draft'}
            </Button>

            {section.ai_draft_text && !isDraftActive && (
              <Button size="small" variant="text" onClick={handleAcceptDraft}>
                Accept Draft →
              </Button>
            )}
          </Box>
        </Box>

        {/* Right pane: editable narrative */}
        <Box>
          <Typography
            variant="caption"
            color="text.secondary"
            fontWeight="bold"
            sx={{ mb: 1, display: 'block' }}
          >
            NARRATIVE (FINAL)
          </Typography>
          <TextField
            multiline
            rows={6}
            fullWidth
            value={localText}
            onChange={(e) => setLocalText(e.target.value)}
            placeholder="Write or paste the final narrative for this research question…"
            size="small"
          />
        </Box>
      </Box>

      {/* Footer: complete + save */}
      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={localComplete}
              onChange={(e) => setLocalComplete(e.target.checked)}
              size="small"
            />
          }
          label={<Typography variant="body2">Mark section complete</Typography>}
        />
        <Button
          size="small"
          variant="contained"
          disabled={isSaving}
          onClick={handleSave}
          startIcon={isSaving ? <CircularProgress size={12} /> : undefined}
        >
          {isSaving ? 'Saving…' : 'Save'}
        </Button>
      </Box>
    </Paper>
  );
}
