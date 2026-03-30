/**
 * Rapid Review search configuration API service (feature 008).
 *
 * Provides typed fetch functions for configuring search restrictions
 * and single-reviewer mode via PUT /api/v1/rapid/studies/{id}/search-config.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

export const ThreatSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  threat_type: z.string(),
  description: z.string(),
  source_detail: z.string().nullable(),
  created_at: z.string(),
});

export type Threat = z.infer<typeof ThreatSchema>;

export const SearchRestrictionItemSchema = z.object({
  type: z.string(),
  source_detail: z.string().default(''),
});

export type SearchRestrictionItem = z.infer<typeof SearchRestrictionItemSchema>;

export const SearchConfigRequestSchema = z.object({
  restrictions: z.array(SearchRestrictionItemSchema).default([]),
  single_reviewer_mode: z.boolean().optional(),
  single_source_acknowledged: z.boolean().optional(),
});

export type SearchConfigRequest = z.infer<typeof SearchConfigRequestSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

export async function updateSearchConfig(
  studyId: number,
  data: SearchConfigRequest,
): Promise<Threat[]> {
  const raw = await api.put(`/api/v1/rapid/studies/${studyId}/search-config`, data);
  return z.array(ThreatSchema).parse(raw);
}
