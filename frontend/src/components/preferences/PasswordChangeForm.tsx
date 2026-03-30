/**
 * Form for changing the authenticated user's password.
 * Uses react-hook-form + Zod with real-time complexity feedback.
 */

import { useState } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import { ApiError } from '../../services/api';
import { changePassword } from '../../services/preferences';

const schema = z
  .object({
    currentPassword: z.string().min(1, 'Required'),
    newPassword: z
      .string()
      .min(12, 'At least 12 characters')
      .regex(/[A-Z]/, 'Must contain an uppercase letter')
      .regex(/\d/, 'Must contain a digit')
      .regex(/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?`~]/, 'Must contain a special character'),
    confirmPassword: z.string().min(1, 'Required'),
  })
  .refine((d) => d.newPassword === d.confirmPassword, {
    path: ['confirmPassword'],
    message: 'Passwords do not match',
  });

type FormValues = z.infer<typeof schema>;

interface ComplexityIndicatorProps {
  password: string;
}

function ComplexityIndicator({ password }: ComplexityIndicatorProps) {
  const checks = [
    { label: '12+ characters', ok: password.length >= 12 },
    { label: 'Uppercase letter', ok: /[A-Z]/.test(password) },
    { label: 'Digit', ok: /\d/.test(password) },
    { label: 'Special character', ok: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?`~]/.test(password) },
  ];

  return (
    <Box sx={{ mt: 0.5, mb: 1 }}>
      {checks.map(({ label, ok }) => (
        <Typography
          key={label}
          variant="caption"
          sx={{ display: 'block', color: ok ? 'success.main' : 'text.secondary' }}
        >
          {ok ? '✓' : '○'} {label}
        </Typography>
      ))}
    </Box>
  );
}

export interface PasswordChangeFormProps {
  onSuccess?: () => void;
}

export default function PasswordChangeForm({ onSuccess }: PasswordChangeFormProps) {
  const [serverError, setServerError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const newPassword = useWatch({ control, name: 'newPassword', defaultValue: '' });

  const onSubmit = async (data: FormValues) => {
    setServerError(null);
    setSuccess(false);
    try {
      await changePassword(data.currentPassword, data.newPassword);
      setSuccess(true);
      reset();
      onSuccess?.();
    } catch (err) {
      if (err instanceof ApiError) {
        setServerError(err.detail);
      } else {
        setServerError('Unexpected error. Please try again.');
      }
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ maxWidth: 420 }}>
      {success && <Alert severity="success" sx={{ mb: 2 }}>Password changed successfully.</Alert>}
      {serverError && <Alert severity="error" sx={{ mb: 2 }}>{serverError}</Alert>}

      <TextField
        {...register('currentPassword')}
        label="Current password"
        type="password"
        fullWidth
        margin="normal"
        error={!!errors.currentPassword}
        helperText={errors.currentPassword?.message}
      />

      <TextField
        {...register('newPassword')}
        label="New password"
        type="password"
        fullWidth
        margin="normal"
        error={!!errors.newPassword}
        helperText={errors.newPassword?.message}
      />
      <ComplexityIndicator password={newPassword} />

      <TextField
        {...register('confirmPassword')}
        label="Confirm new password"
        type="password"
        fullWidth
        margin="normal"
        error={!!errors.confirmPassword}
        helperText={errors.confirmPassword?.message}
      />

      <Button type="submit" variant="contained" disabled={isSubmitting} sx={{ mt: 2 }}>
        {isSubmitting ? 'Saving…' : 'Change Password'}
      </Button>
    </Box>
  );
}
