/**
 * Unit tests for QAModeSelector component (feature 008).
 *
 * Covers radio rendering, mode selection, Save button, success feedback,
 * error state, and threats list visibility.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import QAModeSelector from '../QAModeSelector';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/rapid/useQAConfig', () => ({
  useSetQAMode: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
    isError: false,
  })),
}));

vi.mock('../../../hooks/rapid/useRRProtocol', () => ({
  useRRThreats: vi.fn(() => ({ data: [] })),
}));

import { useSetQAMode } from '../../../hooks/rapid/useQAConfig';
import { useRRThreats } from '../../../hooks/rapid/useRRProtocol';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('QAModeSelector', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders the Quality Appraisal Mode label', () => {
    renderWithQuery(<QAModeSelector studyId={42} currentMode="full" />);
    expect(screen.getByText(/quality appraisal mode/i)).toBeTruthy();
  });

  it('renders all three mode radio options', () => {
    renderWithQuery(<QAModeSelector studyId={42} currentMode="full" />);
    expect(screen.getByText(/full quality appraisal/i)).toBeTruthy();
    expect(screen.getByText(/peer-reviewed venues only/i)).toBeTruthy();
    expect(screen.getByText(/skip quality appraisal/i)).toBeTruthy();
  });

  it('renders Save Mode button', () => {
    renderWithQuery(<QAModeSelector studyId={42} currentMode="full" />);
    expect(screen.getByRole('button', { name: /save mode/i })).toBeTruthy();
  });

  it('calls mutate with selected mode when Save is clicked', () => {
    const mutate = vi.fn();
    vi.mocked(useSetQAMode).mockReturnValue({ mutate, isPending: false, isError: false } as ReturnType<typeof useSetQAMode>);

    renderWithQuery(<QAModeSelector studyId={42} currentMode="full" />);
    fireEvent.click(screen.getByRole('button', { name: /save mode/i }));
    expect(mutate).toHaveBeenCalledWith(
      expect.objectContaining({ mode: 'full' }),
      expect.any(Object),
    );
  });

  it('selects peer_reviewed_only when that radio is clicked', () => {
    renderWithQuery(<QAModeSelector studyId={42} currentMode="full" />);
    const radios = screen.getAllByRole('radio');
    // Find peer_reviewed_only radio
    const peerRadio = radios.find((r) => (r as HTMLInputElement).value === 'peer_reviewed_only');
    if (peerRadio) fireEvent.click(peerRadio);
    // The consequence text should appear for non-full modes
    expect(screen.getByText(/non-peer-reviewed papers are excluded/i)).toBeTruthy();
  });

  it('shows error alert when mutation isError is true', () => {
    vi.mocked(useSetQAMode).mockReturnValue({ mutate: vi.fn(), isPending: false, isError: true } as ReturnType<typeof useSetQAMode>);
    renderWithQuery(<QAModeSelector studyId={42} currentMode="full" />);
    expect(screen.getByText(/failed to save quality appraisal mode/i)).toBeTruthy();
  });

  it('shows QA threats list when mode is not full and threats exist', () => {
    vi.mocked(useRRThreats).mockReturnValue({
      data: [
        { id: 1, study_id: 42, threat_type: 'QA_SKIPPED', description: 'No QA performed', source_detail: null, created_at: '2026-01-01T00:00:00Z' },
      ],
    } as ReturnType<typeof useRRThreats>);

    renderWithQuery(<QAModeSelector studyId={42} currentMode="skipped" />);
    expect(screen.getByText(/quality appraisal threats to validity/i)).toBeTruthy();
  });

  it('does not show QA threats list when mode is full', () => {
    vi.mocked(useRRThreats).mockReturnValue({
      data: [
        { id: 1, study_id: 42, threat_type: 'QA_SKIPPED', description: 'No QA', source_detail: null, created_at: '2026-01-01T00:00:00Z' },
      ],
    } as ReturnType<typeof useRRThreats>);

    renderWithQuery(<QAModeSelector studyId={42} currentMode="full" />);
    expect(screen.queryByText(/quality appraisal threats to validity/i)).toBeNull();
  });

  it('does not show QA threats list when no qa threats exist', () => {
    vi.mocked(useRRThreats).mockReturnValue({ data: [] } as ReturnType<typeof useRRThreats>);
    renderWithQuery(<QAModeSelector studyId={42} currentMode="skipped" />);
    expect(screen.queryByText(/quality appraisal threats to validity/i)).toBeNull();
  });
});
