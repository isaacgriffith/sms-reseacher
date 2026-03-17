/**
 * Zod schemas and inferred TypeScript types for Agent entities (Feature 005).
 */

import { z } from 'zod';

// Task type literal union (no TS enum)
const AgentTaskTypeSchema = z.union([
  z.literal('screener'),
  z.literal('extractor'),
  z.literal('librarian'),
  z.literal('expert'),
  z.literal('quality_judge'),
  z.literal('agent_generator'),
  z.literal('domain_modeler'),
  z.literal('synthesiser'),
  z.literal('validity_assessor'),
]);
export type AgentTaskType = z.infer<typeof AgentTaskTypeSchema>;

export const AgentSummarySchema = z.object({
  id: z.string().uuid(),
  task_type: AgentTaskTypeSchema,
  role_name: z.string(),
  persona_name: z.string(),
  model_id: z.string().uuid(),
  provider_id: z.string().uuid(),
  model_display_name: z.string(),
  provider_display_name: z.string(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type AgentSummary = z.infer<typeof AgentSummarySchema>;

export const AgentSchema = z.object({
  ...AgentSummarySchema.shape,
  role_description: z.string(),
  persona_description: z.string(),
  persona_svg: z.string().nullable(),
  system_message_template: z.string(),
  system_message_undo_buffer: z.string().nullable(),
  version_id: z.number(),
});
export type Agent = z.infer<typeof AgentSchema>;

export const AgentUpdateSchema = z.object({
  version_id: z.number().int(),
  task_type: AgentTaskTypeSchema.optional(),
  role_name: z.string().min(1).optional(),
  role_description: z.string().min(1).optional(),
  persona_name: z.string().min(1).optional(),
  persona_description: z.string().min(1).optional(),
  persona_svg: z.string().nullable().optional(),
  system_message_template: z.string().min(1).optional(),
  model_id: z.string().uuid().optional(),
  provider_id: z.string().uuid().optional(),
  is_active: z.boolean().optional(),
});
export type AgentUpdate = z.infer<typeof AgentUpdateSchema>;

export const AgentCreateSchema = z.object({
  task_type: AgentTaskTypeSchema,
  role_name: z.string().min(1),
  role_description: z.string().min(1),
  persona_name: z.string().min(1),
  persona_description: z.string().min(1),
  system_message_template: z.string().min(1),
  model_id: z.string().uuid(),
  provider_id: z.string().uuid(),
  persona_svg: z.string().nullable().optional(),
});
export type AgentCreate = z.infer<typeof AgentCreateSchema>;

export const SystemMessageGenerateResultSchema = z.object({
  system_message_template: z.string(),
  previous_message_preserved: z.boolean(),
});
export type SystemMessageGenerateResult = z.infer<typeof SystemMessageGenerateResultSchema>;

export const PersonaSvgGenerateResultSchema = z.object({
  svg: z.string(),
});
export type PersonaSvgGenerateResult = z.infer<typeof PersonaSvgGenerateResultSchema>;
