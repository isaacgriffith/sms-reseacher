/**
 * Unit tests for SearchRestrictionPanel component (feature 008).
 *
 * Covers rendering of restriction checkboxes, Save button, and mutation errors.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SearchRestrictionPanel from '../SearchRestrictionPanel';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/rapid/useRRProtocol', () => ({
  useRRThreats: vi.fn(() => ({ data: [] })),
}));

vi.mock('../../../hooks/rapid/useSearchConfig', () => ({
  useUpdateSearchConfig: vi.fn(() => ({ mutate: vi.fn(), isPending: false, isError: false })),
}));

import { useUpdateSearchConfig } from '../../../hooks/rapid/useSearchConfig';

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

describe('SearchRestrictionPanel', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders all four restriction type checkboxes', () => {
    renderWithQuery(<SearchRestrictionPanel studyId={42} />);
    expect(screen.getByText('Year Range')).toBeTruthy();
    expect(screen.getByText('Language')).toBeTruthy();
    expect(screen.getByText('Geography')).toBeTruthy();
    expect(screen.getByText('Study Design')).toBeTruthy();
  });

  it('renders Save Restrictions button', () => {
    renderWithQuery(<SearchRestrictionPanel studyId={42} />);
    expect(screen.getByRole('button', { name: /save restrictions/i })).toBeTruthy();
  });

  it('shows text input for Year Range when checkbox is checked', () => {
    renderWithQuery(<SearchRestrictionPanel studyId={42} />);
    const checkboxes = screen.getAllByRole('checkbox');
    // Click Year Range checkbox (first one)
    fireEvent.click(checkboxes[0]);
    // TextField placeholder should appear
    expect(screen.getByPlaceholderText(/e\.g\. 2015/i)).toBeTruthy();
  });

  it('calls mutate when Save is clicked', () => {
    const mutate = vi.fn();
    vi.mocked(useUpdateSearchConfig).mockReturnValue({ mutate, isPending: false, isError: false } as ReturnType<typeof useUpdateSearchConfig>);
    renderWithQuery(<SearchRestrictionPanel studyId={42} />);
    fireEvent.click(screen.getByRole('button', { name: /save restrictions/i }));
    expect(mutate).toHaveBeenCalled();
  });

  it('shows error alert when mutation fails', () => {
    vi.mocked(useUpdateSearchConfig).mockReturnValue({ mutate: vi.fn(), isPending: false, isError: true } as ReturnType<typeof useUpdateSearchConfig>);
    renderWithQuery(<SearchRestrictionPanel studyId={42} />);
    expect(screen.getByText(/failed to save/i)).toBeTruthy();
  });
});
