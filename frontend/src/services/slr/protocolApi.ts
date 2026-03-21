/**
 * SLR protocol API service (feature 007).
 *
 * All API responses are validated using Zod schemas at the boundary.
 * Functions throw {@link ApiError} on non-2xx responses.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for a single issue identified by the AI protocol reviewer. */
export const ProtocolIssueSchema = z.object({
  section: z.string(),
  severity: z.enum(['critical', 'major', 'minor']),
  description: z.string(),
  suggestion: z.string(),
});
export type ProtocolIssue = z.infer<typeof ProtocolIssueSchema>;

/** Schema for the AI protocol review result. */
export const ProtocolReviewResultSchema = z.object({
  issues: z.array(ProtocolIssueSchema),
  overall_assessment: z.string(),
});
export type ProtocolReviewResult = z.infer<typeof ProtocolReviewResultSchema>;

/** Schema for the full review protocol response. */
export const ReviewProtocolSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  status: z.enum(['draft', 'under_review', 'validated']),
  background: z.string().nullable(),
  rationale: z.string().nullable(),
  research_questions: z.array(z.string()).nullable(),
  pico_population: z.string().nullable(),
  pico_intervention: z.string().nullable(),
  pico_comparison: z.string().nullable(),
  pico_outcome: z.string().nullable(),
  pico_context: z.string().nullable(),
  search_strategy: z.string().nullable(),
  inclusion_criteria: z.array(z.string()).nullable(),
  exclusion_criteria: z.array(z.string()).nullable(),
  data_extraction_strategy: z.string().nullable(),
  synthesis_approach: z.string().nullable(),
  dissemination_strategy: z.string().nullable(),
  timetable: z.string().nullable(),
  review_report: ProtocolReviewResultSchema.nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type ReviewProtocol = z.infer<typeof ReviewProtocolSchema>;

/** Schema for PUT /protocol request body. */
export const ProtocolUpsertSchema = z.object({
  background: z.string().optional(),
  rationale: z.string().optional(),
  research_questions: z.array(z.string()).optional(),
  pico_population: z.string().optional(),
  pico_intervention: z.string().optional(),
  pico_comparison: z.string().optional(),
  pico_outcome: z.string().optional(),
  pico_context: z.string().optional().nullable(),
  search_strategy: z.string().optional(),
  inclusion_criteria: z.array(z.string()).optional(),
  exclusion_criteria: z.array(z.string()).optional(),
  data_extraction_strategy: z.string().optional(),
  synthesis_approach: z.string().optional(),
  dissemination_strategy: z.string().optional(),
  timetable: z.string().optional(),
});
export type ProtocolUpsert = z.infer<typeof ProtocolUpsertSchema>;

/** Schema for the SLR phase status response. */
export const SLRPhasesSchema = z.object({
  study_id: z.number(),
  unlocked_phases: z.array(z.number()),
  protocol_status: z.string().nullable(),
  quality_complete: z.boolean(),
  synthesis_complete: z.boolean(),
});
export type SLRPhases = z.infer<typeof SLRPhasesSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch the current review protocol for an SLR study.
 *
 * @param studyId - The study integer ID.
 * @returns The parsed {@link ReviewProtocol} or throws if not found (404).
 */
export async function getProtocol(studyId: number): Promise<ReviewProtocol> {
  const raw = await api.get<unknown>(`/api/v1/slr/studies/${studyId}/protocol`);
  return ReviewProtocolSchema.parse(raw);
}

/**
 * Create or update the draft protocol for an SLR study.
 *
 * @param studyId - The study integer ID.
 * @param data - Protocol field values to apply.
 * @returns The updated {@link ReviewProtocol}.
 */
export async function upsertProtocol(
  studyId: number,
  data: ProtocolUpsert,
): Promise<ReviewProtocol> {
  const raw = await api.put<unknown>(`/api/v1/slr/studies/${studyId}/protocol`, data);
  return ReviewProtocolSchema.parse(raw);
}

/**
 * Submit the protocol for AI review.
 *
 * @param studyId - The study integer ID.
 * @returns An object with `job_id` and `status`.
 */
export async function submitForReview(studyId: number): Promise<{ job_id: string; status: string }> {
  const raw = await api.post<unknown>(
    `/api/v1/slr/studies/${studyId}/protocol/submit-for-review`,
    {},
  );
  return z.object({ job_id: z.string(), status: z.string() }).parse(raw);
}

/**
 * Approve and validate the reviewed protocol.
 *
 * @param studyId - The study integer ID.
 * @returns An object with `status: "validated"`.
 */
export async function validateProtocol(studyId: number): Promise<{ status: string }> {
  const raw = await api.post<unknown>(
    `/api/v1/slr/studies/${studyId}/protocol/validate`,
    {},
  );
  return z.object({ status: z.string() }).parse(raw);
}

/**
 * Fetch the current SLR phase unlock status for a study.
 *
 * @param studyId - The study integer ID.
 * @returns The parsed {@link SLRPhases} object.
 */
export async function getPhases(studyId: number): Promise<SLRPhases> {
  const raw = await api.get<unknown>(`/api/v1/slr/studies/${studyId}/phases`);
  return SLRPhasesSchema.parse(raw);
}
