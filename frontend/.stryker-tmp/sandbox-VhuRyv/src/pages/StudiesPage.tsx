/**
 * Studies page: lists studies for a research group with actions.
 */
// @ts-nocheck


import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../services/api';
import NewStudyWizard from '../components/studies/NewStudyWizard';

interface StudySummary {
  id: number;
  name: string;
  topic: string | null;
  study_type: string;
  status: string;
  current_phase: number;
  created_at: string;
}

const PHASE_LABELS: Record<number, string> = {
  1: 'Scoping',
  2: 'Search',
  3: 'Screening',
  4: 'Extraction',
  5: 'Reporting',
};

const STATUS_COLOR: Record<string, string> = {
  active: '#16a34a',
  draft: '#64748b',
  completed: '#2563eb',
  archived: '#9ca3af',
};

export default function StudiesPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showWizard, setShowWizard] = useState(false);

  const { data: studies, isLoading, error } = useQuery<StudySummary[]>({
    queryKey: ['studies', groupId],
    queryFn: () => api.get<StudySummary[]>(`/api/v1/groups/${groupId}/studies`),
    enabled: !!groupId,
  });

  const archiveMutation = useMutation({
    mutationFn: (studyId: number) =>
      api.post<{ status: string }>(`/api/v1/studies/${studyId}/archive`, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['studies', groupId] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (studyId: number) => api.delete<void>(`/api/v1/studies/${studyId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['studies', groupId] }),
  });

  if (isLoading) return <p>Loading studies…</p>;
  if (error) return <p style={{ color: 'red' }}>Failed to load studies.</p>;

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.5rem',
        }}
      >
        <h2 style={{ margin: 0 }}>Studies</h2>
        <button
          onClick={() => setShowWizard(true)}
          style={{
            padding: '0.5rem 1rem',
            background: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer',
          }}
        >
          New Study
        </button>
      </div>

      {showWizard && groupId && (
        <NewStudyWizard
          groupId={parseInt(groupId)}
          onClose={() => setShowWizard(false)}
          onCreated={(studyId) => {
            setShowWizard(false);
            queryClient.invalidateQueries({ queryKey: ['studies', groupId] });
            navigate(`/studies/${studyId}`);
          }}
        />
      )}

      {(!studies || studies.length === 0) ? (
        <p style={{ color: '#475569' }}>No studies yet. Create one to get started.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {studies.map((s) => (
            <div
              key={s.id}
              style={{
                padding: '1rem 1.25rem',
                border: '1px solid #e2e8f0',
                borderRadius: '0.5rem',
                background: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
              }}
              onClick={() => navigate(`/studies/${s.id}`)}
            >
              <div>
                <h3 style={{ margin: '0 0 0.25rem', fontSize: '1rem' }}>{s.name}</h3>
                {s.topic && (
                  <p style={{ margin: '0 0 0.25rem', color: '#64748b', fontSize: '0.875rem' }}>
                    {s.topic}
                  </p>
                )}
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8125rem', color: '#64748b' }}>{s.study_type}</span>
                  <span style={{ color: '#cbd5e1' }}>·</span>
                  <span style={{ fontSize: '0.8125rem', color: '#64748b' }}>
                    Phase {s.current_phase}: {PHASE_LABELS[s.current_phase] ?? ''}
                  </span>
                  <span style={{ color: '#cbd5e1' }}>·</span>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: STATUS_COLOR[s.status] ?? '#64748b',
                      textTransform: 'capitalize',
                    }}
                  >
                    {s.status}
                  </span>
                </div>
              </div>

              <div
                style={{ display: 'flex', gap: '0.5rem' }}
                onClick={(e) => e.stopPropagation()}
              >
                {s.status !== 'archived' && (
                  <button
                    onClick={() => archiveMutation.mutate(s.id)}
                    style={{
                      padding: '0.25rem 0.75rem',
                      background: 'transparent',
                      border: '1px solid #cbd5e1',
                      borderRadius: '0.375rem',
                      cursor: 'pointer',
                      fontSize: '0.8125rem',
                      color: '#64748b',
                    }}
                  >
                    Archive
                  </button>
                )}
                <button
                  onClick={() => {
                    if (confirm(`Delete "${s.name}"? This cannot be undone.`)) {
                      deleteMutation.mutate(s.id);
                    }
                  }}
                  style={{
                    padding: '0.25rem 0.75rem',
                    background: 'transparent',
                    border: '1px solid #fca5a5',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontSize: '0.8125rem',
                    color: '#dc2626',
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
