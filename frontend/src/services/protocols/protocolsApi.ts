/**
 * API service functions for Research Protocol Definition (feature 010).
 *
 * Provides typed fetch wrappers for the protocols REST endpoints:
 * listing protocols, fetching protocol detail, and protocol assignment.
 *
 * All API responses are validated using Zod schemas at the boundary.
 * Functions throw {@link ApiError} on non-2xx responses.
 */

import { z } from 'zod';
import { api, ApiError } from '../api';
import { getToken } from '../auth';

export { ApiError };

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for a protocol list item. */
export const ProtocolListItemSchema = z.object({
  id: z.number(),
  name: z.string(),
  study_type: z.string(),
  is_default_template: z.boolean(),
  owner_user_id: z.number().nullable(),
  version_id: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type ProtocolListItem = z.infer<typeof ProtocolListItemSchema>;

/** Schema for a node input slot. */
export const NodeInputSchema = z.object({
  id: z.number(),
  name: z.string(),
  data_type: z.string(),
  is_required: z.boolean(),
});
export type NodeInput = z.infer<typeof NodeInputSchema>;

/** Schema for a node output slot. */
export const NodeOutputSchema = z.object({
  id: z.number(),
  name: z.string(),
  data_type: z.string(),
});
export type NodeOutput = z.infer<typeof NodeOutputSchema>;

/** Schema for a node assignee. */
export const AssigneeSchema = z.object({
  id: z.number(),
  assignee_type: z.string(),
  role: z.string().nullable(),
  agent_id: z.string().nullable(),
});
export type Assignee = z.infer<typeof AssigneeSchema>;

/** Schema for a quality gate. */
export const QualityGateSchema = z.object({
  id: z.number(),
  gate_type: z.string(),
  config: z.record(z.unknown()),
});
export type QualityGate = z.infer<typeof QualityGateSchema>;

/** Schema for a full protocol node with all nested detail. */
export const ProtocolNodeSchema = z.object({
  id: z.number(),
  task_id: z.string(),
  task_type: z.string(),
  label: z.string(),
  description: z.string().nullable(),
  is_required: z.boolean(),
  position_x: z.number().nullable(),
  position_y: z.number().nullable(),
  inputs: z.array(NodeInputSchema),
  outputs: z.array(NodeOutputSchema),
  assignees: z.array(AssigneeSchema),
  quality_gates: z.array(QualityGateSchema),
});
export type ProtocolNode = z.infer<typeof ProtocolNodeSchema>;

/** Schema for an edge condition triple. */
export const EdgeConditionSchema = z.object({
  output_name: z.string(),
  operator: z.string(),
  value: z.number(),
});
export type EdgeCondition = z.infer<typeof EdgeConditionSchema>;

/** Schema for a directed protocol edge. */
export const ProtocolEdgeSchema = z.object({
  id: z.number(),
  edge_id: z.string(),
  source_task_id: z.string(),
  source_output_name: z.string(),
  target_task_id: z.string(),
  target_input_name: z.string(),
  condition: EdgeConditionSchema.nullable(),
});
export type ProtocolEdge = z.infer<typeof ProtocolEdgeSchema>;

/** Schema for a full protocol detail response. */
export const ProtocolDetailSchema = z.object({
  id: z.number(),
  name: z.string(),
  study_type: z.string(),
  is_default_template: z.boolean(),
  owner_user_id: z.number().nullable(),
  version_id: z.number(),
  description: z.string().nullable(),
  nodes: z.array(ProtocolNodeSchema),
  edges: z.array(ProtocolEdgeSchema),
  created_at: z.string(),
  updated_at: z.string(),
});
export type ProtocolDetail = z.infer<typeof ProtocolDetailSchema>;

/** Schema for a study protocol assignment. */
export const ProtocolAssignmentSchema = z.object({
  study_id: z.number(),
  protocol_id: z.number(),
  protocol_name: z.string(),
  is_default_template: z.boolean(),
  assigned_at: z.string(),
  assigned_by_user_id: z.number().nullable(),
});
export type ProtocolAssignment = z.infer<typeof ProtocolAssignmentSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch all protocols visible to the authenticated user.
 *
 * @param studyType - Optional study type filter.
 * @returns Validated list of {@link ProtocolListItem}.
 */
export async function listProtocols(studyType?: string): Promise<ProtocolListItem[]> {
  const qs = studyType ? `?study_type=${encodeURIComponent(studyType)}` : '';
  const raw = await api.get<unknown>(`/api/v1/protocols${qs}`);
  return z.array(ProtocolListItemSchema).parse(raw);
}

/**
 * Fetch full detail for a single protocol.
 *
 * @param id - The integer protocol ID.
 * @returns Validated {@link ProtocolDetail}.
 */
export async function getProtocol(id: number): Promise<ProtocolDetail> {
  const raw = await api.get<unknown>(`/api/v1/protocols/${id}`);
  return ProtocolDetailSchema.parse(raw);
}

/**
 * Fetch the protocol assignment for a study.
 *
 * @param studyId - The integer study ID.
 * @returns Validated {@link ProtocolAssignment}.
 */
export async function getProtocolAssignment(studyId: number): Promise<ProtocolAssignment> {
  const raw = await api.get<unknown>(`/api/v1/studies/${studyId}/protocol-assignment`);
  return ProtocolAssignmentSchema.parse(raw);
}

// ---------------------------------------------------------------------------
// Mutation functions (T055)
// ---------------------------------------------------------------------------

/** Payload for copying a protocol. */
export interface CopyProtocolPayload {
  name: string;
  description?: string | null;
  copy_from_protocol_id: number;
}

/** Payload for creating a protocol from a full graph. */
export interface CreateProtocolPayload {
  name: string;
  description?: string | null;
  study_type: string;
  nodes: unknown[];
  edges: unknown[];
}

/** Payload for updating (replacing) a protocol graph. */
export interface UpdateProtocolPayload {
  id: number;
  version_id: number;
  name: string;
  description?: string | null;
  nodes: unknown[];
  edges: unknown[];
}

/**
 * Copy an existing protocol to a new custom protocol.
 *
 * @param payload - Copy request payload.
 * @returns Validated {@link ProtocolDetail} for the new copy.
 */
export async function copyProtocol(payload: CopyProtocolPayload): Promise<ProtocolDetail> {
  const raw = await api.post<unknown>('/api/v1/protocols', payload);
  return ProtocolDetailSchema.parse(raw);
}

/**
 * Create a new custom protocol from a full graph definition.
 *
 * @param payload - Create request payload.
 * @returns Validated {@link ProtocolDetail} for the new protocol.
 */
export async function createProtocol(payload: CreateProtocolPayload): Promise<ProtocolDetail> {
  const raw = await api.post<unknown>('/api/v1/protocols', payload);
  return ProtocolDetailSchema.parse(raw);
}

/**
 * Update (replace) a custom protocol graph.
 *
 * @param payload - Update request payload including optimistic-lock version_id.
 * @returns Validated updated {@link ProtocolDetail}.
 */
export async function updateProtocol({
  id,
  ...body
}: UpdateProtocolPayload): Promise<ProtocolDetail> {
  const raw = await api.put<unknown>(`/api/v1/protocols/${id}`, body);
  return ProtocolDetailSchema.parse(raw);
}

/**
 * Delete a custom protocol.
 *
 * @param id - The integer protocol ID to delete.
 */
export async function deleteProtocol(id: number): Promise<void> {
  await api.delete(`/api/v1/protocols/${id}`);
}

// ---------------------------------------------------------------------------
// Execution state schemas and functions (T064)
// ---------------------------------------------------------------------------

/** Schema for a single task execution state item. */
export const ExecutionTaskItemSchema = z.object({
  node_id: z.number(),
  task_id: z.string(),
  task_type: z.string(),
  label: z.string(),
  status: z.string(),
  activated_at: z.string().nullable(),
  completed_at: z.string().nullable(),
  gate_failure_detail: z.record(z.unknown()).nullable(),
});
export type ExecutionTaskItem = z.infer<typeof ExecutionTaskItemSchema>;

/** Schema for the full execution state response. */
export const ExecutionStateResponseSchema = z.object({
  study_id: z.number(),
  protocol_id: z.number(),
  tasks: z.array(ExecutionTaskItemSchema),
});
export type ExecutionStateResponse = z.infer<typeof ExecutionStateResponseSchema>;

/** Schema for the complete-task response. */
export const CompleteTaskResponseSchema = z.object({
  completed_task_id: z.string(),
  gate_result: z.string(),
  gate_failure_detail: z.record(z.unknown()).nullable(),
  newly_activated_task_ids: z.array(z.string()),
  all_tasks: z.array(ExecutionTaskItemSchema),
});
export type CompleteTaskResponse = z.infer<typeof CompleteTaskResponseSchema>;

// ---------------------------------------------------------------------------
// YAML export / import (T084)
// ---------------------------------------------------------------------------

/**
 * Reset a study's protocol to the default template for its study type.
 *
 * Sends `{"confirm_reset": true}` as required by the API.
 *
 * @param studyId - The integer study ID.
 * @returns Validated {@link ProtocolAssignment}.
 */
export async function resetProtocol(studyId: number): Promise<ProtocolAssignment> {
  const token = getToken();
  const resp = await fetch(`/api/v1/studies/${studyId}/protocol-assignment`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ confirm_reset: true }),
  });
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const data = await resp.json();
      detail = data?.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(resp.status, detail);
  }
  const raw = await resp.json();
  return ProtocolAssignmentSchema.parse(raw);
}

/**
 * Trigger a YAML file download for a protocol.
 *
 * Uses the browser's Fetch API and creates a temporary anchor element to
 * initiate the download without navigating away.
 *
 * @param id - The integer protocol ID to export.
 * @param filename - Optional override for the downloaded filename.
 */
export async function exportProtocol(id: number, filename?: string): Promise<void> {
  const token = getToken();
  const resp = await fetch(`/api/v1/protocols/${id}/export`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!resp.ok) throw new ApiError(resp.status, `Export failed: ${resp.status}`);
  const blob = await resp.blob();
  const disposition = resp.headers.get('Content-Disposition') ?? '';
  const serverName = disposition.match(/filename="([^"]+)"/)?.[1];
  const name = filename ?? serverName ?? `protocol-${id}.yaml`;
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Upload a YAML file and import it as a new protocol.
 *
 * @param file - The YAML file selected by the user.
 * @returns Validated {@link ProtocolDetail} for the newly created protocol.
 */
export async function importProtocol(file: File): Promise<ProtocolDetail> {
  const token = getToken();
  const form = new FormData();
  form.append('file', file);
  const resp = await fetch('/api/v1/protocols/import', {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const data = await resp.json();
      detail = data?.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(resp.status, detail);
  }
  const raw = await resp.json();
  return ProtocolDetailSchema.parse(raw);
}

/**
 * Assign a protocol to a study.
 *
 * @param studyId - The integer study ID.
 * @param protocolId - The integer protocol ID to assign.
 * @returns Validated {@link ProtocolAssignment}.
 */
export async function assignProtocol(
  studyId: number,
  protocolId: number,
): Promise<ProtocolAssignment> {
  const raw = await api.put<unknown>(`/api/v1/studies/${studyId}/protocol-assignment`, {
    protocol_id: protocolId,
  });
  return ProtocolAssignmentSchema.parse(raw);
}

/**
 * Fetch the full execution state for a study's protocol.
 *
 * @param studyId - The integer study ID.
 * @returns Validated {@link ExecutionStateResponse}.
 */
export async function getExecutionState(studyId: number): Promise<ExecutionStateResponse> {
  const raw = await api.get<unknown>(`/api/v1/studies/${studyId}/execution-state`);
  return ExecutionStateResponseSchema.parse(raw);
}

/**
 * Mark a task complete in a study's protocol execution.
 *
 * @param studyId - The integer study ID.
 * @param taskId - The task_id string of the node to complete.
 * @returns Validated {@link CompleteTaskResponse}.
 */
export async function completeTask(studyId: number, taskId: string): Promise<CompleteTaskResponse> {
  const raw = await api.post<unknown>(
    `/api/v1/studies/${studyId}/execution-state/${taskId}/complete`,
    {},
  );
  return CompleteTaskResponseSchema.parse(raw);
}

/**
 * Approve a human_sign_off gate failure on a task.
 *
 * @param studyId - The integer study ID.
 * @param taskId - The task_id string of the node to approve.
 * @returns Validated {@link CompleteTaskResponse}.
 */
export async function approveTask(studyId: number, taskId: string): Promise<CompleteTaskResponse> {
  const raw = await api.post<unknown>(
    `/api/v1/studies/${studyId}/execution-state/${taskId}/approve`,
    {},
  );
  return CompleteTaskResponseSchema.parse(raw);
}
