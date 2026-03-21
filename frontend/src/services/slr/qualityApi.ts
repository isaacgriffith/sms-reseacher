/**
 * SLR quality assessment API service (feature 007).
 *
 * All API responses are validated using Zod schemas at the boundary.
 * Functions throw {@link ApiError} on non-2xx responses.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for a single checklist item in a response. */
export const ChecklistItemSchema = z.object({
  id: z.number(),
  order: z.number(),
  question: z.string(),
  scoring_method: z.enum(['binary', 'scale_1_3', 'scale_1_5']),
  weight: z.number(),
});
export type ChecklistItem = z.infer<typeof ChecklistItemSchema>;

/** Schema for the full quality assessment checklist response. */
export const ChecklistSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  name: z.string(),
  description: z.string().nullable(),
  items: z.array(ChecklistItemSchema),
});
export type Checklist = z.infer<typeof ChecklistSchema>;

/** Schema for a single score item in a response. */
export const ScoreItemSchema = z.object({
  checklist_item_id: z.number(),
  score_value: z.number(),
  notes: z.string().nullable(),
});
export type ScoreItem = z.infer<typeof ScoreItemSchema>;

/** Schema for one reviewer's scores on a paper. */
export const ReviewerScoresSchema = z.object({
  reviewer_id: z.number(),
  items: z.array(ScoreItemSchema),
  aggregate_quality_score: z.number(),
});
export type ReviewerScores = z.infer<typeof ReviewerScoresSchema>;

/** Schema for all scores on a candidate paper. */
export const QualityScoresSchema = z.object({
  candidate_paper_id: z.number(),
  reviewer_scores: z.array(ReviewerScoresSchema),
});
export type QualityScores = z.infer<typeof QualityScoresSchema>;

/** Schema for a single checklist item in a PUT request. */
export const ChecklistItemInputSchema = z.object({
  order: z.number(),
  question: z.string().min(1),
  scoring_method: z.enum(['binary', 'scale_1_3', 'scale_1_5']),
  weight: z.number().min(0),
});
export type ChecklistItemInput = z.infer<typeof ChecklistItemInputSchema>;

/** Schema for PUT /quality-checklist request body. */
export const ChecklistUpsertSchema = z.object({
  name: z.string().min(1),
  description: z.string().nullable().optional(),
  items: z.array(ChecklistItemInputSchema),
});
export type ChecklistUpsert = z.infer<typeof ChecklistUpsertSchema>;

/** Schema for a single score input in a PUT request. */
export const ScoreItemInputSchema = z.object({
  checklist_item_id: z.number(),
  score_value: z.number(),
  notes: z.string().nullable().optional(),
});
export type ScoreItemInput = z.infer<typeof ScoreItemInputSchema>;

/** Schema for PUT /quality-scores request body. */
export const SubmitScoresSchema = z.object({
  reviewer_id: z.number(),
  scores: z.array(ScoreItemInputSchema),
});
export type SubmitScores = z.infer<typeof SubmitScoresSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch the quality assessment checklist for an SLR study.
 *
 * @param studyId - The study integer ID.
 * @returns The parsed {@link Checklist} or throws if not found (404).
 */
export async function getChecklist(studyId: number): Promise<Checklist> {
  const raw = await api.get<unknown>(`/api/v1/slr/studies/${studyId}/quality-checklist`);
  return ChecklistSchema.parse(raw);
}

/**
 * Create or fully replace the quality assessment checklist for an SLR study.
 *
 * @param studyId - The study integer ID.
 * @param data - Checklist name, description, and item definitions.
 * @returns The updated {@link Checklist}.
 */
export async function upsertChecklist(
  studyId: number,
  data: ChecklistUpsert,
): Promise<Checklist> {
  const raw = await api.put<unknown>(
    `/api/v1/slr/studies/${studyId}/quality-checklist`,
    data,
  );
  return ChecklistSchema.parse(raw);
}

/**
 * Fetch all quality assessment scores for a candidate paper.
 *
 * @param candidatePaperId - The candidate paper integer ID.
 * @returns The parsed {@link QualityScores}.
 */
export async function getQualityScores(candidatePaperId: number): Promise<QualityScores> {
  const raw = await api.get<unknown>(
    `/api/v1/slr/papers/${candidatePaperId}/quality-scores`,
  );
  return QualityScoresSchema.parse(raw);
}

/**
 * Submit or update a reviewer's quality assessment scores for a paper.
 *
 * @param candidatePaperId - The candidate paper integer ID.
 * @param data - Reviewer ID and list of scored items.
 * @returns The updated {@link QualityScores}.
 */
export async function submitQualityScores(
  candidatePaperId: number,
  data: SubmitScores,
): Promise<QualityScores> {
  const raw = await api.put<unknown>(
    `/api/v1/slr/papers/${candidatePaperId}/quality-scores`,
    data,
  );
  return QualityScoresSchema.parse(raw);
}
