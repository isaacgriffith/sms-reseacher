/**
 * ExtractionView: displays and inline-edits all extraction fields for one
 * accepted paper. Sends PATCH with the current version_id for optimistic
 * locking; calls onConflict when the server returns HTTP 409.
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';

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

  if (isLoading) return <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Loading extraction…</p>;
  if (error || !extraction) return <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>Failed to load extraction.</p>;

  const statusColor = STATUS_COLORS[extraction.extraction_status] ?? '#6b7280';

  return (
    <div style={{ fontFamily: 'inherit' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h3 style={{ margin: 0, fontSize: '1rem', color: '#111827' }}>Data Extraction</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {extraction.conflict_flag && (
            <span style={{ padding: '0.125rem 0.5rem', background: '#fef2f2', color: '#dc2626', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600 }}>
              Conflict
            </span>
          )}
          <span
            style={{
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
          </span>
        </div>
      </div>

      <form onSubmit={handleSave}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Research Type */}
          <Field
            label="Research Type"
            fieldKey="research_type"
            editingField={editingField}
            onEdit={setEditingField}
            onCancel={handleCancel}
            onSave={handleSave}
            display={<span style={{ textTransform: 'capitalize' }}>{extraction.research_type.replace('_', ' ')}</span>}
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
            display={<span>{extraction.venue_type || '—'}</span>}
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
            display={<span>{extraction.venue_name ?? '—'}</span>}
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
              <p style={{ margin: 0, fontSize: '0.875rem', color: '#374151', lineHeight: 1.6 }}>
                {extraction.summary ?? '—'}
              </p>
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
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
                {extraction.keywords?.map((kw) => (
                  <span key={kw} style={tagStyle}>{kw}</span>
                )) ?? <span style={{ color: '#9ca3af' }}>—</span>}
              </div>
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
          <div style={fieldContainerStyle}>
            <label style={labelStyle}>Open Codings</label>
            <div style={{ marginTop: '0.375rem' }}>
              {extraction.open_codings?.length ? (
                extraction.open_codings.map((oc, i) => (
                  <div key={i} style={{ marginBottom: '0.625rem', padding: '0.625rem', background: '#f8fafc', borderRadius: '0.375rem' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.8125rem', color: '#1e293b' }}>{oc.code}</div>
                    <div style={{ fontSize: '0.8125rem', color: '#475569', marginTop: '0.25rem' }}>{oc.definition}</div>
                    {oc.evidence_quote && (
                      <blockquote style={{ margin: '0.375rem 0 0', padding: '0.375rem 0.625rem', borderLeft: '3px solid #cbd5e1', color: '#64748b', fontSize: '0.8125rem', fontStyle: 'italic' }}>
                        {oc.evidence_quote}
                      </blockquote>
                    )}
                  </div>
                ))
              ) : (
                <span style={{ color: '#9ca3af', fontSize: '0.875rem' }}>No open codings yet.</span>
              )}
            </div>
          </div>

          {/* Question Data — read-only table */}
          {extraction.question_data && Object.keys(extraction.question_data).length > 0 && (
            <div style={fieldContainerStyle}>
              <label style={labelStyle}>Research Question Answers</label>
              <div style={{ marginTop: '0.375rem' }}>
                {Object.entries(extraction.question_data).map(([qid, answer]) => (
                  <div key={qid} style={{ display: 'grid', gridTemplateColumns: '8rem 1fr', gap: '0.5rem', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                    <span style={{ fontWeight: 600, color: '#374151' }}>{qid}</span>
                    <span style={{ color: '#4b5563' }}>{answer != null ? String(answer) : '—'}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {mutation.isError && !(mutation.error instanceof ApiError && (mutation.error as ApiError).status === 409) && (
          <p style={{ color: '#ef4444', fontSize: '0.8125rem', marginTop: '0.5rem' }}>Save failed. Please try again.</p>
        )}
      </form>

      {extraction.extracted_by_agent && (
        <p style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#9ca3af' }}>
          Extracted by: {extraction.extracted_by_agent} · version {extraction.version_id}
        </p>
      )}
    </div>
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
    <div style={fieldContainerStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
        <label style={labelStyle}>{label}</label>
        {!isEditing && (
          <button type="button" onClick={() => onEdit(fieldKey)} style={editBtnStyle}>
            Edit
          </button>
        )}
      </div>
      {isEditing ? (
        <div>
          {input}
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            <button type="button" onClick={onSave} style={saveBtnStyle}>Save</button>
            <button type="button" onClick={onCancel} style={cancelBtnStyle}>Cancel</button>
          </div>
        </div>
      ) : (
        <div style={{ fontSize: '0.875rem', color: '#374151' }}>{display}</div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const fieldContainerStyle: React.CSSProperties = {
  padding: '0.75rem',
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
  background: '#fff',
};

const labelStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  fontWeight: 600,
  color: '#6b7280',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

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

const tagStyle: React.CSSProperties = {
  padding: '0.125rem 0.5rem',
  background: '#eff6ff',
  color: '#1d4ed8',
  borderRadius: '9999px',
  fontSize: '0.75rem',
};

const editBtnStyle: React.CSSProperties = {
  padding: '0.125rem 0.5rem',
  background: 'transparent',
  border: '1px solid #d1d5db',
  borderRadius: '0.25rem',
  cursor: 'pointer',
  fontSize: '0.75rem',
  color: '#374151',
};

const saveBtnStyle: React.CSSProperties = {
  padding: '0.25rem 0.75rem',
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.8125rem',
};

const cancelBtnStyle: React.CSSProperties = {
  padding: '0.25rem 0.75rem',
  background: 'transparent',
  color: '#374151',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.8125rem',
};
