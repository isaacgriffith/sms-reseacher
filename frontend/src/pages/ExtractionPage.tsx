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
    <div style={{ maxWidth: '72rem', margin: '0 auto', padding: '1.5rem' }}>
      <h2 style={{ margin: '0 0 1.5rem', fontSize: '1.25rem', color: '#111827' }}>
        Data Extraction
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: '18rem 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Sidebar: extraction list */}
        <div style={{ border: '1px solid #e2e8f0', borderRadius: '0.5rem', overflow: 'hidden' }}>
          <div style={{ padding: '0.75rem 1rem', background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
            <h3 style={{ margin: 0, fontSize: '0.875rem', fontWeight: 600, color: '#374151' }}>
              Papers ({extractions.length})
            </h3>
          </div>

          {isLoading && (
            <p style={{ padding: '1rem', color: '#6b7280', fontSize: '0.875rem' }}>Loading…</p>
          )}
          {error && (
            <p style={{ padding: '1rem', color: '#ef4444', fontSize: '0.875rem' }}>
              Failed to load extractions.
            </p>
          )}
          {!isLoading && extractions.length === 0 && (
            <p style={{ padding: '1rem', color: '#9ca3af', fontSize: '0.875rem' }}>
              No extractions yet. Run batch extraction from the study page.
            </p>
          )}

          <div>
            {extractions.map((ex) => (
              <button
                key={ex.id}
                onClick={() => setSelectedId(ex.id)}
                style={{
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
                <div style={{ fontSize: '0.8125rem', fontWeight: 500, color: '#111827' }}>
                  Paper #{ex.candidate_paper_id}
                </div>
                <div style={{ display: 'flex', gap: '0.375rem', marginTop: '0.25rem', flexWrap: 'wrap' }}>
                  <StatusBadge status={ex.extraction_status} />
                  <span style={{ fontSize: '0.6875rem', color: '#9ca3af' }}>
                    {ex.research_type.replace('_', ' ')}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Main: extraction detail */}
        <div>
          {selectedId ? (
            <div style={{ border: '1px solid #e2e8f0', borderRadius: '0.5rem', padding: '1.25rem' }}>
              <ExtractionView
                studyId={numericStudyId}
                extractionId={selectedId}
                onConflict={handleConflict}
              />
            </div>
          ) : (
            <div
              style={{
                border: '1px dashed #d1d5db',
                borderRadius: '0.5rem',
                padding: '3rem',
                textAlign: 'center',
                color: '#9ca3af',
                fontSize: '0.875rem',
              }}
            >
              Select a paper from the list to view or edit its extraction.
            </div>
          )}
        </div>
      </div>

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
    </div>
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
    <span
      style={{
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
    </span>
  );
}
