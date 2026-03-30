/**
 * SingleReviewerWarningBanner: persistent warning shown when single-reviewer
 * mode is enabled. Includes a toggle to enable/disable the mode with a
 * confirmation step before disabling.
 */

import { useState } from 'react';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

import { useUpdateSearchConfig } from '../../hooks/rapid/useSearchConfig';

interface SingleReviewerWarningBannerProps {
  studyId: number;
  singleReviewerMode: boolean;
}

export default function SingleReviewerWarningBanner({
  studyId,
  singleReviewerMode,
}: SingleReviewerWarningBannerProps) {
  const mutation = useUpdateSearchConfig(studyId);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const handleEnable = () => {
    mutation.mutate({ restrictions: [], single_reviewer_mode: true });
  };

  const handleDisableRequest = () => {
    setConfirmOpen(true);
  };

  const handleDisableConfirm = () => {
    setConfirmOpen(false);
    mutation.mutate({ restrictions: [], single_reviewer_mode: false });
  };

  if (!singleReviewerMode) {
    return (
      <Alert
        severity="info"
        sx={{ mb: 2 }}
        action={
          <Button
            size="small"
            color="inherit"
            onClick={handleEnable}
            disabled={mutation.isPending}
            startIcon={mutation.isPending ? <CircularProgress size={12} /> : undefined}
          >
            Enable
          </Button>
        }
      >
        Single-reviewer mode is off. Enable it if only one person will screen papers (this is
        recorded as a threat to validity).
      </Alert>
    );
  }

  return (
    <>
      <Alert
        severity="warning"
        sx={{ mb: 2 }}
        action={
          <Button
            size="small"
            color="inherit"
            onClick={handleDisableRequest}
            disabled={mutation.isPending}
            startIcon={mutation.isPending ? <CircularProgress size={12} /> : undefined}
          >
            Disable
          </Button>
        }
      >
        <strong>Single-Reviewer Mode Active.</strong> Papers will be screened by one reviewer only.
        This limitation is recorded as a threat to validity and will appear in the Evidence
        Briefing.
      </Alert>

      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)}>
        <DialogTitle>Disable Single-Reviewer Mode?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Disabling single-reviewer mode will remove the corresponding threat-to-validity entry.
            You can re-enable it at any time.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)}>Cancel</Button>
          <Button onClick={handleDisableConfirm} color="primary">
            Disable
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
