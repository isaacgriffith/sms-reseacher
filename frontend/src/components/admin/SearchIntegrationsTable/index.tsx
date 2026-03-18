/**
 * SearchIntegrationsTable — admin panel table for managing search integration credentials.
 *
 * Shows all integration types with status badges, masked key indicators, last-tested
 * timestamps, a "Test Now" button, and an edit modal for updating credentials.
 */

import { useReducer } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import {
  useSearchIntegrations,
  useUpsertCredential,
  useTestIntegration,
} from '../../../hooks/useSearchIntegrations';
import type { SearchIntegrationSummary } from '../../../hooks/useSearchIntegrations';

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

interface TableState {
  editingType: string | null;
  formKey: string;
  formToken: string;
}

type TableAction =
  | { type: 'OPEN_EDIT'; integrationType: string }
  | { type: 'CLOSE_EDIT' }
  | { type: 'SET_KEY'; value: string }
  | { type: 'SET_TOKEN'; value: string };

function tableReducer(state: TableState, action: TableAction): TableState {
  switch (action.type) {
    case 'OPEN_EDIT':
      return { editingType: action.integrationType, formKey: '', formToken: '' };
    case 'CLOSE_EDIT':
      return { ...state, editingType: null, formKey: '', formToken: '' };
    case 'SET_KEY':
      return { ...state, formKey: action.value };
    case 'SET_TOKEN':
      return { ...state, formToken: action.value };
    default:
      return state;
  }
}

const initialState: TableState = { editingType: null, formKey: '', formToken: '' };

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function statusColor(configuredVia: string): 'success' | 'warning' | 'error' | 'default' {
  if (configuredVia === 'database' || configuredVia === 'environment') return 'success';
  return 'warning';
}

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString();
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for the SearchIntegrationsTable component. */
export interface SearchIntegrationsTableProps {
  /** Optional title override; defaults to "Search Integrations". */
  title?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Admin table for viewing and managing search integration credentials.
 *
 * @param props - {@link SearchIntegrationsTableProps}
 */
export default function SearchIntegrationsTable({ title = 'Search Integrations' }: SearchIntegrationsTableProps) {
  const { data: integrations = [], isLoading } = useSearchIntegrations();
  const upsertMutation = useUpsertCredential();
  const testMutation = useTestIntegration();
  const [state, dispatch] = useReducer(tableReducer, initialState);

  const editingRecord = integrations.find((i) => i.integration_type === state.editingType);

  function handleSave() {
    if (!state.editingType) return;
    upsertMutation.mutate(
      {
        integrationType: state.editingType,
        body: {
          api_key: state.formKey || null,
          auxiliary_token: state.formToken || null,
          version_id: editingRecord?.version_id ?? null,
        },
      },
      { onSuccess: () => dispatch({ type: 'CLOSE_EDIT' }) }
    );
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>{title}</Typography>

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Database</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Access Type</TableCell>
            <TableCell>Key</TableCell>
            <TableCell>Last Tested</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {integrations.map((row: SearchIntegrationSummary) => (
            <TableRow key={row.integration_type}>
              <TableCell>{row.display_name}</TableCell>
              <TableCell>
                <Chip
                  label={row.configured_via}
                  color={statusColor(row.configured_via)}
                  size="small"
                />
              </TableCell>
              <TableCell>{row.access_type}</TableCell>
              <TableCell>{row.has_api_key ? '••••' : '—'}</TableCell>
              <TableCell>
                {formatDate(row.last_tested_at)}
                {row.last_test_status && (
                  <Typography variant="caption" sx={{ ml: 1, color: 'text.secondary' }}>
                    ({row.last_test_status})
                  </Typography>
                )}
              </TableCell>
              <TableCell align="right">
                <Button
                  size="small"
                  variant="outlined"
                  sx={{ mr: 1 }}
                  onClick={() => testMutation.mutate(row.integration_type)}
                  disabled={testMutation.isPending}
                >
                  Test Now
                </Button>
                <Button
                  size="small"
                  onClick={() => dispatch({ type: 'OPEN_EDIT', integrationType: row.integration_type })}
                >
                  Edit
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Dialog
        open={!!state.editingType}
        onClose={() => dispatch({ type: 'CLOSE_EDIT' })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Credential — {editingRecord?.display_name}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="API Key"
              value={state.formKey}
              onChange={(e) => dispatch({ type: 'SET_KEY', value: e.target.value })}
              placeholder={editingRecord?.has_api_key ? '(leave blank to keep current)' : ''}
              fullWidth
              size="small"
            />
            <TextField
              label="Auxiliary Token (optional)"
              value={state.formToken}
              onChange={(e) => dispatch({ type: 'SET_TOKEN', value: e.target.value })}
              fullWidth
              size="small"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => dispatch({ type: 'CLOSE_EDIT' })}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={upsertMutation.isPending}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
