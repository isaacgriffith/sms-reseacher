/**
 * StakeholderPanel — practitioner stakeholder CRUD table (feature 008).
 *
 * Renders a table of practitioner stakeholders with add/edit/delete
 * actions.  Inline form uses react-hook-form + Zod for validation.
 * Shows an "at least one required" error state when the list is empty.
 *
 * @module StakeholderPanel
 */

import React, { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuItem from '@mui/material/MenuItem';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { Controller, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  useCreateStakeholder,
  useDeleteStakeholder,
  useStakeholders,
  useUpdateStakeholder,
} from '../../hooks/rapid/useStakeholders';
import type { Stakeholder } from '../../services/rapid/stakeholdersApi';

// ---------------------------------------------------------------------------
// Form schema
// ---------------------------------------------------------------------------

const stakeholderFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  role_title: z.string().min(1, 'Role title is required'),
  organisation: z.string().min(1, 'Organisation is required'),
  involvement_type: z.enum(['problem_definer', 'advisor', 'recipient']),
});

type StakeholderFormValues = z.infer<typeof stakeholderFormSchema>;

const INVOLVEMENT_OPTIONS = [
  { value: 'problem_definer', label: 'Problem Definer' },
  { value: 'advisor', label: 'Advisor' },
  { value: 'recipient', label: 'Recipient' },
] as const;

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link StakeholderPanel}. */
interface StakeholderPanelProps {
  /** Integer study ID. */
  studyId: number;
  /** Whether the panel is read-only (e.g. when editing is disabled). */
  readOnly?: boolean;
}

// ---------------------------------------------------------------------------
// Inline form component
// ---------------------------------------------------------------------------

interface StakeholderFormProps {
  studyId: number;
  editTarget: Stakeholder | null;
  onDone: () => void;
}

function StakeholderForm({ studyId, editTarget, onDone }: StakeholderFormProps) {
  const createMutation = useCreateStakeholder(studyId);
  const updateMutation = useUpdateStakeholder(studyId);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<StakeholderFormValues>({
    resolver: zodResolver(stakeholderFormSchema),
    defaultValues: {
      name: editTarget?.name ?? '',
      role_title: editTarget?.role_title ?? '',
      organisation: editTarget?.organisation ?? '',
      involvement_type: editTarget?.involvement_type ?? 'problem_definer',
    },
  });

  const onSubmit = (values: StakeholderFormValues) => {
    if (editTarget) {
      updateMutation.mutate({ id: editTarget.id, data: values }, { onSuccess: onDone });
    } else {
      createMutation.mutate(values, { onSuccess: onDone });
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 2 }}
    >
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Name"
            size="small"
            error={!!errors.name}
            helperText={errors.name?.message}
            sx={{ flex: '1 1 150px' }}
          />
        )}
      />
      <Controller
        name="role_title"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Role Title"
            size="small"
            error={!!errors.role_title}
            helperText={errors.role_title?.message}
            sx={{ flex: '1 1 150px' }}
          />
        )}
      />
      <Controller
        name="organisation"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Organisation"
            size="small"
            error={!!errors.organisation}
            helperText={errors.organisation?.message}
            sx={{ flex: '1 1 150px' }}
          />
        )}
      />
      <Controller
        name="involvement_type"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            select
            label="Involvement Type"
            size="small"
            error={!!errors.involvement_type}
            helperText={errors.involvement_type?.message}
            sx={{ flex: '1 1 150px' }}
          >
            {INVOLVEMENT_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </TextField>
        )}
      />
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start', mt: 0.5 }}>
        <Button type="submit" variant="contained" size="small">
          {editTarget ? 'Update' : 'Add'}
        </Button>
        <Button variant="outlined" size="small" onClick={onDone}>
          Cancel
        </Button>
      </Box>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

/**
 * StakeholderPanel renders a CRUD table for practitioner stakeholders.
 *
 * Shows "at least one required" alert when the list is empty.
 * Inline form appears below the table when adding or editing.
 *
 * @param studyId - The Rapid Review study ID.
 * @param readOnly - When true, hides add/edit/delete controls.
 */
export default function StakeholderPanel({
  studyId,
  readOnly = false,
}: StakeholderPanelProps): React.ReactElement {
  const { data: stakeholders = [], isLoading } = useStakeholders(studyId);
  const deleteMutation = useDeleteStakeholder(studyId);
  const [formVisible, setFormVisible] = useState(false);
  const [editTarget, setEditTarget] = useState<Stakeholder | null>(null);

  const openAdd = () => {
    setEditTarget(null);
    setFormVisible(true);
  };

  const openEdit = (s: Stakeholder) => {
    setEditTarget(s);
    setFormVisible(true);
  };

  const closeForm = () => {
    setFormVisible(false);
    setEditTarget(null);
  };

  if (isLoading) {
    return <Typography variant="body2">Loading stakeholders…</Typography>;
  }

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 1,
        }}
      >
        <Typography variant="subtitle2">Practitioner Stakeholders</Typography>
        {!readOnly && (
          <Button size="small" variant="outlined" onClick={openAdd}>
            + Add Stakeholder
          </Button>
        )}
      </Box>

      {stakeholders.length === 0 && (
        <Alert severity="warning" sx={{ mb: 1 }}>
          At least one practitioner stakeholder is required before the protocol can be validated.
        </Alert>
      )}

      {stakeholders.length > 0 && (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Organisation</TableCell>
              <TableCell>Involvement</TableCell>
              {!readOnly && <TableCell />}
            </TableRow>
          </TableHead>
          <TableBody>
            {stakeholders.map((s) => (
              <TableRow key={s.id}>
                <TableCell>{s.name}</TableCell>
                <TableCell>{s.role_title}</TableCell>
                <TableCell>{s.organisation}</TableCell>
                <TableCell>{s.involvement_type}</TableCell>
                {!readOnly && (
                  <TableCell>
                    <IconButton size="small" onClick={() => openEdit(s)} aria-label="edit">
                      ✏️
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => deleteMutation.mutate(s.id)}
                      aria-label="delete"
                    >
                      🗑️
                    </IconButton>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {!readOnly && formVisible && (
        <StakeholderForm studyId={studyId} editTarget={editTarget} onDone={closeForm} />
      )}
    </Box>
  );
}
