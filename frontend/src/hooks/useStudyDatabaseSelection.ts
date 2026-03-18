/**
 * TanStack Query hook for the study database selection API.
 *
 * Wraps GET /api/v1/studies/{studyId}/database-selection and
 * PUT /api/v1/studies/{studyId}/database-selection.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

/** A single database index selection item returned by the API. */
export interface DatabaseSelectionItem {
  database_index: string;
  is_enabled: boolean;
  status: 'configured' | 'not_configured' | 'unreachable';
  requires_credential: boolean;
  credential_configured: boolean;
}

/** Full database selection response from GET /studies/{id}/database-selection. */
export interface DatabaseSelectionResponse {
  study_id: number;
  selections: DatabaseSelectionItem[];
  snowball_enabled: boolean;
  scihub_enabled: boolean;
  scihub_acknowledged: boolean;
}

/** Request body for PUT /studies/{id}/database-selection. */
export interface DatabaseSelectionUpdateRequest {
  selections: Array<{ database_index: string; is_enabled: boolean }>;
  snowball_enabled: boolean;
  scihub_enabled: boolean;
  scihub_acknowledged: boolean;
}

/**
 * Returns the query key for a study's database selection.
 *
 * @param studyId - The integer study ID.
 * @returns The TanStack Query key array.
 */
export function databaseSelectionKey(studyId: number): [string, number] {
  return ['database-selection', studyId];
}

/**
 * Hook providing read/write access to a study's database index selection.
 *
 * @param studyId - The integer study ID to manage selection for.
 * @returns Object with `data`, `isLoading`, and `updateSelection` mutation.
 */
export function useStudyDatabaseSelection(studyId: number) {
  const queryClient = useQueryClient();
  const queryKey = databaseSelectionKey(studyId);

  const { data, isLoading, error } = useQuery<DatabaseSelectionResponse>({
    queryKey,
    queryFn: () =>
      api.get<DatabaseSelectionResponse>(
        `/api/v1/studies/${studyId}/database-selection`
      ),
    enabled: studyId > 0,
  });

  const updateSelection = useMutation<
    DatabaseSelectionResponse,
    Error,
    DatabaseSelectionUpdateRequest
  >({
    mutationFn: (body: DatabaseSelectionUpdateRequest) =>
      api.put<DatabaseSelectionResponse>(
        `/api/v1/studies/${studyId}/database-selection`,
        body
      ),
    onSuccess: (updated) => {
      queryClient.setQueryData(queryKey, updated);
    },
  });

  return { data, isLoading, error, updateSelection };
}
