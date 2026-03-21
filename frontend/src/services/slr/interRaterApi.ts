/**
 * API client for SLR inter-rater agreement endpoints (feature 007).
 *
 * All functions parse responses with Zod schemas at the API boundary,
 * guaranteeing type safety at runtime.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/**
 * Schema for a single inter-rater agreement record.
 */
export const InterRaterRecordSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  reviewer_a_id: z.number(),
  reviewer_b_id: z.number(),
  round_type: z.string(),
  phase: z.string(),
  kappa_value: z.number().nullable(),
  kappa_undefined_reason: z.string().nullable(),
  n_papers: z.number(),
  threshold_met: z.boolean(),
  created_at: z.string(),
});

export type InterRaterRecord = z.infer<typeof InterRaterRecordSchema>;

/**
 * Schema for the list response.
 */
export const InterRaterListSchema = z.object({
  records: z.array(InterRaterRecordSchema),
});

export type InterRaterList = z.infer<typeof InterRaterListSchema>;

/**
 * Request body for compute / post-discussion endpoints.
 */
export interface ComputeKappaBody {
  reviewer_a_id: number;
  reviewer_b_id: number;
  round_type: string;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch all inter-rater agreement records for a study.
 *
 * @param studyId - The integer study ID.
 * @returns Array of {@link InterRaterRecord} objects.
 */
export async function getInterRaterRecords(studyId: number): Promise<InterRaterList> {
  const raw = await api.get<unknown>(`/api/v1/slr/studies/${studyId}/inter-rater`);
  return InterRaterListSchema.parse(raw);
}

/**
 * Trigger a Kappa computation (pre-discussion) between two reviewers.
 *
 * @param studyId - The integer study ID.
 * @param body - Reviewer IDs and round type.
 * @returns The new {@link InterRaterRecord}.
 */
export async function computeKappa(
  studyId: number,
  body: ComputeKappaBody,
): Promise<InterRaterRecord> {
  const raw = await api.post<unknown>(
    `/api/v1/slr/studies/${studyId}/inter-rater/compute`,
    body,
  );
  return InterRaterRecordSchema.parse(raw);
}

/**
 * Record post-discussion Kappa after Think-Aloud workflow is complete.
 *
 * @param studyId - The integer study ID.
 * @param body - Reviewer IDs and round type.
 * @returns The new post-discussion {@link InterRaterRecord}.
 */
export async function recordPostDiscussionKappa(
  studyId: number,
  body: ComputeKappaBody,
): Promise<InterRaterRecord> {
  const raw = await api.post<unknown>(
    `/api/v1/slr/studies/${studyId}/inter-rater/post-discussion`,
    body,
  );
  return InterRaterRecordSchema.parse(raw);
}
