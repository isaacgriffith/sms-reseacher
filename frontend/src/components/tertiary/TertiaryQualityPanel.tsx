/**
 * TertiaryQualityPanel — DARE quality assessment for a Tertiary study.
 *
 * `07-quality-assessment.md` assigns DARE to tertiary studies and records the
 * reversal that makes it matter: tertiary studies "**do** require
 * primary-study quality assessment, unlike most mapping studies". Before
 * TFIX7 part 3 a tertiary study had nowhere to record one — only a single
 * `reviewer_quality_rating` slider on the extraction form, which the same
 * chapter rejects as a shape.
 *
 * Seeding is an explicit button rather than something that happens on study
 * creation. The checklist is the team's methodological choice; materialising
 * one silently would put questions in their report nobody chose to ask.
 *
 * @module TertiaryQualityPanel
 */

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';
import { useChecklist } from '../../hooks/slr/useQualityAssessment';
import { seedDareChecklist } from '../../services/slr/qualityApi';
import QualityScoreForm from '../slr/QualityScoreForm';

interface AssessablePaper {
  /** Candidate paper id. */
  id: number;
  /** Title shown in the picker. */
  title: string;
}

interface TertiaryQualityPanelProps {
  /** The Tertiary study being assessed. */
  studyId: number;
  /** Included secondary studies available to assess. */
  papers: AssessablePaper[];
}

/**
 * Renders DARE setup and per-paper scoring for a Tertiary study.
 *
 * @param studyId - The Tertiary study id.
 * @param papers - Included secondary studies available to assess.
 */
export default function TertiaryQualityPanel({ studyId, papers }: TertiaryQualityPanelProps) {
  const queryClient = useQueryClient();
  const { data: checklist, isLoading, error } = useChecklist(studyId);
  const [selectedPaperId, setSelectedPaperId] = useState<number | ''>('');

  const seedMutation = useMutation({
    mutationFn: () => seedDareChecklist(studyId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['quality-checklist', studyId] });
    },
  });

  if (isLoading) return <CircularProgress size={24} />;

  // A study with no checklist yet 404s. That is the ordinary starting state,
  // not a failure, so it offers setup rather than reporting an error.
  if (!checklist || error) {
    return (
      <Box>
        <Alert severity="info" sx={{ mb: 2 }}>
          No quality instrument is set up for this study. DARE — four anchored questions
          scored Yes (1) / Partly (0.5) / No (0) — is the instrument for tertiary studies.
          Omitting quality assessment is a legitimate choice, but it should be stated and
          justified in the report rather than left silent.
        </Alert>
        <Button
          variant="contained"
          disabled={seedMutation.isPending}
          onClick={() => seedMutation.mutate()}
        >
          {seedMutation.isPending ? 'Setting up…' : 'Set up DARE'}
        </Button>
        {seedMutation.isError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Could not set up the DARE checklist.
          </Alert>
        )}
      </Box>
    );
  }

  if (papers.length === 0) {
    return (
      <Alert severity="info">
        No included secondary studies to assess yet. Accept papers in Phase 3 first.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
        {checklist.name} quality assessment
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Every answer needs a justification. Scores are recorded per reviewer, so two
        reviewers can be compared — agreement on quality scoring is known to be low even
        among experts, which is why the disagreement is worth seeing.
      </Typography>

      <TextField
        select
        label="Secondary study to assess"
        size="small"
        fullWidth
        sx={{ mb: 2 }}
        value={selectedPaperId}
        onChange={(e) => setSelectedPaperId(Number(e.target.value))}
        inputProps={{ 'aria-label': 'dare-paper-select' }}
      >
        {papers.map((paper) => (
          <MenuItem key={paper.id} value={paper.id}>
            {paper.title}
          </MenuItem>
        ))}
      </TextField>

      {selectedPaperId !== '' && (
        <QualityScoreForm candidatePaperId={selectedPaperId} studyId={studyId} />
      )}
    </Box>
  );
}
