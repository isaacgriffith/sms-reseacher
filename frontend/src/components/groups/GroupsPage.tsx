/**
 * Groups page: lists user's research groups and allows creating a new one.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '../../services/api';
import GroupCard, { GroupSummary } from './GroupCard';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';

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

  if (isLoading) return <Typography>Loading groups…</Typography>;
  if (error) return <Typography sx={{ color: 'red' }}>Failed to load groups.</Typography>;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <Typography variant="h5" sx={{ margin: 0 }}>Research Groups</Typography>
        <Button
          variant="contained"
          onClick={() => setShowCreate((v) => !v)}
          sx={{ padding: '0.5rem 1rem' }}
        >
          {showCreate ? 'Cancel' : 'New Group'}
        </Button>
      </Box>

      {showCreate && (
        <Box
          component="form"
          onSubmit={handleCreate}
          sx={{
            display: 'flex',
            gap: '0.75rem',
            alignItems: 'center',
            marginBottom: '1.5rem',
            padding: '1rem',
            background: '#f8fafc',
            borderRadius: '0.5rem',
          }}
        >
          <TextField
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            placeholder="Group name"
            size="small"
            sx={{ flex: 1 }}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={createMutation.isPending}
            sx={{
              padding: '0.5rem 1rem',
              background: '#16a34a',
              '&:hover': { background: '#15803d' },
            }}
          >
            {createMutation.isPending ? 'Creating…' : 'Create'}
          </Button>
          {createError && <Typography component="span" sx={{ color: 'red', fontSize: '0.875rem' }}>{createError}</Typography>}
        </Box>
      )}

      {groups && groups.length === 0 ? (
        <Typography sx={{ color: '#475569' }}>You are not a member of any research groups yet.</Typography>
      ) : (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
            gap: '1rem',
          }}
        >
          {groups?.map((g) => (
            <GroupCard key={g.id} group={g} />
          ))}
        </Box>
      )}
    </Box>
  );
}
