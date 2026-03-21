/**
 * API client for SLR grey literature CRUD endpoints (feature 007, Phase 8).
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
 * Schema for a single grey literature source.
 */
export const GreyLiteratureSourceSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  source_type: z.string(),
  title: z.string(),
  authors: z.string().nullable(),
  year: z.number().nullable(),
  url: z.string().nullable(),
  description: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type GreyLiteratureSource = z.infer<typeof GreyLiteratureSourceSchema>;

/**
 * Schema for the list response.
 */
export const GreyLiteratureListSchema = z.object({
  sources: z.array(GreyLiteratureSourceSchema),
});

export type GreyLiteratureList = z.infer<typeof GreyLiteratureListSchema>;

/**
 * Request body for creating a grey literature source.
 */
export interface CreateGreyLiteratureBody {
  source_type: string;
  title: string;
  authors?: string | null;
  year?: number | null;
  url?: string | null;
  description?: string | null;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch all grey literature sources for a study.
 *
 * @param studyId - The integer study ID.
 * @returns The {@link GreyLiteratureList} for the study.
 */
export async function listGreyLiterature(studyId: number): Promise<GreyLiteratureList> {
  const raw = await api.get<unknown>(`/api/v1/slr/studies/${studyId}/grey-literature`);
  return GreyLiteratureListSchema.parse(raw);
}

/**
 * Add a new grey literature source to a study.
 *
 * @param studyId - The integer study ID.
 * @param body - Source fields to create.
 * @returns The newly created {@link GreyLiteratureSource}.
 */
export async function addGreyLiteratureSource(
  studyId: number,
  body: CreateGreyLiteratureBody,
): Promise<GreyLiteratureSource> {
  const raw = await api.post<unknown>(
    `/api/v1/slr/studies/${studyId}/grey-literature`,
    body,
  );
  return GreyLiteratureSourceSchema.parse(raw);
}

/**
 * Delete a grey literature source from a study.
 *
 * @param studyId - The integer study ID.
 * @param sourceId - The integer source ID to delete.
 */
export async function deleteGreyLiteratureSource(
  studyId: number,
  sourceId: number,
): Promise<void> {
  await api.delete(`/api/v1/slr/studies/${studyId}/grey-literature/${sourceId}`);
}
