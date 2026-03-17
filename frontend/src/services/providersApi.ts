/**
 * TanStack Query hooks and API client functions for provider and model
 * management endpoints (Feature 005).
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from '@tanstack/react-query';
import { api } from './api';
import {
  AvailableModelSchema,
  ModelRefreshResultSchema,
  ProviderSchema,
  type AvailableModel,
  type ModelRefreshResult,
  type Provider,
  type ProviderCreate,
  type ProviderUpdate,
} from '../types/provider';
import { z } from 'zod';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

const PROVIDERS_KEY = ['admin', 'providers'] as const;
const providerKey = (id: string) => [...PROVIDERS_KEY, id] as const;
const modelsKey = (providerId: string) => [...PROVIDERS_KEY, providerId, 'models'] as const;

// ---------------------------------------------------------------------------
// Read hooks
// ---------------------------------------------------------------------------

/**
 * Fetch all configured LLM providers.
 *
 * @returns TanStack Query result with a parsed list of {@link Provider} objects.
 */
export function useProviders(): UseQueryResult<Provider[]> {
  return useQuery<Provider[]>({
    queryKey: PROVIDERS_KEY,
    queryFn: async () => {
      const raw = await api.get<unknown>('/api/v1/admin/providers');
      return z.array(ProviderSchema).parse(raw);
    },
  });
}

/**
 * Fetch a single provider by ID.
 *
 * @param id - UUID of the provider to fetch.
 * @returns TanStack Query result with a parsed {@link Provider}.
 */
export function useProvider(id: string): UseQueryResult<Provider> {
  return useQuery<Provider>({
    queryKey: providerKey(id),
    queryFn: async () => {
      const raw = await api.get<unknown>(`/api/v1/admin/providers/${id}`);
      return ProviderSchema.parse(raw);
    },
    enabled: Boolean(id),
  });
}

/**
 * Fetch all available models for a specific provider.
 *
 * @param providerId - UUID of the provider.
 * @returns TanStack Query result with a parsed list of {@link AvailableModel} objects.
 */
export function useProviderModels(providerId: string): UseQueryResult<AvailableModel[]> {
  return useQuery<AvailableModel[]>({
    queryKey: modelsKey(providerId),
    queryFn: async () => {
      const raw = await api.get<unknown>(`/api/v1/admin/providers/${providerId}/models`);
      return z.array(AvailableModelSchema).parse(raw);
    },
    enabled: Boolean(providerId),
  });
}

// ---------------------------------------------------------------------------
// Write hooks
// ---------------------------------------------------------------------------

/**
 * Create a new LLM provider.
 *
 * Invalidates the providers list query on success.
 *
 * @returns Mutation result yielding the newly created {@link Provider}.
 */
export function useCreateProvider(): UseMutationResult<Provider, Error, ProviderCreate> {
  const qc = useQueryClient();
  return useMutation<Provider, Error, ProviderCreate>({
    mutationFn: async (body) => {
      const raw = await api.post<unknown>('/api/v1/admin/providers', body);
      return ProviderSchema.parse(raw);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PROVIDERS_KEY });
    },
  });
}

/**
 * Partially update an existing provider.
 *
 * Invalidates the providers list and the specific provider query on success.
 *
 * @returns Mutation result yielding the updated {@link Provider}.
 */
export function useUpdateProvider(): UseMutationResult<
  Provider,
  Error,
  { id: string; data: ProviderUpdate }
> {
  const qc = useQueryClient();
  return useMutation<Provider, Error, { id: string; data: ProviderUpdate }>({
    mutationFn: async ({ id, data }) => {
      const raw = await api.patch<unknown>(`/api/v1/admin/providers/${id}`, data);
      return ProviderSchema.parse(raw);
    },
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: PROVIDERS_KEY });
      qc.invalidateQueries({ queryKey: providerKey(id) });
    },
  });
}

/**
 * Delete a provider by ID.
 *
 * Invalidates the providers list on success.
 *
 * @returns Mutation result (void on success).
 */
export function useDeleteProvider(): UseMutationResult<void, Error, string> {
  const qc = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => api.delete<void>(`/api/v1/admin/providers/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PROVIDERS_KEY });
    },
  });
}

/**
 * Trigger a model-list refresh for a provider.
 *
 * Invalidates the model list query for the provider on success.
 *
 * @returns Mutation result yielding a {@link ModelRefreshResult}.
 */
export function useRefreshModels(): UseMutationResult<ModelRefreshResult, Error, string> {
  const qc = useQueryClient();
  return useMutation<ModelRefreshResult, Error, string>({
    mutationFn: async (providerId) => {
      const raw = await api.post<unknown>(
        `/api/v1/admin/providers/${providerId}/refresh-models`,
        {},
      );
      return ModelRefreshResultSchema.parse(raw);
    },
    onSuccess: (_, providerId) => {
      qc.invalidateQueries({ queryKey: modelsKey(providerId) });
    },
  });
}

/**
 * Toggle the enabled state of a model.
 *
 * Invalidates the model list for the owning provider on success.
 *
 * @returns Mutation result yielding the updated {@link AvailableModel}.
 */
export function useToggleModel(): UseMutationResult<
  AvailableModel,
  Error,
  { providerId: string; modelId: string; is_enabled: boolean }
> {
  const qc = useQueryClient();
  return useMutation<
    AvailableModel,
    Error,
    { providerId: string; modelId: string; is_enabled: boolean }
  >({
    mutationFn: async ({ providerId, modelId, is_enabled }) => {
      const raw = await api.patch<unknown>(
        `/api/v1/admin/providers/${providerId}/models/${modelId}`,
        { is_enabled },
      );
      return AvailableModelSchema.parse(raw);
    },
    onSuccess: (_, { providerId }) => {
      qc.invalidateQueries({ queryKey: modelsKey(providerId) });
    },
  });
}
