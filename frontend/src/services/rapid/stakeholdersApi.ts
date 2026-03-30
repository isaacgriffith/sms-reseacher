/**
 * Rapid Review practitioner stakeholder API service (feature 008).
 *
 * All API responses are validated using Zod schemas at the boundary.
 */

import { z } from 'zod';
import { api } from '../api';

// ---------------------------------------------------------------------------
// Zod schemas
// ---------------------------------------------------------------------------

/** Schema for a practitioner stakeholder. */
export const StakeholderSchema = z.object({
  id: z.number(),
  study_id: z.number(),
  name: z.string(),
  role_title: z.string(),
  organisation: z.string(),
  involvement_type: z.enum(['problem_definer', 'advisor', 'recipient']),
  created_at: z.string(),
  updated_at: z.string(),
});
export type Stakeholder = z.infer<typeof StakeholderSchema>;

/** Schema for creating a stakeholder. */
export const StakeholderCreateSchema = z.object({
  name: z.string().min(1),
  role_title: z.string().min(1),
  organisation: z.string().min(1),
  involvement_type: z.enum(['problem_definer', 'advisor', 'recipient']),
});
export type StakeholderCreate = z.infer<typeof StakeholderCreateSchema>;

/** Schema for updating a stakeholder — all fields optional. */
export const StakeholderUpdateSchema = z.object({
  name: z.string().min(1).optional(),
  role_title: z.string().min(1).optional(),
  organisation: z.string().min(1).optional(),
  involvement_type: z.enum(['problem_definer', 'advisor', 'recipient']).optional(),
});
export type StakeholderUpdate = z.infer<typeof StakeholderUpdateSchema>;

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * List practitioner stakeholders for a study.
 *
 * @param studyId - The integer study ID.
 * @returns List of validated {@link Stakeholder} objects.
 */
export async function listStakeholders(studyId: number): Promise<Stakeholder[]> {
  const raw = await api.get<unknown>(`/api/v1/rapid/studies/${studyId}/stakeholders`);
  return z.array(StakeholderSchema).parse(raw);
}

/**
 * Create a new practitioner stakeholder.
 *
 * @param studyId - The integer study ID.
 * @param data - Stakeholder details.
 * @returns The created {@link Stakeholder}.
 */
export async function createStakeholder(
  studyId: number,
  data: StakeholderCreate,
): Promise<Stakeholder> {
  const raw = await api.post<unknown>(`/api/v1/rapid/studies/${studyId}/stakeholders`, data);
  return StakeholderSchema.parse(raw);
}

/**
 * Update an existing practitioner stakeholder.
 *
 * @param studyId - The integer study ID.
 * @param stakeholderId - The stakeholder to update.
 * @param data - Fields to update.
 * @returns The updated {@link Stakeholder}.
 */
export async function updateStakeholder(
  studyId: number,
  stakeholderId: number,
  data: StakeholderUpdate,
): Promise<Stakeholder> {
  const raw = await api.put<unknown>(
    `/api/v1/rapid/studies/${studyId}/stakeholders/${stakeholderId}`,
    data,
  );
  return StakeholderSchema.parse(raw);
}

/**
 * Delete a practitioner stakeholder.
 *
 * @param studyId - The integer study ID.
 * @param stakeholderId - The stakeholder to delete.
 */
export async function deleteStakeholder(studyId: number, stakeholderId: number): Promise<void> {
  await api.delete<void>(`/api/v1/rapid/studies/${studyId}/stakeholders/${stakeholderId}`);
}
