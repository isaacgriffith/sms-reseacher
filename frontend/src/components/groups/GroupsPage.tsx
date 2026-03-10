/**
 * Groups page: lists user's research groups and allows creating a new one.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';
import GroupCard, { GroupSummary } from './GroupCard';

export default function GroupsPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [createError, setCreateError] = useState<string | null>(null);

  const { data: groups, isLoading, error } = useQuery<GroupSummary[]>({
    queryKey: ['groups'],
    queryFn: () => api.get<GroupSummary[]>('/api/v1/groups'),
  });

  const createMutation = useMutation({
    mutationFn: (name: string) =>
      api.post<{ id: number; name: string }>('/api/v1/groups', { name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      setShowCreate(false);
      setNewGroupName('');
      setCreateError(null);
    },
    onError: (err) => {
      setCreateError(err instanceof ApiError ? err.detail : 'Failed to create group');
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (newGroupName.trim()) {
      createMutation.mutate(newGroupName.trim());
    }
  };

  if (isLoading) return <p>Loading groups…</p>;
  if (error) return <p style={{ color: 'red' }}>Failed to load groups.</p>;

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <h2 style={{ margin: 0 }}>Research Groups</h2>
        <button
          onClick={() => setShowCreate((v) => !v)}
          style={{
            padding: '0.5rem 1rem',
            background: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer',
          }}
        >
          {showCreate ? 'Cancel' : 'New Group'}
        </button>
      </div>

      {showCreate && (
        <form
          onSubmit={handleCreate}
          style={{
            display: 'flex',
            gap: '0.75rem',
            alignItems: 'center',
            marginBottom: '1.5rem',
            padding: '1rem',
            background: '#f8fafc',
            borderRadius: '0.5rem',
          }}
        >
          <input
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            placeholder="Group name"
            style={{ flex: 1, padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #cbd5e1' }}
          />
          <button
            type="submit"
            disabled={createMutation.isPending}
            style={{
              padding: '0.5rem 1rem',
              background: '#16a34a',
              color: '#fff',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: createMutation.isPending ? 'not-allowed' : 'pointer',
            }}
          >
            {createMutation.isPending ? 'Creating…' : 'Create'}
          </button>
          {createError && <span style={{ color: 'red', fontSize: '0.875rem' }}>{createError}</span>}
        </form>
      )}

      {groups && groups.length === 0 ? (
        <p style={{ color: '#475569' }}>You are not a member of any research groups yet.</p>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
            gap: '1rem',
          }}
        >
          {groups?.map((g) => (
            <GroupCard key={g.id} group={g} />
          ))}
        </div>
      )}
    </div>
  );
}
