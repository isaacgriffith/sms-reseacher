/**
 * Page component for browsing and selecting research protocols (feature 010).
 *
 * Lists available protocols via useProtocolList, renders ProtocolList,
 * links to ProtocolEditorPage for each item, and provides Copy and Import actions.
 */

import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import ProtocolList from '../../components/protocols/ProtocolList';
import {
  useAssignProtocol,
  useCopyProtocol,
  useImportProtocol,
  useProtocolList,
} from '../../hooks/protocols/useProtocol';
import { exportProtocol } from '../../services/protocols/protocolsApi';
import type { ProtocolListItem } from '../../services/protocols/protocolsApi';

const STUDY_TYPES = ['', 'SMS', 'SLR', 'Rapid', 'Tertiary'] as const;

/**
 * Protocol Library page — browse, filter, copy, and assign research protocols.
 *
 * @returns Page containing the protocol list, study-type filter, copy dialog, and assign dialog.
 */
export default function ProtocolLibraryPage() {
  const navigate = useNavigate();
  const [studyType, setStudyType] = useState<string>('');
  const { data: protocols, isLoading, error } = useProtocolList(studyType || undefined);
  const copyMutation = useCopyProtocol();
  const assignMutation = useAssignProtocol();
  const importMutation = useImportProtocol();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [importError, setImportError] = useState<string | null>(null);

  const [copySource, setCopySource] = useState<ProtocolListItem | null>(null);
  const [copyName, setCopyName] = useState('');
  const [copyError, setCopyError] = useState<string | null>(null);

  const [assignSource, setAssignSource] = useState<ProtocolListItem | null>(null);
  const [assignStudyId, setAssignStudyId] = useState('');
  const [assignError, setAssignError] = useState<string | null>(null);

  function handleSelect(protocol: ProtocolListItem) {
    navigate(`/protocols/${protocol.id}`);
  }

  function handleCopyClick(protocol: ProtocolListItem) {
    setCopySource(protocol);
    setCopyName(`Copy of ${protocol.name}`);
    setCopyError(null);
  }

  function handleCopyConfirm() {
    if (!copySource || !copyName.trim()) return;
    copyMutation.mutate(
      { name: copyName.trim(), copy_from_protocol_id: copySource.id },
      {
        onSuccess: (created) => {
          setCopySource(null);
          navigate(`/protocols/${created.id}/edit`);
        },
        onError: () => setCopyError('Failed to copy protocol. Name may already be in use.'),
      },
    );
  }

  function handleAssignClick(protocol: ProtocolListItem) {
    setAssignSource(protocol);
    setAssignStudyId('');
    setAssignError(null);
  }

  async function handleExportClick(protocol: ProtocolListItem) {
    try {
      await exportProtocol(protocol.id);
    } catch {
      // error is surfaced via browser console; no modal needed for export
    }
  }

  function handleImportClick() {
    setImportError(null);
    fileInputRef.current?.click();
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    importMutation.mutate(file, {
      onSuccess: (created) => navigate(`/protocols/${created.id}/edit`),
      onError: (err) => setImportError(err.message),
    });
    // reset so the same file can be re-selected after an error
    e.target.value = '';
  }

  function handleAssignConfirm() {
    if (!assignSource || !assignStudyId.trim()) return;
    const studyId = parseInt(assignStudyId, 10);
    if (isNaN(studyId)) {
      setAssignError('Please enter a valid numeric study ID.');
      return;
    }
    assignMutation.mutate(
      { studyId, protocolId: assignSource.id },
      {
        onSuccess: () => setAssignSource(null),
        onError: () =>
          setAssignError('Failed to assign protocol. Check the study ID and try again.'),
      },
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Protocol Library</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={handleImportClick}
            disabled={importMutation.isPending}
          >
            {importMutation.isPending ? 'Importing…' : 'Import YAML'}
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".yaml,.yml"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </Box>
      </Box>

      {importError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setImportError(null)}>
          {importError}
        </Alert>
      )}

      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="body2">Filter by study type:</Typography>
        <Select
          size="small"
          value={studyType}
          onChange={(e) => setStudyType(e.target.value)}
          displayEmpty
          sx={{ minWidth: 140 }}
        >
          {STUDY_TYPES.map((t) => (
            <MenuItem key={t} value={t}>
              {t || 'All'}
            </MenuItem>
          ))}
        </Select>
      </Box>

      {isLoading && <CircularProgress size={24} />}
      {error && <Typography color="error">Failed to load protocols.</Typography>}
      {protocols && (
        <ProtocolList
          protocols={protocols}
          onSelect={handleSelect}
          onCopy={handleCopyClick}
          onAssign={handleAssignClick}
          onExport={handleExportClick}
        />
      )}

      <Dialog open={copySource !== null} onClose={() => setCopySource(null)}>
        <DialogTitle>Copy Protocol</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
          <Typography variant="body2">
            Creating a copy of <strong>{copySource?.name}</strong>.
          </Typography>
          <TextField
            label="New protocol name"
            size="small"
            value={copyName}
            onChange={(e) => setCopyName(e.target.value)}
            autoFocus
          />
          {copyError && (
            <Typography color="error" variant="caption">
              {copyError}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCopySource(null)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCopyConfirm}
            disabled={!copyName.trim() || copyMutation.isPending}
          >
            Copy
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={assignSource !== null} onClose={() => setAssignSource(null)}>
        <DialogTitle>Assign to Study</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
          <Typography variant="body2">
            Assigning <strong>{assignSource?.name}</strong> to a study.
          </Typography>
          <TextField
            label="Study ID"
            size="small"
            value={assignStudyId}
            onChange={(e) => setAssignStudyId(e.target.value)}
            autoFocus
            type="number"
          />
          {assignError && (
            <Typography color="error" variant="caption">
              {assignError}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignSource(null)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleAssignConfirm}
            disabled={!assignStudyId.trim() || assignMutation.isPending}
          >
            Assign
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
