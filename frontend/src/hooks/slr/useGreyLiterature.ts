/**
 * TanStack Query hooks for SLR grey literature API (feature 007, Phase 8).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  addGreyLiteratureSource,
  deleteGreyLiteratureSource,
  listGreyLiterature,
  type CreateGreyLiteratureBody,
  type GreyLiteratureList,
  type GreyLiteratureSource,
} from '../../services/slr/greyLiteratureApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's grey literature sources. */
export function greyLiteratureKey(studyId: number): [string, number] {
  return ['slr-grey-literature', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for all grey literature sources for a study.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for {@link GreyLiteratureList}.
 */
export function useGreyLiterature(studyId: number) {
  return useQuery<GreyLiteratureList>({
    queryKey: greyLiteratureKey(studyId),
    queryFn: () => listGreyLiterature(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Mutation hook to add a grey literature source.
 *
 * Invalidates the grey literature list query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation with `mutate(body)`.
 */
export function useAddSource(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<GreyLiteratureSource, Error, CreateGreyLiteratureBody>({
    mutationFn: (body) => addGreyLiteratureSource(studyId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: greyLiteratureKey(studyId) });
    },
  });
}

/**
 * Mutation hook to delete a grey literature source by ID.
 *
 * Invalidates the grey literature list query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation with `mutate(sourceId)`.
 */
export function useDeleteSource(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: (sourceId) => deleteGreyLiteratureSource(studyId, sourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: greyLiteratureKey(studyId) });
    },
  });
}
