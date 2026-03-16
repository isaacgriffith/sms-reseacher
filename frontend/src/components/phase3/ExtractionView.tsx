/**
 * ExtractionView: displays and inline-edits all extraction fields for one
 * accepted paper. Sends PATCH with the current version_id for optimistic
 * locking; calls onConflict when the server returns HTTP 409.
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';

interface Extraction {
  id: number;
  candidate_paper_id: number;
  research_type: string;
  venue_type: string;
  venue_name: string | null;
  author_details: Array<{ name: string; institution: string | null; locale: string | null }> | null;
  summary: string | null;
  open_codings: Array<{ code: string; definition: string; evidence_quote: string }> | null;
  keywords: string[] | null;
  question_data: Record<string, unknown> | null;
  extraction_status: 'pending' | 'ai_complete' | 'validated' | 'human_reviewed';
  version_id: number;
  extracted_by_agent: string | null;
  conflict_flag: boolean;
}

interface ConflictPayload {
  error: string;
  your_version: Record<string, unknown>;
  current_version: Record<string, unknown>;
}

interface PatchBody {
  version_id: number;
  venue_type?: string;
  venue_name?: string | null;
  summary?: string | null;
  research_type?: string;
  keywords?: string[] | null;
}

interface ExtractionViewProps {
  studyId: number;
  extractionId: number;
  /** Called with the 409 payload when a concurrent edit conflict is detected. */
  onConflict: (payload: ConflictPayload) => void;
}

const STATUS_COLORS: Record<string, string> = {
  pending: '#d97706',
  ai_complete: '#2563eb',
  validated: '#16a34a',
  human_reviewed: '#7c3aed',
};

const RESEARCH_TYPES = [
  'evaluation',
  'solution_proposal',
  'validation',
  'philosophical',
  'opinion',
  'personal_experience',
  'unknown',
];

export default function ExtractionView({ studyId, extractionId, onConflict }: ExtractionViewProps) {
  const queryClient = useQueryClient();
  const [editingField, setEditingField] = useState<string | null>(null);

  const { data: extraction, isLoading, error } = useQuery<Extraction>({
    queryKey: ['extraction', studyId, extractionId],
    queryFn: () => api.get<Extraction>(`/api/v1/studies/${studyId}/extractions/${extractionId}`),
  });

  const { register, handleSubmit, reset } = useForm<PatchBody>();

  const mutation = useMutation({
    mutationFn: (body: PatchBody) =>
      api.patch<Extraction>(`/api/v1/studies/${studyId}/extractions/${extractionId}`, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['extraction', studyId, extractionId] });
      setEditingField(null);
    },
    onError: (err: unknown) => {
      if (err instanceof ApiError && err.status === 409) {
        const payload = err.detail as unknown as ConflictPayload;
        onConflict(payload);
      }
    },
  });

  const handleSave = handleSubmit((data) => {
    if (!extraction) return;
    mutation.mutate({ ...data, version_id: extraction.version_id });
    reset();
  });

  const handleCancel = () => {
    setEditingField(null);
    reset();
  };

  if (isLoading) return <Typography sx={{ color: '#6b7280', fontSize: '0.875rem' }}>Loading extraction…</Typography>;
  if (error || !extraction) return <Typography sx={{ color: '#ef4444', fontSize: '0.875rem' }}>Failed to load extraction.</Typography>;

  const statusColor = STATUS_COLORS[extraction.extraction_status] ?? '#6b7280';

  return (
    <Box sx={{ fontFamily: 'inherit' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <Typography variant="subtitle1" sx={{ margin: 0, fontSize: '1rem', color: '#111827' }}>Data Extraction</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {extraction.conflict_flag && (
            <Typography component="span" sx={{ padding: '0.125rem 0.5rem', background: '#fef2f2', color: '#dc2626', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600 }}>
              Conflict
            </Typography>
          )}
          <Typography
            component="span"
            sx={{
              padding: '0.125rem 0.5rem',
              background: `${statusColor}18`,
              color: statusColor,
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: 600,
              textTransform: 'capitalize',
            }}
          >
            {extraction.extraction_status.replace('_', ' ')}
          </Typography>
        </Box>
      </Box>

      <form onSubmit={handleSave}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Research Type */}
          <Field
            label="Research Type"
            fieldKey="research_type"
            editingField={editingField}
            onEdit={setEditingField}
            onCancel={handleCancel}
            onSave={handleSave}
            display={<Typography component="span" sx={{ textTransform: 'capitalize' }}>{extraction.research_type.replace('_', ' ')}</Typography>}
            input={
              <select
                {...register('research_type')}
                defaultValue={extraction.research_type}
                style={selectStyle}
              >
                {RESEARCH_TYPES.map((rt) => (
                  <option key={rt} value={rt}>{rt.replace('_', ' ')}</option>
                ))}
              </select>
            }
          />

          {/* Venue Type */}
          <Field
            label="Venue Type"
            fieldKey="venue_type"
            editingField={editingField}
            onEdit={setEditingField}
            onCancel={handleCancel}
            onSave={handleSave}
            display={<Typography component="span">{extraction.venue_type || '—'}</Typography>}
            input={
              <input
                {...register('venue_type')}
                defaultValue={extraction.venue_type}
                style={inputStyle}
              />
            }
          />

          {/* Venue Name */}
          <Field
            label="Venue Name"
            fieldKey="venue_name"
            editingField={editingField}
            onEdit={setEditingField}
            onCancel={handleCancel}
            onSave={handleSave}
            display={<Typography component="span">{extraction.venue_name ?? '—'}</Typography>}
            input={
              <input
                {...register('venue_name')}
                defaultValue={extraction.venue_name ?? ''}
                style={inputStyle}
              />
            }
          />

          {/* Summary */}
          <Field
            label="Summary"
            fieldKey="summary"
            editingField={editingField}
            onEdit={setEditingField}
            onCancel={handleCancel}
            onSave={handleSave}
            display={
              <Typography sx={{ margin: 0, fontSize: '0.875rem', color: '#374151', lineHeight: 1.6 }}>
                {extraction.summary ?? '—'}
              </Typography>
            }
            input={
              <textarea
                {...register('summary')}
                defaultValue={extraction.summary ?? ''}
                rows={4}
                style={{ ...inputStyle, resize: 'vertical' }}
              />
            }
          />

          {/* Keywords (read-only display for now; inline edit of comma-separated) */}
          <Field
            label="Keywords"
            fieldKey="keywords"
            editingField={editingField}
            onEdit={setEditingField}
            onCancel={handleCancel}
            onSave={handleSave}
            display={
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
                {extraction.keywords?.map((kw) => (
                  <Typography component="span" key={kw} sx={{ padding: '0.125rem 0.5rem', background: '#eff6ff', color: '#1d4ed8', borderRadius: '9999px', fontSize: '0.75rem' }}>{kw}</Typography>
                )) ?? <Typography component="span" sx={{ color: '#9ca3af' }}>—</Typography>}
              </Box>
            }
            input={
              <input
                {...register('keywords', {
                  setValueAs: (v: string) => v.split(',').map((s) => s.trim()).filter(Boolean),
                })}
                defaultValue={extraction.keywords?.join(', ') ?? ''}
                placeholder="comma-separated keywords"
                style={inputStyle}
              />
            }
          />

          {/* Open Codings — read-only list */}
          <Paper variant="outlined" sx={{ padding: '0.75rem', border: '1px solid #e2e8f0', borderRadius: '0.5rem', background: '#fff' }}>
            <Typography component="label" sx={{ fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Open Codings</Typography>
            <Box sx={{ marginTop: '0.375rem' }}>
              {extraction.open_codings?.length ? (
                extraction.open_codings.map((oc, i) => (
                  <Box key={i} sx={{ marginBottom: '0.625rem', padding: '0.625rem', background: '#f8fafc', borderRadius: '0.375rem' }}>
                    <Typography sx={{ fontWeight: 600, fontSize: '0.8125rem', color: '#1e293b' }}>{oc.code}</Typography>
                    <Typography sx={{ fontSize: '0.8125rem', color: '#475569', marginTop: '0.25rem' }}>{oc.definition}</Typography>
                    {oc.evidence_quote && (
                      <blockquote style={{ margin: '0.375rem 0 0', padding: '0.375rem 0.625rem', borderLeft: '3px solid #cbd5e1', color: '#64748b', fontSize: '0.8125rem', fontStyle: 'italic' }}>
                        {oc.evidence_quote}
                      </blockquote>
                    )}
                  </Box>
                ))
              ) : (
                <Typography component="span" sx={{ color: '#9ca3af', fontSize: '0.875rem' }}>No open codings yet.</Typography>
              )}
            </Box>
          </Paper>

          {/* Question Data — read-only table */}
          {extraction.question_data && Object.keys(extraction.question_data).length > 0 && (
            <Paper variant="outlined" sx={{ padding: '0.75rem', border: '1px solid #e2e8f0', borderRadius: '0.5rem', background: '#fff' }}>
              <Typography component="label" sx={{ fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Research Question Answers</Typography>
              <Box sx={{ marginTop: '0.375rem' }}>
                {Object.entries(extraction.question_data).map(([qid, answer]) => (
                  <Box key={qid} sx={{ display: 'grid', gridTemplateColumns: '8rem 1fr', gap: '0.5rem', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                    <Typography component="span" sx={{ fontWeight: 600, color: '#374151', fontSize: '0.875rem' }}>{qid}</Typography>
                    <Typography component="span" sx={{ color: '#4b5563', fontSize: '0.875rem' }}>{answer != null ? String(answer) : '—'}</Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          )}
        </Box>

        {mutation.isError && !(mutation.error instanceof ApiError && (mutation.error as ApiError).status === 409) && (
          <Typography sx={{ color: '#ef4444', fontSize: '0.8125rem', marginTop: '0.5rem' }}>Save failed. Please try again.</Typography>
        )}
      </form>

      {extraction.extracted_by_agent && (
        <Typography sx={{ marginTop: '1rem', fontSize: '0.75rem', color: '#9ca3af' }}>
          Extracted by: {extraction.extracted_by_agent} · version {extraction.version_id}
        </Typography>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Field sub-component
// ---------------------------------------------------------------------------

interface FieldProps {
  label: string;
  fieldKey: string;
  editingField: string | null;
  onEdit: (key: string) => void;
  onCancel: () => void;
  onSave: () => void;
  display: React.ReactNode;
  input: React.ReactNode;
}

function Field({ label, fieldKey, editingField, onEdit, onCancel, onSave, display, input }: FieldProps) {
  const isEditing = editingField === fieldKey;
  return (
    <Paper variant="outlined" sx={{ padding: '0.75rem', border: '1px solid #e2e8f0', borderRadius: '0.5rem', background: '#fff' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
        <Typography component="label" sx={{ fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</Typography>
        {!isEditing && (
          <Button
            type="button"
            variant="outlined"
            size="small"
            onClick={() => onEdit(fieldKey)}
            sx={{ padding: '0.125rem 0.5rem', fontSize: '0.75rem', color: '#374151', borderColor: '#d1d5db' }}
          >
            Edit
          </Button>
        )}
      </Box>
      {isEditing ? (
        <Box>
          {input}
          <Box sx={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            <Button
              type="button"
              variant="contained"
              size="small"
              onClick={onSave}
              sx={{ padding: '0.25rem 0.75rem', fontSize: '0.8125rem' }}
            >
              Save
            </Button>
            <Button
              type="button"
              variant="outlined"
              size="small"
              onClick={onCancel}
              sx={{ padding: '0.25rem 0.75rem', color: '#374151', borderColor: '#d1d5db', fontSize: '0.8125rem' }}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      ) : (
        <Box sx={{ fontSize: '0.875rem', color: '#374151' }}>{display}</Box>
      )}
    </Paper>
  );
}

// ---------------------------------------------------------------------------
// Styles (for native elements that remain)
// ---------------------------------------------------------------------------

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.375rem 0.625rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  boxSizing: 'border-box',
};

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  background: '#fff',
  cursor: 'pointer',
};
