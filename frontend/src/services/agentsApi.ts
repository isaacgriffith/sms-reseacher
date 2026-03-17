/**
 * TanStack Query hooks and API client functions for agent management
 * endpoints (Feature 005).
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from './api';
import {
  AgentSchema,
  AgentSummarySchema,
  AgentCreateSchema,
  AgentUpdateSchema,
  SystemMessageGenerateResultSchema,
  PersonaSvgGenerateResultSchema,
} from '../types/agent';
import type {
  Agent,
  AgentCreate,
  AgentUpdate,
  SystemMessageGenerateResult,
  PersonaSvgGenerateResult,
} from '../types/agent';
import { z } from 'zod';

const BASE = '/api/v1/admin';

/**
 * Fetch all agents with optional task_type / is_active filters.
 *
 * @param params - Optional filter parameters.
 * @returns TanStack Query result with a parsed list of {@link AgentSummary} objects.
 */
export function useAgents(params?: { task_type?: string; is_active?: boolean }) {
  const qs = new URLSearchParams();
  if (params?.task_type) qs.set('task_type', params.task_type);
  if (params?.is_active !== undefined) qs.set('is_active', String(params.is_active));
  const queryString = qs.toString();
  return useQuery({
    queryKey: ['agents', params],
    queryFn: async () => {
      const url = `${BASE}/agents${queryString ? `?${queryString}` : ''}`;
      const raw = await api.get<unknown[]>(url);
      return z.array(AgentSummarySchema).parse(raw);
    },
  });
}

/**
 * Fetch a single agent with full fields by ID.
 *
 * @param id - UUID of the agent, or null to disable the query.
 * @returns TanStack Query result with a parsed {@link Agent}.
 */
export function useAgent(id: string | null) {
  return useQuery({
    queryKey: ['agents', id],
    enabled: !!id,
    queryFn: async () => {
      const raw = await api.get<unknown>(`${BASE}/agents/${id}`);
      return AgentSchema.parse(raw);
    },
  });
}

/**
 * Fetch all valid agent task type strings.
 *
 * @returns TanStack Query result with a list of task type strings.
 */
export function useAgentTaskTypes() {
  return useQuery({
    queryKey: ['agent-task-types'],
    queryFn: async () => {
      const raw = await api.get<string[]>(`${BASE}/agent-task-types`);
      return z.array(z.string()).parse(raw);
    },
  });
}

/**
 * Create a new agent.
 *
 * Invalidates the agents list query on success.
 *
 * @returns Mutation result yielding the newly created {@link Agent}.
 */
export function useCreateAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: AgentCreate): Promise<Agent> => {
      AgentCreateSchema.parse(body);
      const raw = await api.post<unknown>(`${BASE}/agents`, body);
      return AgentSchema.parse(raw);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  });
}

/**
 * Generate or regenerate the system message template for an agent.
 *
 * Invalidates the specific agent query on success.
 *
 * @returns Mutation result yielding a {@link SystemMessageGenerateResult}.
 */
export function useGenerateSystemMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (agentId: string): Promise<SystemMessageGenerateResult> => {
      const raw = await api.post<unknown>(`${BASE}/agents/${agentId}/generate-system-message`, {});
      return SystemMessageGenerateResultSchema.parse(raw);
    },
    onSuccess: (_data, agentId) => {
      qc.invalidateQueries({ queryKey: ['agents', agentId] });
    },
  });
}

/**
 * Update an existing agent (partial update / PATCH).
 *
 * Invalidates both the agent list and the individual agent query on success.
 *
 * @returns Mutation result yielding the updated {@link Agent}.
 */
export function useUpdateAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: AgentUpdate }): Promise<Agent> => {
      AgentUpdateSchema.parse(data);
      const raw = await api.patch<unknown>(`${BASE}/agents/${id}`, data);
      return AgentSchema.parse(raw);
    },
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: ['agents'] });
      qc.invalidateQueries({ queryKey: ['agents', id] });
    },
  });
}

/**
 * Soft-delete an agent (sets is_active=false).
 *
 * Invalidates the agents list query on success.
 *
 * @returns Mutation result (void on success).
 */
export function useDeleteAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await api.delete<void>(`${BASE}/agents/${id}`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  });
}

/**
 * Restore the previous system message from the undo buffer.
 *
 * Invalidates both the agent list and the individual agent query on success.
 *
 * @returns Mutation result yielding the updated {@link Agent}.
 */
export function useUndoSystemMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (agentId: string): Promise<Agent> => {
      const raw = await api.post<unknown>(`${BASE}/agents/${agentId}/undo-system-message`, {});
      return AgentSchema.parse(raw);
    },
    onSuccess: (_, agentId) => {
      qc.invalidateQueries({ queryKey: ['agents'] });
      qc.invalidateQueries({ queryKey: ['agents', agentId] });
    },
  });
}

/**
 * Generate a persona SVG avatar using an LLM.
 *
 * @returns Mutation result yielding a {@link PersonaSvgGenerateResult}.
 */
export function useGeneratePersonaSvg() {
  return useMutation({
    mutationFn: async (body: {
      persona_name: string;
      persona_description: string;
      agent_id?: string | null;
    }): Promise<PersonaSvgGenerateResult> => {
      const raw = await api.post<unknown>(`${BASE}/agents/generate-persona-svg`, body);
      return PersonaSvgGenerateResultSchema.parse(raw);
    },
  });
}
