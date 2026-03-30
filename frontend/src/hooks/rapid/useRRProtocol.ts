/**
 * TanStack Query hooks for the Rapid Review protocol API (feature 008).
 *
 * Wraps protocol CRUD, validation, and threat queries.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import {
  getProtocol,
  getThreats,
  updateProtocol,
  validateProtocol,
  type RRProtocol,
  type RRProtocolUpdate,
  type Threat,
} from '../../services/rapid/protocolApi';
import { ApiError } from '../../services/api';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for a study's RR protocol. */
export function rrProtocolKey(studyId: number): [string, number] {
  return ['rr-protocol', studyId];
}

/** @returns TanStack Query key for a study's RR threats. */
export function rrThreatsKey(studyId: number): [string, number] {
  return ['rr-threats', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the current Rapid Review protocol.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the {@link RRProtocol}.
 */
export function useRRProtocol(studyId: number) {
  return useQuery<RRProtocol>({
    queryKey: rrProtocolKey(studyId),
    queryFn: () => getProtocol(studyId),
    enabled: studyId > 0,
  });
}

/**
 * Query hook for threats-to-validity for a Rapid Review study.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack Query result for the list of {@link Threat} objects.
 */
export function useRRThreats(studyId: number) {
  return useQuery<Threat[]>({
    queryKey: rrThreatsKey(studyId),
    queryFn: () => getThreats(studyId),
    enabled: studyId > 0,
  });
}

/** State returned by {@link useUpdateRRProtocol} when a 409 is received. */
export interface InvalidationPending {
  papersAtRisk: number;
  pendingData: RRProtocolUpdate;
}

/**
 * Mutation hook for updating the Rapid Review protocol.
 *
 * Handles 409 Conflict (invalidation acknowledgment) by storing the
 * pending payload in local state; callers can detect this and show a
 * confirmation dialog, then call {@link confirmInvalidation}.
 *
 * @param studyId - The integer study ID.
 * @returns Mutation object plus acknowledgment helpers.
 */
export function useUpdateRRProtocol(studyId: number) {
  const queryClient = useQueryClient();
  const [invalidationPending, setInvalidationPending] = useState<InvalidationPending | null>(null);

  const mutation = useMutation<RRProtocol, Error, RRProtocolUpdate>({
    mutationFn: (data) => updateProtocol(studyId, data, false),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: rrProtocolKey(studyId) });
    },
    onError: (error, variables) => {
      if (error instanceof ApiError && error.status === 409) {
        let papersAtRisk = 0;
        try {
          const detail = JSON.parse(error.detail) as { papers_at_risk?: number };
          papersAtRisk = detail.papers_at_risk ?? 0;
        } catch {
          // ignore parse failures
        }
        setInvalidationPending({ papersAtRisk, pendingData: variables });
      }
    },
  });

  const confirmMutation = useMutation<RRProtocol, Error, RRProtocolUpdate>({
    mutationFn: (data) => updateProtocol(studyId, data, true),
    onSuccess: () => {
      setInvalidationPending(null);
      void queryClient.invalidateQueries({ queryKey: rrProtocolKey(studyId) });
    },
  });

  /**
   * Confirm paper invalidation and resend the pending update.
   *
   * @param data - The protocol update payload to resend with acknowledgment.
   */
  function confirmInvalidation(data: RRProtocolUpdate): void {
    setInvalidationPending(null);
    confirmMutation.mutate(data);
  }

  /**
   * Cancel the pending invalidation without submitting.
   */
  function cancelInvalidation(): void {
    setInvalidationPending(null);
  }

  return { mutation, invalidationPending, confirmInvalidation, cancelInvalidation };
}

/**
 * Mutation hook for validating the Rapid Review protocol.
 *
 * Invalidates the protocol query on success.
 *
 * @param studyId - The integer study ID.
 * @returns TanStack mutation object.
 */
export function useValidateRRProtocol(studyId: number) {
  const queryClient = useQueryClient();
  return useMutation<RRProtocol, Error, void>({
    mutationFn: () => validateProtocol(studyId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: rrProtocolKey(studyId) });
    },
  });
}
