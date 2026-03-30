/**
 * Rapid Review protocol API service (feature 008).
 *
 * All API responses are validated using Zod schemas at the boundary.
 * Functions throw {@link ApiError} on non-2xx responses.
 */

import { z } from 'zod';
import { api, ApiError } from '../api';

export { ApiError };

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for a context restriction entry. */
export const ContextRestrictionSchema = z.object({
  type: z.string(),
  description: z.string(),
});
export type ContextRestriction = z.infer<typeof ContextRestrictionSchema>;

/** Schema for the full RR protocol response. */
export const RRProtocolSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  status: z.enum(['draft', 'validated']),
  practical_problem: z.string().nullable(),
  research_questions: z.array(z.string()).nullable(),
  time_budget_days: z.number().nullable(),
  effort_budget_hours: z.number().nullable(),
  context_restrictions: z.array(ContextRestrictionSchema).nullable(),
  dissemination_medium: z.string().nullable(),
  problem_scoping_notes: z.string().nullable(),
  search_strategy_notes: z.string().nullable(),
  inclusion_criteria: z.array(z.string()).nullable(),
  exclusion_criteria: z.array(z.string()).nullable(),
  single_reviewer_mode: z.boolean(),
  single_source_acknowledged: z.boolean(),
  quality_appraisal_mode: z.enum(['full', 'peer_reviewed_only', 'skipped']),
  version_id: z.number(),
  research_gap_warnings: z.array(z.string()).default([]),
  created_at: z.string(),
  updated_at: z.string(),
});
export type RRProtocol = z.infer<typeof RRProtocolSchema>;

/** Schema for PUT /protocol request body. */
export const RRProtocolUpdateSchema = z.object({
  practical_problem: z.string().optional(),
  research_questions: z.array(z.string()).optional(),
  time_budget_days: z.number().optional(),
  effort_budget_hours: z.number().optional(),
  context_restrictions: z.array(ContextRestrictionSchema).optional(),
  dissemination_medium: z.string().optional(),
  problem_scoping_notes: z.string().optional(),
  search_strategy_notes: z.string().optional(),
  inclusion_criteria: z.array(z.string()).optional(),
  exclusion_criteria: z.array(z.string()).optional(),
  single_source_acknowledged: z.boolean().optional(),
});
export type RRProtocolUpdate = z.infer<typeof RRProtocolUpdateSchema>;

/** Schema for the threat response. */
export const ThreatSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  threat_type: z.string(),
  description: z.string(),
  source_detail: z.string().nullable(),
  created_at: z.string(),
});
export type Threat = z.infer<typeof ThreatSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch the Rapid Review protocol for a study.
 *
 * @param studyId - The integer study ID.
 * @returns The validated {@link RRProtocol}.
 */
export async function getProtocol(studyId: number): Promise<RRProtocol> {
  const raw = await api.get<unknown>(`/api/v1/rapid/studies/${studyId}/protocol`);
  return RRProtocolSchema.parse(raw);
}

/**
 * Update the Rapid Review protocol.
 *
 * Pass `acknowledgeInvalidation=true` when the protocol is currently
 * validated and the caller has confirmed paper invalidation.
 *
 * @param studyId - The integer study ID.
 * @param data - Partial protocol update fields.
 * @param acknowledgeInvalidation - Whether the caller confirmed the cascade.
 * @returns The updated {@link RRProtocol}.
 */
export async function updateProtocol(
  studyId: number,
  data: RRProtocolUpdate,
  acknowledgeInvalidation = false,
): Promise<RRProtocol> {
  const qs = acknowledgeInvalidation ? '?acknowledge_invalidation=true' : '';
  const raw = await api.put<unknown>(`/api/v1/rapid/studies/${studyId}/protocol${qs}`, data);
  return RRProtocolSchema.parse(raw);
}

/**
 * Validate the Rapid Review protocol.
 *
 * @param studyId - The integer study ID.
 * @returns The validated {@link RRProtocol} with status="validated".
 */
export async function validateProtocol(studyId: number): Promise<RRProtocol> {
  const raw = await api.post<unknown>(`/api/v1/rapid/studies/${studyId}/protocol/validate`, {});
  return RRProtocolSchema.parse(raw);
}

/**
 * Fetch all threats-to-validity for a study.
 *
 * @param studyId - The integer study ID.
 * @returns List of validated {@link Threat} objects.
 */
export async function getThreats(studyId: number): Promise<Threat[]> {
  const raw = await api.get<unknown>(`/api/v1/rapid/studies/${studyId}/threats`);
  return z.array(ThreatSchema).parse(raw);
}
