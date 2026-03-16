/**
 * DiffViewer: shows a two-column diff of `your_version` vs `current_version`
 * from a 409 conflict response. Offers "Keep Mine", "Keep Theirs", and
 * "Merge" actions, then resubmits the PATCH with the resolved version_id.
 */

import { useMutation } from '@tanstack/react-query';
import { api } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

interface ConflictPayload {
  error: string;
  your_version: Record<string, unknown>;
  current_version: Record<string, unknown>;
}

interface DiffViewerProps {
  studyId: number;
  extractionId: number;
  conflict: ConflictPayload;
  /** Called after a successful resolution so the parent can close the modal. */
  onResolved: () => void;
  /** Called if the user dismisses the dialog without resolving. */
  onDismiss: () => void;
}

const DISPLAY_FIELDS: Array<{ key: string; label: string }> = [
  { key: 'research_type', label: 'Research Type' },
  { key: 'venue_type', label: 'Venue Type' },
  { key: 'venue_name', label: 'Venue Name' },
  { key: 'summary', label: 'Summary' },
  { key: 'keywords', label: 'Keywords' },
];

function stringify(value: unknown): string {
  if (value == null) return '—';
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'object') return JSON.stringify(value, null, 2);
  return String(value);
}

export default function DiffViewer({
  studyId,
  extractionId,
  conflict,
  onResolved,
  onDismiss,
}: DiffViewerProps) {
  const { your_version, current_version } = conflict;

  const mutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api.patch(`/api/v1/studies/${studyId}/extractions/${extractionId}`, body),
    onSuccess: onResolved,
  });

  const keepMine = () => {
    const { version_id: _, ...fields } = your_version;
    mutation.mutate({
      version_id: current_version['version_id'],
      ...fields,
    });
  };

  const keepTheirs = () => {
    onResolved();
  };

  const merge = () => {
    // Simple merge: prefer your values for non-null fields, fall back to theirs
    const merged: Record<string, unknown> = { version_id: current_version['version_id'] };
    for (const { key } of DISPLAY_FIELDS) {
      merged[key] = your_version[key] ?? current_version[key];
    }
    mutation.mutate(merged);
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.45)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 50,
      }}
    >
      <Box
        sx={{
          background: '#fff',
          borderRadius: '0.75rem',
          padding: '1.5rem',
          maxWidth: '56rem',
          width: '95%',
          maxHeight: '90vh',
          overflowY: 'auto',
          boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <Typography variant="subtitle1" sx={{ margin: 0, fontSize: '1rem', color: '#111827' }}>Edit Conflict Detected</Typography>
          <Button
            onClick={onDismiss}
            aria-label="Dismiss"
            sx={{ background: 'transparent', border: 'none', fontSize: '1rem', cursor: 'pointer', color: '#6b7280', padding: '0.25rem', minWidth: 'auto' }}
          >
            ✕
          </Button>
        </Box>

        <Typography sx={{ margin: '0 0 1rem', fontSize: '0.875rem', color: '#6b7280' }}>
          Another user edited this extraction while you were working. Choose how to resolve the conflict.
        </Typography>

        {/* Diff table */}
        <Box sx={{ overflowX: 'auto', marginBottom: '1.25rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
            <thead>
              <tr>
                <th style={thStyle}>Field</th>
                <th style={{ ...thStyle, color: '#2563eb' }}>Your Version</th>
                <th style={{ ...thStyle, color: '#16a34a' }}>Current Version</th>
              </tr>
            </thead>
            <tbody>
              {DISPLAY_FIELDS.map(({ key, label }) => {
                const mine = stringify(your_version[key]);
                const theirs = stringify(current_version[key]);
                const isDiff = mine !== theirs;
                return (
                  <tr key={key} style={{ background: isDiff ? '#fffbeb' : 'transparent' }}>
                    <td style={{ ...tdStyle, fontWeight: 600, color: '#374151' }}>{label}</td>
                    <td style={{ ...tdStyle, color: '#1d4ed8', whiteSpace: 'pre-wrap' }}>{mine}</td>
                    <td style={{ ...tdStyle, color: '#15803d', whiteSpace: 'pre-wrap' }}>{theirs}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Box>

        {mutation.isError && (
          <Typography sx={{ color: '#ef4444', fontSize: '0.8125rem', marginBottom: '0.75rem' }}>
            Resolution failed. Please try again.
          </Typography>
        )}

        {/* Action buttons */}
        <Box sx={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            onClick={keepMine}
            disabled={mutation.isPending}
            sx={{ padding: '0.5rem 1rem', background: '#2563eb', fontSize: '0.875rem', fontWeight: 500 }}
          >
            Keep Mine
          </Button>
          <Button
            variant="contained"
            onClick={keepTheirs}
            disabled={mutation.isPending}
            sx={{ padding: '0.5rem 1rem', background: '#16a34a', '&:hover': { background: '#15803d' }, fontSize: '0.875rem', fontWeight: 500 }}
          >
            Keep Theirs
          </Button>
          <Button
            variant="contained"
            onClick={merge}
            disabled={mutation.isPending}
            sx={{ padding: '0.5rem 1rem', background: '#7c3aed', '&:hover': { background: '#6d28d9' }, fontSize: '0.875rem', fontWeight: 500 }}
          >
            Merge
          </Button>
          <Button
            variant="outlined"
            onClick={onDismiss}
            disabled={mutation.isPending}
            sx={{ padding: '0.5rem 1rem', color: '#374151', borderColor: '#d1d5db', fontSize: '0.875rem', fontWeight: 500 }}
          >
            Cancel
          </Button>
        </Box>
      </Box>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const thStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  textAlign: 'left',
  borderBottom: '2px solid #e2e8f0',
  fontWeight: 600,
  fontSize: '0.75rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: '#6b7280',
};

const tdStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  borderBottom: '1px solid #f1f5f9',
  verticalAlign: 'top',
};
