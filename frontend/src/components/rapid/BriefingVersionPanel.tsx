/**
 * BriefingVersionPanel — lists evidence briefing versions with publish, download,
 * and share link actions (feature 008).
 *
 * @module BriefingVersionPanel
 */

import React from 'react';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import { exportBriefing } from '../../services/rapid/briefingApi';
import {
  useBriefings,
  useCreateShareToken,
  usePublishBriefing,
} from '../../hooks/rapid/useBriefingVersions';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link BriefingVersionPanel}. */
interface BriefingVersionPanelProps {
  /** Integer study ID. */
  studyId: number;
  /** Called when the user clicks a briefing row to preview it. */
  onSelectBriefing: (briefingId: number) => void;
  /** Currently selected briefing ID, or null if none. */
  selectedBriefingId: number | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Renders a table of evidence briefing versions with per-row actions:
 * - Publish (DRAFT rows)
 * - Download PDF / HTML
 * - Copy Share Link (PUBLISHED rows)
 *
 * @param studyId - The study whose briefings to display.
 * @param onSelectBriefing - Callback to preview a briefing.
 * @param selectedBriefingId - Highlights the selected row.
 */
export default function BriefingVersionPanel({
  studyId,
  onSelectBriefing,
  selectedBriefingId,
}: BriefingVersionPanelProps): React.ReactElement {
  const { data: briefings, isLoading } = useBriefings(studyId);
  const publishMutation = usePublishBriefing(studyId);
  const shareTokenMutation = useCreateShareToken(studyId);

  const [downloadingId, setDownloadingId] = React.useState<string | null>(null);

  const handlePublish = (briefingId: number) => {
    const confirmed = window.confirm(
      'Publish this briefing? Published briefings can be shared publicly.',
    );
    if (!confirmed) return;
    publishMutation.mutate(briefingId);
  };

  const handleDownload = async (briefingId: number, format: 'pdf' | 'html', version: number) => {
    const key = `${briefingId}-${format}`;
    setDownloadingId(key);
    try {
      const blob = await exportBriefing(studyId, briefingId, format);
      downloadBlob(blob, `briefing-v${version}.${format}`);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleCopyShareLink = (briefingId: number) => {
    shareTokenMutation.mutate(briefingId, {
      onSuccess: (shareToken) => {
        void navigator.clipboard.writeText(shareToken.share_url);
      },
    });
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
        <CircularProgress size={20} />
        <Typography>Loading briefings…</Typography>
      </Box>
    );
  }

  if (!briefings || briefings.length === 0) {
    return <></>;
  }

  return (
    <Paper variant="outlined" sx={{ mt: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Version</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Generated</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {briefings.map((b) => {
            const isSelected = b.id === selectedBriefingId;
            const isGenerating = !b.pdf_available;

            return (
              <TableRow
                key={b.id}
                hover
                selected={isSelected}
                onClick={() => onSelectBriefing(b.id)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell>
                  <Typography variant="body2" fontWeight={isSelected ? 700 : 400}>
                    v{b.version_number}
                  </Typography>
                </TableCell>

                <TableCell>
                  {isGenerating ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <CircularProgress size={12} />
                      <Typography variant="caption">Generating…</Typography>
                    </Box>
                  ) : (
                    <Chip
                      label={b.status === 'published' ? 'Published' : 'Draft'}
                      color={b.status === 'published' ? 'success' : 'info'}
                      size="small"
                    />
                  )}
                </TableCell>

                <TableCell>
                  <Typography variant="caption">{formatDate(b.generated_at)}</Typography>
                </TableCell>

                <TableCell onClick={(e) => e.stopPropagation()}>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {b.status === 'draft' && !isGenerating && (
                      <Button
                        size="small"
                        variant="outlined"
                        color="primary"
                        disabled={publishMutation.isPending}
                        onClick={() => handlePublish(b.id)}
                      >
                        Publish
                      </Button>
                    )}

                    {b.pdf_available && (
                      <Button
                        size="small"
                        variant="text"
                        disabled={downloadingId === `${b.id}-pdf`}
                        onClick={() => void handleDownload(b.id, 'pdf', b.version_number)}
                      >
                        {downloadingId === `${b.id}-pdf` ? <CircularProgress size={14} /> : 'PDF'}
                      </Button>
                    )}

                    {b.html_available && (
                      <Button
                        size="small"
                        variant="text"
                        disabled={downloadingId === `${b.id}-html`}
                        onClick={() => void handleDownload(b.id, 'html', b.version_number)}
                      >
                        {downloadingId === `${b.id}-html` ? <CircularProgress size={14} /> : 'HTML'}
                      </Button>
                    )}

                    {b.status === 'published' && (
                      <Button
                        size="small"
                        variant="text"
                        color="secondary"
                        disabled={shareTokenMutation.isPending}
                        onClick={() => handleCopyShareLink(b.id)}
                      >
                        Copy Share Link
                      </Button>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Paper>
  );
}
