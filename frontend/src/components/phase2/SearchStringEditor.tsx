/**
 * SearchStringEditor: text area for search string, AI generation, version history.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';

interface Iteration {
  id: number;
  iteration_number: number;
  result_set_count: number;
  test_set_recall: number;
  ai_adequacy_judgment: string | null;
  human_approved: boolean | null;
}

interface SearchString {
  id: number;
  study_id: number;
  version: number;
  string_text: string;
  is_active: boolean;
  created_by_agent: string | null;
  iterations: Iteration[];
}

interface SearchStringEditorProps {
  studyId: number;
  onSearchStringCreated?: (id: number) => void;
}

export default function SearchStringEditor({ studyId, onSearchStringCreated }: SearchStringEditorProps) {
  const qc = useQueryClient();
  const [manualText, setManualText] = useState('');
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const { data: strings = [], isLoading } = useQuery<SearchString[]>({
    queryKey: ['search-strings', studyId],
    queryFn: () => api.get<SearchString[]>(`/api/v1/studies/${studyId}/search-strings`),
  });

  const createManual = useMutation({
    mutationFn: (text: string) =>
      api.post<SearchString>(`/api/v1/studies/${studyId}/search-strings`, {
        string_text: text,
      }),
    onSuccess: (ss) => {
      qc.invalidateQueries({ queryKey: ['search-strings', studyId] });
      setManualText('');
      setSelectedId(ss.id);
      onSearchStringCreated?.(ss.id);
    },
  });

  const generateAI = useMutation({
    mutationFn: () =>
      api.post<SearchString>(`/api/v1/studies/${studyId}/search-strings/generate`, {}),
    onSuccess: (ss) => {
      setGenerateError(null);
      qc.invalidateQueries({ queryKey: ['search-strings', studyId] });
      setSelectedId(ss.id);
      onSearchStringCreated?.(ss.id);
    },
    onError: (err) => {
      setGenerateError(err instanceof ApiError ? err.detail : 'Generation failed');
    },
  });

  const selected = selectedId
    ? strings.find((s) => s.id === selectedId) ?? strings[0]
    : strings[0];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, fontSize: '1rem', color: '#111827' }}>Search String</h3>
        <button
          onClick={() => generateAI.mutate()}
          disabled={generateAI.isPending}
          style={{
            padding: '0.375rem 0.75rem',
            background: '#7c3aed',
            color: '#fff',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: generateAI.isPending ? 'not-allowed' : 'pointer',
            fontSize: '0.875rem',
            opacity: generateAI.isPending ? 0.6 : 1,
          }}
        >
          {generateAI.isPending ? 'Generating…' : '✨ Generate with AI'}
        </button>
      </div>

      {generateError && (
        <p style={{ color: '#ef4444', fontSize: '0.875rem', margin: '0 0 0.75rem' }}>{generateError}</p>
      )}

      {/* Manual entry */}
      <div style={{ marginBottom: '1rem' }}>
        <textarea
          value={manualText}
          onChange={(e) => setManualText(e.target.value)}
          placeholder="Enter Boolean search string manually…"
          rows={4}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
            fontFamily: 'monospace',
            resize: 'vertical',
            boxSizing: 'border-box',
          }}
        />
        <button
          onClick={() => createManual.mutate(manualText)}
          disabled={createManual.isPending || !manualText.trim()}
          style={{
            marginTop: '0.5rem',
            padding: '0.375rem 0.75rem',
            background: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: createManual.isPending || !manualText.trim() ? 'not-allowed' : 'pointer',
            fontSize: '0.875rem',
            opacity: createManual.isPending || !manualText.trim() ? 0.6 : 1,
          }}
        >
          {createManual.isPending ? 'Saving…' : 'Save String'}
        </button>
      </div>

      {/* Version history */}
      {isLoading && <p style={{ color: '#64748b', fontSize: '0.875rem' }}>Loading…</p>}
      {strings.length > 0 && (
        <div>
          <h4 style={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}>
            Version History ({strings.length})
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {strings.map((ss) => (
              <div
                key={ss.id}
                onClick={() => setSelectedId(ss.id)}
                style={{
                  border: `1px solid ${selected?.id === ss.id ? '#2563eb' : '#e2e8f0'}`,
                  borderRadius: '0.375rem',
                  padding: '0.625rem 0.75rem',
                  cursor: 'pointer',
                  background: selected?.id === ss.id ? '#eff6ff' : '#fff',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#374151' }}>
                    v{ss.version}
                  </span>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    {ss.created_by_agent && (
                      <span style={{
                        fontSize: '0.75rem', background: '#f3e8ff', color: '#7c3aed',
                        padding: '1px 6px', borderRadius: '999px',
                      }}>
                        AI
                      </span>
                    )}
                    {ss.is_active && (
                      <span style={{
                        fontSize: '0.75rem', background: '#dcfce7', color: '#16a34a',
                        padding: '1px 6px', borderRadius: '999px',
                      }}>
                        Active
                      </span>
                    )}
                  </div>
                </div>
                <code style={{
                  display: 'block',
                  fontSize: '0.75rem',
                  color: '#1e293b',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  maxHeight: '4rem',
                  overflow: 'hidden',
                }}>
                  {ss.string_text}
                </code>
                {ss.iterations.length > 0 && (
                  <div style={{ marginTop: '0.375rem', fontSize: '0.75rem', color: '#64748b' }}>
                    {ss.iterations.length} test iteration{ss.iterations.length !== 1 ? 's' : ''} •{' '}
                    Last recall: {(ss.iterations[ss.iterations.length - 1].test_set_recall * 100).toFixed(0)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Selected string full view */}
      {selected && (
        <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#f8fafc', borderRadius: '0.5rem' }}>
          <h4 style={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}>
            v{selected.version} — Full String
          </h4>
          <code style={{
            display: 'block',
            fontSize: '0.8125rem',
            color: '#1e293b',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}>
            {selected.string_text}
          </code>
        </div>
      )}
    </div>
  );
}
