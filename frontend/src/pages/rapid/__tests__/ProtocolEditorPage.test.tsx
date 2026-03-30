/**
 * Unit tests for ProtocolEditorPage (feature 008).
 *
 * Covers loading state, error state, protocol rendering, stepper,
 * validated banner, Validate Protocol button, and mutation errors.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProtocolEditorPage from '../ProtocolEditorPage';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/rapid/useRRProtocol', () => ({
  useRRProtocol: vi.fn(),
  useUpdateRRProtocol: vi.fn(),
  useValidateRRProtocol: vi.fn(),
}));

vi.mock('../../../components/rapid/ProtocolForm', () => ({
  default: ({ protocol }: { protocol: { id: number }; studyId: number; readOnly: boolean; onSubmit: (d: unknown) => void; isSaving: boolean }) => (
    <div data-testid="protocol-form">Protocol Form (id={protocol.id})</div>
  ),
}));

import {
  useRRProtocol,
  useUpdateRRProtocol,
  useValidateRRProtocol,
} from '../../../hooks/rapid/useRRProtocol';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const BASE_PROTOCOL = {
  id: 1,
  study_id: 42,
  status: 'draft' as const,
  practical_problem: 'A problem',
  research_questions: ['RQ1'],
  time_budget_days: null,
  effort_budget_hours: null,
  context_restrictions: null,
  dissemination_medium: null,
  problem_scoping_notes: null,
  search_strategy_notes: null,
  inclusion_criteria: null,
  exclusion_criteria: null,
  single_reviewer_mode: false,
  single_source_acknowledged: false,
  quality_appraisal_mode: 'full' as const,
  version_id: 1,
  research_gap_warnings: [],
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

function setupDefaultMocks() {
  vi.mocked(useRRProtocol).mockReturnValue({ data: BASE_PROTOCOL, isLoading: false, error: null } as ReturnType<typeof useRRProtocol>);
  vi.mocked(useUpdateRRProtocol).mockReturnValue({
    mutation: { mutate: vi.fn(), isPending: false, isError: false, error: null },
    invalidationPending: null,
    confirmInvalidation: vi.fn(),
    cancelInvalidation: vi.fn(),
  } as ReturnType<typeof useUpdateRRProtocol>);
  vi.mocked(useValidateRRProtocol).mockReturnValue({ mutate: vi.fn(), isPending: false, isError: false, error: null } as ReturnType<typeof useValidateRRProtocol>);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ProtocolEditorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  describe('loading state', () => {
    it('shows loading indicator when protocol is loading', () => {
      vi.mocked(useRRProtocol).mockReturnValue({ data: undefined, isLoading: true, error: null } as ReturnType<typeof useRRProtocol>);
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByText(/loading protocol/i)).toBeTruthy();
    });
  });

  describe('error state', () => {
    it('shows error alert when protocol load fails', () => {
      vi.mocked(useRRProtocol).mockReturnValue({ data: undefined, isLoading: false, error: new Error('fail') } as ReturnType<typeof useRRProtocol>);
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByText(/failed to load the protocol/i)).toBeTruthy();
    });

    it('shows error alert when protocol is undefined after load', () => {
      vi.mocked(useRRProtocol).mockReturnValue({ data: undefined, isLoading: false, error: null } as ReturnType<typeof useRRProtocol>);
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByText(/failed to load the protocol/i)).toBeTruthy();
    });
  });

  describe('normal rendering', () => {
    it('renders the stepper with Draft and Validated labels', () => {
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByText('Draft')).toBeTruthy();
      expect(screen.getByText('Validated')).toBeTruthy();
    });

    it('renders ProtocolForm with the protocol', () => {
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByTestId('protocol-form')).toBeTruthy();
    });

    it('renders Validate Protocol button for draft protocol', () => {
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByRole('button', { name: /validate protocol/i })).toBeTruthy();
    });
  });

  describe('validated protocol', () => {
    it('shows validated banner when protocol status is validated', () => {
      vi.mocked(useRRProtocol).mockReturnValue({ data: { ...BASE_PROTOCOL, status: 'validated' }, isLoading: false, error: null } as ReturnType<typeof useRRProtocol>);
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByText(/protocol is validated/i)).toBeTruthy();
    });

    it('does not render Validate Protocol button when protocol is validated', () => {
      vi.mocked(useRRProtocol).mockReturnValue({ data: { ...BASE_PROTOCOL, status: 'validated' }, isLoading: false, error: null } as ReturnType<typeof useRRProtocol>);
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.queryByRole('button', { name: /validate protocol/i })).toBeNull();
    });
  });

  describe('mutation error states', () => {
    it('shows update error alert when updateMutation.isError is true', () => {
      vi.mocked(useUpdateRRProtocol).mockReturnValue({
        mutation: { mutate: vi.fn(), isPending: false, isError: true, error: new Error('Save failed') },
        invalidationPending: null,
        confirmInvalidation: vi.fn(),
        cancelInvalidation: vi.fn(),
      } as ReturnType<typeof useUpdateRRProtocol>);
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByText(/save failed/i)).toBeTruthy();
    });

    it('shows validate error alert when validateMutation.isError is true', () => {
      vi.mocked(useValidateRRProtocol).mockReturnValue({ mutate: vi.fn(), isPending: false, isError: true, error: new Error('Validation failed') } as ReturnType<typeof useValidateRRProtocol>);
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByText(/validation failed/i)).toBeTruthy();
    });
  });

  describe('invalidation dialog', () => {
    it('shows invalidation dialog when invalidationPending is set', () => {
      vi.mocked(useUpdateRRProtocol).mockReturnValue({
        mutation: { mutate: vi.fn(), isPending: false, isError: false, error: null },
        invalidationPending: { papersAtRisk: 3 },
        confirmInvalidation: vi.fn(),
        cancelInvalidation: vi.fn(),
      } as ReturnType<typeof useUpdateRRProtocol>);
      renderWithQuery(<ProtocolEditorPage studyId={42} />);
      expect(screen.getByText(/confirm protocol edit/i)).toBeTruthy();
      expect(screen.getByText(/3 paper\(s\)/i)).toBeTruthy();
    });
  });
});
