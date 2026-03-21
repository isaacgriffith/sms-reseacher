/**
 * TanStack Query hooks for SLR data synthesis API (feature 007).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getSynthesisResult,
  listSynthesisResults,
  startSynthesis,
  type StartSynthesisBody,
  type SynthesisList,
  type SynthesisResult,
} from '../../services/slr/synthesisApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's synthesis result list. */
export function synthesisListKey(studyId: number): [string, number] {
  return ['slr-synthesis-list', studyId];
}

/** @returns TanStack Query key for a single synthesis result. */
export function synthesisResultKey(synthesisId: number): [string, number] {
  return ['slr-synthesis-result', synthesisId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for all synthesis results for a study.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for {@link SynthesisList}.
 */
export function useSynthesisResults(studyId: number) {
  return useQuery<SynthesisList>({
    queryKey: synthesisListKey(studyId),
    queryFn: () => listSynthesisResults(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Mutation hook to start a new synthesis run.
 *
 * Invalidates the synthesis results list query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation with `mutate(body)`.
 */
export function useStartSynthesis(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<SynthesisResult, Error, StartSynthesisBody>({
    mutationFn: (body) => startSynthesis(studyId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: synthesisListKey(studyId) });
    },
  });
}

/**
 * Query hook for a single synthesis result with polling while in-progress.
 *
 * Polls every 2 seconds while the status is "pending" or "running".
 *
 * @param synthesisId - The integer synthesis result ID.
 * @returns TanStack Query result for {@link SynthesisResult}.
 */
export function useSynthesisResult(synthesisId: number) {
  return useQuery<SynthesisResult>({
    queryKey: synthesisResultKey(synthesisId),
    queryFn: () => getSynthesisResult(synthesisId),
    enabled: synthesisId > 0,
    refetchInterval: (query) => {
      const s = query.state.data?.status;
      return s === 'running' || s === 'pending' ? 2000 : false;
    },
  });
}
