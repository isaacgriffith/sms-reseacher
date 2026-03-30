/**
 * Tertiary Study seed-import API service (feature 009).
 *
 * All API responses are validated using Zod schemas at the boundary.
 * Functions throw {@link ApiError} on non-2xx responses.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for a single seed import summary (list item). */
export const SeedImportSummarySchema = z.object({
  id: z.number(),
  target_study_id: z.number(),
  source_study_id: z.number(),
  source_study_title: z.string().nullable(),
  source_study_type: z.string().nullable(),
  imported_at: z.string(),
  records_added: z.number(),
  records_skipped: z.number(),
  imported_by_user_id: z.number().nullable(),
});
export type SeedImportSummary = z.infer<typeof SeedImportSummarySchema>;

/** Schema for the POST /seed-imports 201 response. */
export const SeedImportCreatedSchema = z.object({
  id: z.number(),
  records_added: z.number(),
  records_skipped: z.number(),
  imported_at: z.string(),
});
export type SeedImportCreated = z.infer<typeof SeedImportCreatedSchema>;

/** Schema for a study listed as an available import source. */
export const StudySummarySchema = z.object({
  id: z.number(),
  name: z.string(),
  topic: z.string().nullable(),
  study_type: z.string(),
  status: z.string(),
  current_phase: z.number(),
  created_at: z.string(),
});
export type StudySummary = z.infer<typeof StudySummarySchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * List all seed import records for a Tertiary Study.
 *
 * @param studyId - The integer study ID.
 * @returns Array of {@link SeedImportSummary}.
 */
export async function listSeedImports(studyId: number): Promise<SeedImportSummary[]> {
  const raw = await api.get<unknown[]>(`/api/v1/tertiary/studies/${studyId}/seed-imports`);
  return raw.map((item) => SeedImportSummarySchema.parse(item));
}

/**
 * Import included papers from a source study into this Tertiary Study.
 *
 * @param studyId - The target Tertiary Study ID.
 * @param sourceStudyId - The source study to import from.
 * @returns The created {@link SeedImportCreated} record.
 */
export async function createSeedImport(
  studyId: number,
  sourceStudyId: number,
): Promise<SeedImportCreated> {
  const raw = await api.post<unknown>(
    `/api/v1/tertiary/studies/${studyId}/seed-imports`,
    { source_study_id: sourceStudyId },
  );
  return SeedImportCreatedSchema.parse(raw);
}

/**
 * List all studies in a group to find available import sources.
 *
 * @param groupId - The research group ID.
 * @returns Array of {@link StudySummary}.
 */
export async function listGroupStudies(groupId: number): Promise<StudySummary[]> {
  const raw = await api.get<unknown[]>(`/api/v1/groups/${groupId}/studies`);
  return raw.map((item) => StudySummarySchema.parse(item));
}
