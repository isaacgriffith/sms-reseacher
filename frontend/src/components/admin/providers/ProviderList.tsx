/**
 * ProviderList: MUI Table displaying all configured LLM providers.
 *
 * Shows provider type (chip), display name, enabled status (chip),
 * has_api_key badge, and action buttons for edit, delete, and
 * model-list refresh.
 */

import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Tooltip from '@mui/material/Tooltip';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import RefreshIcon from '@mui/icons-material/Refresh';
import type { Provider } from '../../../types/provider';

/** Props for {@link ProviderList}. */
export interface ProviderListProps {
  /** List of providers to display. */
  providers: Provider[];
  /** Called when the user clicks the edit button for a provider. */
  onEdit: (p: Provider) => void;
  /** Called when the user clicks the delete button, receiving the provider ID. */
  onDelete: (id: string) => void;
  /** Called when the user clicks the refresh-models button, receiving the provider ID. */
  onRefresh: (id: string) => void;
}

const TYPE_COLORS: Record<string, 'default' | 'primary' | 'secondary'> = {
  anthropic: 'primary',
  openai: 'secondary',
  ollama: 'default',
};

/**
 * Renders a table of LLM providers with action controls.
 *
 * @param props - {@link ProviderListProps}
 * @returns MUI Table element.
 */
export default function ProviderList({ providers, onEdit, onDelete, onRefresh }: ProviderListProps) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small" aria-label="providers table">
        <TableHead>
          <TableRow>
            <TableCell>Type</TableCell>
            <TableCell>Display Name</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>API Key</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {providers.map((p) => (
            <TableRow key={p.id} hover>
              <TableCell>
                <Chip
                  label={p.provider_type}
                  size="small"
                  color={TYPE_COLORS[p.provider_type] ?? 'default'}
                />
              </TableCell>
              <TableCell>{p.display_name}</TableCell>
              <TableCell>
                <Chip
                  label={p.is_enabled ? 'Enabled' : 'Disabled'}
                  size="small"
                  color={p.is_enabled ? 'success' : 'default'}
                />
              </TableCell>
              <TableCell>
                {p.has_api_key ? (
                  <Chip label="Set" size="small" color="info" />
                ) : (
                  <Chip label="Not set" size="small" variant="outlined" />
                )}
              </TableCell>
              <TableCell align="right">
                <Tooltip title="Refresh models">
                  <IconButton size="small" onClick={() => onRefresh(p.id)} aria-label="refresh models">
                    <RefreshIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Edit">
                  <IconButton size="small" onClick={() => onEdit(p)} aria-label="edit provider">
                    <EditIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                  <IconButton size="small" onClick={() => onDelete(p.id)} aria-label="delete provider" color="error">
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
          {providers.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 3 }}>
                No providers configured. Click &ldquo;Add Provider&rdquo; to get started.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
