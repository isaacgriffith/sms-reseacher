/**
 * SynthesisConfigForm — react-hook-form + Zod form for configuring a
 * synthesis run.  Approach selection shows/hides relevant field groups.
 *
 * @module SynthesisConfigForm
 */

import React from 'react';
import { useForm, useWatch, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormLabel from '@mui/material/FormLabel';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';

// ---------------------------------------------------------------------------
// Zod schema
// ---------------------------------------------------------------------------

const PaperEntrySchema = z.object({
  label: z.string().min(1, 'Label required'),
  effect_size: z.coerce.number(),
  se: z.coerce.number().optional(),
  ci_lower: z.coerce.number().optional(),
  ci_upper: z.coerce.number().optional(),
  weight: z.coerce.number().optional(),
  sample_size: z.coerce.number().optional(),
  unit: z.string().optional(),
});

const ThemeEntrySchema = z.object({
  theme_name: z.string().min(1, 'Theme name required'),
  paper_ids_text: z.string(),
});

const SynthesisFormSchema = z.object({
  approach: z.string().min(1, 'Select an approach'),
  model_type: z.string().optional(),
  heterogeneity_threshold: z.coerce.number().optional(),
  confidence_interval: z.coerce.number().optional(),
  papers: z.array(PaperEntrySchema).optional(),
  themes: z.array(ThemeEntrySchema).optional(),
});

export type SynthesisFormData = z.infer<typeof SynthesisFormSchema>;

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface SynthesisConfigFormProps {
  /** The study being synthesised (passed to the parent on submit). */
  studyId: number;
  /** Called with validated form data when the user submits. */
  onSubmit: (data: SynthesisFormData) => void;
  /** Disables the submit button while a request is in flight. */
  isSubmitting?: boolean;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface MetaAnalysisFieldsProps {
  control: ReturnType<typeof useForm<SynthesisFormData>>['control'];
  register: ReturnType<typeof useForm<SynthesisFormData>>['register'];
  fields: ReturnType<typeof useFieldArray>['fields'];
  append: ReturnType<typeof useFieldArray>['append'];
  remove: ReturnType<typeof useFieldArray>['remove'];
}

/**
 * Fields shown for meta_analysis approach: model type, thresholds, paper rows.
 */
function MetaAnalysisFields({ control, register, fields, append, remove }: MetaAnalysisFieldsProps) {
  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Controller
          name="model_type"
          control={control}
          defaultValue="auto"
          render={({ field }) => (
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel id="model-type-label">Model type</InputLabel>
              <Select
                {...field}
                labelId="model-type-label"
                label="Model type"
                size="small"
              >
                <MenuItem value="auto">Auto</MenuItem>
                <MenuItem value="fixed">Fixed</MenuItem>
                <MenuItem value="random">Random</MenuItem>
              </Select>
            </FormControl>
          )}
        />
        <TextField
          {...register('heterogeneity_threshold')}
          label="Het. threshold"
          type="number"
          size="small"
          defaultValue={0.1}
          sx={{ width: 160 }}
        />
        <TextField
          {...register('confidence_interval')}
          label="CI level"
          type="number"
          size="small"
          defaultValue={0.95}
          sx={{ width: 120 }}
        />
      </Box>
      <PaperRows fields={fields} register={register} append={append} remove={remove} showSe />
    </Box>
  );
}

interface DescriptiveFieldsProps {
  register: ReturnType<typeof useForm<SynthesisFormData>>['register'];
  fields: ReturnType<typeof useFieldArray>['fields'];
  append: ReturnType<typeof useFieldArray>['append'];
  remove: ReturnType<typeof useFieldArray>['remove'];
}

/**
 * Fields shown for descriptive approach: paper rows with sample size + unit.
 */
function DescriptiveFields({ register, fields, append, remove }: DescriptiveFieldsProps) {
  return <PaperRows fields={fields} register={register} append={append} remove={remove} showSe={false} />;
}

interface PaperRowsProps {
  fields: ReturnType<typeof useFieldArray>['fields'];
  register: ReturnType<typeof useForm<SynthesisFormData>>['register'];
  append: ReturnType<typeof useFieldArray>['append'];
  remove: ReturnType<typeof useFieldArray>['remove'];
  showSe: boolean;
}

/** Dynamic paper entry rows shared by MetaAnalysis and Descriptive forms. */
function PaperRows({ fields, register, append, remove, showSe }: PaperRowsProps) {
  return (
    <Box>
      <Typography variant="caption" sx={{ mb: 1, display: 'block' }}>Papers</Typography>
      {fields.map((field, index) => (
        <Box key={field.id} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
          <TextField {...register(`papers.${index}.label`)} label="Label" size="small" sx={{ width: 120 }} />
          <TextField {...register(`papers.${index}.effect_size`)} label="Effect" size="small" type="number" sx={{ width: 80 }} />
          {showSe && (
            <TextField {...register(`papers.${index}.se`)} label="SE" size="small" type="number" sx={{ width: 70 }} />
          )}
          <TextField {...register(`papers.${index}.ci_lower`)} label="CI Low" size="small" type="number" sx={{ width: 80 }} />
          <TextField {...register(`papers.${index}.ci_upper`)} label="CI High" size="small" type="number" sx={{ width: 80 }} />
          {!showSe && (
            <>
              <TextField {...register(`papers.${index}.sample_size`)} label="N" size="small" type="number" sx={{ width: 70 }} />
              <TextField {...register(`papers.${index}.unit`)} label="Unit" size="small" sx={{ width: 80 }} />
            </>
          )}
          <IconButton size="small" onClick={() => remove(index)} aria-label={`Remove paper ${index + 1}`}>✕</IconButton>
        </Box>
      ))}
      <Button size="small" onClick={() => append({ label: '', effect_size: 0 })}>+ Add paper</Button>
    </Box>
  );
}

interface QualitativeFieldsProps {
  register: ReturnType<typeof useForm<SynthesisFormData>>['register'];
  themeFields: ReturnType<typeof useFieldArray>['fields'];
  appendTheme: ReturnType<typeof useFieldArray>['append'];
  removeTheme: ReturnType<typeof useFieldArray>['remove'];
}

/**
 * Fields shown for qualitative approach: theme builder with paper IDs.
 */
function QualitativeFields({ register, themeFields, appendTheme, removeTheme }: QualitativeFieldsProps) {
  return (
    <Box>
      <Typography variant="caption" sx={{ mb: 1, display: 'block' }} data-testid="qualitative-themes-label">Themes</Typography>
      {themeFields.map((field, index) => (
        <Box key={field.id} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
          <TextField
            {...register(`themes.${index}.theme_name`)}
            label="Theme name"
            size="small"
            sx={{ width: 160 }}
          />
          <TextField
            {...register(`themes.${index}.paper_ids_text`)}
            label="Paper IDs (comma-separated)"
            size="small"
            sx={{ width: 240 }}
          />
          <IconButton size="small" onClick={() => removeTheme(index)} aria-label={`Remove theme ${index + 1}`}>✕</IconButton>
        </Box>
      ))}
      <Button size="small" onClick={() => appendTheme({ theme_name: '', paper_ids_text: '' })}>+ Add theme</Button>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

/**
 * SynthesisConfigForm composes approach selection with conditional field
 * groups for meta-analysis, descriptive, and qualitative synthesis.
 *
 * @param props - {@link SynthesisConfigFormProps}
 */
export default function SynthesisConfigForm({
  studyId: _studyId,
  onSubmit,
  isSubmitting = false,
}: SynthesisConfigFormProps) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<SynthesisFormData>({
    resolver: zodResolver(SynthesisFormSchema),
    defaultValues: {
      approach: '',
      model_type: 'auto',
      heterogeneity_threshold: 0.1,
      confidence_interval: 0.95,
      papers: [],
      themes: [],
    },
  });

  const approach = useWatch({ control, name: 'approach' });

  const { fields: paperFields, append: appendPaper, remove: removePaper } = useFieldArray({
    control,
    name: 'papers',
  });

  const { fields: themeFields, append: appendTheme, remove: removeTheme } = useFieldArray({
    control,
    name: 'themes',
  });

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <FormControl component="fieldset" sx={{ mb: 2 }}>
        <FormLabel component="legend">Synthesis approach</FormLabel>
        <Controller
          name="approach"
          control={control}
          render={({ field }) => (
            <RadioGroup row {...field}>
              <FormControlLabel value="meta_analysis" control={<Radio />} label="Meta-analysis" />
              <FormControlLabel value="descriptive" control={<Radio />} label="Descriptive" />
              <FormControlLabel value="qualitative" control={<Radio />} label="Qualitative" />
            </RadioGroup>
          )}
        />
        {errors.approach && (
          <Typography color="error" variant="caption">{errors.approach.message}</Typography>
        )}
      </FormControl>

      {approach === 'meta_analysis' && (
        <MetaAnalysisFields
          control={control}
          register={register}
          fields={paperFields}
          append={appendPaper}
          remove={removePaper}
        />
      )}

      {approach === 'descriptive' && (
        <DescriptiveFields
          register={register}
          fields={paperFields}
          append={appendPaper}
          remove={removePaper}
        />
      )}

      {approach === 'qualitative' && (
        <QualitativeFields
          register={register}
          themeFields={themeFields}
          appendTheme={appendTheme}
          removeTheme={removeTheme}
        />
      )}

      <Box sx={{ mt: 2 }}>
        <Button
          type="submit"
          variant="contained"
          disabled={isSubmitting}
          data-testid="synthesis-submit"
        >
          {isSubmitting ? 'Running…' : 'Run Synthesis'}
        </Button>
      </Box>
    </Box>
  );
}
