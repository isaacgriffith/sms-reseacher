/**
 * TanStack Query hooks for the SLR quality assessment API (feature 007).
 *
 * Wraps checklist CRUD and score submission/retrieval queries.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getChecklist,
  getQualityScores,
  submitQualityScores,
  upsertChecklist,
  type Checklist,
  type ChecklistUpsert,
  type QualityScores,
  type SubmitScores,
} from '../../services/slr/qualityApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's quality assessment checklist. */
export function checklistKey(studyId: number): [string, number] {
  return ['slr-quality-checklist', studyId];
}

/** @returns TanStack Query key for a candidate paper's quality scores. */
export function qualityScoresKey(candidatePaperId: number): [string, number] {
  return ['slr-quality-scores', candidatePaperId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the quality assessment checklist of a study.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the {@link Checklist}.
 */
export function useChecklist(studyId: number) {
  return useQuery<Checklist>({
    queryKey: checklistKey(studyId),
    queryFn: () => getChecklist(studyId),
    enabled: studyId > 0,
    retry: (failureCount, error) => {
      if ((error as { status?: number })?.status === 404) return false;
      return failureCount < 2;
    },
  });
}

/**
 * Query hook for all quality assessment scores on a candidate paper.
 *
 * @param candidatePaperId - The integer candidate paper ID.
 * @returns TanStack Query result for {@link QualityScores}.
 */
export function useQualityScores(candidatePaperId: number) {
  return useQuery<QualityScores>({
    queryKey: qualityScoresKey(candidatePaperId),
    queryFn: () => getQualityScores(candidatePaperId),
    enabled: candidatePaperId > 0,
  });
}

/**
 * Mutation hook for creating or replacing the study's quality checklist.
 *
 * Invalidates the checklist query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation with `mutate(data)`.
 */
export function useUpsertChecklist(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<Checklist, Error, ChecklistUpsert>({
    mutationFn: (data) => upsertChecklist(studyId, data),
    onSuccess: (updated) => {
      queryClient.setQueryData(checklistKey(studyId), updated);
    },
  });
}

/**
 * Mutation hook for submitting quality assessment scores for a paper.
 *
 * Invalidates the quality-scores query on success so the UI reflects the
 * latest submitted scores.
 *
 * @param candidatePaperId - The integer candidate paper ID.
 * @returns TanStack mutation with `mutate(data)`.
 */
export function useSubmitScores(candidatePaperId: number) {
  const queryClient = useQueryClient();
  return useMutation<QualityScores, Error, SubmitScores>({
    mutationFn: (data) => submitQualityScores(candidatePaperId, data),
    onSuccess: (updated) => {
      queryClient.setQueryData(qualityScoresKey(candidatePaperId), updated);
    },
  });
}
