/**
 * Unit tests for SingleReviewerWarningBanner component (feature 008).
 *
 * Covers rendering in both single-reviewer-off and single-reviewer-on states,
 * Enable/Disable button actions, and the confirmation dialog flow.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SingleReviewerWarningBanner from '../SingleReviewerWarningBanner';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/rapid/useSearchConfig', () => ({
  useUpdateSearchConfig: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
  })),
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

describe('SingleReviewerWarningBanner', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('single-reviewer mode OFF', () => {
    it('renders info alert when mode is off', () => {
      renderWithQuery(<SingleReviewerWarningBanner studyId={42} singleReviewerMode={false} />);
      expect(screen.getByText(/single-reviewer mode is off/i)).toBeTruthy();
    });

    it('renders Enable button when mode is off', () => {
      renderWithQuery(<SingleReviewerWarningBanner studyId={42} singleReviewerMode={false} />);
      expect(screen.getByRole('button', { name: /enable/i })).toBeTruthy();
    });

    it('calls mutate with single_reviewer_mode=true when Enable is clicked', () => {
      const mutate = vi.fn();
      vi.mocked(useUpdateSearchConfig).mockReturnValue({ mutate, isPending: false } as ReturnType<typeof useUpdateSearchConfig>);
      renderWithQuery(<SingleReviewerWarningBanner studyId={42} singleReviewerMode={false} />);
      fireEvent.click(screen.getByRole('button', { name: /enable/i }));
      expect(mutate).toHaveBeenCalledWith(
        expect.objectContaining({ single_reviewer_mode: true }),
      );
    });
  });

  describe('single-reviewer mode ON', () => {
    it('renders warning alert when mode is on', () => {
      renderWithQuery(<SingleReviewerWarningBanner studyId={42} singleReviewerMode={true} />);
      expect(screen.getByText(/single-reviewer mode active/i)).toBeTruthy();
    });

    it('renders Disable button when mode is on', () => {
      renderWithQuery(<SingleReviewerWarningBanner studyId={42} singleReviewerMode={true} />);
      expect(screen.getByRole('button', { name: /disable/i })).toBeTruthy();
    });

    it('opens confirmation dialog when Disable is clicked', () => {
      renderWithQuery(<SingleReviewerWarningBanner studyId={42} singleReviewerMode={true} />);
      fireEvent.click(screen.getByRole('button', { name: /disable/i }));
      expect(screen.getByText(/disable single-reviewer mode/i)).toBeTruthy();
    });

    it('calls mutate with single_reviewer_mode=false when dialog Disable is confirmed', () => {
      const mutate = vi.fn();
      vi.mocked(useUpdateSearchConfig).mockReturnValue({ mutate, isPending: false } as ReturnType<typeof useUpdateSearchConfig>);
      renderWithQuery(<SingleReviewerWarningBanner studyId={42} singleReviewerMode={true} />);
      // Open dialog
      fireEvent.click(screen.getByRole('button', { name: /disable/i }));
      // Click the dialog's Disable confirm button
      const disableButtons = screen.getAllByRole('button', { name: /disable/i });
      // The last "Disable" button is in the dialog
      fireEvent.click(disableButtons[disableButtons.length - 1]);
      expect(mutate).toHaveBeenCalledWith(
        expect.objectContaining({ single_reviewer_mode: false }),
      );
    });

    it('does not call mutate when Cancel is clicked in dialog', () => {
      const mutate = vi.fn();
      vi.mocked(useUpdateSearchConfig).mockReturnValue({ mutate, isPending: false } as ReturnType<typeof useUpdateSearchConfig>);
      renderWithQuery(<SingleReviewerWarningBanner studyId={42} singleReviewerMode={true} />);
      // Open dialog
      fireEvent.click(screen.getByRole('button', { name: /disable/i }));
      // Dialog is open
      expect(screen.getByText(/disable single-reviewer mode/i)).toBeTruthy();
      // Click Cancel
      fireEvent.click(screen.getByRole('button', { name: /cancel/i }));
      // mutate should not have been called
      expect(mutate).not.toHaveBeenCalled();
    });
  });
});
