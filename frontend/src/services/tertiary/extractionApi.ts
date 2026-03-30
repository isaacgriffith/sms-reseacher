/**
 * Tertiary Study data extraction API service (feature 009).
 *
 * All API responses are validated using Zod schemas at the boundary.
 * Functions throw {@link ApiError} on non-2xx responses.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for a single extraction record. */
export const TertiaryExtractionSchema = z.object({
  id: z.number(),
  candidate_paper_id: z.number(),
  paper_title: z.string().nullable(),
  secondary_study_type: z.string().nullable(),
  research_questions_addressed: z.array(z.string()).nullable(),
  databases_searched: z.array(z.string()).nullable(),
  study_period_start: z.number().nullable(),
  study_period_end: z.number().nullable(),
  primary_study_count: z.number().nullable(),
  synthesis_approach_used: z.string().nullable(),
  key_findings: z.string().nullable(),
  research_gaps: z.string().nullable(),
  reviewer_quality_rating: z.number().nullable(),
  extraction_status: z.string(),
  extracted_by_agent: z.string().nullable(),
  validated_by_reviewer_id: z.number().nullable(),
  version_id: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type TertiaryExtraction = z.infer<typeof TertiaryExtractionSchema>;

/** Schema for the AI-assist 202 response. */
export const AiAssistResponseSchema = z.object({
  job_id: z.string(),
  status: z.string(),
  paper_count: z.number(),
});
export type AiAssistResponse = z.infer<typeof AiAssistResponseSchema>;

/** Schema for PUT /extractions/{id} request body. */
export const TertiaryExtractionUpdateSchema = z.object({
  secondary_study_type: z.string().nullable().optional(),
  research_questions_addressed: z.array(z.string()).nullable().optional(),
  databases_searched: z.array(z.string()).nullable().optional(),
  study_period_start: z.number().nullable().optional(),
  study_period_end: z.number().nullable().optional(),
  primary_study_count: z.number().nullable().optional(),
  synthesis_approach_used: z.string().nullable().optional(),
  key_findings: z.string().nullable().optional(),
  research_gaps: z.string().nullable().optional(),
  reviewer_quality_rating: z.number().nullable().optional(),
  extraction_status: z.string().optional(),
  version_id: z.number().optional(),
});
export type TertiaryExtractionUpdate = z.infer<typeof TertiaryExtractionUpdateSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * List all extraction records for a Tertiary Study.
 *
 * @param studyId - The integer study ID.
 * @param statusFilter - Optional extraction status filter.
 * @returns Array of {@link TertiaryExtraction}.
 */
export async function listExtractions(
  studyId: number,
  statusFilter?: string,
): Promise<TertiaryExtraction[]> {
  const url = statusFilter
    ? `/api/v1/tertiary/studies/${studyId}/extractions?status=${encodeURIComponent(statusFilter)}`
    : `/api/v1/tertiary/studies/${studyId}/extractions`;
  const raw = await api.get<unknown[]>(url);
  return raw.map((item) => TertiaryExtractionSchema.parse(item));
}

/**
 * Update an extraction record.
 *
 * @param studyId - The Tertiary Study ID.
 * @param extractionId - The extraction record ID.
 * @param data - Fields to update.
 * @returns The updated {@link TertiaryExtraction}.
 */
export async function updateExtraction(
  studyId: number,
  extractionId: number,
  data: TertiaryExtractionUpdate,
): Promise<TertiaryExtraction> {
  const raw = await api.put<unknown>(
    `/api/v1/tertiary/studies/${studyId}/extractions/${extractionId}`,
    data,
  );
  return TertiaryExtractionSchema.parse(raw);
}

/**
 * Trigger AI-assisted pre-fill for all pending extractions.
 *
 * @param studyId - The Tertiary Study ID.
 * @returns The {@link AiAssistResponse} with job_id and paper_count.
 */
export async function triggerAiAssist(studyId: number): Promise<AiAssistResponse> {
  const raw = await api.post<unknown>(
    `/api/v1/tertiary/studies/${studyId}/extractions/ai-assist`,
    {},
  );
  return AiAssistResponseSchema.parse(raw);
}
