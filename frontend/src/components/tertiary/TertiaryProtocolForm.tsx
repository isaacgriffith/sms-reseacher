/**
 * TertiaryProtocolForm — react-hook-form form for creating and editing a
 * Tertiary Study protocol.
 *
 * Renders all protocol fields as controlled inputs using react-hook-form + Zod.
 * Blocked and read-only when `status === "validated"`.
 * Uses `useWatch` for reactive field display (recency_cutoff_year).
 *
 * @module TertiaryProtocolForm
 */

import React, { useEffect } from 'react';
import { Controller, useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormGroup from '@mui/material/FormGroup';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Slider from '@mui/material/Slider';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import type { TertiaryProtocol, TertiaryProtocolUpdate } from '../../services/tertiary/protocolApi';

// ---------------------------------------------------------------------------
// Zod validation schema
// ---------------------------------------------------------------------------

const SECONDARY_STUDY_TYPE_OPTIONS = ['SLR', 'SMS', 'RAPID_REVIEW'] as const;

const TertiaryProtocolFormSchema = z.object({
  background: z.string().optional(),
  research_questions: z.string().min(1, 'At least one research question is required'),
  secondary_study_types: z.array(z.string()).min(1, 'Select at least one secondary study type'),
  inclusion_criteria: z.string().optional(),
  exclusion_criteria: z.string().optional(),
  recency_cutoff_year: z.number().int().min(1900).max(2100).nullable(),
  search_strategy: z.string().optional(),
  quality_threshold: z.number().min(0).max(1).nullable(),
  synthesis_approach: z.enum(['narrative', 'thematic', 'meta_analysis', 'descriptive', 'qualitative', '']),
  dissemination_strategy: z.string().optional(),
});

type TertiaryProtocolFormValues = z.infer<typeof TertiaryProtocolFormSchema>;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function arrayToText(arr: string[] | null | undefined): string {
  return (arr ?? []).join('\n');
}

function textToArray(text: string): string[] {
  return text.split('\n').map((s) => s.trim()).filter(Boolean);
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

/** Wraps a group of form controls under a section heading. */
function FormSection({ title, children }: SectionProps) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600, color: '#374151' }}>
        {title}
      </Typography>
      {children}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Props and component
// ---------------------------------------------------------------------------

/** Props for {@link TertiaryProtocolForm}. */
export interface TertiaryProtocolFormProps {
  /** Current protocol data (null if none created yet). */
  protocol: TertiaryProtocol | null;
  /** Whether the form is currently saving. */
  isSaving?: boolean;
  /** Called with the updated protocol data on submit. */
  onSave: (data: TertiaryProtocolUpdate) => void;
}

/**
 * TertiaryProtocolForm renders all Tertiary Study protocol fields.
 *
 * The form is read-only when the protocol status is `"validated"`.
 * Uses `useWatch` to reactively display the recency cutoff year value.
 *
 * @param protocol - The current protocol data or null.
 * @param isSaving - Whether a save operation is in progress.
 * @param onSave - Callback receiving the form data on submit.
 */
export default function TertiaryProtocolForm({
  protocol,
  isSaving = false,
  onSave,
}: TertiaryProtocolFormProps) {
  const isReadOnly = protocol?.status === 'validated';

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TertiaryProtocolFormValues>({
    resolver: zodResolver(TertiaryProtocolFormSchema),
    defaultValues: {
      background: protocol?.background ?? '',
      research_questions: arrayToText(protocol?.research_questions),
      secondary_study_types: protocol?.secondary_study_types ?? ['SLR', 'SMS'],
      inclusion_criteria: arrayToText(protocol?.inclusion_criteria),
      exclusion_criteria: arrayToText(protocol?.exclusion_criteria),
      recency_cutoff_year: protocol?.recency_cutoff_year ?? null,
      search_strategy: protocol?.search_strategy ?? '',
      quality_threshold: protocol?.quality_threshold ?? 0.6,
      synthesis_approach: (protocol?.synthesis_approach ?? '') as TertiaryProtocolFormValues['synthesis_approach'],
      dissemination_strategy: protocol?.dissemination_strategy ?? '',
    },
  });

  // Sync form when protocol data changes
  useEffect(() => {
    if (protocol) {
      reset({
        background: protocol.background ?? '',
        research_questions: arrayToText(protocol.research_questions),
        secondary_study_types: protocol.secondary_study_types ?? ['SLR', 'SMS'],
        inclusion_criteria: arrayToText(protocol.inclusion_criteria),
        exclusion_criteria: arrayToText(protocol.exclusion_criteria),
        recency_cutoff_year: protocol.recency_cutoff_year ?? null,
        search_strategy: protocol.search_strategy ?? '',
        quality_threshold: protocol.quality_threshold ?? 0.6,
        synthesis_approach: (protocol.synthesis_approach ?? '') as TertiaryProtocolFormValues['synthesis_approach'],
        dissemination_strategy: protocol.dissemination_strategy ?? '',
      });
    }
  }, [protocol, reset]);

  // Reactive display for recency_cutoff_year
  const recencyYear = useWatch({ control, name: 'recency_cutoff_year' });

  function onSubmit(values: TertiaryProtocolFormValues) {
    onSave({
      background: values.background || null,
      research_questions: textToArray(values.research_questions),
      secondary_study_types: values.secondary_study_types,
      inclusion_criteria: textToArray(values.inclusion_criteria ?? ''),
      exclusion_criteria: textToArray(values.exclusion_criteria ?? ''),
      recency_cutoff_year: values.recency_cutoff_year,
      search_strategy: values.search_strategy || null,
      quality_threshold: values.quality_threshold,
      synthesis_approach: values.synthesis_approach || null,
      dissemination_strategy: values.dissemination_strategy || null,
      version_id: protocol?.version_id,
    });
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} aria-label="Tertiary Protocol form">
      {isReadOnly && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Protocol validated. Fields are read-only.
        </Alert>
      )}

      <FormSection title="Background">
        <Controller
          name="background"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Background"
              multiline
              minRows={3}
              fullWidth
              disabled={isReadOnly}
              helperText="Motivation for conducting this tertiary study"
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'background' }}
            />
          )}
        />
      </FormSection>

      <FormSection title="Research Questions">
        <Controller
          name="research_questions"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Research Questions (one per line)"
              multiline
              minRows={3}
              fullWidth
              error={!!errors.research_questions}
              helperText={errors.research_questions?.message ?? 'Enter one RQ per line'}
              disabled={isReadOnly}
              inputProps={{ 'aria-label': 'research_questions' }}
            />
          )}
        />
      </FormSection>

      <SecondaryStudyTypesSection control={control} errors={errors} isReadOnly={isReadOnly} />

      <InclusionExclusionSection control={control} errors={errors} isReadOnly={isReadOnly} />

      <FormSection title="Search Configuration">
        <Controller
          name="search_strategy"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Search Strategy"
              multiline
              minRows={2}
              fullWidth
              disabled={isReadOnly}
              helperText="Describe how secondary studies will be identified"
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'search_strategy' }}
            />
          )}
        />
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1, color: '#374151' }}>
            Recency Cutoff Year
            {recencyYear !== null && recencyYear !== undefined ? ` — ${recencyYear}` : ' — not set'}
          </Typography>
          <Controller
            name="recency_cutoff_year"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                type="number"
                label="Earliest year for included secondary studies"
                fullWidth
                disabled={isReadOnly}
                value={field.value ?? ''}
                onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : null)}
                inputProps={{ min: 1900, max: 2100, 'aria-label': 'recency_cutoff_year' }}
              />
            )}
          />
        </Box>
      </FormSection>

      <SynthesisSection control={control} errors={errors} isReadOnly={isReadOnly} />

      {!isReadOnly && (
        <Button type="submit" variant="contained" disabled={isSaving} sx={{ mt: 1 }}>
          {isSaving ? 'Saving…' : 'Save Protocol'}
        </Button>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Sub-components (extracted to stay within 100 JSX lines per component)
// ---------------------------------------------------------------------------

interface SubFormProps {
  control: ReturnType<typeof useForm<TertiaryProtocolFormValues>>['control'];
  errors: ReturnType<typeof useForm<TertiaryProtocolFormValues>>['formState']['errors'];
  isReadOnly: boolean;
}

/** Secondary study type multi-select checkboxes. */
function SecondaryStudyTypesSection({ control, errors, isReadOnly }: SubFormProps) {
  return (
    <FormSection title="Accepted Secondary Study Types">
      <Controller
        name="secondary_study_types"
        control={control}
        render={({ field }) => (
          <FormControl error={!!errors.secondary_study_types} component="fieldset">
            <FormGroup row>
              {SECONDARY_STUDY_TYPE_OPTIONS.map((opt) => (
                <FormControlLabel
                  key={opt}
                  label={opt.replace('_', ' ')}
                  disabled={isReadOnly}
                  control={
                    <Checkbox
                      checked={field.value.includes(opt)}
                      onChange={(e) => {
                        const next = e.target.checked
                          ? [...field.value, opt]
                          : field.value.filter((v) => v !== opt);
                        field.onChange(next);
                      }}
                      inputProps={{ 'aria-label': opt }}
                    />
                  }
                />
              ))}
            </FormGroup>
            {errors.secondary_study_types && (
              <FormHelperText>
                {typeof errors.secondary_study_types.message === 'string'
                  ? errors.secondary_study_types.message
                  : 'Select at least one type'}
              </FormHelperText>
            )}
          </FormControl>
        )}
      />
    </FormSection>
  );
}

/** Inclusion and exclusion criteria text areas. */
function InclusionExclusionSection({ control, errors, isReadOnly }: SubFormProps) {
  return (
    <FormSection title="Inclusion & Exclusion Criteria">
      <Controller
        name="inclusion_criteria"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Inclusion Criteria (one per line)"
            multiline
            minRows={3}
            fullWidth
            error={!!errors.inclusion_criteria}
            helperText={errors.inclusion_criteria?.message ?? 'One criterion per line'}
            disabled={isReadOnly}
            sx={{ mb: 2 }}
            inputProps={{ 'aria-label': 'inclusion_criteria' }}
          />
        )}
      />
      <Controller
        name="exclusion_criteria"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Exclusion Criteria (one per line)"
            multiline
            minRows={3}
            fullWidth
            error={!!errors.exclusion_criteria}
            helperText={errors.exclusion_criteria?.message ?? 'One criterion per line'}
            disabled={isReadOnly}
            inputProps={{ 'aria-label': 'exclusion_criteria' }}
          />
        )}
      />
    </FormSection>
  );
}

/** Synthesis approach, quality threshold, and dissemination strategy. */
function SynthesisSection({ control, errors, isReadOnly }: SubFormProps) {
  return (
    <FormSection title="Synthesis & Quality">
      <Controller
        name="synthesis_approach"
        control={control}
        render={({ field }) => (
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="synthesis-approach-label">Synthesis Approach</InputLabel>
            <Select
              {...field}
              labelId="synthesis-approach-label"
              label="Synthesis Approach"
              disabled={isReadOnly}
              inputProps={{ 'aria-label': 'synthesis_approach' }}
            >
              <MenuItem value="">— not set —</MenuItem>
              <MenuItem value="narrative">Narrative</MenuItem>
              <MenuItem value="thematic">Thematic</MenuItem>
              <MenuItem value="descriptive">Descriptive</MenuItem>
              <MenuItem value="qualitative">Qualitative</MenuItem>
              <MenuItem value="meta_analysis">Meta-analysis</MenuItem>
            </Select>
            {errors.synthesis_approach && (
              <FormHelperText error>{errors.synthesis_approach.message}</FormHelperText>
            )}
          </FormControl>
        )}
      />
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ mb: 1 }}>
          Quality Threshold (0 = no threshold, 1 = perfect)
        </Typography>
        <Controller
          name="quality_threshold"
          control={control}
          render={({ field }) => (
            <Slider
              {...field}
              value={field.value ?? 0.6}
              onChange={(_, val) => field.onChange(val as number)}
              min={0}
              max={1}
              step={0.05}
              valueLabelDisplay="auto"
              disabled={isReadOnly}
              aria-label="quality_threshold"
            />
          )}
        />
      </Box>
      <Controller
        name="dissemination_strategy"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Dissemination Strategy"
            fullWidth
            disabled={isReadOnly}
            helperText="How will results be published or shared?"
            inputProps={{ 'aria-label': 'dissemination_strategy' }}
          />
        )}
      />
    </FormSection>
  );
}
