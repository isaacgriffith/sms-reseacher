/**
 * Multi-step dialog for enrolling in TOTP 2FA.
 * Steps: idle → qr_display → code_entry → backup_codes
 */

import { useReducer, useRef } from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Stepper from '@mui/material/Stepper';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';

import { useTotpSetup, useTotpConfirm } from '../../hooks/useTotp';
import type { TotpSetupData } from '../../services/preferences';

// ---------------------------------------------------------------------------
// State machine
// ---------------------------------------------------------------------------

type Step0 = { step: 'idle' };
type Step1 = { step: 'qr_display'; data: TotpSetupData };
type Step2 = { step: 'code_entry'; data: TotpSetupData };
type Step3 = { step: 'backup_codes'; codes: string[] };
type SetupState = Step0 | Step1 | Step2 | Step3;

type SetupAction =
  | { type: 'OPEN_QR'; data: TotpSetupData }
  | { type: 'PROCEED_TO_CODE' }
  | { type: 'SHOW_BACKUP'; codes: string[] }
  | { type: 'CLOSE' };

function reducer(state: SetupState, action: SetupAction): SetupState {
  switch (action.type) {
    case 'OPEN_QR':
      return { step: 'qr_display', data: action.data };
    case 'PROCEED_TO_CODE':
      return state.step === 'qr_display' ? { step: 'code_entry', data: state.data } : state;
    case 'SHOW_BACKUP':
      return { step: 'backup_codes', codes: action.codes };
    case 'CLOSE':
      return { step: 'idle' };
  }
}

const STEP_LABELS = ['Scan QR code', 'Enter code', 'Save backup codes'];

function stepIndex(s: SetupState): number {
  if (s.step === 'qr_display') return 0;
  if (s.step === 'code_entry') return 1;
  if (s.step === 'backup_codes') return 2;
  return -1;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface QrStepProps {
  data: TotpSetupData;
  onNext: () => void;
  onClose: () => void;
}

function QrStep({ data, onNext, onClose }: QrStepProps) {
  return (
    <>
      <DialogContent>
        <Typography gutterBottom>
          Scan this QR code with your authenticator app (e.g. Google Authenticator, Authy).
        </Typography>
        <Box sx={{ textAlign: 'center', my: 2 }}>
          <img
            src={`data:image/png;base64,${data.qr_code_image}`}
            alt="TOTP QR code"
            style={{ maxWidth: 200 }}
          />
        </Box>
        <Typography variant="body2" color="text.secondary">
          Can't scan? Enter this key manually:
        </Typography>
        <Typography
          variant="body2"
          sx={{ fontFamily: 'monospace', wordBreak: 'break-all', mt: 0.5 }}
          aria-label="manual key"
        >
          {data.manual_key}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onNext}>Next</Button>
      </DialogActions>
    </>
  );
}

interface CodeStepProps {
  onConfirm: (code: string) => void;
  onClose: () => void;
  isPending: boolean;
  error: string | null;
}

function CodeStep({ onConfirm, onClose, isPending, error }: CodeStepProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <>
      <DialogContent>
        <Typography gutterBottom>
          Enter the 6-digit code from your authenticator app to complete setup.
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <TextField
          inputRef={inputRef}
          label="Authentication code"
          inputProps={{ inputMode: 'numeric', maxLength: 6 }}
          fullWidth
          autoFocus
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          disabled={isPending}
          onClick={() => {
            const code = inputRef.current?.value ?? '';
            if (code.length === 6) onConfirm(code);
          }}
        >
          {isPending ? 'Verifying…' : 'Verify'}
        </Button>
      </DialogActions>
    </>
  );
}

interface BackupCodesStepProps {
  codes: string[];
  onDone: () => void;
}

function BackupCodesStep({ codes, onDone }: BackupCodesStepProps) {
  const handleCopyAll = () => {
    void navigator.clipboard.writeText(codes.join('\n'));
  };
  return (
    <>
      <DialogContent>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Save these backup codes in a secure location. Each can only be used once.
        </Alert>
        <Box
          component="ul"
          sx={{ listStyle: 'none', p: 0, fontFamily: 'monospace', columns: 2, m: 0 }}
        >
          {codes.map((c) => (
            <li key={c}>{c}</li>
          ))}
        </Box>
        <Button size="small" onClick={handleCopyAll} sx={{ mt: 1 }}>
          Copy all
        </Button>
      </DialogContent>
      <DialogActions>
        <Button variant="contained" onClick={onDone}>
          I have saved these codes
        </Button>
      </DialogActions>
    </>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export interface TwoFactorSetupDialogProps {
  onEnabled: () => void;
}

export default function TwoFactorSetupDialog({ onEnabled }: TwoFactorSetupDialogProps) {
  const [state, dispatch] = useReducer(reducer, { step: 'idle' });
  const setupMutation = useTotpSetup();
  const confirmMutation = useTotpConfirm();

  const handleOpen = async () => {
    try {
      const data = await setupMutation.mutateAsync();
      dispatch({ type: 'OPEN_QR', data });
    } catch {
      // error shown via setupMutation.error
    }
  };

  const handleConfirm = async (code: string) => {
    try {
      const result = await confirmMutation.mutateAsync(code);
      dispatch({ type: 'SHOW_BACKUP', codes: result.backup_codes });
    } catch (err) {
      // error visible via confirmMutation.error
    }
  };

  const handleClose = () => dispatch({ type: 'CLOSE' });
  const handleDone = () => {
    dispatch({ type: 'CLOSE' });
    onEnabled();
  };

  const isOpen = state.step !== 'idle';
  const activeStep = stepIndex(state);

  return (
    <>
      <Button
        variant="contained"
        onClick={() => void handleOpen()}
        disabled={setupMutation.isPending}
      >
        {setupMutation.isPending ? 'Loading…' : 'Enable 2FA'}
      </Button>
      {setupMutation.isError && (
        <Alert severity="error" sx={{ mt: 1 }}>
          {setupMutation.error?.message ?? 'Failed to start setup'}
        </Alert>
      )}

      <Dialog open={isOpen} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Set up two-factor authentication</DialogTitle>
        {isOpen && (
          <Box sx={{ px: 3, pt: 1 }}>
            <Stepper activeStep={activeStep}>
              {STEP_LABELS.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>
        )}

        {state.step === 'qr_display' && (
          <QrStep
            data={state.data}
            onNext={() => dispatch({ type: 'PROCEED_TO_CODE' })}
            onClose={handleClose}
          />
        )}
        {state.step === 'code_entry' && (
          <CodeStep
            onConfirm={(code) => void handleConfirm(code)}
            onClose={handleClose}
            isPending={confirmMutation.isPending}
            error={confirmMutation.isError ? (confirmMutation.error?.message ?? 'Invalid code') : null}
          />
        )}
        {state.step === 'backup_codes' && (
          <BackupCodesStep codes={state.codes} onDone={handleDone} />
        )}
      </Dialog>
    </>
  );
}
