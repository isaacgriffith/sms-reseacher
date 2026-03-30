/**
 * TanStack Query hooks for the Tertiary Study protocol API (feature 009).
 *
 * Wraps protocol GET, PUT (update), and POST (validate) operations.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getProtocol,
  updateProtocol,
  validateProtocol,
  type TertiaryProtocol,
  type TertiaryProtocolUpdate,
} from '../../services/tertiary/protocolApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's Tertiary protocol. */
export function tertiaryProtocolKey(studyId: number): [string, number] {
  return ['tertiary-protocol', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the Tertiary Study protocol.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the {@link TertiaryProtocol}.
 */
export function useTertiaryProtocol(studyId: number) {
  return useQuery<TertiaryProtocol>({
    queryKey: tertiaryProtocolKey(studyId),
    queryFn: () => getProtocol(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Mutation hook for updating the Tertiary Study protocol.
 *
 * Invalidates the protocol query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation with `mutate(data)`.
 */
export function useUpdateTertiaryProtocol(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<TertiaryProtocol, Error, TertiaryProtocolUpdate>({
    mutationFn: (data) => updateProtocol(studyId, data),
    onSuccess: (updated) => {
      queryClient.setQueryData(tertiaryProtocolKey(studyId), updated);
    },
  });
}

/**
 * Mutation hook to validate (approve) the Tertiary Study protocol.
 *
 * Invalidates the protocol query on success so the status change is reflected.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation with `mutate()`.
 */
export function useValidateTertiaryProtocol(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<{ job_id: string; status: string }, Error, void>({
    mutationFn: () => validateProtocol(studyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tertiaryProtocolKey(studyId) });
    },
  });
}
