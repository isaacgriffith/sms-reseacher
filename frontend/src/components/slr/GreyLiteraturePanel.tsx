/**
 * GreyLiteraturePanel — manage non-database grey literature sources.
 *
 * Displays a table of sources and allows adding / deleting entries via
 * dialog and icon-button actions.
 */

import { memo, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import DeleteIcon from '@mui/icons-material/Delete';
import type { GreyLiteratureSource } from '../../services/slr/greyLiteratureApi';
import type { CreateGreyLiteratureBody } from '../../services/slr/greyLiteratureApi';
import { useGreyLiterature, useAddSource, useDeleteSource } from '../../hooks/slr/useGreyLiterature';

// ---------------------------------------------------------------------------
// Source type options
// ---------------------------------------------------------------------------

const SOURCE_TYPES = [
  { value: 'technical_report', label: 'Technical Report' },
  { value: 'dissertation', label: 'Dissertation' },
  { value: 'rejected_publication', label: 'Rejected Publication' },
  { value: 'work_in_progress', label: 'Work in Progress' },
];

// ---------------------------------------------------------------------------
// AddSourceDialog sub-component
// ---------------------------------------------------------------------------

interface AddSourceDialogProps {
  /** Whether the dialog is open. */
  open: boolean;
  /** Called when the dialog should close. */
  onClose: () => void;
  /** Called with the form data when the user submits. */
  onSubmit: (data: CreateGreyLiteratureBody) => void;
  /** Whether the mutation is in progress. */
  isPending: boolean;
}

/**
 * Modal dialog for adding a new grey literature source.
 *
 * @param props - {@link AddSourceDialogProps}
 */
function AddSourceDialog({ open, onClose, onSubmit, isPending }: AddSourceDialogProps) {
  const { control, handleSubmit, reset } = useForm<CreateGreyLiteratureBody>({
    defaultValues: {
      source_type: 'technical_report',
      title: '',
      authors: '',
      year: undefined,
      url: '',
      description: '',
    },
  });

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>Add Grey Literature Source</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <Controller
            name="source_type"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <Select {...field} size="small" displayEmpty aria-label="Source type">
                {SOURCE_TYPES.map((t) => (
                  <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
                ))}
              </Select>
            )}
          />
          <Controller
            name="title"
            control={control}
            rules={{ required: true }}
            render={({ field }) => (
              <TextField {...field} label="Title" size="small" required fullWidth />
            )}
          />
          <Controller
            name="authors"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="Authors" size="small" fullWidth />
            )}
          />
          <Controller
            name="year"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Year"
                size="small"
                type="number"
                fullWidth
                onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : undefined)}
              />
            )}
          />
          <Controller
            name="url"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="URL" size="small" fullWidth />
            )}
          />
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <TextField {...field} label="Description" size="small" multiline rows={3} fullWidth />
            )}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={isPending}>Cancel</Button>
        <Button
          variant="contained"
          disabled={isPending}
          onClick={handleSubmit(onSubmit)}
          data-testid="add-source-submit"
        >
          {isPending ? 'Adding…' : 'Add'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// SourceRow sub-component
// ---------------------------------------------------------------------------

interface SourceRowProps {
  /** The grey literature source to display. */
  source: GreyLiteratureSource;
  /** Called when the delete button is clicked. */
  onDelete: (id: number) => void;
  /** Whether a delete mutation is in progress. */
  isDeleting: boolean;
}

/**
 * A single table row for a grey literature source.
 *
 * @param props - {@link SourceRowProps}
 */
function SourceRow({ source, onDelete, isDeleting }: SourceRowProps) {
  const typeLabel =
    SOURCE_TYPES.find((t) => t.value === source.source_type)?.label ?? source.source_type;

  return (
    <TableRow>
      <TableCell>
        <Chip label={typeLabel} size="small" variant="outlined" />
      </TableCell>
      <TableCell>{source.title}</TableCell>
      <TableCell>{source.authors ?? '—'}</TableCell>
      <TableCell>{source.year ?? '—'}</TableCell>
      <TableCell>
        <IconButton
          size="small"
          aria-label={`Delete ${source.title}`}
          disabled={isDeleting}
          onClick={() => onDelete(source.id)}
          data-testid={`delete-source-${source.id}`}
        >
          <DeleteIcon fontSize="small" />
        </IconButton>
      </TableCell>
    </TableRow>
  );
}

// ---------------------------------------------------------------------------
// GreyLiteraturePanel — main component
// ---------------------------------------------------------------------------

interface GreyLiteraturePanelProps {
  /** The integer study ID. */
  studyId: number;
}

/**
 * Panel for listing, adding, and deleting grey literature sources.
 *
 * @param props - {@link GreyLiteraturePanelProps}
 */
function GreyLiteraturePanel({ studyId }: GreyLiteraturePanelProps) {
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data, isLoading, error } = useGreyLiterature(studyId);
  const addSource = useAddSource(studyId);
  const deleteSource = useDeleteSource(studyId);

  const handleSubmit = (formData: CreateGreyLiteratureBody) => {
    addSource.mutate(formData, {
      onSuccess: () => setDialogOpen(false),
    });
  };

  if (isLoading) {
    return <CircularProgress size={20} aria-label="Loading grey literature sources" />;
  }
  if (error) {
    return (
      <Alert severity="error" data-testid="grey-lit-error">
        Failed to load grey literature sources.
      </Alert>
    );
  }

  const sources = data?.sources ?? [];

  return (
    <Box data-testid="grey-literature-panel">
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="subtitle2">Grey Literature Sources</Typography>
        <Button
          size="small"
          variant="outlined"
          onClick={() => setDialogOpen(true)}
          data-testid="add-source-btn"
        >
          Add Source
        </Button>
      </Box>

      {addSource.isError && (
        <Alert severity="warning" sx={{ mb: 1 }}>
          {(addSource.error as Error).message}
        </Alert>
      )}

      {sources.length === 0 ? (
        <Typography variant="body2" color="text.secondary" data-testid="grey-lit-empty">
          No grey literature sources tracked yet.
        </Typography>
      ) : (
        <Table size="small" aria-label="Grey literature sources">
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Authors</TableCell>
              <TableCell>Year</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sources.map((s) => (
              <SourceRow
                key={s.id}
                source={s}
                onDelete={(id) => deleteSource.mutate(id)}
                isDeleting={deleteSource.isPending}
              />
            ))}
          </TableBody>
        </Table>
      )}

      <AddSourceDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleSubmit}
        isPending={addSource.isPending}
      />
    </Box>
  );
}

export default memo(GreyLiteraturePanel);
