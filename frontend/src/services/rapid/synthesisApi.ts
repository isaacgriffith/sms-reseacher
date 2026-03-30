/**
 * Rapid Review narrative synthesis API service (feature 008).
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

/** Schema for a single narrative synthesis section. */
export const NarrativeSectionSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  rq_index: z.number(),
  research_question: z.string(),
  narrative_text: z.string().nullable(),
  ai_draft_text: z.string().nullable(),
  is_complete: z.boolean(),
  ai_draft_job_id: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type NarrativeSection = z.infer<typeof NarrativeSectionSchema>;

/** Schema for PUT /synthesis/{section_id} request body. */
export const SectionUpdateSchema = z.object({
  narrative_text: z.string().optional(),
  is_complete: z.boolean().optional(),
});
export type SectionUpdate = z.infer<typeof SectionUpdateSchema>;

/** Schema for POST /synthesis/{section_id}/ai-draft response. */
export const AIDraftResponseSchema = z.object({
  job_id: z.string(),
  section_id: z.number(),
  status: z.string(),
});
export type AIDraftResponse = z.infer<typeof AIDraftResponseSchema>;

/** Schema for POST /synthesis/complete response. */
export const SynthesisCompleteResponseSchema = z.object({
  synthesis_complete: z.boolean(),
});
export type SynthesisCompleteResponse = z.infer<typeof SynthesisCompleteResponseSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch all narrative synthesis sections for a study.
 *
 * @param studyId - The integer study ID.
 * @returns List of validated {@link NarrativeSection} objects.
 */
export async function listSections(studyId: number): Promise<NarrativeSection[]> {
  const raw = await api.get<unknown>(`/api/v1/rapid/studies/${studyId}/synthesis`);
  return z.array(NarrativeSectionSchema).parse(raw);
}

/**
 * Update a narrative synthesis section.
 *
 * @param studyId - The integer study ID.
 * @param sectionId - The section primary key.
 * @param data - Fields to update.
 * @returns The updated {@link NarrativeSection}.
 */
export async function updateSection(
  studyId: number,
  sectionId: number,
  data: SectionUpdate,
): Promise<NarrativeSection> {
  const raw = await api.put<unknown>(
    `/api/v1/rapid/studies/${studyId}/synthesis/${sectionId}`,
    data,
  );
  return NarrativeSectionSchema.parse(raw);
}

/**
 * Enqueue an AI draft generation job for a synthesis section.
 *
 * @param studyId - The integer study ID.
 * @param sectionId - The section primary key.
 * @returns {@link AIDraftResponse} with the enqueued job ID.
 */
export async function requestAIDraft(studyId: number, sectionId: number): Promise<AIDraftResponse> {
  const raw = await api.post<unknown>(
    `/api/v1/rapid/studies/${studyId}/synthesis/${sectionId}/ai-draft`,
    {},
  );
  return AIDraftResponseSchema.parse(raw);
}

/**
 * Finalise synthesis, gating Evidence Briefing generation.
 *
 * @param studyId - The integer study ID.
 * @returns {@link SynthesisCompleteResponse}.
 */
export async function completeSynthesis(studyId: number): Promise<SynthesisCompleteResponse> {
  const raw = await api.post<unknown>(`/api/v1/rapid/studies/${studyId}/synthesis/complete`, {});
  return SynthesisCompleteResponseSchema.parse(raw);
}
