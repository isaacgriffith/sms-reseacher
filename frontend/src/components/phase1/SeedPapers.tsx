/**
 * Seed papers management: add/remove by DOI or manual entry,
 * trigger Librarian agent, display suggestions.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';

interface PaperRef {
  id: number;
  title: string;
  doi: string | null;
  authors: unknown[] | null;
  year: number | null;
  venue: string | null;
}

interface SeedPaperItem {
  id: number;
  paper: PaperRef;
  added_by: string;
}

interface SuggestedPaper {
  title: string;
  authors: string[];
  year: number | null;
  venue: string | null;
  doi: string | null;
  rationale: string;
}

interface Props {
  studyId: number;
}

export default function SeedPapers({ studyId }: Props) {
  const queryClient = useQueryClient();
  const [doi, setDoi] = useState('');
  const [manualTitle, setManualTitle] = useState('');
  const [suggestions, setSuggestions] = useState<SuggestedPaper[] | null>(null);
  const [librarianLoading, setLibrarianLoading] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  const { data: seeds, isLoading } = useQuery<SeedPaperItem[]>({
    queryKey: ['seeds', studyId],
    queryFn: () => api.get<SeedPaperItem[]>(`/api/v1/studies/${studyId}/seeds/papers`),
  });

  const addMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api.post<SeedPaperItem>(`/api/v1/studies/${studyId}/seeds/papers`, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seeds', studyId] });
      setDoi('');
      setManualTitle('');
      setAddError(null);
    },
    onError: () => setAddError('Failed to add paper'),
  });

  const deleteMutation = useMutation({
    mutationFn: (seedId: number) =>
      api.delete<void>(`/api/v1/studies/${studyId}/seeds/papers/${seedId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['seeds', studyId] }),
  });

  const handleAddDoi = () => {
    if (!doi.trim()) return;
    addMutation.mutate({ doi: doi.trim() });
  };

  const handleAddManual = () => {
    if (!manualTitle.trim()) return;
    addMutation.mutate({ title: manualTitle.trim() });
  };

  const handleLibrarian = async () => {
    setLibrarianLoading(true);
    setSuggestions(null);
    try {
      const result = await api.post<{ suggestions: { papers: SuggestedPaper[] } }>(
        `/api/v1/studies/${studyId}/seeds/librarian`,
        {},
      );
      setSuggestions(result.suggestions.papers);
    } catch {
      setSuggestions([]);
    } finally {
      setLibrarianLoading(false);
    }
  };

  return (
    <div>
      <h3 style={{ margin: '0 0 1rem' }}>Seed Papers</h3>

      {/* Add by DOI */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <input
          value={doi}
          onChange={(e) => setDoi(e.target.value)}
          placeholder="DOI (e.g. 10.1145/1234)"
          style={{ flex: 1, padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}
          onKeyDown={(e) => e.key === 'Enter' && handleAddDoi()}
        />
        <button
          onClick={handleAddDoi}
          disabled={addMutation.isPending}
          style={{ padding: '0.5rem 1rem', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer', whiteSpace: 'nowrap' }}
        >
          Add by DOI
        </button>
      </div>

      {/* Add manually */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          value={manualTitle}
          onChange={(e) => setManualTitle(e.target.value)}
          placeholder="Paper title (manual entry)"
          style={{ flex: 1, padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}
          onKeyDown={(e) => e.key === 'Enter' && handleAddManual()}
        />
        <button
          onClick={handleAddManual}
          disabled={addMutation.isPending}
          style={{ padding: '0.5rem 1rem', background: '#475569', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer', whiteSpace: 'nowrap' }}
        >
          Add Manually
        </button>
      </div>

      {addError && <p style={{ color: 'red', fontSize: '0.875rem', marginBottom: '0.75rem' }}>{addError}</p>}

      {/* Librarian trigger */}
      <button
        onClick={handleLibrarian}
        disabled={librarianLoading}
        style={{
          marginBottom: '1.5rem',
          padding: '0.5rem 1rem',
          background: librarianLoading ? '#94a3b8' : '#7c3aed',
          color: '#fff',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: librarianLoading ? 'not-allowed' : 'pointer',
        }}
      >
        {librarianLoading ? '🔍 Searching…' : '🤖 Suggest with Librarian AI'}
      </button>

      {/* Librarian suggestions */}
      {suggestions !== null && (
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#f5f3ff', borderRadius: '0.5rem' }}>
          <h4 style={{ margin: '0 0 0.75rem', color: '#6d28d9' }}>Librarian Suggestions</h4>
          {suggestions.length === 0 ? (
            <p style={{ color: '#64748b', fontSize: '0.875rem' }}>No suggestions available.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {suggestions.map((p, i) => (
                <li key={i} style={{ marginBottom: '0.75rem', paddingBottom: '0.75rem', borderBottom: i < suggestions.length - 1 ? '1px solid #ddd6fe' : 'none' }}>
                  <p style={{ margin: '0 0 0.25rem', fontWeight: 500, fontSize: '0.875rem' }}>{p.title}</p>
                  <p style={{ margin: '0 0 0.125rem', color: '#64748b', fontSize: '0.8125rem' }}>
                    {p.authors.join(', ')} {p.year ? `(${p.year})` : ''} {p.venue ? `— ${p.venue}` : ''}
                  </p>
                  <p style={{ margin: '0 0 0.25rem', color: '#4b5563', fontSize: '0.8125rem', fontStyle: 'italic' }}>{p.rationale}</p>
                  <button
                    onClick={() => addMutation.mutate(p.doi ? { doi: p.doi } : { title: p.title, authors: p.authors, year: p.year, venue: p.venue })}
                    style={{ padding: '0.2rem 0.625rem', background: '#7c3aed', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontSize: '0.75rem' }}
                  >
                    + Add as Seed
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Current seeds list */}
      <h4 style={{ margin: '0 0 0.75rem' }}>Added Seeds ({seeds?.length ?? 0})</h4>
      {isLoading ? (
        <p>Loading…</p>
      ) : !seeds || seeds.length === 0 ? (
        <p style={{ color: '#64748b', fontSize: '0.875rem' }}>No seed papers yet.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {seeds.map((s) => (
            <li
              key={s.id}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                padding: '0.625rem 0',
                borderBottom: '1px solid #e2e8f0',
              }}
            >
              <div>
                <p style={{ margin: '0 0 0.125rem', fontWeight: 500, fontSize: '0.875rem' }}>{s.paper.title}</p>
                <p style={{ margin: 0, color: '#64748b', fontSize: '0.8125rem' }}>
                  {s.paper.doi ?? 'No DOI'} · Added by {s.added_by}
                </p>
              </div>
              <button
                onClick={() => deleteMutation.mutate(s.id)}
                style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer', flexShrink: 0, marginLeft: '0.5rem' }}
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
