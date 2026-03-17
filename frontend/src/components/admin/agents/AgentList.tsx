/**
 * AgentList — MUI Table listing all agents with task type, role/persona,
 * model display name, active status, and an Edit action button.
 */

import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import type { AgentSummary } from '../../../types/agent';

/** Props for {@link AgentList}. */
interface AgentListProps {
  /** List of agent summaries to display. */
  agents: AgentSummary[];
  /** Called when the user clicks the Edit button for an agent. */
  onEdit: (agent: AgentSummary) => void;
}

/**
 * Renders a table of agent summaries.
 *
 * @param props - {@link AgentListProps}
 */
export default function AgentList({ agents, onEdit }: AgentListProps) {
  return (
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Task Type</TableCell>
          <TableCell>Role Name</TableCell>
          <TableCell>Persona Name</TableCell>
          <TableCell>Model</TableCell>
          <TableCell>Status</TableCell>
          <TableCell align="right">Actions</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {agents.map((agent) => (
          <TableRow key={agent.id} hover>
            <TableCell>
              <Chip label={agent.task_type} size="small" variant="outlined" />
            </TableCell>
            <TableCell>{agent.role_name}</TableCell>
            <TableCell>{agent.persona_name}</TableCell>
            <TableCell>{agent.model_display_name}</TableCell>
            <TableCell>
              <Chip
                label={agent.is_active ? 'Active' : 'Inactive'}
                size="small"
                color={agent.is_active ? 'success' : 'default'}
              />
            </TableCell>
            <TableCell align="right">
              <IconButton size="small" onClick={() => onEdit(agent)} aria-label="Edit agent">
                <EditIcon fontSize="small" />
              </IconButton>
            </TableCell>
          </TableRow>
        ))}
        {agents.length === 0 && (
          <TableRow>
            <TableCell colSpan={6} align="center" sx={{ py: 3, color: 'text.secondary' }}>
              No agents found.
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
