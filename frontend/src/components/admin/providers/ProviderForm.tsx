/**
 * ProviderForm: react-hook-form + Zod form for creating or editing an LLM provider.
 *
 * Conditionally renders api_key (Anthropic/OpenAI) or base_url (Ollama) based
 * on the selected provider_type, using useWatch for reactive field switching.
 */

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import FormControlLabel from '@mui/material/FormControlLabel';
import MenuItem from '@mui/material/MenuItem';
import Stack from '@mui/material/Stack';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useCreateProvider, useUpdateProvider } from '../../../services/providersApi';
import type { Provider } from '../../../types/provider';

const FormSchema = z.object({
  provider_type: z.union([z.literal('anthropic'), z.literal('openai'), z.literal('ollama')]),
  display_name: z.string().min(1, 'Display name is required'),
  api_key: z.string().optional(),
  base_url: z.string().optional(),
  is_enabled: z.boolean(),
});

type FormValues = z.infer<typeof FormSchema>;

/** Props for {@link ProviderForm}. */
export interface ProviderFormProps {
  /** When present, the form operates in edit mode for this provider. */
  provider?: Provider;
  /** Called after a successful create or update. */
  onSuccess: () => void;
  /** Called when the user cancels. */
  onCancel: () => void;
}

/**
 * Form for creating or editing an LLM provider.
 *
 * @param props - {@link ProviderFormProps}
 * @returns Form element.
 */
export default function ProviderForm({ provider, onSuccess, onCancel }: ProviderFormProps) {
  const isEdit = provider !== undefined;
  const createMutation = useCreateProvider();
  const updateMutation = useUpdateProvider();
  const isPending = createMutation.isPending || updateMutation.isPending;
  const mutationError = createMutation.error ?? updateMutation.error;

  const { register, handleSubmit, control, reset, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      provider_type: provider?.provider_type ?? 'anthropic',
      display_name: provider?.display_name ?? '',
      api_key: '',
      base_url: provider?.base_url ?? '',
      is_enabled: provider?.is_enabled ?? true,
    },
  });

  useEffect(() => {
    if (provider) {
      reset({
        provider_type: provider.provider_type,
        display_name: provider.display_name,
        api_key: '',
        base_url: provider.base_url ?? '',
        is_enabled: provider.is_enabled,
      });
    }
  }, [provider, reset]);

  const providerType = useWatch({ control, name: 'provider_type' });
  const isEnabled = useWatch({ control, name: 'is_enabled' });
  const needsApiKey = providerType === 'anthropic' || providerType === 'openai';

  const onSubmit = async (values: FormValues) => {
    if (isEdit && provider) {
      await updateMutation.mutateAsync({
        id: provider.id,
        data: {
          display_name: values.display_name,
          api_key: values.api_key || undefined,
          base_url: values.base_url || undefined,
          is_enabled: values.is_enabled,
        },
      });
    } else {
      await createMutation.mutateAsync({
        provider_type: values.provider_type,
        display_name: values.display_name,
        api_key: values.api_key || undefined,
        base_url: values.base_url || undefined,
        is_enabled: values.is_enabled,
      });
    }
    onSuccess();
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Stack spacing={2}>
        <TextField
          select
          label="Provider Type"
          defaultValue={provider?.provider_type ?? 'anthropic'}
          {...register('provider_type')}
          error={Boolean(errors.provider_type)}
          helperText={errors.provider_type?.message}
          disabled={isEdit}
          size="small"
          fullWidth
        >
          <MenuItem value="anthropic">Anthropic</MenuItem>
          <MenuItem value="openai">OpenAI</MenuItem>
          <MenuItem value="ollama">Ollama</MenuItem>
        </TextField>

        <TextField
          label="Display Name"
          {...register('display_name')}
          error={Boolean(errors.display_name)}
          helperText={errors.display_name?.message}
          size="small"
          fullWidth
        />

        {needsApiKey && (
          <TextField
            label={isEdit ? 'API Key (leave blank to keep existing)' : 'API Key'}
            type="password"
            {...register('api_key')}
            error={Boolean(errors.api_key)}
            helperText={errors.api_key?.message}
            size="small"
            fullWidth
          />
        )}

        {providerType === 'ollama' && (
          <TextField
            label="Base URL"
            placeholder="http://localhost:11434"
            {...register('base_url')}
            error={Boolean(errors.base_url)}
            helperText={errors.base_url?.message}
            size="small"
            fullWidth
          />
        )}

        <FormControlLabel
          control={<Switch checked={isEnabled} {...register('is_enabled')} />}
          label="Enabled"
        />

        {mutationError && (
          <Typography color="error" variant="body2">
            {mutationError.message}
          </Typography>
        )}

        <Stack direction="row" spacing={1} justifyContent="flex-end">
          <Button onClick={onCancel} disabled={isPending}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={isPending}>
            {isEdit ? 'Save Changes' : 'Add Provider'}
          </Button>
        </Stack>
      </Stack>
    </Box>
  );
}
