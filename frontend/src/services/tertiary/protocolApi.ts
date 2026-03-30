/**
 * Tertiary Study protocol API service (feature 009).
 *
 * All API responses are validated using Zod schemas at the boundary.
 * Functions throw {@link ApiError} on non-2xx responses.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for the full Tertiary Study protocol response. */
export const TertiaryProtocolSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  status: z.enum(['draft', 'validated']),
  background: z.string().nullable(),
  research_questions: z.array(z.string()).nullable(),
  secondary_study_types: z.array(z.string()).nullable(),
  inclusion_criteria: z.array(z.string()).nullable(),
  exclusion_criteria: z.array(z.string()).nullable(),
  recency_cutoff_year: z.number().nullable(),
  search_strategy: z.string().nullable(),
  quality_threshold: z.number().nullable(),
  synthesis_approach: z.string().nullable(),
  dissemination_strategy: z.string().nullable(),
  version_id: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type TertiaryProtocol = z.infer<typeof TertiaryProtocolSchema>;

/** Schema for PUT /tertiary/studies/{id}/protocol request body. */
export const TertiaryProtocolUpdateSchema = z.object({
  background: z.string().optional().nullable(),
  research_questions: z.array(z.string()).optional(),
  secondary_study_types: z.array(z.string()).optional(),
  inclusion_criteria: z.array(z.string()).optional(),
  exclusion_criteria: z.array(z.string()).optional(),
  recency_cutoff_year: z.number().optional().nullable(),
  search_strategy: z.string().optional().nullable(),
  quality_threshold: z.number().optional().nullable(),
  synthesis_approach: z.string().optional().nullable(),
  dissemination_strategy: z.string().optional().nullable(),
  version_id: z.number().optional(),
});
export type TertiaryProtocolUpdate = z.infer<typeof TertiaryProtocolUpdateSchema>;

/** Schema for the validate response. */
const ValidateResponseSchema = z.object({
  job_id: z.string(),
  status: z.string(),
});

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch the current Tertiary Study protocol (auto-creates draft if absent).
 *
 * @param studyId - The study integer ID.
 * @returns The parsed {@link TertiaryProtocol}.
 */
export async function getProtocol(studyId: number): Promise<TertiaryProtocol> {
  const raw = await api.get<unknown>(`/api/v1/tertiary/studies/${studyId}/protocol`);
  return TertiaryProtocolSchema.parse(raw);
}

/**
 * Update the Tertiary Study protocol fields.
 *
 * @param studyId - The study integer ID.
 * @param data - Protocol fields to update (all optional).
 * @returns The updated {@link TertiaryProtocol}.
 */
export async function updateProtocol(
  studyId: number,
  data: TertiaryProtocolUpdate,
): Promise<TertiaryProtocol> {
  const raw = await api.put<unknown>(`/api/v1/tertiary/studies/${studyId}/protocol`, data);
  return TertiaryProtocolSchema.parse(raw);
}

/**
 * Validate (approve) the Tertiary Study protocol and queue an AI review job.
 *
 * @param studyId - The study integer ID.
 * @returns An object with `job_id` and `status`.
 */
export async function validateProtocol(
  studyId: number,
): Promise<{ job_id: string; status: string }> {
  const raw = await api.post<unknown>(
    `/api/v1/tertiary/studies/${studyId}/protocol/validate`,
    {},
  );
  return ValidateResponseSchema.parse(raw);
}
