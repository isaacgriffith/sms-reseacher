/**
 * Rapid Review evidence briefing API service (feature 008).
 *
 * All API responses are validated using Zod schemas at the boundary.
 * Functions throw {@link ApiError} on non-2xx responses.
 */

import { z } from 'zod';
import { api, ApiError } from '../api';
import { getToken } from '../auth';

export { ApiError };

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for a briefing list entry. */
export const BriefingSummarySchema = z.object({
  id: z.number(),
  study_id: z.number(),
  version_number: z.number(),
  status: z.enum(['draft', 'published']),
  title: z.string(),
  generated_at: z.string().nullable(),
  pdf_available: z.boolean(),
  html_available: z.boolean(),
});
export type BriefingSummary = z.infer<typeof BriefingSummarySchema>;

/** Schema for a full briefing with content sections. */
export const BriefingDetailSchema = BriefingSummarySchema.extend({
  summary: z.string().nullable(),
  findings: z.record(z.string(), z.string()),
  target_audience: z.string().nullable(),
  reference_complementary: z.string().nullable(),
  institution_logos: z.array(z.string()),
});
export type BriefingDetail = z.infer<typeof BriefingDetailSchema>;

/** Schema for a share token. */
export const ShareTokenSchema = z.object({
  token: z.string(),
  share_url: z.string(),
  briefing_id: z.number(),
  created_at: z.string(),
  revoked_at: z.string().nullable(),
  expires_at: z.string().nullable(),
});
export type ShareToken = z.infer<typeof ShareTokenSchema>;

/** Schema for the generate briefing job response. */
export const GenerateBriefingResponseSchema = z.object({
  job_id: z.string(),
  status: z.string(),
  estimated_version_number: z.number(),
});
export type GenerateBriefingResponse = z.infer<typeof GenerateBriefingResponseSchema>;

/** Schema for the public briefing (unauthenticated access). */
export const PublicBriefingSchema = BriefingDetailSchema.extend({
  threats: z.array(
    z.object({
      threat_type: z.string(),
      description: z.string(),
      source_detail: z.string().nullable(),
    }),
  ),
});
export type PublicBriefing = z.infer<typeof PublicBriefingSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

const BASE_URL = import.meta.env.VITE_API_URL ?? '';

/**
 * List all evidence briefing versions for a study.
 *
 * @param studyId - The integer study ID.
 * @returns List of validated {@link BriefingSummary} objects.
 */
export async function listBriefings(studyId: number): Promise<BriefingSummary[]> {
  const raw = await api.get<unknown>(`/api/v1/rapid/studies/${studyId}/briefings`);
  return z.array(BriefingSummarySchema).parse(raw);
}

/**
 * Enqueue an evidence briefing generation job.
 *
 * @param studyId - The integer study ID.
 * @returns {@link GenerateBriefingResponse} with the enqueued job ID.
 */
export async function generateBriefing(studyId: number): Promise<GenerateBriefingResponse> {
  const raw = await api.post<unknown>(`/api/v1/rapid/studies/${studyId}/briefings/generate`, {});
  return GenerateBriefingResponseSchema.parse(raw);
}

/**
 * Fetch a single briefing's full detail.
 *
 * @param studyId - The integer study ID.
 * @param briefingId - The briefing primary key.
 * @returns Validated {@link BriefingDetail}.
 */
export async function getBriefing(studyId: number, briefingId: number): Promise<BriefingDetail> {
  const raw = await api.get<unknown>(`/api/v1/rapid/studies/${studyId}/briefings/${briefingId}`);
  return BriefingDetailSchema.parse(raw);
}

/**
 * Publish a draft briefing.
 *
 * @param studyId - The integer study ID.
 * @param briefingId - The briefing primary key.
 * @returns Updated {@link BriefingDetail} with status 'published'.
 */
export async function publishBriefing(
  studyId: number,
  briefingId: number,
): Promise<BriefingDetail> {
  const raw = await api.post<unknown>(
    `/api/v1/rapid/studies/${studyId}/briefings/${briefingId}/publish`,
    {},
  );
  return BriefingDetailSchema.parse(raw);
}

/**
 * Export a briefing as PDF or HTML, returning a raw binary Blob.
 *
 * Uses a direct fetch call (not the api wrapper) since the response is binary.
 *
 * @param studyId - The integer study ID.
 * @param briefingId - The briefing primary key.
 * @param format - Export format: 'pdf' or 'html'.
 * @returns Binary {@link Blob} of the exported file.
 */
export async function exportBriefing(
  studyId: number,
  briefingId: number,
  format: 'pdf' | 'html',
): Promise<Blob> {
  const resp = await fetch(
    `${BASE_URL}/api/v1/rapid/studies/${studyId}/briefings/${briefingId}/export?format=${format}`,
    {
      headers: { Authorization: `Bearer ${getToken() ?? ''}` },
    },
  );
  if (!resp.ok) throw new ApiError(resp.status, resp.statusText);
  return resp.blob();
}

/**
 * Create a share token for a published briefing.
 *
 * @param studyId - The integer study ID.
 * @param briefingId - The briefing primary key.
 * @returns Validated {@link ShareToken}.
 */
export async function createShareToken(studyId: number, briefingId: number): Promise<ShareToken> {
  const raw = await api.post<unknown>(
    `/api/v1/rapid/studies/${studyId}/briefings/${briefingId}/share`,
    {},
  );
  return ShareTokenSchema.parse(raw);
}

/**
 * Revoke an active share token.
 *
 * @param studyId - The integer study ID.
 * @param token - The share token string to revoke.
 */
export async function revokeShareToken(studyId: number, token: string): Promise<void> {
  await api.delete<void>(`/api/v1/rapid/studies/${studyId}/briefings/share/${token}/revoke`);
}

/**
 * Fetch a public briefing using a share token (no authentication required).
 *
 * @param token - The share token string.
 * @returns Validated {@link PublicBriefing}.
 */
export async function getPublicBriefing(token: string): Promise<PublicBriefing> {
  const resp = await fetch(`${BASE_URL}/api/v1/public/briefings/${token}`);
  if (!resp.ok) throw new ApiError(resp.status, resp.statusText);
  const raw: unknown = await resp.json();
  return PublicBriefingSchema.parse(raw);
}

/**
 * Export a public briefing using a share token (no authentication required).
 *
 * @param token - The share token string.
 * @param format - Export format: 'pdf' or 'html'.
 * @returns Binary {@link Blob} of the exported file.
 */
export async function exportPublicBriefing(token: string, format: 'pdf' | 'html'): Promise<Blob> {
  const resp = await fetch(`${BASE_URL}/api/v1/public/briefings/${token}/export?format=${format}`);
  if (!resp.ok) throw new ApiError(resp.status, resp.statusText);
  return resp.blob();
}
