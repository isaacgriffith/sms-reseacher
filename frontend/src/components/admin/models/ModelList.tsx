/**
 * ModelList: MUI Table displaying available models for a given provider,
 * with toggleable enabled/disabled state for each model.
 */

import Paper from '@mui/material/Paper';
import Switch from '@mui/material/Switch';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import { useProviderModels, useToggleModel } from '../../../services/providersApi';

/** Props for {@link ModelList}. */
export interface ModelListProps {
  /** UUID of the provider whose models to display. */
  providerId: string;
}

/**
 * Renders a table of available models for the given provider with
 * enable/disable toggles.
 *
 * @param props - {@link ModelListProps}
 * @returns MUI Table element or loading/error state.
 */
export default function ModelList({ providerId }: ModelListProps) {
  const { data: models, isLoading, error } = useProviderModels(providerId);
  const toggleMutation = useToggleModel();

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error" variant="body2">
        Failed to load models: {error.message}
      </Typography>
    );
  }

  const handleToggle = (modelId: string, currentEnabled: boolean) => {
    toggleMutation.mutate({ providerId, modelId, is_enabled: !currentEnabled });
  };

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small" aria-label="models table">
        <TableHead>
          <TableRow>
            <TableCell>Model Identifier</TableCell>
            <TableCell>Display Name</TableCell>
            <TableCell align="center">Enabled</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(models ?? []).map((m) => (
            <TableRow key={m.id} hover>
              <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                {m.model_identifier}
              </TableCell>
              <TableCell>{m.display_name}</TableCell>
              <TableCell align="center">
                <Switch
                  checked={m.is_enabled}
                  onChange={() => handleToggle(m.id, m.is_enabled)}
                  disabled={toggleMutation.isPending}
                  size="small"
                  inputProps={{ 'aria-label': `toggle ${m.model_identifier}` }}
                />
              </TableCell>
            </TableRow>
          ))}
          {(models ?? []).length === 0 && (
            <TableRow>
              <TableCell colSpan={3} align="center" sx={{ color: 'text.secondary', py: 3 }}>
                No models found. Use &ldquo;Refresh Models&rdquo; on the provider to fetch the catalog.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
