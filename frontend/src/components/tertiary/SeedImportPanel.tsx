/**
 * SeedImportPanel — displays completed seed imports and allows importing
 * included papers from an existing platform SMS / SLR / Rapid Review study.
 *
 * @module SeedImportPanel
 */

import React, { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import { useCreateSeedImport, useSeedImports, useGroupStudies } from '../../hooks/tertiary/useSeedImports';
import type { StudySummary } from '../../services/tertiary/seedImportApi';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link SeedImportPanel}. */
export interface SeedImportPanelProps {
  /** The Tertiary Study receiving the seed corpus. */
  studyId: number;
  /** The research group ID — used to list available source studies. */
  groupId: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * SeedImportPanel renders the seed import list and an import dialog.
 *
 * @param studyId - The target Tertiary Study ID.
 * @param groupId - The research group to list source studies from.
 */
export default function SeedImportPanel({ studyId, groupId }: SeedImportPanelProps) {
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: imports = [], isLoading, error } = useSeedImports(studyId);
  const importMutation = useCreateSeedImport(studyId);

  function handleImportSuccess() {
    setDialogOpen(false);
    importMutation.reset();
  }

  if (isLoading) return <CircularProgress size={24} />;
  if (error) return <Alert severity="error">Failed to load seed imports.</Alert>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Seed Imports
        </Typography>
        <Button variant="contained" onClick={() => setDialogOpen(true)}>
          Import from Platform Study
        </Button>
      </Box>

      {imports.length === 0 ? (
        <Alert severity="info">
          No seed imports yet. Use the button above to import included papers from an existing
          SMS, SLR, or Rapid Review study.
        </Alert>
      ) : (
        <ImportTable imports={imports} />
      )}

      <ImportDialog
        open={dialogOpen}
        studyId={studyId}
        groupId={groupId}
        existingSourceIds={new Set(imports.map((i) => i.source_study_id))}
        mutation={importMutation}
        onClose={() => setDialogOpen(false)}
        onSuccess={handleImportSuccess}
      />
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Import table sub-component
// ---------------------------------------------------------------------------

interface ImportTableProps {
  imports: {
    id: number;
    source_study_title: string | null;
    source_study_type: string | null;
    imported_at: string;
    records_added: number;
    records_skipped: number;
  }[];
}

/**
 * Renders a table of completed seed import records.
 *
 * @param imports - List of seed import summary objects.
 */
function ImportTable({ imports }: ImportTableProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      {imports.map((imp) => (
        <Box
          key={imp.id}
          sx={{
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
            p: 2,
            display: 'grid',
            gridTemplateColumns: '1fr auto',
            gap: 1,
          }}
        >
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {imp.source_study_title ?? `Study #${imp.id}`}
              {imp.source_study_type ? ` (${imp.source_study_type})` : ''}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Imported {new Date(imp.imported_at).toLocaleDateString()}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="body2" color="success.main">
              +{imp.records_added} added
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {imp.records_skipped} skipped
            </Typography>
          </Box>
        </Box>
      ))}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Import dialog sub-component
// ---------------------------------------------------------------------------

interface ImportDialogProps {
  open: boolean;
  studyId: number;
  groupId: number;
  existingSourceIds: Set<number>;
  mutation: ReturnType<typeof useCreateSeedImport>;
  onClose: () => void;
  onSuccess: () => void;
}

/**
 * Dialog for selecting a source study and triggering the import.
 *
 * @param open - Whether the dialog is visible.
 * @param studyId - Target Tertiary Study ID (unused directly but available for context).
 * @param groupId - Group to list source studies from.
 * @param existingSourceIds - Already-imported source study IDs (shown as disabled).
 * @param mutation - The TanStack mutation instance.
 * @param onClose - Callback to close without importing.
 * @param onSuccess - Callback called after a successful import.
 */
function ImportDialog({
  open,
  groupId,
  existingSourceIds,
  mutation,
  onClose,
  onSuccess,
}: ImportDialogProps) {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const { data: studies = [], isLoading: studiesLoading } = useGroupStudies(groupId);

  // Filter to SMS/SLR/RAPID study types only.
  const importableStudies = studies.filter((s) =>
    ['SMS', 'SLR', 'RAPID'].includes(s.study_type.toUpperCase()),
  );

  function handleConfirm() {
    if (selectedId === null) return;
    mutation.mutate(selectedId, { onSuccess });
  }

  function handleClose() {
    setSelectedId(null);
    mutation.reset();
    onClose();
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Import from Platform Study</DialogTitle>
      <DialogContent>
        {mutation.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {(mutation.error as Error)?.message ?? 'Import failed.'}
          </Alert>
        )}

        {studiesLoading ? (
          <CircularProgress size={24} />
        ) : importableStudies.length === 0 ? (
          <Alert severity="info">
            No SMS, SLR, or Rapid Review studies found in this group.
          </Alert>
        ) : (
          <StudySelectList
            studies={importableStudies}
            existingSourceIds={existingSourceIds}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={mutation.isPending}>
          Cancel
        </Button>
        <Button
          variant="contained"
          disabled={selectedId === null || mutation.isPending}
          onClick={handleConfirm}
        >
          {mutation.isPending ? 'Importing…' : 'Import'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Study select list sub-component
// ---------------------------------------------------------------------------

interface StudySelectListProps {
  studies: StudySummary[];
  existingSourceIds: Set<number>;
  selectedId: number | null;
  onSelect: (id: number) => void;
}

/**
 * Renders a selectable list of platform studies for the import dialog.
 *
 * @param studies - Available source studies.
 * @param existingSourceIds - Studies already imported (rendered as disabled).
 * @param selectedId - Currently selected study ID.
 * @param onSelect - Callback when user selects a study.
 */
function StudySelectList({ studies, existingSourceIds, selectedId, onSelect }: StudySelectListProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mt: 1 }}>
      {studies.map((s, idx) => {
        const alreadyImported = existingSourceIds.has(s.id);
        const isSelected = selectedId === s.id;
        return (
          <React.Fragment key={s.id}>
            {idx > 0 && <Divider />}
            <Box
              onClick={() => !alreadyImported && onSelect(s.id)}
              sx={{
                p: 1.5,
                borderRadius: 1,
                cursor: alreadyImported ? 'default' : 'pointer',
                bgcolor: isSelected ? 'primary.light' : 'transparent',
                opacity: alreadyImported ? 0.5 : 1,
                '&:hover': alreadyImported ? {} : { bgcolor: 'action.hover' },
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {s.name}
                {alreadyImported ? ' (already imported)' : ''}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {s.study_type} · Phase {s.current_phase}
              </Typography>
            </Box>
          </React.Fragment>
        );
      })}
    </Box>
  );
}
