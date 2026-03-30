/**
 * TanStack Query hooks for the Rapid Review narrative synthesis API (feature 008).
 *
 * Includes polling when any section has an active AI draft job in progress.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  completeSynthesis,
  listSections,
  requestAIDraft,
  updateSection,
  type NarrativeSection,
  type SectionUpdate,
  type SynthesisCompleteResponse,
  type AIDraftResponse,
} from '../../services/rapid/synthesisApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's synthesis sections. */
export function rrSynthesisSectionsKey(studyId: number): [string, number] {
  return ['rr-synthesis-sections', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for all narrative synthesis sections for a study.
 *
 * Polls every 3 seconds when any section has an active AI draft job
 * (i.e., {@link NarrativeSection.ai_draft_job_id} is non-null).
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the section list.
 */
export function useNarrativeSections(studyId: number) {
  return useQuery<NarrativeSection[]>({
    queryKey: rrSynthesisSectionsKey(studyId),
    queryFn: () => listSections(studyId),
    enabled: studyId > 0,
    refetchInterval: (query) => {
      const sections = query.state.data;
      if (!sections) return false;
      const anyActive = sections.some((s) => s.ai_draft_job_id !== null);
      return anyActive ? 3000 : false;
    },
  });
}

/**
 * Mutation hook for updating a synthesis section's text or completion status.
 *
 * Invalidates the section list query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation object.
 */
export function useUpdateSection(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<NarrativeSection, Error, { sectionId: number; data: SectionUpdate }>({
    mutationFn: ({ sectionId, data }) => updateSection(studyId, sectionId, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: rrSynthesisSectionsKey(studyId) });
    },
  });
}

/**
 * Mutation hook for requesting an AI draft for a synthesis section.
 *
 * Triggers immediate refetch of the section list on success so polling
 * starts as soon as the job is enqueued.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation object.
 */
export function useRequestAIDraft(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<AIDraftResponse, Error, number>({
    mutationFn: (sectionId) => requestAIDraft(studyId, sectionId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: rrSynthesisSectionsKey(studyId) });
    },
  });
}

/**
 * Mutation hook for finalising synthesis.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation object.
 */
export function useCompleteSynthesis(studyId: number) {
  return useMutation<SynthesisCompleteResponse, Error, void>({
    mutationFn: () => completeSynthesis(studyId),
  });
}
