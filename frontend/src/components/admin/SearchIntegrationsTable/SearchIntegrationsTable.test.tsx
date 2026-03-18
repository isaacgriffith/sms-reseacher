/**
 * Tests for SearchIntegrationsTable component.
 *
 * Mocks TanStack Query hooks to verify:
 * - Loading state renders a spinner
 * - Table renders integration display names
 * - "configured" badge shown for database/environment-sourced credentials
 * - "not_configured" badge shown for missing credentials
 * - Masked key indicator "••••" shown when has_api_key=true
 * - "Test Now" button rendered for each row
 * - Clicking Test Now calls the test mutation
 * - Edit modal opens and submit calls upsert mutation
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the hooks module
vi.mock('../../../hooks/useSearchIntegrations', () => ({
  useSearchIntegrations: vi.fn(),
  useUpsertCredential: vi.fn(),
  useTestIntegration: vi.fn(),
  SEARCH_INTEGRATIONS_KEY: ['search-integrations'],
  searchIntegrationKey: (t: string) => ['search-integration', t],
}));

import {
  useSearchIntegrations,
  useUpsertCredential,
  useTestIntegration,
} from '../../../hooks/useSearchIntegrations';
import SearchIntegrationsTable from './index';

const mockUseSearchIntegrations = useSearchIntegrations as ReturnType<typeof vi.fn>;
const mockUseUpsertCredential = useUpsertCredential as ReturnType<typeof vi.fn>;
const mockUseTestIntegration = useTestIntegration as ReturnType<typeof vi.fn>;

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const MOCK_INTEGRATIONS = [
  {
    integration_type: 'ieee_xplore',
    display_name: 'IEEE Xplore',
    access_type: 'official_api',
    has_api_key: true,
    has_auxiliary_token: false,
    configured_via: 'database',
    last_tested_at: '2026-03-17T10:00:00Z',
    last_test_status: 'success',
    version_id: 2,
  },
  {
    integration_type: 'elsevier',
    display_name: 'Elsevier (Scopus/SciDirect/Inspec)',
    access_type: 'subscription_required',
    has_api_key: false,
    has_auxiliary_token: false,
    configured_via: 'not_configured',
    last_tested_at: null,
    last_test_status: null,
    version_id: 1,
  },
];

describe('SearchIntegrationsTable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseUpsertCredential.mockReturnValue({ mutate: vi.fn(), isPending: false });
    mockUseTestIntegration.mockReturnValue({ mutate: vi.fn(), isPending: false });
  });

  describe('loading state', () => {
    it('renders a spinner while loading', () => {
      mockUseSearchIntegrations.mockReturnValue({ data: [], isLoading: true });
      renderWithQuery(<SearchIntegrationsTable />);
      expect(document.querySelector('[role="progressbar"]')).toBeTruthy();
    });
  });

  describe('loaded state', () => {
    beforeEach(() => {
      mockUseSearchIntegrations.mockReturnValue({
        data: MOCK_INTEGRATIONS,
        isLoading: false,
      });
    });

    it('renders integration display names', () => {
      renderWithQuery(<SearchIntegrationsTable />);
      expect(screen.getByText('IEEE Xplore')).toBeTruthy();
      expect(screen.getByText('Elsevier (Scopus/SciDirect/Inspec)')).toBeTruthy();
    });

    it('shows "database" badge for configured integration', () => {
      renderWithQuery(<SearchIntegrationsTable />);
      expect(screen.getByText('database')).toBeTruthy();
    });

    it('shows "not_configured" badge for unconfigured integration', () => {
      renderWithQuery(<SearchIntegrationsTable />);
      expect(screen.getByText('not_configured')).toBeTruthy();
    });

    it('shows masked key indicator for row with has_api_key=true', () => {
      renderWithQuery(<SearchIntegrationsTable />);
      expect(screen.getByText('••••')).toBeTruthy();
    });

    it('shows em-dash when no key stored', () => {
      renderWithQuery(<SearchIntegrationsTable />);
      const dashes = screen.getAllByText('—');
      expect(dashes.length).toBeGreaterThan(0);
    });

    it('renders Test Now button for each row', () => {
      renderWithQuery(<SearchIntegrationsTable />);
      const buttons = screen.getAllByRole('button', { name: /test now/i });
      expect(buttons).toHaveLength(MOCK_INTEGRATIONS.length);
    });

    it('calls test mutation when Test Now is clicked', async () => {
      const testMutate = vi.fn();
      mockUseTestIntegration.mockReturnValue({ mutate: testMutate, isPending: false });
      renderWithQuery(<SearchIntegrationsTable />);
      const [firstTestBtn] = screen.getAllByRole('button', { name: /test now/i });
      fireEvent.click(firstTestBtn);
      await waitFor(() => {
        expect(testMutate).toHaveBeenCalledWith('ieee_xplore');
      });
    });

    it('renders Edit button for each row', () => {
      renderWithQuery(<SearchIntegrationsTable />);
      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      expect(editButtons).toHaveLength(MOCK_INTEGRATIONS.length);
    });

    it('opens edit modal when Edit is clicked', async () => {
      renderWithQuery(<SearchIntegrationsTable />);
      const [firstEditBtn] = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(firstEditBtn);
      await waitFor(() => {
        expect(screen.getByText(/edit credential/i)).toBeTruthy();
      });
    });

    it('calls upsert mutation on Save', async () => {
      const upsertMutate = vi.fn((_vars, { onSuccess }: { onSuccess: () => void }) =>
        onSuccess()
      );
      mockUseUpsertCredential.mockReturnValue({ mutate: upsertMutate, isPending: false });
      renderWithQuery(<SearchIntegrationsTable />);
      const [firstEditBtn] = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(firstEditBtn);
      await waitFor(() => screen.getByRole('dialog'));
      const saveBtn = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveBtn);
      await waitFor(() => {
        expect(upsertMutate).toHaveBeenCalled();
      });
    });
  });
});
