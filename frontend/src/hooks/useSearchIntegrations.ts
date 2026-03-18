/**
 * TanStack Query hooks for the admin search integrations API.
 *
 * Wraps:
 * - GET  /api/v1/admin/search-integrations
 * - GET  /api/v1/admin/search-integrations/{type}
 * - PUT  /api/v1/admin/search-integrations/{type}
 * - POST /api/v1/admin/search-integrations/{type}/test
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

/** Summary record for a single search integration credential. */
export interface SearchIntegrationSummary {
  integration_type: string;
  display_name: string;
  access_type: string;
  has_api_key: boolean;
  has_auxiliary_token: boolean;
  configured_via: 'database' | 'environment' | 'not_configured';
  last_tested_at: string | null;
  last_test_status: string | null;
  version_id: number;
}

/** Request body for PUT /admin/search-integrations/{type}. */
export interface UpdateCredentialRequest {
  api_key?: string | null;
  auxiliary_token?: string | null;
  config_json?: Record<string, unknown> | null;
  version_id?: number | null;
}

/** Variables for the upsert mutation (type + body). */
export interface UpsertCredentialVars {
  integrationType: string;
  body: UpdateCredentialRequest;
}

/** Response from POST /admin/search-integrations/{type}/test. */
export interface TestResult {
  integration_type: string;
  status: string;
  message: string;
  tested_at: string;
}

/** The stable query key for the integration list. */
export const SEARCH_INTEGRATIONS_KEY = ['search-integrations'] as const;

/**
 * Returns the query key for a single integration type.
 *
 * @param integrationType - The integration type string (e.g. "ieee_xplore").
 * @returns TanStack Query key array.
 */
export function searchIntegrationKey(integrationType: string): [string, string] {
  return ['search-integration', integrationType];
}

/**
 * Hook that fetches the list of all search integration credential summaries.
 *
 * @returns TanStack Query result with `data: SearchIntegrationSummary[]`.
 */
export function useSearchIntegrations() {
  return useQuery<SearchIntegrationSummary[]>({
    queryKey: SEARCH_INTEGRATIONS_KEY,
    queryFn: () => api.get<SearchIntegrationSummary[]>('/api/v1/admin/search-integrations'),
  });
}

/**
 * Hook that fetches a single search integration credential summary.
 *
 * @param integrationType - The integration type to fetch.
 * @returns TanStack Query result with `data: SearchIntegrationSummary`.
 */
export function useSearchIntegration(integrationType: string) {
  return useQuery<SearchIntegrationSummary>({
    queryKey: searchIntegrationKey(integrationType),
    queryFn: () =>
      api.get<SearchIntegrationSummary>(
        `/api/v1/admin/search-integrations/${integrationType}`
      ),
    enabled: !!integrationType,
  });
}

/**
 * Mutation hook for creating or updating a search integration credential.
 *
 * Invalidates the integrations list query on success.
 *
 * @returns TanStack Query mutation with `mutate({ integrationType, body })`.
 */
export function useUpsertCredential() {
  const queryClient = useQueryClient();
  return useMutation<SearchIntegrationSummary, Error, UpsertCredentialVars>({
    mutationFn: ({ integrationType, body }) =>
      api.put<SearchIntegrationSummary>(
        `/api/v1/admin/search-integrations/${integrationType}`,
        body
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SEARCH_INTEGRATIONS_KEY });
    },
  });
}

/**
 * Mutation hook for running a live connectivity test on an integration.
 *
 * Invalidates the integrations list query on success so last_tested_at refreshes.
 *
 * @returns TanStack Query mutation with `mutate(integrationType)`.
 */
export function useTestIntegration() {
  const queryClient = useQueryClient();
  return useMutation<TestResult, Error, string>({
    mutationFn: (integrationType: string) =>
      api.post<TestResult>(
        `/api/v1/admin/search-integrations/${integrationType}/test`,
        {}
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SEARCH_INTEGRATIONS_KEY });
    },
  });
}
