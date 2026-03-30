/**
 * TanStack Query hooks for the Rapid Review stakeholder API (feature 008).
 *
 * Wraps stakeholder CRUD with optimistic updates.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createStakeholder,
  deleteStakeholder,
  listStakeholders,
  updateStakeholder,
  type Stakeholder,
  type StakeholderCreate,
  type StakeholderUpdate,
} from '../../services/rapid/stakeholdersApi';
import { rrProtocolKey } from './useRRProtocol';

// ---------------------------------------------------------------------------
// Query key
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's stakeholder list. */
export function stakeholdersKey(studyId: number): [string, number] {
  return ['rr-stakeholders', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the practitioner stakeholder list.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the list of {@link Stakeholder} objects.
 */
export function useStakeholders(studyId: number) {
  return useQuery<Stakeholder[]>({
    queryKey: stakeholdersKey(studyId),
    queryFn: () => listStakeholders(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Mutation hook for creating a practitioner stakeholder.
 *
 * Invalidates the stakeholder list on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation object.
 */
export function useCreateStakeholder(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<Stakeholder, Error, StakeholderCreate>({
    mutationFn: (data) => createStakeholder(studyId, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: stakeholdersKey(studyId) });
    },
  });
}

/**
 * Mutation hook for updating a practitioner stakeholder.
 *
 * Optimistically updates the local cache, then invalidates on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation object.
 */
export function useUpdateStakeholder(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<Stakeholder, Error, { id: number; data: StakeholderUpdate }>({
    mutationFn: ({ id, data }) => updateStakeholder(studyId, id, data),
    onSuccess: (updated) => {
      queryClient.setQueryData<Stakeholder[]>(stakeholdersKey(studyId), (prev) =>
        prev ? prev.map((s) => (s.id === updated.id ? updated : s)) : [updated],
      );
    },
  });
}

/**
 * Mutation hook for deleting a practitioner stakeholder.
 *
 * Optimistically removes from the cache, then invalidates protocol query
 * on success (deletion of last stakeholder may reset protocol status).
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation object.
 */
export function useDeleteStakeholder(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: (id) => deleteStakeholder(studyId, id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: stakeholdersKey(studyId) });
      const previous = queryClient.getQueryData<Stakeholder[]>(stakeholdersKey(studyId));
      queryClient.setQueryData<Stakeholder[]>(
        stakeholdersKey(studyId),
        (prev) => prev?.filter((s) => s.id !== id) ?? [],
      );
      return { previous };
    },
    onError: (_err, _id, context) => {
      const ctx = context as { previous?: Stakeholder[] } | undefined;
      if (ctx?.previous) {
        queryClient.setQueryData(stakeholdersKey(studyId), ctx.previous);
      }
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: rrProtocolKey(studyId) });
      void queryClient.invalidateQueries({ queryKey: stakeholdersKey(studyId) });
    },
  });
}
