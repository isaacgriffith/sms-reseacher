/**
 * TanStack Query hooks for the Tertiary Study extraction API (feature 009).
 *
 * Wraps extraction list (GET), update (PUT), and AI-assist trigger (POST).
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listExtractions,
  triggerAiAssist,
  updateExtraction,
  type AiAssistResponse,
  type TertiaryExtraction,
  type TertiaryExtractionUpdate,
} from '../../services/tertiary/extractionApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's extraction list. */
export function extractionsKey(studyId: number): [string, number] {
  return ['tertiary-extractions', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the list of extraction records for a Tertiary Study.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for {@link TertiaryExtraction}[].
 */
export function useExtractions(studyId: number) {
  return useQuery<TertiaryExtraction[]>({
    queryKey: extractionsKey(studyId),
    queryFn: () => listExtractions(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Mutation hook to update a single extraction record.
 *
 * Invalidates the extractions list on success.
 *
 * @param studyId - The Tertiary Study ID.
 * @returns TanStack mutation with `mutate({ extractionId, data })`.
 */
export function useUpdateExtraction(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<
    TertiaryExtraction,
    Error,
    { extractionId: number; data: TertiaryExtractionUpdate }
  >({
    mutationFn: ({ extractionId, data }) => updateExtraction(studyId, extractionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: extractionsKey(studyId) });
    },
  });
}

/**
 * Mutation hook to trigger AI-assisted extraction pre-fill.
 *
 * Refetches extractions list after a short delay to pick up ai_complete records.
 *
 * @param studyId - The Tertiary Study ID.
 * @returns TanStack mutation with `mutate()`.
 */
export function useAiAssist(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<AiAssistResponse, Error, void>({
    mutationFn: () => triggerAiAssist(studyId),
    onSuccess: () => {
      // Poll for updated statuses after the job is enqueued.
      queryClient.invalidateQueries({ queryKey: extractionsKey(studyId) });
    },
  });
}
