/**
 * QualityScoreForm — react-hook-form form for scoring a candidate paper.
 *
 * Renders one input per checklist item (binary checkbox, or scale slider).
 * Shows a live computed aggregate score via useWatch.
 *
 * @module QualityScoreForm
 */

import React from 'react';
import { useForm, useWatch, Controller } from 'react-hook-form';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Slider from '@mui/material/Slider';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import {
  useChecklist,
  useQualityScores,
  useSubmitScores,
} from '../../hooks/slr/useQualityAssessment';
import type { ChecklistItem } from '../../services/slr/qualityApi';

// ---------------------------------------------------------------------------
// Helper: compute aggregate score from form values
// ---------------------------------------------------------------------------

function computeAggregate(
  values: Record<string, number>,
  items: ChecklistItem[],
): number {
  let weightedSum = 0;
  let totalWeight = 0;
  for (const item of items) {
    const val = values[`score_${item.id}`];
    if (val !== undefined) {
      weightedSum += val * item.weight;
      totalWeight += item.weight;
    }
  }
  return totalWeight === 0 ? 0 : weightedSum / totalWeight;
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface QualityScoreFormProps {
  /** Candidate paper to score. */
  candidatePaperId: number;
  /** Reviewer submitting scores. */
  reviewerId: number;
  /** Study whose checklist to load. */
  studyId: number;
}

/**
 * QualityScoreForm renders scoring inputs for each checklist item.
 *
 * Binary items render as a Checkbox, scale items render as a Slider.
 * A live aggregate score is shown below the items.
 *
 * @param candidatePaperId - The paper being scored.
 * @param reviewerId - The reviewer submitting scores.
 * @param studyId - The study whose checklist defines the items.
 */
export default function QualityScoreForm({
  candidatePaperId,
  reviewerId,
  studyId,
}: QualityScoreFormProps) {
  const { data: checklist, isLoading: checklistLoading } = useChecklist(studyId);
  const { data: scores } = useQualityScores(candidatePaperId);
  const submitMutation = useSubmitScores(candidatePaperId);

  const items = checklist?.items ?? [];

  // Build default values from existing scores
  const defaultValues: Record<string, number | string> = {};
  const existingItems = scores?.reviewer_scores.find(
    (r) => r.reviewer_id === reviewerId,
  )?.items ?? [];
  for (const item of items) {
    const existing = existingItems.find((s) => s.checklist_item_id === item.id);
    defaultValues[`score_${item.id}`] = existing?.score_value ?? (item.scoring_method === 'binary' ? 0 : 1);
    defaultValues[`notes_${item.id}`] = existing?.notes ?? '';
  }

  const { control, handleSubmit } = useForm({ defaultValues });

  const watched = useWatch({ control }) as Record<string, number | string>;

  const scoreValues: Record<string, number> = {};
  for (const item of items) {
    const val = watched[`score_${item.id}`];
    scoreValues[`score_${item.id}`] = typeof val === 'number' ? val : Number(val ?? 0);
  }
  const aggregate = computeAggregate(scoreValues, items);

  function onSubmit(values: Record<string, number | string>) {
    const scoresList = items.map((item) => ({
      checklist_item_id: item.id,
      score_value: Number(values[`score_${item.id}`] ?? 0),
      notes: (values[`notes_${item.id}`] as string) || null,
    }));
    submitMutation.mutate({ reviewer_id: reviewerId, scores: scoresList });
  }

  if (checklistLoading) return <CircularProgress size={24} />;
  if (!checklist) return <Typography>No checklist defined for this study.</Typography>;

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} aria-label="Quality score form">
      {items.map((item) => (
        <Box key={item.id} sx={{ mb: 2, p: 1, border: '1px solid #e0e0e0', borderRadius: 1 }}>
          <Typography variant="body2" sx={{ mb: 0.5 }}>
            {item.question} (weight: {item.weight})
          </Typography>
          {item.scoring_method === 'binary' ? (
            <Controller
              name={`score_${item.id}`}
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={!!field.value}
                      onChange={(e) => field.onChange(e.target.checked ? 1 : 0)}
                      inputProps={{ 'aria-label': `binary-score-${item.id}` }}
                    />
                  }
                  label="Yes"
                />
              )}
            />
          ) : (
            <Controller
              name={`score_${item.id}`}
              control={control}
              render={({ field }) => (
                <Slider
                  value={typeof field.value === 'number' ? field.value : 1}
                  onChange={(_, val) => field.onChange(val)}
                  min={1}
                  max={item.scoring_method === 'scale_1_3' ? 3 : 5}
                  step={1}
                  marks
                  valueLabelDisplay="auto"
                  aria-label={`scale-score-${item.id}`}
                />
              )}
            />
          )}
          <Controller
            name={`notes_${item.id}`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                value={field.value ?? ''}
                label="Notes (optional)"
                size="small"
                fullWidth
                inputProps={{ 'aria-label': `notes-${item.id}` }}
              />
            )}
          />
        </Box>
      ))}

      <Typography sx={{ mb: 1 }}>
        Aggregate score: <strong>{aggregate.toFixed(2)}</strong>
      </Typography>

      <Button type="submit" variant="contained" disabled={submitMutation.isPending}>
        {submitMutation.isPending ? 'Submitting...' : 'Submit Scores'}
      </Button>
    </Box>
  );
}
