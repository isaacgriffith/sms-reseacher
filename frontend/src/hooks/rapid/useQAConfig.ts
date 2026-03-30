/**
 * TanStack Query hooks for Rapid Review quality appraisal configuration (feature 008).
 *
 * Provides query and mutation hooks for getting and setting the quality
 * appraisal mode, with threat list cache updates on success.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getQualityConfig,
  setQualityConfig,
  type QAMode,
  type QualityConfigResponse,
} from '../../services/rapid/qualityApi';
import { rrThreatsKey } from './useRRProtocol';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's RR quality config. */
export function rrQualityConfigKey(studyId: number): [string, number] {
  return ['rr-quality-config', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the Rapid Review quality appraisal configuration.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the {@link QualityConfigResponse}.
 */
export function useQualityConfig(studyId: number) {
  return useQuery<QualityConfigResponse>({
    queryKey: rrQualityConfigKey(studyId),
    queryFn: () => getQualityConfig(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Mutation hook for setting the quality appraisal mode.
 *
 * On success, invalidates both the quality config query and the threats
 * query so all consumers reflect the updated state.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation object.
 */
export function useSetQAMode(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<QualityConfigResponse, Error, { mode: QAMode }>({
    mutationFn: ({ mode }) => setQualityConfig(studyId, mode),
    onSuccess: (data) => {
      queryClient.setQueryData(rrQualityConfigKey(studyId), data);
      queryClient.setQueryData(rrThreatsKey(studyId), data.threats);
    },
  });
}
