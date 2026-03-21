/**
 * ProtocolEditorPage — Phase 1 page for SLR protocol editing and review.
 *
 * Composes ProtocolForm + ProtocolReviewReport + action buttons.
 * Renders an MUI Stepper showing protocol status flow:
 *   Draft → Under Review → Validated
 *
 * @module ProtocolEditorPage
 */

import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Alert from '@mui/material/Alert';
import Divider from '@mui/material/Divider';
import ProtocolForm from '../../components/slr/ProtocolForm';
import ProtocolReviewReport from '../../components/slr/ProtocolReviewReport';
import {
  useProtocol,
  useUpsertProtocol,
  useSubmitForReview,
  useValidateProtocol,
} from '../../hooks/slr/useProtocol';
import type { ReviewProtocol } from '../../services/slr/protocolApi';

// ---------------------------------------------------------------------------
// Stepper configuration
// ---------------------------------------------------------------------------

const STEPS = ['Draft', 'Under Review', 'Validated'];

const STATUS_STEP: Record<string, number> = {
  draft: 0,
  under_review: 1,
  validated: 2,
};

// ---------------------------------------------------------------------------
// Props and component
// ---------------------------------------------------------------------------

interface ProtocolEditorPageProps {
  /** Integer study ID from the parent page. */
  studyId: number;
}

/**
 * ProtocolEditorPage composes the full protocol editor UI.
 *
 * Layout:
 * - MUI Stepper showing current protocol status.
 * - ProtocolForm for editing fields (read-only when validated).
 * - Action buttons: Submit for Review, Approve Protocol.
 * - ProtocolReviewReport showing AI feedback.
 *
 * @param studyId - The study whose protocol to edit.
 */
export default function ProtocolEditorPage({ studyId }: ProtocolEditorPageProps) {
  const { data: protocol, isLoading, error } = useProtocol(studyId);
  const upsertMutation = useUpsertProtocol(studyId);
  const submitMutation = useSubmitForReview(studyId);
  const validateMutation = useValidateProtocol(studyId);

  if (isLoading) {
    return <Typography sx={{ color: '#6b7280' }}>Loading protocol…</Typography>;
  }

  if (error && (error as { status?: number })?.status !== 404) {
    return <Alert severity="error">Failed to load protocol.</Alert>;
  }

  const currentStatus = protocol?.status ?? 'draft';
  const activeStep = STATUS_STEP[currentStatus] ?? 0;
  const isUnderReview = currentStatus === 'under_review';
  const isValidated = currentStatus === 'validated';

  function handleSave(data: Partial<ReviewProtocol>) {
    upsertMutation.mutate(data as Parameters<typeof upsertMutation.mutate>[0]);
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Review Protocol
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {upsertMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to save protocol: {(upsertMutation.error as Error)?.message}
        </Alert>
      )}
      {submitMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to submit for review: {(submitMutation.error as Error)?.message}
        </Alert>
      )}
      {validateMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to validate protocol: {(validateMutation.error as Error)?.message}
        </Alert>
      )}

      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4, mb: 3 }}>
        <ProtocolForm
          protocol={protocol ?? null}
          isSaving={upsertMutation.isPending}
          onSave={handleSave}
        />

        <Box>
          <ProtocolReviewReport protocol={protocol ?? null} />
        </Box>
      </Box>

      <Divider sx={{ mb: 2 }} />

      <ActionButtons
        isValidated={isValidated}
        isUnderReview={isUnderReview}
        hasProtocol={!!protocol}
        isSubmitting={submitMutation.isPending}
        isValidating={validateMutation.isPending}
        onSubmitForReview={() => submitMutation.mutate()}
        onValidate={() => validateMutation.mutate()}
      />
    </Box>
  );
}

// ---------------------------------------------------------------------------
// ActionButtons sub-component (extracted to stay within 100 JSX lines)
// ---------------------------------------------------------------------------

interface ActionButtonsProps {
  isValidated: boolean;
  isUnderReview: boolean;
  hasProtocol: boolean;
  isSubmitting: boolean;
  isValidating: boolean;
  onSubmitForReview: () => void;
  onValidate: () => void;
}

/**
 * ActionButtons renders the Submit for Review and Approve Protocol buttons.
 *
 * @param props - Button state and callback props.
 */
function ActionButtons({
  isValidated,
  isUnderReview,
  hasProtocol,
  isSubmitting,
  isValidating,
  onSubmitForReview,
  onValidate,
}: ActionButtonsProps) {
  if (isValidated) {
    return (
      <Alert severity="success">
        Protocol validated. Proceed to Phase 2: Database Search.
      </Alert>
    );
  }

  return (
    <Box sx={{ display: 'flex', gap: 2 }}>
      <Button
        variant="outlined"
        disabled={!hasProtocol || isUnderReview || isSubmitting}
        onClick={onSubmitForReview}
      >
        {isSubmitting ? 'Submitting…' : 'Submit for AI Review'}
      </Button>

      <Button
        variant="contained"
        color="success"
        disabled={!hasProtocol || isUnderReview || isValidating}
        onClick={onValidate}
      >
        {isValidating ? 'Approving…' : 'Approve Protocol'}
      </Button>
    </Box>
  );
}
