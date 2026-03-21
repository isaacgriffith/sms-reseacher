/**
 * ProtocolForm — react-hook-form form for creating and editing an SLR protocol.
 *
 * Renders all 11 protocol fields as controlled inputs.
 * Blocked and read-only when `status === "validated"`.
 * Uses `useWatch` for conditional `pico_context` field display.
 *
 * @module ProtocolForm
 */

import React, { useEffect } from 'react';
import { useForm, useWatch, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import FormHelperText from '@mui/material/FormHelperText';
import type { ReviewProtocol } from '../../services/slr/protocolApi';

// ---------------------------------------------------------------------------
// Zod validation schema
// ---------------------------------------------------------------------------

const ProtocolFormSchema = z.object({
  background: z.string().min(1, 'Background is required'),
  rationale: z.string().min(1, 'Rationale is required'),
  research_questions: z.string().min(1, 'At least one research question is required'),
  pico_population: z.string().min(1, 'Population is required'),
  pico_intervention: z.string().min(1, 'Intervention is required'),
  pico_comparison: z.string().min(1, 'Comparison is required'),
  pico_outcome: z.string().min(1, 'Outcome is required'),
  pico_context: z.string().optional(),
  search_strategy: z.string().min(1, 'Search strategy is required'),
  inclusion_criteria: z.string().min(1, 'Inclusion criteria are required'),
  exclusion_criteria: z.string().min(1, 'Exclusion criteria are required'),
  data_extraction_strategy: z.string().min(1, 'Data extraction strategy is required'),
  synthesis_approach: z.enum(['meta_analysis', 'descriptive', 'qualitative']),
  dissemination_strategy: z.string().min(1, 'Dissemination strategy is required'),
  timetable: z.string().min(1, 'Timetable is required'),
});

type ProtocolFormValues = z.infer<typeof ProtocolFormSchema>;

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface ProtocolSectionProps {
  title: string;
  children: React.ReactNode;
}

/**
 * ProtocolSection wraps a group of fields under a section heading.
 *
 * @param title - Section heading text.
 * @param children - Form controls to render inside the section.
 */
function ProtocolSection({ title, children }: ProtocolSectionProps) {
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
// Helpers to convert between form strings and array fields
// ---------------------------------------------------------------------------

function arrayToText(arr: string[] | null | undefined): string {
  return (arr ?? []).join('\n');
}

function textToArray(text: string): string[] {
  return text.split('\n').map((s) => s.trim()).filter(Boolean);
}

// ---------------------------------------------------------------------------
// Props and component
// ---------------------------------------------------------------------------

interface ProtocolFormProps {
  /** Current protocol data (null if none created yet). */
  protocol: ReviewProtocol | null;
  /** Whether the form is currently saving. */
  isSaving?: boolean;
  /** Called with partial protocol data when the user saves. */
  onSave: (data: Partial<ReviewProtocol>) => void;
}

/**
 * ProtocolForm renders all SLR protocol fields with validation.
 *
 * The form is read-only when the protocol status is `"validated"`.
 * `pico_context` is optional and can be omitted.
 *
 * @param protocol - The current protocol data or null.
 * @param isSaving - Whether a save operation is in progress.
 * @param onSave - Callback receiving the form data on submit.
 */
export default function ProtocolForm({ protocol, isSaving = false, onSave }: ProtocolFormProps) {
  const isReadOnly = protocol?.status === 'validated';

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProtocolFormValues>({
    resolver: zodResolver(ProtocolFormSchema),
    defaultValues: {
      background: protocol?.background ?? '',
      rationale: protocol?.rationale ?? '',
      research_questions: arrayToText(protocol?.research_questions),
      pico_population: protocol?.pico_population ?? '',
      pico_intervention: protocol?.pico_intervention ?? '',
      pico_comparison: protocol?.pico_comparison ?? '',
      pico_outcome: protocol?.pico_outcome ?? '',
      pico_context: protocol?.pico_context ?? '',
      search_strategy: protocol?.search_strategy ?? '',
      inclusion_criteria: arrayToText(protocol?.inclusion_criteria),
      exclusion_criteria: arrayToText(protocol?.exclusion_criteria),
      data_extraction_strategy: protocol?.data_extraction_strategy ?? '',
      synthesis_approach: (protocol?.synthesis_approach as ProtocolFormValues['synthesis_approach']) ?? 'descriptive',
      dissemination_strategy: protocol?.dissemination_strategy ?? '',
      timetable: protocol?.timetable ?? '',
    },
  });

  // Sync form when protocol data loads
  useEffect(() => {
    if (protocol) {
      reset({
        background: protocol.background ?? '',
        rationale: protocol.rationale ?? '',
        research_questions: arrayToText(protocol.research_questions),
        pico_population: protocol.pico_population ?? '',
        pico_intervention: protocol.pico_intervention ?? '',
        pico_comparison: protocol.pico_comparison ?? '',
        pico_outcome: protocol.pico_outcome ?? '',
        pico_context: protocol.pico_context ?? '',
        search_strategy: protocol.search_strategy ?? '',
        inclusion_criteria: arrayToText(protocol.inclusion_criteria),
        exclusion_criteria: arrayToText(protocol.exclusion_criteria),
        data_extraction_strategy: protocol.data_extraction_strategy ?? '',
        synthesis_approach: (protocol.synthesis_approach as ProtocolFormValues['synthesis_approach']) ?? 'descriptive',
        dissemination_strategy: protocol.dissemination_strategy ?? '',
        timetable: protocol.timetable ?? '',
      });
    }
  }, [protocol, reset]);

  // Watch pico_context to show conditional helper text
  const picoContext = useWatch({ control, name: 'pico_context' });

  function onSubmit(values: ProtocolFormValues) {
    onSave({
      background: values.background,
      rationale: values.rationale,
      research_questions: textToArray(values.research_questions),
      pico_population: values.pico_population,
      pico_intervention: values.pico_intervention,
      pico_comparison: values.pico_comparison,
      pico_outcome: values.pico_outcome,
      pico_context: values.pico_context ?? null,
      search_strategy: values.search_strategy,
      inclusion_criteria: textToArray(values.inclusion_criteria),
      exclusion_criteria: textToArray(values.exclusion_criteria),
      data_extraction_strategy: values.data_extraction_strategy,
      synthesis_approach: values.synthesis_approach,
      dissemination_strategy: values.dissemination_strategy,
      timetable: values.timetable,
    });
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} aria-label="Protocol form">
      <ProtocolSection title="Background & Rationale">
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
              error={!!errors.background}
              helperText={errors.background?.message}
              disabled={isReadOnly}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'background' }}
            />
          )}
        />
        <Controller
          name="rationale"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Rationale"
              multiline
              minRows={2}
              fullWidth
              error={!!errors.rationale}
              helperText={errors.rationale?.message}
              disabled={isReadOnly}
              inputProps={{ 'aria-label': 'rationale' }}
            />
          )}
        />
      </ProtocolSection>

      <ProtocolSection title="Research Questions">
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
      </ProtocolSection>

      <ProtocolSection title="PICO Framework">
        <Controller
          name="pico_population"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Population"
              fullWidth
              error={!!errors.pico_population}
              helperText={errors.pico_population?.message}
              disabled={isReadOnly}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'pico_population' }}
            />
          )}
        />
        <Controller
          name="pico_intervention"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Intervention"
              fullWidth
              error={!!errors.pico_intervention}
              helperText={errors.pico_intervention?.message}
              disabled={isReadOnly}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'pico_intervention' }}
            />
          )}
        />
        <Controller
          name="pico_comparison"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Comparison"
              fullWidth
              error={!!errors.pico_comparison}
              helperText={errors.pico_comparison?.message}
              disabled={isReadOnly}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'pico_comparison' }}
            />
          )}
        />
        <Controller
          name="pico_outcome"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Outcome"
              fullWidth
              error={!!errors.pico_outcome}
              helperText={errors.pico_outcome?.message}
              disabled={isReadOnly}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'pico_outcome' }}
            />
          )}
        />
        <Controller
          name="pico_context"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Context (optional)"
              fullWidth
              disabled={isReadOnly}
              helperText={picoContext ? 'Context provided' : 'Optional — include if PICOS variant'}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'pico_context' }}
            />
          )}
        />
      </ProtocolSection>

      <ProtocolSection title="Search & Criteria">
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
              error={!!errors.search_strategy}
              helperText={errors.search_strategy?.message}
              disabled={isReadOnly}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'search_strategy' }}
            />
          )}
        />
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
      </ProtocolSection>

      <ProtocolSection title="Synthesis & Reporting">
        <Controller
          name="data_extraction_strategy"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Data Extraction Strategy"
              multiline
              minRows={2}
              fullWidth
              error={!!errors.data_extraction_strategy}
              helperText={errors.data_extraction_strategy?.message}
              disabled={isReadOnly}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'data_extraction_strategy' }}
            />
          )}
        />
        <Controller
          name="synthesis_approach"
          control={control}
          render={({ field }) => (
            <FormControl fullWidth error={!!errors.synthesis_approach} sx={{ mb: 2 }}>
              <InputLabel id="synthesis-approach-label">Synthesis Approach</InputLabel>
              <Select
                {...field}
                labelId="synthesis-approach-label"
                label="Synthesis Approach"
                disabled={isReadOnly}
                inputProps={{ 'aria-label': 'synthesis_approach' }}
              >
                <MenuItem value="meta_analysis">Meta-analysis</MenuItem>
                <MenuItem value="descriptive">Descriptive</MenuItem>
                <MenuItem value="qualitative">Qualitative</MenuItem>
              </Select>
              {errors.synthesis_approach && (
                <FormHelperText>{errors.synthesis_approach.message}</FormHelperText>
              )}
            </FormControl>
          )}
        />
        <Controller
          name="dissemination_strategy"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Dissemination Strategy"
              fullWidth
              error={!!errors.dissemination_strategy}
              helperText={errors.dissemination_strategy?.message}
              disabled={isReadOnly}
              sx={{ mb: 2 }}
              inputProps={{ 'aria-label': 'dissemination_strategy' }}
            />
          )}
        />
        <Controller
          name="timetable"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Timetable"
              fullWidth
              error={!!errors.timetable}
              helperText={errors.timetable?.message}
              disabled={isReadOnly}
              inputProps={{ 'aria-label': 'timetable' }}
            />
          )}
        />
      </ProtocolSection>

      {!isReadOnly && (
        <Button
          type="submit"
          variant="contained"
          disabled={isSaving}
          sx={{ mt: 1 }}
        >
          {isSaving ? 'Saving…' : 'Save Protocol'}
        </Button>
      )}
    </Box>
  );
}
