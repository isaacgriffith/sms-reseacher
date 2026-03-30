/**
 * Rapid Review quality appraisal configuration API service (feature 008).
 *
 * Provides typed fetch functions for getting and setting the quality
 * appraisal mode via GET/PUT /api/v1/rapid/studies/{id}/quality-config.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

/** Zod schema for a threat-to-validity entry. */
export const ThreatSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  threat_type: z.string(),
  description: z.string(),
  source_detail: z.string().nullable(),
  created_at: z.string(),
});
export type Threat = z.infer<typeof ThreatSchema>;

/** Quality appraisal mode union type — matches backend RRQualityAppraisalMode. */
export type QAMode = 'full' | 'peer_reviewed_only' | 'skipped';

/** Zod schema for the quality config response. */
export const QualityConfigResponseSchema = z.object({
  quality_appraisal_mode: z.enum(['full', 'peer_reviewed_only', 'skipped']),
  threats: z.array(ThreatSchema),
});
export type QualityConfigResponse = z.infer<typeof QualityConfigResponseSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch the current quality appraisal configuration for a study.
 *
 * @param studyId - The integer study ID.
 * @returns The validated {@link QualityConfigResponse}.
 */
export async function getQualityConfig(studyId: number): Promise<QualityConfigResponse> {
  const raw = await api.get<unknown>(`/api/v1/rapid/studies/${studyId}/quality-config`);
  return QualityConfigResponseSchema.parse(raw);
}

/**
 * Set the quality appraisal mode for a study.
 *
 * @param studyId - The integer study ID.
 * @param mode - The target quality appraisal mode.
 * @returns The updated {@link QualityConfigResponse}.
 */
export async function setQualityConfig(
  studyId: number,
  mode: QAMode,
): Promise<QualityConfigResponse> {
  const raw = await api.put<unknown>(`/api/v1/rapid/studies/${studyId}/quality-config`, {
    mode,
  });
  return QualityConfigResponseSchema.parse(raw);
}
