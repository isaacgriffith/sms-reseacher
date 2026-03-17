/**
 * Zod schemas and inferred TypeScript types for LLM Provider and AvailableModel
 * entities (Feature 005).
 *
 * Provider type is represented as a string literal union — no TypeScript enum.
 */

import { z } from 'zod';

/** String literal union of valid provider backend types. */
export const ProviderTypeSchema = z.union([
  z.literal('anthropic'),
  z.literal('openai'),
  z.literal('ollama'),
]);

/** Inferred TypeScript type for a provider backend type. */
export type ProviderType = z.infer<typeof ProviderTypeSchema>;

/** Zod schema for a Provider record as returned by the API. */
export const ProviderSchema = z.object({
  id: z.string().uuid(),
  provider_type: ProviderTypeSchema,
  display_name: z.string(),
  has_api_key: z.boolean(),
  base_url: z.string().nullable(),
  is_enabled: z.boolean(),
  version_id: z.number().int(),
});

/** Inferred TypeScript type for a Provider record. */
export type Provider = z.infer<typeof ProviderSchema>;

/** Zod schema for the provider creation request body. */
export const ProviderCreateSchema = z.object({
  provider_type: ProviderTypeSchema,
  display_name: z.string().min(1),
  api_key: z.string().optional(),
  base_url: z.string().optional(),
  is_enabled: z.boolean().default(true),
});

/** Inferred TypeScript type for a provider creation payload. */
export type ProviderCreate = z.infer<typeof ProviderCreateSchema>;

/** Zod schema for the provider partial-update request body. */
export const ProviderUpdateSchema = z.object({
  display_name: z.string().min(1).optional(),
  api_key: z.string().optional(),
  base_url: z.string().optional(),
  is_enabled: z.boolean().optional(),
});

/** Inferred TypeScript type for a provider update payload. */
export type ProviderUpdate = z.infer<typeof ProviderUpdateSchema>;

/** Zod schema for an AvailableModel record as returned by the API. */
export const AvailableModelSchema = z.object({
  id: z.string().uuid(),
  provider_id: z.string().uuid(),
  model_identifier: z.string(),
  display_name: z.string(),
  is_enabled: z.boolean(),
  version_id: z.number().int(),
});

/** Inferred TypeScript type for an AvailableModel record. */
export type AvailableModel = z.infer<typeof AvailableModelSchema>;

/** Zod schema for a model-refresh result. */
export const ModelRefreshResultSchema = z.object({
  models_added: z.number().int(),
  models_removed: z.number().int(),
  models_total: z.number().int(),
});

/** Inferred TypeScript type for a model-refresh result. */
export type ModelRefreshResult = z.infer<typeof ModelRefreshResultSchema>;

/** Zod schema for the model toggle request body. */
export const ModelToggleSchema = z.object({
  is_enabled: z.boolean(),
});

/** Inferred TypeScript type for a model toggle payload. */
export type ModelToggle = z.infer<typeof ModelToggleSchema>;
