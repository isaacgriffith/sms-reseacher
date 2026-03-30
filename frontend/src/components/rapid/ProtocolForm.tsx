/**
 * ProtocolForm — Rapid Review protocol editor form (feature 008).
 *
 * Renders all protocol fields; embeds {@link StakeholderPanel} and
 * {@link ThreatToValidityList}.  Shows a research-gap warning banner when
 * any research question triggers the keyword heuristic.
 *
 * @module ProtocolForm
 */

import React from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { Controller, useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { RRProtocol, RRProtocolUpdate } from '../../services/rapid/protocolApi';
import { useRRThreats } from '../../hooks/rapid/useRRProtocol';
import StakeholderPanel from './StakeholderPanel';
import ThreatToValidityList from './ThreatToValidityList';

// ---------------------------------------------------------------------------
// Form schema
// ---------------------------------------------------------------------------

const protocolFormSchema = z.object({
  practical_problem: z.string().min(1, 'Practical problem is required'),
  research_questions_raw: z.string().min(1, 'At least one research question is required'),
  time_budget_days: z.string().optional(),
  effort_budget_hours: z.string().optional(),
  dissemination_medium: z.string().optional(),
  problem_scoping_notes: z.string().optional(),
  search_strategy_notes: z.string().optional(),
});

type ProtocolFormValues = z.infer<typeof protocolFormSchema>;

const GAP_KEYWORDS = ['gap', 'future work', 'what is missing', 'lack of'];

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link ProtocolForm}. */
interface ProtocolFormProps {
  /** Integer study ID. */
  studyId: number;
  /** Current protocol data (pre-filled into form). */
  protocol: RRProtocol;
  /** Whether the form should be read-only. */
  readOnly?: boolean;
  /** Callback invoked with transformed update payload on form submit. */
  onSubmit: (data: RRProtocolUpdate) => void;
  /** Whether a save operation is in progress. */
  isSaving?: boolean;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Renders all Rapid Review protocol fields.
 *
 * Uses `useWatch` to display a research-gap warning banner when any
 * research question contains gap-related keywords (mirroring the backend
 * heuristic).  Embeds {@link StakeholderPanel} and
 * {@link ThreatToValidityList} sections.
 *
 * @param studyId - The Rapid Review study ID.
 * @param protocol - Current protocol data.
 * @param readOnly - When true disables all inputs.
 * @param onSubmit - Callback with the update payload.
 * @param isSaving - Disables the save button while true.
 */
export default function ProtocolForm({
  studyId,
  protocol,
  readOnly = false,
  onSubmit,
  isSaving = false,
}: ProtocolFormProps): React.ReactElement {
  const { data: threats = [] } = useRRThreats(studyId);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<ProtocolFormValues>({
    resolver: zodResolver(protocolFormSchema),
    defaultValues: {
      practical_problem: protocol.practical_problem ?? '',
      research_questions_raw: (protocol.research_questions ?? []).join('\n'),
      time_budget_days: protocol.time_budget_days?.toString() ?? '',
      effort_budget_hours: protocol.effort_budget_hours?.toString() ?? '',
      dissemination_medium: protocol.dissemination_medium ?? '',
      problem_scoping_notes: protocol.problem_scoping_notes ?? '',
      search_strategy_notes: protocol.search_strategy_notes ?? '',
    },
  });

  const rqRaw = useWatch({ control, name: 'research_questions_raw' });

  const gapWarnings = (rqRaw ?? '').split('\n').filter((q) => {
    const lower = q.toLowerCase();
    return GAP_KEYWORDS.some((kw) => lower.includes(kw));
  });

  const handleFormSubmit = (values: ProtocolFormValues) => {
    const questions = values.research_questions_raw
      .split('\n')
      .map((q) => q.trim())
      .filter(Boolean);

    const timeBudget = values.time_budget_days ? parseInt(values.time_budget_days, 10) : undefined;
    const effortBudget = values.effort_budget_hours
      ? parseInt(values.effort_budget_hours, 10)
      : undefined;

    const payload: RRProtocolUpdate = {
      practical_problem: values.practical_problem,
      research_questions: questions,
      ...(timeBudget !== undefined && { time_budget_days: timeBudget }),
      ...(effortBudget !== undefined && { effort_budget_hours: effortBudget }),
      ...(values.dissemination_medium && {
        dissemination_medium: values.dissemination_medium,
      }),
      ...(values.problem_scoping_notes && {
        problem_scoping_notes: values.problem_scoping_notes,
      }),
      ...(values.search_strategy_notes && {
        search_strategy_notes: values.search_strategy_notes,
      }),
    };
    onSubmit(payload);
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(handleFormSubmit)}
      sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}
    >
      {gapWarnings.length > 0 && (
        <Alert severity="warning">
          <Typography variant="body2" fontWeight={600}>
            Research-gap style questions detected
          </Typography>
          <Typography variant="body2">
            Rapid Reviews focus on practical problems, not research gaps. Consider rephrasing the
            following:
          </Typography>
          <ul style={{ margin: '4px 0 0', paddingLeft: '1.25rem' }}>
            {gapWarnings.map((q, i) => (
              <li key={i}>
                <Typography variant="caption">{q}</Typography>
              </li>
            ))}
          </ul>
        </Alert>
      )}

      <Controller
        name="practical_problem"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Practical Problem *"
            multiline
            rows={3}
            disabled={readOnly}
            error={!!errors.practical_problem}
            helperText={errors.practical_problem?.message}
            fullWidth
          />
        )}
      />

      <Controller
        name="research_questions_raw"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Research Questions * (one per line)"
            multiline
            rows={4}
            disabled={readOnly}
            error={!!errors.research_questions_raw}
            helperText={
              errors.research_questions_raw?.message ?? 'Enter one research question per line'
            }
            fullWidth
          />
        )}
      />

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Controller
          name="time_budget_days"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Time Budget (days)"
              type="number"
              disabled={readOnly}
              error={!!errors.time_budget_days}
              sx={{ flex: 1 }}
            />
          )}
        />
        <Controller
          name="effort_budget_hours"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Effort Budget (hours)"
              type="number"
              disabled={readOnly}
              error={!!errors.effort_budget_hours}
              sx={{ flex: 1 }}
            />
          )}
        />
      </Box>

      <Controller
        name="dissemination_medium"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Dissemination Medium" disabled={readOnly} fullWidth />
        )}
      />

      <Controller
        name="problem_scoping_notes"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Problem Scoping Notes"
            multiline
            rows={3}
            disabled={readOnly}
            fullWidth
          />
        )}
      />

      <Controller
        name="search_strategy_notes"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Search Strategy Notes"
            multiline
            rows={3}
            disabled={readOnly}
            fullWidth
          />
        )}
      />

      <Divider />

      <StakeholderPanel studyId={studyId} readOnly={readOnly} />

      {threats.length > 0 && (
        <>
          <Divider />
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Threats to Validity
            </Typography>
            <ThreatToValidityList threats={threats} />
          </Box>
        </>
      )}

      {!readOnly && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            type="submit"
            variant="contained"
            disabled={isSaving}
            startIcon={isSaving ? <CircularProgress size={16} /> : undefined}
          >
            {isSaving ? 'Saving…' : 'Save Protocol'}
          </Button>
        </Box>
      )}
    </Box>
  );
}
