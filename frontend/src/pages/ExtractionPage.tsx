/**
 * ExtractionPage: lists accepted papers for a study and renders
 * ExtractionView for the selected paper. Opens DiffViewer as a modal
 * when a 409 conflict response is received from the PATCH endpoint.
 */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import ExtractionView from '../components/phase3/ExtractionView';
import DiffViewer from '../components/shared/DiffViewer';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';

interface Extraction {
  id: number;
  candidate_paper_id: number;
  extraction_status: string;
  research_type: string;
  version_id: number;
}

interface ConflictPayload {
  error: string;
  your_version: Record<string, unknown>;
  current_version: Record<string, unknown>;
}

export default function ExtractionPage() {
  const { studyId } = useParams<{ studyId: string }>();
  const numericStudyId = Number(studyId);
  const queryClient = useQueryClient();

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [conflict, setConflict] = useState<ConflictPayload | null>(null);

  const { data: extractions = [], isLoading, error } = useQuery<Extraction[]>({
    queryKey: ['extractions', numericStudyId],
    queryFn: () => api.get<Extraction[]>(`/api/v1/studies/${numericStudyId}/extractions`),
    enabled: !!numericStudyId,
  });

  const handleConflict = (payload: ConflictPayload) => {
    setConflict(payload);
  };

  const handleResolved = () => {
    setConflict(null);
    if (selectedId) {
      queryClient.invalidateQueries({ queryKey: ['extraction', numericStudyId, selectedId] });
    }
    queryClient.invalidateQueries({ queryKey: ['extractions', numericStudyId] });
  };

  const handleDismiss = () => {
    setConflict(null);
  };

  return (
    <Container maxWidth={false} sx={{ maxWidth: '72rem', margin: '0 auto', padding: '1.5rem' }}>
      <Typography variant="h5" sx={{ margin: '0 0 1.5rem', fontSize: '1.25rem', color: '#111827' }}>
        Data Extraction
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: '18rem 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Sidebar: extraction list */}
        <Paper variant="outlined" sx={{ border: '1px solid #e2e8f0', borderRadius: '0.5rem', overflow: 'hidden' }}>
          <Box sx={{ padding: '0.75rem 1rem', background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
            <Typography variant="subtitle2" sx={{ margin: 0, fontSize: '0.875rem', fontWeight: 600, color: '#374151' }}>
              Papers ({extractions.length})
            </Typography>
          </Box>

          {isLoading && (
            <Typography sx={{ padding: '1rem', color: '#6b7280', fontSize: '0.875rem' }}>Loading…</Typography>
          )}
          {error && (
            <Typography sx={{ padding: '1rem', color: '#ef4444', fontSize: '0.875rem' }}>
              Failed to load extractions.
            </Typography>
          )}
          {!isLoading && extractions.length === 0 && (
            <Typography sx={{ padding: '1rem', color: '#9ca3af', fontSize: '0.875rem' }}>
              No extractions yet. Run batch extraction from the study page.
            </Typography>
          )}

          <Box>
            {extractions.map((ex) => (
              <Box
                key={ex.id}
                component="button"
                onClick={() => setSelectedId(ex.id)}
                sx={{
                  display: 'block',
                  width: '100%',
                  padding: '0.75rem 1rem',
                  textAlign: 'left',
                  background: selectedId === ex.id ? '#eff6ff' : 'transparent',
                  border: 'none',
                  borderBottom: '1px solid #f1f5f9',
                  cursor: 'pointer',
                  borderLeft: selectedId === ex.id ? '3px solid #2563eb' : '3px solid transparent',
                }}
              >
                <Box sx={{ fontSize: '0.8125rem', fontWeight: 500, color: '#111827' }}>
                  Paper #{ex.candidate_paper_id}
                </Box>
                <Box sx={{ display: 'flex', gap: '0.375rem', marginTop: '0.25rem', flexWrap: 'wrap' }}>
                  <StatusBadge status={ex.extraction_status} />
                  <Typography component="span" sx={{ fontSize: '0.6875rem', color: '#9ca3af' }}>
                    {ex.research_type.replace('_', ' ')}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Box>
        </Paper>

        {/* Main: extraction detail */}
        <Box>
          {selectedId ? (
            <Paper variant="outlined" sx={{ border: '1px solid #e2e8f0', borderRadius: '0.5rem', padding: '1.25rem' }}>
              <ExtractionView
                studyId={numericStudyId}
                extractionId={selectedId}
                onConflict={handleConflict}
              />
            </Paper>
          ) : (
            <Box
              sx={{
                border: '1px dashed #d1d5db',
                borderRadius: '0.5rem',
                padding: '3rem',
                textAlign: 'center',
                color: '#9ca3af',
                fontSize: '0.875rem',
              }}
            >
              Select a paper from the list to view or edit its extraction.
            </Box>
          )}
        </Box>
      </Box>

      {/* DiffViewer modal */}
      {conflict && selectedId && (
        <DiffViewer
          studyId={numericStudyId}
          extractionId={selectedId}
          conflict={conflict}
          onResolved={handleResolved}
          onDismiss={handleDismiss}
        />
      )}
    </Container>
  );
}

// ---------------------------------------------------------------------------
// StatusBadge helper
// ---------------------------------------------------------------------------

const STATUS_COLORS: Record<string, string> = {
  pending: '#d97706',
  ai_complete: '#2563eb',
  validated: '#16a34a',
  human_reviewed: '#7c3aed',
};

function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status] ?? '#6b7280';
  return (
    <Typography
      component="span"
      sx={{
        padding: '0.0625rem 0.375rem',
        background: `${color}18`,
        color,
        borderRadius: '9999px',
        fontSize: '0.6875rem',
        fontWeight: 600,
        textTransform: 'capitalize',
      }}
    >
      {status.replace('_', ' ')}
    </Typography>
  );
}
