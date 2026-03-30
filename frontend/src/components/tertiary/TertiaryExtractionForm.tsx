/**
 * TertiaryExtractionForm — data extraction form for a single secondary study.
 *
 * Renders the nine secondary-study-specific extraction fields using
 * react-hook-form + Zod. Shows AI-suggested values in read-only comparison
 * mode when `extraction_status === "ai_complete"`. Uses `useWatch` for
 * derived display logic.
 *
 * @module TertiaryExtractionForm
 */

import React from 'react';
import { Controller, useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Slider from '@mui/material/Slider';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import type { TertiaryExtraction, TertiaryExtractionUpdate } from '../../services/tertiary/extractionApi';

// ---------------------------------------------------------------------------
// Zod schema
// ---------------------------------------------------------------------------

const ExtractionFormSchema = z.object({
  secondary_study_type: z.enum(['SLR', 'SMS', 'RAPID_REVIEW', 'UNKNOWN', '']),
  research_questions_addressed: z.string(),
  databases_searched: z.string(),
  study_period_start: z.number().int().min(1900).max(2100).nullable(),
  study_period_end: z.number().int().min(1900).max(2100).nullable(),
  primary_study_count: z.number().int().min(0).nullable(),
  synthesis_approach_used: z.string(),
  key_findings: z.string(),
  research_gaps: z.string(),
  reviewer_quality_rating: z.number().min(0).max(1).nullable(),
});

type ExtractionFormValues = z.infer<typeof ExtractionFormSchema>;

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link TertiaryExtractionForm}. */
export interface TertiaryExtractionFormProps {
  /** The extraction record to display and edit. */
  extraction: TertiaryExtraction;
  /** Whether the save mutation is in progress. */
  isSaving: boolean;
  /** Called with the update payload when the user submits. */
  onSave: (data: TertiaryExtractionUpdate) => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function toLines(arr: string[] | null | undefined): string {
  return (arr ?? []).join('\n');
}

function fromLines(text: string): string[] {
  return text
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * TertiaryExtractionForm renders all nine extraction fields.
 *
 * Shows an AI-suggestion banner when `extraction_status === "ai_complete"`.
 *
 * @param extraction - The extraction record to display.
 * @param isSaving - Whether save is in progress.
 * @param onSave - Save callback receiving the update payload.
 */
export default function TertiaryExtractionForm({
  extraction,
  isSaving,
  onSave,
}: TertiaryExtractionFormProps) {
  const { control, handleSubmit } = useForm<ExtractionFormValues>({
    resolver: zodResolver(ExtractionFormSchema),
    defaultValues: {
      secondary_study_type:
        (extraction.secondary_study_type as ExtractionFormValues['secondary_study_type']) ?? '',
      research_questions_addressed: toLines(extraction.research_questions_addressed),
      databases_searched: toLines(extraction.databases_searched),
      study_period_start: extraction.study_period_start ?? null,
      study_period_end: extraction.study_period_end ?? null,
      primary_study_count: extraction.primary_study_count ?? null,
      synthesis_approach_used: extraction.synthesis_approach_used ?? '',
      key_findings: extraction.key_findings ?? '',
      research_gaps: extraction.research_gaps ?? '',
      reviewer_quality_rating: extraction.reviewer_quality_rating ?? 0.5,
    },
  });

  const qualityRating = useWatch({ control, name: 'reviewer_quality_rating' });
  const isAiComplete = extraction.extraction_status === 'ai_complete';

  function handleSave(values: ExtractionFormValues) {
    onSave({
      secondary_study_type: values.secondary_study_type || null,
      research_questions_addressed: fromLines(values.research_questions_addressed),
      databases_searched: fromLines(values.databases_searched),
      study_period_start: values.study_period_start,
      study_period_end: values.study_period_end,
      primary_study_count: values.primary_study_count,
      synthesis_approach_used: values.synthesis_approach_used || null,
      key_findings: values.key_findings || null,
      research_gaps: values.research_gaps || null,
      reviewer_quality_rating: values.reviewer_quality_rating,
      extraction_status: 'human_reviewed',
      version_id: extraction.version_id,
    });
  }

  return (
    <Box component="form" onSubmit={handleSubmit(handleSave)} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {isAiComplete && (
        <Alert severity="info" icon={false}>
          <Chip label="AI Pre-filled" color="primary" size="small" sx={{ mr: 1 }} />
          Review the AI-suggested values below and edit as needed before saving.
        </Alert>
      )}

      <TypeAndPeriodRow control={control} />
      <ListFieldsSection control={control} />
      <TextFieldsSection control={control} />
      <QualityRow control={control} qualityRating={qualityRating} />

      <Button type="submit" variant="contained" disabled={isSaving}>
        {isSaving ? 'Saving…' : 'Save Extraction'}
      </Button>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface SubProps {
  control: ReturnType<typeof useForm<ExtractionFormValues>>['control'];
}

interface QualitySubProps extends SubProps {
  qualityRating: number | null;
}

/**
 * Row with study type select and study period year inputs.
 */
function TypeAndPeriodRow({ control }: SubProps) {
  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 2 }}>
      <Controller
        name="secondary_study_type"
        control={control}
        render={({ field }) => (
          <Box>
            <Typography variant="caption">Study Type</Typography>
            <Select {...field} size="small" fullWidth displayEmpty>
              <MenuItem value="">Unknown</MenuItem>
              {['SLR', 'SMS', 'RAPID_REVIEW', 'UNKNOWN'].map((t) => (
                <MenuItem key={t} value={t}>{t}</MenuItem>
              ))}
            </Select>
          </Box>
        )}
      />
      <Controller
        name="study_period_start"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Period Start (year)"
            type="number"
            size="small"
            value={field.value ?? ''}
            onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : null)}
          />
        )}
      />
      <Controller
        name="study_period_end"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Period End (year)"
            type="number"
            size="small"
            value={field.value ?? ''}
            onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : null)}
          />
        )}
      />
    </Box>
  );
}

/**
 * Tag-input style textarea fields for RQs and databases searched.
 */
function ListFieldsSection({ control }: SubProps) {
  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
      <Controller
        name="research_questions_addressed"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Research Questions Addressed (one per line)"
            multiline
            rows={3}
            size="small"
          />
        )}
      />
      <Controller
        name="databases_searched"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Databases Searched (one per line)"
            multiline
            rows={3}
            size="small"
          />
        )}
      />
    </Box>
  );
}

/**
 * Primary study count, synthesis approach, key findings, research gaps.
 */
function TextFieldsSection({ control }: SubProps) {
  return (
    <>
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
        <Controller
          name="primary_study_count"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Primary Study Count"
              type="number"
              size="small"
              value={field.value ?? ''}
              onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : null)}
            />
          )}
        />
        <Controller
          name="synthesis_approach_used"
          control={control}
          render={({ field }) => (
            <TextField {...field} label="Synthesis Approach Used" size="small" />
          )}
        />
      </Box>
      <Controller
        name="key_findings"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Key Findings" multiline rows={4} size="small" />
        )}
      />
      <Controller
        name="research_gaps"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Research Gaps" multiline rows={3} size="small" />
        )}
      />
    </>
  );
}

/**
 * Reviewer quality rating slider.
 */
function QualityRow({ control, qualityRating }: QualitySubProps) {
  return (
    <Box>
      <Typography variant="caption">
        Reviewer Quality Rating: {qualityRating != null ? qualityRating.toFixed(2) : '—'}
      </Typography>
      <Controller
        name="reviewer_quality_rating"
        control={control}
        render={({ field }) => (
          <Slider
            value={field.value ?? 0.5}
            onChange={(_, v) => field.onChange(v)}
            min={0}
            max={1}
            step={0.05}
            marks={[{ value: 0, label: '0' }, { value: 0.5, label: '0.5' }, { value: 1, label: '1' }]}
          />
        )}
      />
    </Box>
  );
}
