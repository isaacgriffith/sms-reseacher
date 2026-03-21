/**
 * TanStack Query hooks for the SLR review protocol API (feature 007).
 *
 * Wraps protocol CRUD, submission, validation, and phase-gate queries.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getPhases,
  getProtocol,
  submitForReview,
  upsertProtocol,
  validateProtocol,
  type ProtocolUpsert,
  type ReviewProtocol,
  type SLRPhases,
} from '../../services/slr/protocolApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's protocol. */
export function protocolKey(studyId: number): [string, number] {
  return ['slr-protocol', studyId];
}

/** @returns TanStack Query key for a study's SLR phases. */
export function phasesKey(studyId: number): [string, number] {
  return ['slr-phases', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the current review protocol.
 *
 * Polls every 5 seconds while `status === "under_review"` so the UI
 * automatically reflects when the AI review report arrives.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the {@link ReviewProtocol}.
 */
export function useProtocol(studyId: number) {
  return useQuery<ReviewProtocol>({
    queryKey: protocolKey(studyId),
    queryFn: () => getProtocol(studyId),
    enabled: studyId > 0,
    refetchInterval: (query) => {
      const data = query.state.data;
      return data?.status === 'under_review' ? 5000 : false;
    },
    retry: (failureCount, error) => {
      // Don't retry 404 — protocol hasn't been created yet
      if ((error as { status?: number })?.status === 404) return false;
      return failureCount < 2;
    },
  });
}

/**
 * Query hook for SLR phase unlock status.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for {@link SLRPhases}.
 */
export function usePhases(studyId: number) {
  return useQuery<SLRPhases>({
    queryKey: phasesKey(studyId),
    queryFn: () => getPhases(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Mutation hook for creating or updating the draft protocol.
 *
 * Invalidates the protocol and phases queries on success.
 *
 * @returns TanStack mutation with `mutate(data)`.
 */
export function useUpsertProtocol(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<ReviewProtocol, Error, ProtocolUpsert>({
    mutationFn: (data) => upsertProtocol(studyId, data),
    onSuccess: (updated) => {
      queryClient.setQueryData(protocolKey(studyId), updated);
      queryClient.invalidateQueries({ queryKey: phasesKey(studyId) });
    },
  });
}

/**
 * Mutation hook to submit the protocol for AI review.
 *
 * Invalidates the protocol query on success so polling picks up the
 * status change to `under_review`.
 *
 * @returns TanStack mutation with `mutate()`.
 */
export function useSubmitForReview(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<{ job_id: string; status: string }, Error, void>({
    mutationFn: () => submitForReview(studyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: protocolKey(studyId) });
    },
  });
}

/**
 * Mutation hook to validate (approve) the reviewed protocol.
 *
 * Invalidates protocol and phases queries on success.
 *
 * @returns TanStack mutation with `mutate()`.
 */
export function useValidateProtocol(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<{ status: string }, Error, void>({
    mutationFn: () => validateProtocol(studyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: protocolKey(studyId) });
      queryClient.invalidateQueries({ queryKey: phasesKey(studyId) });
    },
  });
}
