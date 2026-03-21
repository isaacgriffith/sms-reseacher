/**
 * QualityChecklistEditor — react-hook-form editor for quality assessment checklists.
 *
 * Renders a dynamic list of checklist items. Items can be added, removed, and
 * edited inline. Submitting the form calls useUpsertChecklist.
 *
 * @module QualityChecklistEditor
 */

import React from 'react';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Typography from '@mui/material/Typography';
import { useChecklist, useUpsertChecklist } from '../../hooks/slr/useQualityAssessment';

const ChecklistItemFormSchema = z.object({
  question: z.string().min(1, 'Question is required'),
  scoring_method: z.enum(['binary', 'scale_1_3', 'scale_1_5']),
  weight: z.number().min(0),
});

const ChecklistFormSchema = z.object({
  name: z.string().min(1, 'Checklist name is required'),
  description: z.string().optional(),
  items: z.array(ChecklistItemFormSchema),
});

type ChecklistFormValues = z.infer<typeof ChecklistFormSchema>;

interface QualityChecklistEditorProps {
  /** Integer study ID from the parent page. */
  studyId: number;
}

/**
 * QualityChecklistEditor renders the form for creating or updating a quality
 * assessment checklist for an SLR study.
 *
 * @param studyId - The study whose checklist to edit.
 */
export default function QualityChecklistEditor({ studyId }: QualityChecklistEditorProps) {
  const { data: checklist } = useChecklist(studyId);
  const upsertMutation = useUpsertChecklist(studyId);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<ChecklistFormValues>({
    resolver: zodResolver(ChecklistFormSchema),
    defaultValues: {
      name: checklist?.name ?? '',
      description: checklist?.description ?? '',
      items: checklist?.items.map((item) => ({
        question: item.question,
        scoring_method: item.scoring_method,
        weight: item.weight,
      })) ?? [],
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: 'items' });

  function onSubmit(values: ChecklistFormValues) {
    upsertMutation.mutate({
      name: values.name,
      description: values.description ?? null,
      items: values.items.map((item, idx) => ({
        order: idx + 1,
        question: item.question,
        scoring_method: item.scoring_method,
        weight: item.weight,
      })),
    });
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} aria-label="Quality checklist editor">
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Checklist Name"
            fullWidth
            error={!!errors.name}
            helperText={errors.name?.message}
            inputProps={{ 'aria-label': 'checklist-name' }}
            sx={{ mb: 2 }}
          />
        )}
      />
      <Controller
        name="description"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Description (optional)"
            fullWidth
            inputProps={{ 'aria-label': 'checklist-description' }}
            sx={{ mb: 2 }}
          />
        )}
      />

      {fields.map((field, index) => (
        <Box key={field.id} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'flex-start' }}>
          <Controller
            name={`items.${index}.question`}
            control={control}
            render={({ field: f }) => (
              <TextField
                {...f}
                label="Question"
                fullWidth
                error={!!errors.items?.[index]?.question}
                helperText={errors.items?.[index]?.question?.message}
                inputProps={{ 'aria-label': `item-question-${index}` }}
              />
            )}
          />
          <Controller
            name={`items.${index}.scoring_method`}
            control={control}
            render={({ field: f }) => (
              <FormControl sx={{ minWidth: 140 }}>
                <InputLabel id={`scoring-method-label-${index}`}>Method</InputLabel>
                <Select
                  {...f}
                  labelId={`scoring-method-label-${index}`}
                  label="Method"
                  inputProps={{ 'aria-label': `item-scoring-${index}` }}
                >
                  <MenuItem value="binary">Binary</MenuItem>
                  <MenuItem value="scale_1_3">Scale 1-3</MenuItem>
                  <MenuItem value="scale_1_5">Scale 1-5</MenuItem>
                </Select>
              </FormControl>
            )}
          />
          <Controller
            name={`items.${index}.weight`}
            control={control}
            render={({ field: f }) => (
              <TextField
                {...f}
                label="Weight"
                type="number"
                sx={{ width: 90 }}
                onChange={(e) => f.onChange(parseFloat(e.target.value))}
                inputProps={{ 'aria-label': `item-weight-${index}`, min: 0, step: 0.1 }}
              />
            )}
          />
          <Button
            variant="text"
            color="error"
            onClick={() => remove(index)}
            aria-label={`remove-item-${index}`}
          >
            Remove
          </Button>
        </Box>
      ))}

      {errors.items && !Array.isArray(errors.items) && (
        <Typography color="error" variant="caption">
          {(errors.items as { message?: string }).message}
        </Typography>
      )}

      <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
        <Button
          type="button"
          variant="outlined"
          onClick={() => append({ question: '', scoring_method: 'binary', weight: 1.0 })}
          aria-label="Add Item"
        >
          Add Item
        </Button>
        <Button type="submit" variant="contained" disabled={upsertMutation.isPending}>
          {upsertMutation.isPending ? 'Saving...' : 'Save Checklist'}
        </Button>
      </Box>
    </Box>
  );
}
