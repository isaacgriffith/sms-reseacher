/**
 * DiffViewer: shows a two-column diff of `your_version` vs `current_version`
 * from a 409 conflict response. Offers "Keep Mine", "Keep Theirs", and
 * "Merge" actions, then resubmits the PATCH with the resolved version_id.
 */

import { useMutation } from '@tanstack/react-query';
import { api } from '../../services/api';

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
    <div style={overlayStyle}>
      <div style={dialogStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#111827' }}>Edit Conflict Detected</h3>
          <button onClick={onDismiss} style={closeBtnStyle} aria-label="Dismiss">✕</button>
        </div>

        <p style={{ margin: '0 0 1rem', fontSize: '0.875rem', color: '#6b7280' }}>
          Another user edited this extraction while you were working. Choose how to resolve the conflict.
        </p>

        {/* Diff table */}
        <div style={{ overflowX: 'auto', marginBottom: '1.25rem' }}>
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
        </div>

        {mutation.isError && (
          <p style={{ color: '#ef4444', fontSize: '0.8125rem', marginBottom: '0.75rem' }}>
            Resolution failed. Please try again.
          </p>
        )}

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            onClick={keepMine}
            disabled={mutation.isPending}
            style={{ ...actionBtnStyle, background: '#2563eb', color: '#fff' }}
          >
            Keep Mine
          </button>
          <button
            onClick={keepTheirs}
            disabled={mutation.isPending}
            style={{ ...actionBtnStyle, background: '#16a34a', color: '#fff' }}
          >
            Keep Theirs
          </button>
          <button
            onClick={merge}
            disabled={mutation.isPending}
            style={{ ...actionBtnStyle, background: '#7c3aed', color: '#fff' }}
          >
            Merge
          </button>
          <button
            onClick={onDismiss}
            disabled={mutation.isPending}
            style={{ ...actionBtnStyle, background: 'transparent', color: '#374151', border: '1px solid #d1d5db' }}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0,0,0,0.45)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 50,
};

const dialogStyle: React.CSSProperties = {
  background: '#fff',
  borderRadius: '0.75rem',
  padding: '1.5rem',
  maxWidth: '56rem',
  width: '95%',
  maxHeight: '90vh',
  overflowY: 'auto',
  boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
};

const closeBtnStyle: React.CSSProperties = {
  background: 'transparent',
  border: 'none',
  fontSize: '1rem',
  cursor: 'pointer',
  color: '#6b7280',
  padding: '0.25rem',
};

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

const actionBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 500,
};
