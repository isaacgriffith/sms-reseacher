/**
 * 2FA status panel: enable via dialog, disable inline, or regenerate backup codes.
 */

import { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import { useTotpDisable, useBackupCodesRegenerate } from '../../hooks/useTotp';
import TwoFactorSetupDialog from './TwoFactorSetupDialog';

export interface TwoFactorSettingsProps {
  totpEnabled: boolean;
  onStatusChange: () => void;
}

interface ActionFormProps {
  actionLabel: string;
  pendingLabel: string;
  successMessage: string;
  onSubmit: (password: string, totpCode: string) => Promise<void>;
  isPending: boolean;
  error: string | null;
  extraContent?: React.ReactNode;
}

function ActionForm({
  actionLabel,
  pendingLabel,
  successMessage,
  onSubmit,
  isPending,
  error,
  extraContent,
}: ActionFormProps) {
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(false);
    try {
      await onSubmit(password, totpCode);
      setSuccess(true);
      setPassword('');
      setTotpCode('');
    } catch {
      // Error displayed via the `error` prop from the parent mutation state
    }
  };

  return (
    <Box component="form" onSubmit={(e) => void handleSubmit(e)} sx={{ mt: 2 }}>
      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}
      {success && !error && <Alert severity="success" sx={{ mb: 1 }}>{successMessage}</Alert>}
      <TextField
        label="Current password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        size="small"
        fullWidth
        required
        sx={{ mb: 1 }}
      />
      <TextField
        label="Authenticator code"
        value={totpCode}
        onChange={(e) => setTotpCode(e.target.value)}
        size="small"
        inputProps={{ maxLength: 10 }}
        fullWidth
        required
        sx={{ mb: 1 }}
      />
      {extraContent}
      <Button type="submit" variant="contained" disabled={isPending} color="error">
        {isPending ? pendingLabel : actionLabel}
      </Button>
    </Box>
  );
}

export default function TwoFactorSettings({ totpEnabled, onStatusChange }: TwoFactorSettingsProps) {
  const disableMutation = useTotpDisable();
  const regenMutation = useBackupCodesRegenerate();
  const [newCodes, setNewCodes] = useState<string[] | null>(null);

  const handleDisable = async (password: string, totpCode: string) => {
    await disableMutation.mutateAsync({ password, totpCode });
    onStatusChange();
  };

  const handleRegen = async (password: string, totpCode: string) => {
    const result = await regenMutation.mutateAsync({ password, totpCode });
    setNewCodes(result.backup_codes);
  };

  return (
    <Paper variant="outlined" sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Typography variant="subtitle1">Two-Factor Authentication</Typography>
        <Chip
          label={totpEnabled ? 'Enabled' : 'Disabled'}
          color={totpEnabled ? 'success' : 'default'}
          size="small"
        />
      </Box>

      {!totpEnabled && (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Add an extra layer of security by requiring a one-time code at login.
          </Typography>
          <TwoFactorSetupDialog onEnabled={onStatusChange} />
        </>
      )}

      {totpEnabled && (
        <>
          <Typography variant="subtitle2" sx={{ mt: 1 }}>Disable 2FA</Typography>
          <ActionForm
            actionLabel="Disable 2FA"
            pendingLabel="Disabling…"
            successMessage="Two-factor authentication has been disabled."
            onSubmit={handleDisable}
            isPending={disableMutation.isPending}
            error={disableMutation.isError ? (disableMutation.error?.message ?? 'Error') : null}
          />

          <Typography variant="subtitle2" sx={{ mt: 3 }}>Regenerate backup codes</Typography>
          <ActionForm
            actionLabel="Regenerate codes"
            pendingLabel="Regenerating…"
            successMessage="New backup codes generated."
            onSubmit={handleRegen}
            isPending={regenMutation.isPending}
            error={regenMutation.isError ? (regenMutation.error?.message ?? 'Error') : null}
            extraContent={
              newCodes && (
                <Box
                  component="ul"
                  sx={{ listStyle: 'none', p: 0, fontFamily: 'monospace', columns: 2, mb: 1 }}
                >
                  {newCodes.map((c) => <li key={c}>{c}</li>)}
                </Box>
              )
            }
          />
        </>
      )}
    </Paper>
  );
}
