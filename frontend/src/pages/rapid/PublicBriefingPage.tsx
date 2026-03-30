/**
 * PublicBriefingPage — unauthenticated public view of a shared evidence briefing
 * (feature 008).
 *
 * Accessed via /public/briefings/:token. No auth context is available.
 *
 * @module PublicBriefingPage
 */

import React from 'react';
import { useParams } from 'react-router-dom';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import BriefingPreview from '../../components/rapid/BriefingPreview';
import {
  exportPublicBriefing,
  getPublicBriefing,
  ApiError,
  type PublicBriefing,
} from '../../services/rapid/briefingApi';

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * PublicBriefingPage renders a read-only evidence briefing for unauthenticated
 * visitors who have received a share link.
 *
 * Uses `useEffect` + `useState` for data fetching since there is no TanStack
 * Query context in public routes.
 */
export default function PublicBriefingPage(): React.ReactElement {
  const { token } = useParams<{ token: string }>();

  const [briefing, setBriefing] = React.useState<PublicBriefing | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [notFound, setNotFound] = React.useState(false);
  const [fetchError, setFetchError] = React.useState<string | null>(null);
  const [downloading, setDownloading] = React.useState(false);

  React.useEffect(() => {
    if (!token) {
      setNotFound(true);
      setLoading(false);
      return;
    }

    let cancelled = false;

    const load = async () => {
      try {
        const data = await getPublicBriefing(token);
        if (!cancelled) setBriefing(data);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && (err.status === 404 || err.status === 410)) {
          setNotFound(true);
        } else {
          setFetchError(err instanceof Error ? err.message : 'Failed to load briefing.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const handleDownload = async (format: 'pdf' | 'html') => {
    if (!token) return;
    setDownloading(true);
    try {
      const blob = await exportPublicBriefing(token, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `briefing.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CircularProgress size={24} />
          <Typography>Loading briefing…</Typography>
        </Box>
      </Container>
    );
  }

  if (notFound) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Alert severity="warning">
          This briefing is no longer available or the link has expired.
        </Alert>
      </Container>
    );
  }

  if (fetchError || !briefing) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Alert severity="error">
          {fetchError ?? 'Unable to load this briefing. Please try again later.'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">Evidence Briefing</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            disabled={downloading || !briefing.pdf_available}
            onClick={() => void handleDownload('pdf')}
          >
            {downloading ? <CircularProgress size={14} /> : 'Download PDF'}
          </Button>
          {briefing.html_available && (
            <Button
              variant="outlined"
              size="small"
              disabled={downloading}
              onClick={() => void handleDownload('html')}
            >
              Download HTML
            </Button>
          )}
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      <BriefingPreview briefing={briefing} threats={briefing.threats} />
    </Container>
  );
}
