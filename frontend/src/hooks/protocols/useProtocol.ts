/**
 * TanStack Query hooks for the protocol library API (feature 010).
 *
 * Wraps protocol list, detail, assignment queries, and write mutations.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  assignProtocol,
  copyProtocol,
  createProtocol,
  deleteProtocol,
  getProtocol,
  getProtocolAssignment,
  importProtocol,
  listProtocols,
  resetProtocol,
  updateProtocol,
  type CopyProtocolPayload,
  type CreateProtocolPayload,
  type ProtocolAssignment,
  type ProtocolDetail,
  type ProtocolListItem,
  type UpdateProtocolPayload,
} from '../../services/protocols/protocolsApi';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

/** @returns TanStack Query key for the protocol list. */
export function protocolListKey(studyType?: string): [string, string?] {
  return ['protocols', studyType];
}

/** @returns TanStack Query key for a protocol detail. */
export function protocolDetailKey(id: number): [string, number] {
  return ['protocol', id];
}

/** @returns TanStack Query key for a study's protocol assignment. */
export function protocolAssignmentKey(studyId: number): [string, number] {
  return ['protocol-assignment', studyId];
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/**
 * Query hook for the list of visible protocols.
 *
 * @param studyType - Optional study type filter.
 * @returns TanStack Query result for the list of {@link ProtocolListItem}.
 */
export function useProtocolList(studyType?: string) {
  return useQuery<ProtocolListItem[]>({
    queryKey: protocolListKey(studyType),
    queryFn: () => listProtocols(studyType),
  });
}

/**
 * Query hook for full protocol detail.
 *
 * @param id - The integer protocol ID. Pass 0 to disable.
 * @returns TanStack Query result for the {@link ProtocolDetail}.
 */
export function useProtocolDetail(id: number) {
  return useQuery<ProtocolDetail>({
    queryKey: protocolDetailKey(id),
    queryFn: () => getProtocol(id),
    enabled: id > 0,
  });
}

/**
 * Query hook for a study's current protocol assignment.
 *
 * @param studyId - The integer study ID. Pass 0 to disable.
 * @returns TanStack Query result for the {@link ProtocolAssignment}.
 */
export function useProtocolAssignment(studyId: number) {
  return useQuery<ProtocolAssignment>({
    queryKey: protocolAssignmentKey(studyId),
    queryFn: () => getProtocolAssignment(studyId),
    enabled: studyId > 0,
  });
}

// ---------------------------------------------------------------------------
// Mutation hooks (T055)
// ---------------------------------------------------------------------------

/**
 * Mutation hook for copying a protocol.
 *
 * Invalidates the protocol list on success.
 */
export function useCopyProtocol() {
  const qc = useQueryClient();
  return useMutation<ProtocolDetail, Error, CopyProtocolPayload>({
    mutationFn: copyProtocol,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['protocols'] }),
  });
}

/**
 * Mutation hook for creating a protocol from a full graph.
 *
 * Invalidates the protocol list on success.
 */
export function useCreateProtocol() {
  const qc = useQueryClient();
  return useMutation<ProtocolDetail, Error, CreateProtocolPayload>({
    mutationFn: createProtocol,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['protocols'] }),
  });
}

/**
 * Mutation hook for updating (replacing) a protocol graph.
 *
 * Invalidates both the protocol list and the updated protocol's detail query.
 */
export function useUpdateProtocol() {
  const qc = useQueryClient();
  return useMutation<ProtocolDetail, Error, UpdateProtocolPayload>({
    mutationFn: updateProtocol,
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['protocols'] });
      qc.invalidateQueries({ queryKey: protocolDetailKey(data.id) });
    },
  });
}

/**
 * Mutation hook for deleting a protocol.
 *
 * Invalidates the protocol list on success.
 */
export function useDeleteProtocol() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: deleteProtocol,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['protocols'] }),
  });
}

/**
 * Mutation hook for importing a protocol from a YAML file.
 *
 * Invalidates the protocol list on success.
 *
 * @returns TanStack Mutation result for {@link ProtocolDetail}.
 */
export function useImportProtocol() {
  const qc = useQueryClient();
  return useMutation<ProtocolDetail, Error, File>({
    mutationFn: importProtocol,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['protocols'] }),
  });
}

/**
 * Mutation hook for resetting a study's protocol to the default template.
 *
 * Invalidates the protocol assignment and execution state queries on success.
 *
 * @returns TanStack Mutation result for {@link ProtocolAssignment}.
 */
export function useResetProtocol() {
  const qc = useQueryClient();
  return useMutation<ProtocolAssignment, Error, number>({
    mutationFn: resetProtocol,
    onSuccess: (_, studyId) => {
      qc.invalidateQueries({ queryKey: ['protocol-assignment', studyId] });
      qc.invalidateQueries({ queryKey: ['execution-state', studyId] });
    },
  });
}

/**
 * Mutation hook for assigning a protocol to a study.
 *
 * Invalidates the protocol assignment and execution state queries on success.
 */
export function useAssignProtocol() {
  const qc = useQueryClient();
  return useMutation<ProtocolAssignment, Error, { studyId: number; protocolId: number }>({
    mutationFn: ({ studyId, protocolId }) => assignProtocol(studyId, protocolId),
    onSuccess: (_, { studyId }) => {
      qc.invalidateQueries({ queryKey: ['protocol-assignment', studyId] });
      qc.invalidateQueries({ queryKey: ['execution-state', studyId] });
    },
  });
}
