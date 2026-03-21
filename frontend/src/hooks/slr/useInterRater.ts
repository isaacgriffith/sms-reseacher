/**
 * TanStack Query hooks for SLR inter-rater agreement API (feature 007).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  computeKappa,
  getInterRaterRecords,
  recordPostDiscussionKappa,
  type ComputeKappaBody,
  type InterRaterList,
  type InterRaterRecord,
} from '../../services/slr/interRaterApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's inter-rater records. */
export function interRaterKey(studyId: number): [string, number] {
  return ['slr-inter-rater', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for all inter-rater agreement records for a study.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for {@link InterRaterList}.
 */
export function useInterRaterRecords(studyId: number) {
  return useQuery<InterRaterList>({
    queryKey: interRaterKey(studyId),
    queryFn: () => getInterRaterRecords(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Mutation hook to compute pre-discussion Kappa.
 *
 * Invalidates the inter-rater records query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation with `mutate(body)`.
 */
export function useComputeKappa(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<InterRaterRecord, Error, ComputeKappaBody>({
    mutationFn: (body) => computeKappa(studyId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: interRaterKey(studyId) });
    },
  });
}

/**
 * Mutation hook to record post-discussion Kappa.
 *
 * Invalidates the inter-rater records query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation with `mutate(body)`.
 */
export function usePostDiscussionKappa(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<InterRaterRecord, Error, ComputeKappaBody>({
    mutationFn: (body) => recordPostDiscussionKappa(studyId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: interRaterKey(studyId) });
    },
  });
}
