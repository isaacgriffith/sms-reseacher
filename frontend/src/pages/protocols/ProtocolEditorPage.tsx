/**
 * Dual-pane protocol editor page (feature 010).
 *
 * Left pane: ProtocolGraph (D3 visual editor with drag-to-reposition).
 * Right pane: ProtocolTextEditor (YAML editor with 300ms debounced sync).
 * Bottom: validation error display, save/discard CTAs.
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Typography from '@mui/material/Typography';
import ProtocolGraph from '../../components/protocols/ProtocolGraph';
import ProtocolNodePanel from '../../components/protocols/ProtocolNodePanel';
import ProtocolTextEditor from '../../components/protocols/ProtocolTextEditor';
import { useProtocolDetail } from '../../hooks/protocols/useProtocol';
import { useUpdateProtocol } from '../../hooks/protocols/useProtocol';
import { useProtocolEditor } from '../../hooks/protocols/useProtocolEditor';
import type { EditorNode } from '../../hooks/protocols/useProtocolEditor';

/**
 * Protocol editor page — wraps the dual-pane editor with load/save lifecycle.
 *
 * @returns Editor page.
 */
export default function ProtocolEditorPage() {
  const { id } = useParams<{ id: string }>();
  const protocolId = parseInt(id ?? '0', 10);
  const navigate = useNavigate();

  const { data: protocol, isLoading, error } = useProtocolDetail(protocolId);
  const updateMutation = useUpdateProtocol();

  const [conflictVersion, setConflictVersion] = useState<number | null>(null);

  if (isLoading) return <CircularProgress sx={{ m: 4 }} />;
  if (error || !protocol) return <Alert severity="error">Failed to load protocol.</Alert>;

  return (
    <EditorContent
      protocol={protocol}
      updateMutation={updateMutation}
      conflictVersion={conflictVersion}
      setConflictVersion={setConflictVersion}
      navigate={navigate}
    />
  );
}

function EditorContent({
  protocol,
  updateMutation,
  conflictVersion,
  setConflictVersion,
  navigate,
}: {
  protocol: import('../../services/protocols/protocolsApi').ProtocolDetail;
  updateMutation: ReturnType<typeof useUpdateProtocol>;
  conflictVersion: number | null;
  setConflictVersion: (v: number | null) => void;
  navigate: ReturnType<typeof useNavigate>;
}) {
  const { graph, yamlText, yamlError, dispatch, dispatchYamlDebounced } =
    useProtocolEditor(protocol);
  const [selectedNodeState, setSelectedNode] = useState<EditorNode | null>(null);

  function handleSave() {
    updateMutation.mutate(
      {
        id: protocol.id,
        version_id: protocol.version_id,
        name: protocol.name,
        description: protocol.description,
        nodes: graph.nodes,
        edges: graph.edges,
      },
      {
        onSuccess: () => navigate(`/protocols/${protocol.id}`),
        onError: (err: unknown) => {
          const detail = (err as { detail?: { current_version_id?: number } })?.detail;
          if (detail?.current_version_id) {
            setConflictVersion(detail.current_version_id);
          }
        },
      },
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Typography variant="h6" sx={{ flex: 1 }}>
          {protocol.name}
        </Typography>
        <Button variant="contained" onClick={handleSave} disabled={updateMutation.isPending}>
          Save
        </Button>
        <Button onClick={() => navigate(-1)}>Discard</Button>
      </Box>

      {updateMutation.isError && !conflictVersion && (
        <Alert severity="error" sx={{ mx: 2, mt: 1 }}>
          Save failed. Check validation errors.
        </Alert>
      )}

      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Box sx={{ flex: 1, p: 1, overflow: 'auto' }}>
          <ProtocolGraph
            nodes={graph.nodes}
            edges={graph.edges}
            editMode
            onNodeClick={(n) => {
              dispatch({ type: 'SELECT_NODE', payload: { task_id: n.task_id } });
              setSelectedNode(n as EditorNode);
            }}
            onNodeMove={(taskId, x, y) =>
              dispatch({
                type: 'UPDATE_NODE',
                payload: { task_id: taskId, position_x: x, position_y: y },
              })
            }
            width={640}
            height={520}
          />
        </Box>
        <Box
          sx={{
            width: 360,
            p: 1,
            borderLeft: '1px solid',
            borderColor: 'divider',
            overflow: 'auto',
          }}
        >
          <ProtocolTextEditor
            value={yamlText}
            onChange={dispatchYamlDebounced}
            parseError={yamlError}
          />
        </Box>
      </Box>

      <ProtocolNodePanel
        node={selectedNodeState}
        onClose={() => setSelectedNode(null)}
        editMode
        onSave={(updates) => dispatch({ type: 'UPDATE_NODE', payload: updates })}
      />

      <Dialog open={conflictVersion !== null} onClose={() => setConflictVersion(null)}>
        <DialogTitle>Edit Conflict</DialogTitle>
        <DialogContent>
          <Typography>
            This protocol was modified by someone else (version {conflictVersion}). Please reload to
            get the latest version before saving.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConflictVersion(null)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              setConflictVersion(null);
              navigate(0);
            }}
          >
            Reload
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
