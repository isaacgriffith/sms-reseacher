/**
 * CriteriaForm: add/remove inclusion and exclusion criteria with reorder support.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';

interface Criterion {
  id: number;
  study_id: number;
  description: string;
  order_index: number;
}

interface CriteriaFormProps {
  studyId: number;
}

function CriterionList({
  title,
  items,
  onAdd,
  onDelete,
  onMoveUp,
  onMoveDown,
  isAdding,
}: {
  title: string;
  items: Criterion[];
  onAdd: (description: string) => void;
  onDelete: (id: number) => void;
  onMoveUp: (index: number) => void;
  onMoveDown: (index: number) => void;
  isAdding: boolean;
}) {
  const [newText, setNewText] = useState('');

  const handleAdd = () => {
    const trimmed = newText.trim();
    if (!trimmed) return;
    onAdd(trimmed);
    setNewText('');
  };

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <h4 style={{ margin: '0 0 0.75rem', fontSize: '0.9375rem', color: '#374151' }}>{title}</h4>

      <ol style={{ margin: '0 0 0.75rem', paddingLeft: '1.5rem' }}>
        {items.map((item, idx) => (
          <li
            key={item.id}
            style={{
              marginBottom: '0.5rem',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.5rem',
            }}
          >
            <span style={{ flex: 1, fontSize: '0.875rem', color: '#374151', paddingTop: '2px' }}>
              {item.description}
            </span>
            <div style={{ display: 'flex', gap: '0.25rem', flexShrink: 0 }}>
              <button
                onClick={() => onMoveUp(idx)}
                disabled={idx === 0}
                title="Move up"
                style={reorderBtnStyle(idx === 0)}
              >
                ↑
              </button>
              <button
                onClick={() => onMoveDown(idx)}
                disabled={idx === items.length - 1}
                title="Move down"
                style={reorderBtnStyle(idx === items.length - 1)}
              >
                ↓
              </button>
              <button
                onClick={() => onDelete(item.id)}
                title="Remove"
                style={{
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#ef4444',
                  fontSize: '0.875rem',
                  padding: '0 4px',
                }}
              >
                ✕
              </button>
            </div>
          </li>
        ))}
        {items.length === 0 && (
          <li style={{ fontSize: '0.875rem', color: '#9ca3af', listStyle: 'none', marginLeft: '-1.5rem' }}>
            No criteria added yet.
          </li>
        )}
      </ol>

      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          value={newText}
          onChange={(e) => setNewText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
          placeholder="Add criterion…"
          style={{
            flex: 1,
            padding: '0.375rem 0.625rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
          }}
        />
        <button
          onClick={handleAdd}
          disabled={isAdding || !newText.trim()}
          style={{
            padding: '0.375rem 0.75rem',
            background: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: isAdding || !newText.trim() ? 'not-allowed' : 'pointer',
            fontSize: '0.875rem',
            opacity: isAdding || !newText.trim() ? 0.6 : 1,
          }}
        >
          Add
        </button>
      </div>
    </div>
  );
}

function reorderBtnStyle(disabled: boolean) {
  return {
    background: 'transparent',
    border: '1px solid #d1d5db',
    borderRadius: '0.25rem',
    cursor: disabled ? 'not-allowed' : 'pointer',
    color: disabled ? '#9ca3af' : '#374151',
    fontSize: '0.75rem',
    padding: '0 4px',
    opacity: disabled ? 0.5 : 1,
  } as const;
}

export default function CriteriaForm({ studyId }: CriteriaFormProps) {
  const qc = useQueryClient();

  const { data: inclusion = [] } = useQuery<Criterion[]>({
    queryKey: ['criteria', studyId, 'inclusion'],
    queryFn: () => api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/inclusion`),
  });

  const { data: exclusion = [] } = useQuery<Criterion[]>({
    queryKey: ['criteria', studyId, 'exclusion'],
    queryFn: () => api.get<Criterion[]>(`/api/v1/studies/${studyId}/criteria/exclusion`),
  });

  const addInclusion = useMutation({
    mutationFn: (description: string) =>
      api.post<Criterion>(`/api/v1/studies/${studyId}/criteria/inclusion`, {
        description,
        order_index: inclusion.length,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['criteria', studyId, 'inclusion'] }),
  });

  const addExclusion = useMutation({
    mutationFn: (description: string) =>
      api.post<Criterion>(`/api/v1/studies/${studyId}/criteria/exclusion`, {
        description,
        order_index: exclusion.length,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['criteria', studyId, 'exclusion'] }),
  });

  const deleteInclusion = useMutation({
    mutationFn: (id: number) =>
      api.delete<void>(`/api/v1/studies/${studyId}/criteria/inclusion/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['criteria', studyId, 'inclusion'] }),
  });

  const deleteExclusion = useMutation({
    mutationFn: (id: number) =>
      api.delete<void>(`/api/v1/studies/${studyId}/criteria/exclusion/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['criteria', studyId, 'exclusion'] }),
  });

  // Reorder helpers — optimistic local reorder (no server-side order endpoint needed)
  const [incOrder, setIncOrder] = useState<number[] | null>(null);
  const [excOrder, setExcOrder] = useState<number[] | null>(null);

  const sortedInclusion = incOrder
    ? [...inclusion].sort((a, b) => incOrder.indexOf(a.id) - incOrder.indexOf(b.id))
    : [...inclusion].sort((a, b) => a.order_index - b.order_index);

  const sortedExclusion = excOrder
    ? [...exclusion].sort((a, b) => excOrder.indexOf(a.id) - excOrder.indexOf(b.id))
    : [...exclusion].sort((a, b) => a.order_index - b.order_index);

  const moveInc = (idx: number, dir: -1 | 1) => {
    const ordered = sortedInclusion.map((c) => c.id);
    const swapIdx = idx + dir;
    [ordered[idx], ordered[swapIdx]] = [ordered[swapIdx], ordered[idx]];
    setIncOrder(ordered);
  };

  const moveExc = (idx: number, dir: -1 | 1) => {
    const ordered = sortedExclusion.map((c) => c.id);
    const swapIdx = idx + dir;
    [ordered[idx], ordered[swapIdx]] = [ordered[swapIdx], ordered[idx]];
    setExcOrder(ordered);
  };

  return (
    <div>
      <h3 style={{ margin: '0 0 1rem', fontSize: '1rem', color: '#111827' }}>
        Inclusion / Exclusion Criteria
      </h3>

      <CriterionList
        title="Inclusion Criteria"
        items={sortedInclusion}
        onAdd={(desc) => addInclusion.mutate(desc)}
        onDelete={(id) => deleteInclusion.mutate(id)}
        onMoveUp={(idx) => moveInc(idx, -1)}
        onMoveDown={(idx) => moveInc(idx, 1)}
        isAdding={addInclusion.isPending}
      />

      <CriterionList
        title="Exclusion Criteria"
        items={sortedExclusion}
        onAdd={(desc) => addExclusion.mutate(desc)}
        onDelete={(id) => deleteExclusion.mutate(id)}
        onMoveUp={(idx) => moveExc(idx, -1)}
        onMoveDown={(idx) => moveExc(idx, 1)}
        isAdding={addExclusion.isPending}
      />
    </div>
  );
}
