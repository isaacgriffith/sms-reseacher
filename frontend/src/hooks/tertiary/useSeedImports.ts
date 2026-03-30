/**
 * TanStack Query hooks for the Tertiary Study seed-import API (feature 009).
 *
 * Wraps seed import list (GET) and create (POST) operations.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createSeedImport,
  listGroupStudies,
  listSeedImports,
  type SeedImportCreated,
  type SeedImportSummary,
  type StudySummary,
} from '../../services/tertiary/seedImportApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's seed import list. */
export function seedImportsKey(studyId: number): [string, number] {
  return ['tertiary-seed-imports', studyId];
}

/** @returns TanStack Query key for a group's study list. */
export function groupStudiesKey(groupId: number): [string, number] {
  return ['group-studies', groupId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the list of seed imports for a Tertiary Study.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for {@link SeedImportSummary}[].
 */
export function useSeedImports(studyId: number) {
  return useQuery<SeedImportSummary[]>({
    queryKey: seedImportsKey(studyId),
    queryFn: () => listSeedImports(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Query hook for available platform studies in a group (import sources).
 *
 * @param groupId - The research group ID. Pass 0 to disable.
 * @returns TanStack Query result for {@link StudySummary}[].
 */
export function useGroupStudies(groupId: number) {
  return useQuery<StudySummary[]>({
    queryKey: groupStudiesKey(groupId),
    queryFn: () => listGroupStudies(groupId),
    enabled: groupId > 0,
  });
}

/**
 * Mutation hook to trigger a seed import from a source study.
 *
 * Invalidates the seed imports list on success.
 *
 * @param studyId - The target Tertiary Study ID.
 * @returns TanStack mutation with `mutate(sourceStudyId)`.
 */
export function useCreateSeedImport(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<SeedImportCreated, Error, number>({
    mutationFn: (sourceStudyId) => createSeedImport(studyId, sourceStudyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seedImportsKey(studyId) });
    },
  });
}
