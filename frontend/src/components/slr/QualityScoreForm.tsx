/**
 * QualityScoreForm — react-hook-form form for scoring a candidate paper.
 *
 * Renders one input per checklist item (binary checkbox, or scale slider).
 * Shows a live computed aggregate score via useWatch.
 *
 * @module QualityScoreForm
 */

import { useForm, useWatch, Controller } from 'react-hook-form';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Slider from '@mui/material/Slider';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormHelperText from '@mui/material/FormHelperText';
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

function computeAggregate(values: Record<string, number>, items: ChecklistItem[]): number {
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

/** DARE's three anchor values, highest first, as they appear on the form. */
const YES_PARTIAL_NO_VALUES = ['1', '0.5', '0'] as const;

/** Y / P / N labels, keyed by the value each scores. */
const YES_PARTIAL_NO_LABELS: Record<string, string> = {
  '1': 'Yes',
  '0.5': 'Partly',
  '0': 'No',
};

/**
 * Anchor lookup tolerant of how the value is written.
 *
 * The backend keys anchors `'1.0' | '0.5' | '0.0'`, while a radio's value is
 * the string `'1' | '0.5' | '0'`. Comparing numerically rather than by string
 * avoids an anchor silently rendering blank on a `'1'` vs `'1.0'` mismatch.
 */
function anchorFor(item: ChecklistItem, value: string): string | undefined {
  const anchors = item.anchors;
  if (!anchors) return undefined;
  const target = Number(value);
  const match = Object.keys(anchors).find((key) => Number(key) === target);
  return match === undefined ? undefined : anchors[match];
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface QualityScoreFormProps {
  /** Candidate paper to score. */
  candidatePaperId: number;
  /** Study whose checklist to load. */
  studyId: number;
}

/**
 * QualityScoreForm renders scoring inputs for each checklist item.
 *
 * Binary items render as a Checkbox, scale items render as a Slider.
 * A live aggregate score is shown below the items. The submitting reviewer
 * is resolved server-side from the session — this form never sends a
 * client-supplied reviewer id. It prefills from the viewer's own prior score
 * using `viewer_reviewer_id` from the scores response, matched explicitly
 * against `null`/`undefined` rather than truthiness, because `0` is a valid
 * reviewer id.
 *
 * @param candidatePaperId - The paper being scored.
 * @param studyId - The study whose checklist defines the items.
 */
export default function QualityScoreForm({ candidatePaperId, studyId }: QualityScoreFormProps) {
  const { data: checklist, isLoading: checklistLoading } = useChecklist(studyId);
  const { data: scores } = useQualityScores(candidatePaperId);
  const submitMutation = useSubmitScores(candidatePaperId);

  const items = checklist?.items ?? [];

  // Build default values from the viewer's own prior scores, if any. `0` is
  // a legitimate reviewer id, so this must not use a truthiness check.
  const defaultValues: Record<string, number | string> = {};
  const viewerReviewerId = scores?.viewer_reviewer_id;
  const hasViewerReviewerId = viewerReviewerId !== null && viewerReviewerId !== undefined;
  const existingItems = hasViewerReviewerId
    ? (scores?.reviewer_scores.find((r) => r.reviewer_id === viewerReviewerId)?.items ?? [])
    : [];
  for (const item of items) {
    const existing = existingItems.find((s) => s.checklist_item_id === item.id);
    if (item.scoring_method === 'yes_partial_no') {
      // Deliberately '' — an anchored judgement must not be preselected. The
      // old tertiary rating slider defaulted to 0.5 and submitted it, which
      // recorded an assessment nobody made (TFIX7 part 1). A default here
      // would reintroduce exactly that, one instrument over.
      defaultValues[`score_${item.id}`] =
        existing?.score_value === undefined ? '' : String(existing.score_value);
    } else {
      defaultValues[`score_${item.id}`] =
        existing?.score_value ?? (item.scoring_method === 'binary' ? 0 : 1);
    }
    defaultValues[`notes_${item.id}`] = existing?.notes ?? '';
  }

  const { control, handleSubmit } = useForm({ defaultValues });

  const anchored = items.filter((item) => item.scoring_method === 'yes_partial_no');
  const isAnchoredInstrument = anchored.length > 0 && anchored.length === items.length;

  const watched = useWatch({ control }) as Record<string, number | string>;

  const scoreValues: Record<string, number> = {};
  for (const item of items) {
    const val = watched[`score_${item.id}`];
    // An unanswered anchored item contributes nothing, rather than counting
    // as a zero — "not assessed" and "scored N" are different findings.
    if (item.scoring_method === 'yes_partial_no' && (val === '' || val === undefined)) continue;
    scoreValues[`score_${item.id}`] = typeof val === 'number' ? val : Number(val ?? 0);
  }
  const aggregate = computeAggregate(scoreValues, items);
  // For an anchored instrument the headline figure is the running total on
  // its own scale, so it must be the sum of what has been answered — not the
  // mean rescaled, which would read "2 out of 2" with one question answered.
  const anchoredTotal = Object.values(scoreValues).reduce((sum, value) => sum + value, 0);

  function onSubmit(values: Record<string, number | string>) {
    const scoresList = items.map((item) => ({
      checklist_item_id: item.id,
      score_value: Number(values[`score_${item.id}`] ?? 0),
      notes: (values[`notes_${item.id}`] as string) || null,
    }));
    submitMutation.mutate({ scores: scoresList });
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
          ) : item.scoring_method === 'yes_partial_no' ? (
            <Controller
              name={`score_${item.id}`}
              control={control}
              rules={{ required: 'Select a score for this question.' }}
              render={({ field, fieldState }) => (
                <>
                  <RadioGroup
                    value={field.value ?? ''}
                    onChange={(e) => field.onChange(e.target.value)}
                  >
                    {YES_PARTIAL_NO_VALUES.map((value) => (
                      <FormControlLabel
                        key={value}
                        value={value}
                        control={
                          <Radio
                            size="small"
                            inputProps={{ 'aria-label': `ypn-score-${item.id}-${value}` }}
                          />
                        }
                        label={
                          <Box>
                            <Typography variant="body2" component="span">
                              {YES_PARTIAL_NO_LABELS[value]} ({value})
                            </Typography>
                            {anchorFor(item, value) && (
                              <Typography variant="caption" display="block" color="text.secondary">
                                {anchorFor(item, value)}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    ))}
                  </RadioGroup>
                  {fieldState.error && (
                    <FormHelperText error>{fieldState.error.message}</FormHelperText>
                  )}
                </>
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
            rules={
              item.scoring_method === 'yes_partial_no'
                ? {
                    // 04-tertiary.md: "justification per answer is mandatory,
                    // not optional metadata". Enforced server-side too — this
                    // is the courtesy copy, not the guarantee.
                    validate: (value) =>
                      String(value ?? '').trim().length > 0 ||
                      'A justification is required for this answer.',
                  }
                : undefined
            }
            render={({ field, fieldState }) => (
              <TextField
                {...field}
                value={field.value ?? ''}
                label={
                  item.scoring_method === 'yes_partial_no'
                    ? 'Justification (required)'
                    : 'Notes (optional)'
                }
                size="small"
                fullWidth
                multiline={item.scoring_method === 'yes_partial_no'}
                error={!!fieldState.error}
                helperText={fieldState.error?.message}
                inputProps={{ 'aria-label': `notes-${item.id}` }}
              />
            )}
          />
        </Box>
      ))}

      <Typography sx={{ mb: 1 }}>
        {isAnchoredInstrument ? (
          <>
            {checklist.name} score:{' '}
            <strong>
              {anchoredTotal.toFixed(2)} out of {items.length}
            </strong>
          </>
        ) : (
          <>
            Aggregate score: <strong>{aggregate.toFixed(2)}</strong>
          </>
        )}
      </Typography>

      <Button type="submit" variant="contained" disabled={submitMutation.isPending}>
        {submitMutation.isPending ? 'Submitting...' : 'Submit Scores'}
      </Button>
    </Box>
  );
}
