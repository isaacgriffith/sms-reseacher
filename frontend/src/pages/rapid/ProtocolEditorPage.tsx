/**
 * ProtocolEditorPage — Phase 1 page for Rapid Review protocol editing (feature 008).
 *
 * Composes ProtocolForm with action buttons for protocol validation.
 * Handles the 409 invalidation confirmation dialog.
 *
 * @module ProtocolEditorPage
 */

import React, { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Stepper from '@mui/material/Stepper';
import Typography from '@mui/material/Typography';
import ProtocolForm from '../../components/rapid/ProtocolForm';
import {
  useRRProtocol,
  useUpdateRRProtocol,
  useValidateRRProtocol,
} from '../../hooks/rapid/useRRProtocol';
import type { RRProtocolUpdate } from '../../services/rapid/protocolApi';

// ---------------------------------------------------------------------------
// Stepper config
// ---------------------------------------------------------------------------

const STEPS = ['Draft', 'Validated'];

const STATUS_STEP: Record<string, number> = {
  draft: 0,
  validated: 1,
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link ProtocolEditorPage}. */
interface ProtocolEditorPageProps {
  /** Integer study ID from the parent page. */
  studyId: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * ProtocolEditorPage renders the full Rapid Review protocol editor.
 *
 * Layout:
 * - MUI Stepper showing protocol status (Draft → Validated).
 * - ProtocolForm for editing all fields.
 * - "Validate Protocol" action button.
 * - Invalidation confirmation dialog when editing a validated protocol.
 *
 * @param studyId - The study whose protocol to edit.
 */
export default function ProtocolEditorPage({
  studyId,
}: ProtocolEditorPageProps): React.ReactElement {
  const { data: protocol, isLoading, error } = useRRProtocol(studyId);
  const validateMutation = useValidateRRProtocol(studyId);
  const {
    mutation: updateMutation,
    invalidationPending,
    confirmInvalidation,
    cancelInvalidation,
  } = useUpdateRRProtocol(studyId);

  const [pendingUpdate, setPendingUpdate] = useState<RRProtocolUpdate | null>(null);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CircularProgress size={20} />
        <Typography>Loading protocol…</Typography>
      </Box>
    );
  }

  if (error || !protocol) {
    return <Alert severity="error">Failed to load the protocol. Please refresh the page.</Alert>;
  }

  const activeStep = STATUS_STEP[protocol.status] ?? 0;
  const isValidated = protocol.status === 'validated';

  const handleSave = (data: RRProtocolUpdate) => {
    setPendingUpdate(data);
    updateMutation.mutate(data, {
      onError: (err) => {
        const asStatus = err as { status?: number };
        if (!asStatus.status || asStatus.status !== 409) {
          setPendingUpdate(null);
        }
      },
      onSuccess: () => {
        setPendingUpdate(null);
      },
    });
  };

  const handleConfirmInvalidation = () => {
    if (pendingUpdate) {
      confirmInvalidation(pendingUpdate);
    }
  };

  return (
    <Box>
      {/* Status stepper */}
      <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Validated banner */}
      {isValidated && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Protocol is validated. Phase 2 (Search Configuration) is now unlocked. Editing the
          protocol will reset it to Draft and invalidate collected papers.
        </Alert>
      )}

      {/* Mutation errors */}
      {updateMutation.isError && !invalidationPending && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {updateMutation.error?.message ?? 'Failed to save protocol.'}
        </Alert>
      )}
      {validateMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {validateMutation.error?.message ?? 'Validation failed.'}
        </Alert>
      )}

      {/* Protocol form */}
      <ProtocolForm
        studyId={studyId}
        protocol={protocol}
        readOnly={false}
        onSubmit={handleSave}
        isSaving={updateMutation.isPending}
      />

      {/* Validate button */}
      {!isValidated && (
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="success"
            disabled={validateMutation.isPending}
            onClick={() => validateMutation.mutate()}
            startIcon={validateMutation.isPending ? <CircularProgress size={16} /> : undefined}
          >
            {validateMutation.isPending ? 'Validating…' : 'Validate Protocol'}
          </Button>
        </Box>
      )}

      {/* Invalidation confirmation dialog */}
      <Dialog
        open={!!invalidationPending}
        onClose={cancelInvalidation}
        aria-labelledby="invalidation-dialog-title"
      >
        <DialogTitle id="invalidation-dialog-title">Confirm Protocol Edit</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This protocol has been validated. Editing it will reset its status to Draft and mark{' '}
            <strong>{invalidationPending?.papersAtRisk ?? 0} paper(s)</strong> as requiring
            re-screening. Do you want to continue?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelInvalidation} color="inherit">
            Cancel
          </Button>
          <Button onClick={handleConfirmInvalidation} color="warning" variant="contained">
            Edit and Invalidate Papers
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
