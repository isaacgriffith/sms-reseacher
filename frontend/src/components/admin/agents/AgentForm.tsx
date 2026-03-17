/**
 * AgentForm — react-hook-form + Zod edit form for an existing Agent.
 *
 * - Embeds {@link SystemMessageEditor} for the template field.
 * - "Generate/Update System Message" calls useGenerateSystemMessage.
 * - "Undo" calls useUndoSystemMessage (disabled when canUndo is false).
 * - useWatch on model_id warns if the selected model is disabled.
 */

import { useEffect, useRef } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import FormControlLabel from '@mui/material/FormControlLabel';
import MenuItem from '@mui/material/MenuItem';
import Stack from '@mui/material/Stack';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import SystemMessageEditor from './SystemMessageEditor';
import type { SystemMessageEditorHandle } from './SystemMessageEditor';
import { useUpdateAgent, useGenerateSystemMessage, useUndoSystemMessage } from '../../../services/agentsApi';
import { useProviderModels } from '../../../services/providersApi';
import type { Agent } from '../../../types/agent';
import type { AgentSummary } from '../../../types/agent';

const AgentTaskTypeSchema = z.union([
  z.literal('screener'),
  z.literal('extractor'),
  z.literal('librarian'),
  z.literal('expert'),
  z.literal('quality_judge'),
  z.literal('agent_generator'),
  z.literal('domain_modeler'),
  z.literal('synthesiser'),
  z.literal('validity_assessor'),
]);

const FormSchema = z.object({
  task_type: AgentTaskTypeSchema,
  role_name: z.string().min(1, 'Role name is required'),
  role_description: z.string().min(1, 'Role description is required'),
  persona_name: z.string().min(1, 'Persona name is required'),
  persona_description: z.string().min(1, 'Persona description is required'),
  persona_svg: z.string().optional(),
  system_message_template: z.string().min(1, 'System message template is required'),
  model_id: z.string().uuid('Model ID must be a valid UUID'),
  provider_id: z.string().uuid('Provider ID must be a valid UUID'),
  is_active: z.boolean(),
});

type FormValues = z.infer<typeof FormSchema>;

/** Props for {@link AgentForm}. */
interface AgentFormProps {
  /** The agent to edit — required; this form is edit-only. */
  agent: Agent | AgentSummary;
  /** Called after a successful save. */
  onSuccess: () => void;
  /** Called when the user cancels without saving. */
  onCancel: () => void;
}

/**
 * Edit form for an existing Agent.
 *
 * @param props - {@link AgentFormProps}
 */
export default function AgentForm({ agent, onSuccess, onCancel }: AgentFormProps) {
  const editorRef = useRef<SystemMessageEditorHandle>(null);
  const updateMutation = useUpdateAgent();
  const generateMutation = useGenerateSystemMessage();
  const undoMutation = useUndoSystemMessage();

  const fullAgent = 'system_message_template' in agent ? (agent as Agent) : null;

  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      task_type: agent.task_type,
      role_name: agent.role_name,
      role_description: fullAgent?.role_description ?? '',
      persona_name: agent.persona_name,
      persona_description: fullAgent?.persona_description ?? '',
      persona_svg: fullAgent?.persona_svg ?? '',
      system_message_template: fullAgent?.system_message_template ?? '',
      model_id: agent.model_id,
      provider_id: agent.provider_id,
      is_active: agent.is_active,
    },
  });

  const watchedModelId = useWatch({ control, name: 'model_id' });
  const watchedProviderId = useWatch({ control, name: 'provider_id' });
  const watchedTemplate = useWatch({ control, name: 'system_message_template' });

  // Warn if the selected model becomes disabled
  const { data: models = [] } = useProviderModels(watchedProviderId || '');
  const selectedModel = models.find((m) => m.id === watchedModelId);
  const modelDisabledWarning = selectedModel && !selectedModel.is_enabled;

  // Track undo buffer availability
  const canUndo = !!fullAgent?.system_message_undo_buffer;

  useEffect(() => {
    if (fullAgent?.system_message_template) {
      setValue('system_message_template', fullAgent.system_message_template);
    }
  }, [fullAgent?.system_message_template, setValue]);

  const onSubmit = (values: FormValues) => {
    const versionId = fullAgent?.version_id ?? 0;
    updateMutation.mutate(
      {
        id: agent.id,
        data: {
          version_id: versionId,
          task_type: values.task_type,
          role_name: values.role_name,
          role_description: values.role_description,
          persona_name: values.persona_name,
          persona_description: values.persona_description,
          persona_svg: values.persona_svg || null,
          system_message_template: values.system_message_template,
          model_id: values.model_id,
          provider_id: values.provider_id,
          is_active: values.is_active,
        },
      },
      { onSuccess },
    );
  };

  const handleGenerate = () => {
    generateMutation.mutate(agent.id, {
      onSuccess: (result) => {
        setValue('system_message_template', result.system_message_template);
        editorRef.current?.focus();
      },
    });
  };

  const handleUndo = () => {
    undoMutation.mutate(agent.id, {
      onSuccess: (updated) => {
        setValue('system_message_template', updated.system_message_template);
      },
    });
  };

  const TASK_TYPES = [
    'screener', 'extractor', 'librarian', 'expert', 'quality_judge',
    'agent_generator', 'domain_modeler', 'synthesiser', 'validity_assessor',
  ];

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Stack spacing={2}>
        {(updateMutation.isError || generateMutation.isError || undoMutation.isError) && (
          <Alert severity="error">
            {String(
              (updateMutation.error ?? generateMutation.error ?? undoMutation.error) || 'An error occurred',
            )}
          </Alert>
        )}

        <TextField
          select
          label="Task Type"
          defaultValue={agent.task_type}
          {...register('task_type')}
          error={!!errors.task_type}
          helperText={errors.task_type?.message}
          size="small"
          fullWidth
        >
          {TASK_TYPES.map((t) => (
            <MenuItem key={t} value={t}>{t}</MenuItem>
          ))}
        </TextField>

        <TextField
          label="Role Name"
          {...register('role_name')}
          error={!!errors.role_name}
          helperText={errors.role_name?.message}
          size="small"
          fullWidth
        />

        <TextField
          label="Role Description"
          {...register('role_description')}
          error={!!errors.role_description}
          helperText={errors.role_description?.message}
          multiline
          minRows={2}
          size="small"
          fullWidth
        />

        <TextField
          label="Persona Name"
          {...register('persona_name')}
          error={!!errors.persona_name}
          helperText={errors.persona_name?.message}
          size="small"
          fullWidth
        />

        <TextField
          label="Persona Description"
          {...register('persona_description')}
          error={!!errors.persona_description}
          helperText={errors.persona_description?.message}
          multiline
          minRows={2}
          size="small"
          fullWidth
        />

        {modelDisabledWarning && (
          <Alert severity="warning">
            The currently selected model is disabled. Consider choosing an enabled model.
          </Alert>
        )}

        <Box>
          <SystemMessageEditor
            ref={editorRef}
            value={watchedTemplate}
            onChange={(val) => setValue('system_message_template', val)}
            onUndo={handleUndo}
            canUndo={canUndo || (undoMutation.isSuccess && !undoMutation.isPending)}
            disabled={generateMutation.isPending || undoMutation.isPending}
          />
          {errors.system_message_template && (
            <Box sx={{ color: 'error.main', fontSize: '0.75rem', mt: 0.5 }}>
              {errors.system_message_template.message}
            </Box>
          )}
        </Box>

        <Button
          variant="outlined"
          size="small"
          onClick={handleGenerate}
          disabled={generateMutation.isPending}
          startIcon={generateMutation.isPending ? <CircularProgress size={14} /> : null}
        >
          {generateMutation.isPending ? 'Generating…' : 'Generate / Update System Message'}
        </Button>

        <FormControlLabel
          control={
            <Switch defaultChecked={agent.is_active} {...register('is_active')} />
          }
          label="Active"
        />

        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
          <Button variant="text" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting || updateMutation.isPending}
            startIcon={updateMutation.isPending ? <CircularProgress size={14} /> : null}
          >
            {updateMutation.isPending ? 'Saving…' : 'Save'}
          </Button>
        </Box>
      </Stack>
    </Box>
  );
}
