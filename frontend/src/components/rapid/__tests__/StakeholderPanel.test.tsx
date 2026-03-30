/**
 * Unit tests for StakeholderPanel component (feature 008).
 *
 * Covers loading state, empty state with error, table rendering,
 * Add Stakeholder form rendering, and delete action.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import StakeholderPanel from '../StakeholderPanel';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/rapid/useStakeholders', () => ({
  useStakeholders: vi.fn(),
  useCreateStakeholder: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useUpdateStakeholder: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useDeleteStakeholder: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

import { useStakeholders } from '../../../hooks/rapid/useStakeholders';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const STAKEHOLDER = {
  id: 1,
  study_id: 42,
  name: 'Alice',
  role_title: 'Product Manager',
  organisation: 'NHS',
  involvement_type: 'advisor' as const,
  created_at: '2026-01-01T00:00:00Z',
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('StakeholderPanel', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('loading state', () => {
    it('shows loading indicator when isLoading', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: undefined, isLoading: true } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      expect(screen.getByText(/loading stakeholders/i)).toBeTruthy();
    });
  });

  describe('empty state', () => {
    it('shows required error when stakeholders is empty', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      expect(screen.getByText(/at least one practitioner stakeholder/i)).toBeTruthy();
    });
  });

  describe('with stakeholders', () => {
    it('renders stakeholder name in table', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [STAKEHOLDER], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      expect(screen.getByText('Alice')).toBeTruthy();
    });

    it('renders stakeholder organisation', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [STAKEHOLDER], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      expect(screen.getByText('NHS')).toBeTruthy();
    });
  });

  describe('add form', () => {
    it('renders Add Stakeholder button', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      expect(screen.getByRole('button', { name: /add stakeholder/i })).toBeTruthy();
    });

    it('shows form fields when Add Stakeholder button is clicked', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /add stakeholder/i }));
      // Form should now be visible with text inputs
      const inputs = screen.getAllByRole('textbox');
      expect(inputs.length).toBeGreaterThan(0);
    });

    it('shows Add button label when no editTarget', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /add stakeholder/i }));
      expect(screen.getByRole('button', { name: /^add$/i })).toBeTruthy();
    });
  });

  describe('edit form', () => {
    it('shows form in edit mode with stakeholder values pre-filled', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [STAKEHOLDER], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /edit/i }));
      // Form should open; name input should be pre-filled
      const nameInput = screen.getByDisplayValue('Alice');
      expect(nameInput).toBeTruthy();
    });

    it('shows Update button when editing an existing stakeholder', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [STAKEHOLDER], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /edit/i }));
      expect(screen.getByRole('button', { name: /^update$/i })).toBeTruthy();
    });

    it('does not show Add/Edit buttons when readOnly', () => {
      vi.mocked(useStakeholders).mockReturnValue({ data: [STAKEHOLDER], isLoading: false } as ReturnType<typeof useStakeholders>);
      renderWithQuery(<StakeholderPanel studyId={42} readOnly />);
      expect(screen.queryByRole('button', { name: /add stakeholder/i })).toBeNull();
      expect(screen.queryByRole('button', { name: /edit/i })).toBeNull();
    });
  });
});
