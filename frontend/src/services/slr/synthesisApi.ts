/**
 * API client for SLR data synthesis endpoints (feature 007).
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
 * Schema for a single synthesis result record.
 */
export const SynthesisResultSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  approach: z.string(),
  status: z.string(),
  model_type: z.string().nullable(),
  parameters: z.record(z.unknown()).nullable(),
  computed_statistics: z.record(z.unknown()).nullable(),
  forest_plot_svg: z.string().nullable(),
  funnel_plot_svg: z.string().nullable(),
  qualitative_themes: z.record(z.unknown()).nullable(),
  sensitivity_analysis: z.record(z.unknown()).nullable(),
  error_message: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type SynthesisResult = z.infer<typeof SynthesisResultSchema>;

/**
 * Schema for the list response.
 */
export const SynthesisListSchema = z.object({
  results: z.array(SynthesisResultSchema),
});

export type SynthesisList = z.infer<typeof SynthesisListSchema>;

/**
 * Request body for starting a new synthesis run.
 */
export interface StartSynthesisBody {
  approach: string;
  parameters: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch all synthesis results for a study.
 *
 * @param studyId - The integer study ID.
 * @returns A {@link SynthesisList} containing all results.
 */
export async function listSynthesisResults(studyId: number): Promise<SynthesisList> {
  const raw = await api.get<unknown>(`/api/v1/slr/studies/${studyId}/synthesis`);
  return SynthesisListSchema.parse(raw);
}

/**
 * Start a new synthesis run for a study.
 *
 * @param studyId - The integer study ID.
 * @param body - Approach and optional parameters.
 * @returns The newly created {@link SynthesisResult} with status "pending".
 */
export async function startSynthesis(
  studyId: number,
  body: StartSynthesisBody,
): Promise<SynthesisResult> {
  const raw = await api.post<unknown>(`/api/v1/slr/studies/${studyId}/synthesis`, body);
  return SynthesisResultSchema.parse(raw);
}

/**
 * Fetch a single synthesis result by ID.
 *
 * @param synthesisId - The integer synthesis result ID.
 * @returns The {@link SynthesisResult}.
 */
export async function getSynthesisResult(synthesisId: number): Promise<SynthesisResult> {
  const raw = await api.get<unknown>(`/api/v1/slr/synthesis/${synthesisId}`);
  return SynthesisResultSchema.parse(raw);
}
