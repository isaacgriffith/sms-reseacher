/**
 * Execution state view for a running protocol (feature 010, T066/T077).
 *
 * Shows TaskExecutionState statuses on each protocol node with colour coding,
 * gate failure details, and human sign-off approve buttons.
 */

import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import {
  useApproveTask,
  useCompleteTask,
  useExecutionState,
} from '../../hooks/protocols/useExecutionState';
import type { ExecutionTaskItem } from '../../services/protocols/protocolsApi';

interface ExecutionStateViewProps {
  /** ID of the study whose execution state to display. */
  studyId: number;
  /** When true, ACTIVE tasks show a "Mark Complete" button and GATE_FAILED human_sign_off tasks show "Approve". */
  isAdmin?: boolean;
}

function statusColor(s: string): string {
  switch (s) {
    case 'active':
      return '#1d4ed8';
    case 'complete':
      return '#15803d';
    case 'gate_failed':
      return '#dc2626';
    default:
      return '#6b7280';
  }
}

function TaskCard({
  task,
  studyId,
  isAdmin,
}: {
  task: ExecutionTaskItem;
  studyId: number;
  isAdmin: boolean;
}) {
  const completeTaskMutation = useCompleteTask();
  const approveTaskMutation = useApproveTask();
  const color = statusColor(task.status);
  const isSkipped = task.status === 'skipped';
  const detail = task.gate_failure_detail as Record<string, unknown> | null;
  const isHumanSignOff = detail?.gate_type === 'human_sign_off';

  return (
    <Box
      sx={{
        p: 1.5,
        mb: 1,
        border: `1px solid ${color}`,
        borderRadius: 1,
        fontStyle: isSkipped ? 'italic' : 'normal',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          {task.label}
        </Typography>
        <Chip label={task.task_type} size="small" variant="outlined" />
        <Chip
          label={task.status}
          size="small"
          sx={{ color, borderColor: color }}
          variant="outlined"
        />
      </Box>

      {detail && (
        <Alert severity="error" sx={{ mb: 0.5, py: 0 }}>
          {detail.gate_type === 'metric_threshold' && (
            <Typography variant="caption">
              {String(detail.metric_name)}: {String(detail.measured_value ?? 'N/A')} (threshold{' '}
              {String(detail.operator)} {String(detail.threshold)}).{' '}
              {detail.remediation ? String(detail.remediation) : ''}
            </Typography>
          )}
          {isHumanSignOff && (
            <Typography variant="caption">
              Human sign-off required: {String(detail.prompt ?? '')}
            </Typography>
          )}
          {!['metric_threshold', 'human_sign_off'].includes(String(detail.gate_type)) && (
            <Typography variant="caption">{JSON.stringify(detail)}</Typography>
          )}
        </Alert>
      )}

      {task.status === 'active' && isAdmin && (
        <Button
          size="small"
          variant="contained"
          disabled={completeTaskMutation.isPending}
          onClick={() => completeTaskMutation.mutate({ studyId, taskId: task.task_id })}
        >
          Mark Complete
        </Button>
      )}

      {task.status === 'gate_failed' && isHumanSignOff && isAdmin && (
        <Button
          size="small"
          variant="contained"
          color="warning"
          disabled={approveTaskMutation.isPending}
          onClick={() => approveTaskMutation.mutate({ studyId, taskId: task.task_id })}
        >
          Approve
        </Button>
      )}
    </Box>
  );
}

/**
 * Renders all protocol task nodes sorted by status with colour coding.
 *
 * @param props - Component props.
 * @returns MUI Box containing the execution state display.
 */
export default function ExecutionStateView({ studyId, isAdmin = false }: ExecutionStateViewProps) {
  const { data, isLoading, error } = useExecutionState(studyId);

  if (isLoading) return <CircularProgress size={24} />;
  if (error) return <Typography color="error">Failed to load execution state.</Typography>;
  if (!data || data.tasks.length === 0) {
    return <Typography sx={{ color: 'text.secondary' }}>No tasks found.</Typography>;
  }

  const order = ['active', 'gate_failed', 'pending', 'complete', 'skipped'];
  const sorted = [...data.tasks].sort((a, b) => order.indexOf(a.status) - order.indexOf(b.status));

  return (
    <Box>
      {sorted.map((task) => (
        <TaskCard key={task.node_id} task={task} studyId={studyId} isAdmin={isAdmin} />
      ))}
    </Box>
  );
}
