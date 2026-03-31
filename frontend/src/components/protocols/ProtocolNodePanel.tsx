/**
 * Side panel showing detail for the currently selected protocol node (feature 010).
 *
 * In read-only mode displays node fields. In edit mode shows react-hook-form
 * for editing label, description, is_required, and delegates to QualityGateEditor.
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useForm } from 'react-hook-form';
import type { ProtocolNode } from '../../services/protocols/protocolsApi';
import type { EditorNode } from '../../hooks/protocols/useProtocolEditor';
import QualityGateEditor from './QualityGateEditor';

interface ProtocolNodePanelProps {
  /** The selected node to display, or null to hide the panel. */
  node: ProtocolNode | EditorNode | null;
  /** Called when the panel should close. */
  onClose: () => void;
  /** Edit mode: if true, show editable form. */
  editMode?: boolean;
  /** Called when user saves node changes (edit mode only). */
  onSave?: (updates: Partial<EditorNode> & { task_id: string }) => void;
}

interface NodeForm {
  label: string;
  description: string;
  is_required: boolean;
}

/**
 * MUI Drawer panel for a selected protocol node.
 * Read-only unless editMode=true.
 *
 * @param props - Component props.
 * @returns MUI Drawer containing node detail sections.
 */
export default function ProtocolNodePanel({
  node,
  onClose,
  editMode = false,
  onSave,
}: ProtocolNodePanelProps) {
  const { register, handleSubmit, reset } = useForm<NodeForm>({
    values: node
      ? { label: node.label, description: node.description ?? '', is_required: node.is_required }
      : undefined,
  });

  function onSubmit(data: NodeForm) {
    if (node && onSave) {
      onSave({ task_id: node.task_id, ...data });
    }
    onClose();
  }

  return (
    <Drawer
      anchor="right"
      open={node !== null}
      onClose={() => {
        reset();
        onClose();
      }}
      PaperProps={{ sx: { width: 340, p: 2 } }}
    >
      {node && (
        <Box>
          {editMode ? (
            <Box
              component="form"
              onSubmit={handleSubmit(onSubmit)}
              sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}
            >
              <TextField label="Label" size="small" {...register('label')} />
              <TextField
                label="Description"
                size="small"
                multiline
                rows={2}
                {...register('description')}
              />
              <Chip
                label={node.task_type}
                size="small"
                color="primary"
                sx={{ alignSelf: 'flex-start' }}
              />
              <Divider />
              <Typography variant="subtitle2">Quality Gates</Typography>
              <QualityGateEditor
                gates={node.quality_gates}
                onChange={(gates) => onSave?.({ task_id: node.task_id, quality_gates: gates })}
              />
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Button type="submit" variant="contained" size="small">
                  Save
                </Button>
                <Button
                  size="small"
                  onClick={() => {
                    reset();
                    onClose();
                  }}
                >
                  Cancel
                </Button>
              </Box>
            </Box>
          ) : (
            <>
              <Typography variant="h6" sx={{ mb: 0.5 }}>
                {node.label}
              </Typography>
              <Chip label={node.task_type} size="small" color="primary" sx={{ mb: 1 }} />
              {node.description && (
                <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                  {node.description}
                </Typography>
              )}
              <Divider sx={{ mb: 1 }} />
              <Typography variant="subtitle2">Inputs</Typography>
              <List dense disablePadding>
                {node.inputs.map((inp) => (
                  <ListItem key={inp.id} disablePadding>
                    <ListItemText
                      primary={inp.name}
                      secondary={`${inp.data_type}${inp.is_required ? ' · required' : ' · optional'}`}
                    />
                  </ListItem>
                ))}
                {node.inputs.length === 0 && (
                  <ListItem disablePadding>
                    <ListItemText secondary="None" />
                  </ListItem>
                )}
              </List>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2">Outputs</Typography>
              <List dense disablePadding>
                {node.outputs.map((out) => (
                  <ListItem key={out.id} disablePadding>
                    <ListItemText primary={out.name} secondary={out.data_type} />
                  </ListItem>
                ))}
                {node.outputs.length === 0 && (
                  <ListItem disablePadding>
                    <ListItemText secondary="None" />
                  </ListItem>
                )}
              </List>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2">Quality Gates</Typography>
              <List dense disablePadding>
                {node.quality_gates.map((gate) => (
                  <ListItem key={gate.id} disablePadding>
                    <ListItemText
                      primary={gate.gate_type}
                      secondary={JSON.stringify(gate.config)}
                    />
                  </ListItem>
                ))}
                {node.quality_gates.length === 0 && (
                  <ListItem disablePadding>
                    <ListItemText secondary="None" />
                  </ListItem>
                )}
              </List>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2">Assignees</Typography>
              <List dense disablePadding>
                {node.assignees.map((a) => (
                  <ListItem key={a.id} disablePadding>
                    <ListItemText
                      primary={a.role ?? a.agent_id ?? '—'}
                      secondary={a.assignee_type}
                    />
                  </ListItem>
                ))}
                {node.assignees.length === 0 && (
                  <ListItem disablePadding>
                    <ListItemText secondary="None" />
                  </ListItem>
                )}
              </List>
            </>
          )}
        </Box>
      )}
    </Drawer>
  );
}
