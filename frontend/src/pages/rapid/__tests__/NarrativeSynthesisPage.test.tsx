/**
 * Unit tests for NarrativeSynthesisPage (feature 008).
 *
 * Covers loading state, error state, empty sections, section rendering,
 * Mark All Complete button, Finalize Synthesis CTA, and error handling.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import NarrativeSynthesisPage from '../NarrativeSynthesisPage';

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../../../hooks/rapid/useNarrativeSynthesis', () => ({
  useNarrativeSections: vi.fn(),
  useUpdateSection: vi.fn(),
  useRequestAIDraft: vi.fn(),
  useCompleteSynthesis: vi.fn(),
}));

vi.mock('../../../services/rapid/synthesisApi', () => ({
  ApiError: class ApiError extends Error {
    status: number;
    detail: string;
    constructor(status: number, detail: string) {
      super(detail);
      this.status = status;
      this.detail = detail;
    }
  },
}));

vi.mock('../../../components/rapid/NarrativeSectionEditor', () => ({
  default: ({ section }: { section: { rq_index: number; narrative_text: string | null } }) => (
    <div data-testid={`section-editor-${section.rq_index}`}>
      Section {section.rq_index}
    </div>
  ),
}));

import {
  useNarrativeSections,
  useUpdateSection,
  useRequestAIDraft,
  useCompleteSynthesis,
} from '../../../hooks/rapid/useNarrativeSynthesis';
import { ApiError } from '../../../services/rapid/synthesisApi';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const BASE_SECTION = {
  id: 1,
  study_id: 42,
  rq_index: 0,
  rq_text: 'What is the effect?',
  narrative_text: 'Some findings here.',
  is_complete: false,
  ai_draft_job_id: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

function setupDefaultMocks() {
  vi.mocked(useNarrativeSections).mockReturnValue({ data: [BASE_SECTION], isLoading: false, error: null } as ReturnType<typeof useNarrativeSections>);
  vi.mocked(useUpdateSection).mockReturnValue({ mutate: vi.fn(), isPending: false, variables: undefined } as ReturnType<typeof useUpdateSection>);
  vi.mocked(useRequestAIDraft).mockReturnValue({ mutate: vi.fn(), isPending: false, variables: undefined, isError: false, error: null } as ReturnType<typeof useRequestAIDraft>);
  vi.mocked(useCompleteSynthesis).mockReturnValue({ mutate: vi.fn(), isPending: false } as ReturnType<typeof useCompleteSynthesis>);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('NarrativeSynthesisPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  describe('loading state', () => {
    it('shows loading indicator when isLoading is true', () => {
      vi.mocked(useNarrativeSections).mockReturnValue({ data: undefined, isLoading: true, error: null } as ReturnType<typeof useNarrativeSections>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByText(/loading synthesis sections/i)).toBeTruthy();
    });
  });

  describe('error state', () => {
    it('shows error alert when load fails', () => {
      vi.mocked(useNarrativeSections).mockReturnValue({ data: undefined, isLoading: false, error: new Error('fail') } as ReturnType<typeof useNarrativeSections>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByText(/failed to load synthesis sections/i)).toBeTruthy();
    });

    it('shows error alert when sections is undefined after load', () => {
      vi.mocked(useNarrativeSections).mockReturnValue({ data: undefined, isLoading: false, error: null } as ReturnType<typeof useNarrativeSections>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByText(/failed to load synthesis sections/i)).toBeTruthy();
    });
  });

  describe('empty sections state', () => {
    it('shows info alert when sections is empty', () => {
      vi.mocked(useNarrativeSections).mockReturnValue({ data: [], isLoading: false, error: null } as ReturnType<typeof useNarrativeSections>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByText(/no synthesis sections yet/i)).toBeTruthy();
    });
  });

  describe('normal rendering', () => {
    it('renders the Narrative Synthesis heading', () => {
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByText('Narrative Synthesis')).toBeTruthy();
    });

    it('renders NarrativeSectionEditor for each section', () => {
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByTestId('section-editor-0')).toBeTruthy();
    });

    it('renders Mark All Sections Complete button when not all complete', () => {
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByRole('button', { name: /mark all sections complete/i })).toBeTruthy();
    });

    it('does not render Mark All button when all sections are complete', () => {
      const completedSection = { ...BASE_SECTION, is_complete: true };
      vi.mocked(useNarrativeSections).mockReturnValue({ data: [completedSection], isLoading: false, error: null } as ReturnType<typeof useNarrativeSections>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.queryByRole('button', { name: /mark all sections complete/i })).toBeNull();
    });

    it('renders Finalize Synthesis button', () => {
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByRole('button', { name: /finalize synthesis/i })).toBeTruthy();
    });
  });

  describe('finalize synthesis', () => {
    it('calls completeMutation.mutate when Finalize is clicked', () => {
      const mutate = vi.fn();
      vi.mocked(useCompleteSynthesis).mockReturnValue({ mutate, isPending: false } as ReturnType<typeof useCompleteSynthesis>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /finalize synthesis/i }));
      expect(mutate).toHaveBeenCalledWith(undefined, expect.any(Object));
    });

    it('shows success banner when synthesis is completed', async () => {
      let capturedOnSuccess: (() => void) | undefined;
      vi.mocked(useCompleteSynthesis).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onSuccess?: () => void }) => {
          capturedOnSuccess = opts?.onSuccess;
        },
        isPending: false,
      } as ReturnType<typeof useCompleteSynthesis>);

      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /finalize synthesis/i }));
      capturedOnSuccess?.();

      await waitFor(() => {
        expect(screen.getByText(/synthesis finalised/i)).toBeTruthy();
      });
    });

    it('shows generic error message for non-422 finalize error', async () => {
      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useCompleteSynthesis).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useCompleteSynthesis>);

      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /finalize synthesis/i }));
      capturedOnError?.(new Error('Server failure'));

      await waitFor(() => {
        expect(screen.getByText(/server failure/i)).toBeTruthy();
      });
    });

    it('shows 422 error message with incomplete sections', async () => {
      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useCompleteSynthesis).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useCompleteSynthesis>);

      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /finalize synthesis/i }));

      const errorDetail = JSON.stringify({ detail: 'Sections not done', incomplete_sections: [0, 1] });
      capturedOnError?.(new ApiError(422, errorDetail));

      await waitFor(() => {
        expect(screen.getByText(/sections not done/i)).toBeTruthy();
      });
    });
  });

  describe('mark all complete', () => {
    it('calls updateSection for each incomplete section when Mark All is clicked', () => {
      const mutate = vi.fn();
      vi.mocked(useUpdateSection).mockReturnValue({ mutate, isPending: false, variables: undefined } as ReturnType<typeof useUpdateSection>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /mark all sections complete/i }));
      expect(mutate).toHaveBeenCalledWith(
        expect.objectContaining({ data: expect.objectContaining({ is_complete: true }) }),
      );
    });

    it('does not call updateSection for already-complete sections', () => {
      const mutate = vi.fn();
      vi.mocked(useUpdateSection).mockReturnValue({ mutate, isPending: false, variables: undefined } as ReturnType<typeof useUpdateSection>);
      const completeSection = { ...BASE_SECTION, is_complete: true };
      const incompleteSection = { ...BASE_SECTION, id: 2, rq_index: 1, is_complete: false };
      vi.mocked(useNarrativeSections).mockReturnValue({
        data: [completeSection, incompleteSection],
        isLoading: false,
        error: null,
      } as ReturnType<typeof useNarrativeSections>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /mark all sections complete/i }));
      // Only called once for the incomplete section
      expect(mutate).toHaveBeenCalledTimes(1);
      expect(mutate).toHaveBeenCalledWith(
        expect.objectContaining({ sectionId: 2 }),
      );
    });
  });

  describe('finalize error edge cases', () => {
    it('shows fallback message when 422 JSON has no detail field', async () => {
      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useCompleteSynthesis).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useCompleteSynthesis>);

      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /finalize synthesis/i }));

      const errorDetail = JSON.stringify({ incomplete_sections: [0] });
      capturedOnError?.(new ApiError(422, errorDetail));

      await waitFor(() => {
        expect(screen.getByText(/some sections are incomplete/i)).toBeTruthy();
      });
    });

    it('shows catch fallback when 422 has non-JSON body', async () => {
      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useCompleteSynthesis).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useCompleteSynthesis>);

      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /finalize synthesis/i }));

      capturedOnError?.(new ApiError(422, 'not valid json {{{'));

      await waitFor(() => {
        expect(screen.getByText(/some sections must be completed/i)).toBeTruthy();
      });
    });

    it('shows isPending state on Finalize button', () => {
      vi.mocked(useCompleteSynthesis).mockReturnValue({ mutate: vi.fn(), isPending: true } as ReturnType<typeof useCompleteSynthesis>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByRole('button', { name: /finalising/i })).toBeTruthy();
    });

    it('shows fallback when 422 JSON has detail but no incomplete_sections', async () => {
      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useCompleteSynthesis).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useCompleteSynthesis>);

      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /finalize synthesis/i }));

      const errorDetail = JSON.stringify({ detail: 'Two sections incomplete' });
      capturedOnError?.(new ApiError(422, errorDetail));

      await waitFor(() => {
        expect(screen.getByText(/two sections incomplete/i)).toBeTruthy();
      });
    });

    it('shows fallback message when non-422 error has no message', async () => {
      let capturedOnError: ((err: Error) => void) | undefined;
      vi.mocked(useCompleteSynthesis).mockReturnValue({
        mutate: (_arg: undefined, opts?: { onError?: (err: Error) => void }) => {
          capturedOnError = opts?.onError;
        },
        isPending: false,
      } as ReturnType<typeof useCompleteSynthesis>);

      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      fireEvent.click(screen.getByRole('button', { name: /finalize synthesis/i }));

      capturedOnError?.(Object.assign(new Error(), { message: undefined as unknown as string }));

      await waitFor(() => {
        expect(screen.getByText(/failed to finalise synthesis/i)).toBeTruthy();
      });
    });
  });

  describe('section editor props coverage', () => {
    it('renders with updateMutation pending for matching section', () => {
      vi.mocked(useUpdateSection).mockReturnValue({
        mutate: vi.fn(),
        isPending: true,
        variables: { sectionId: BASE_SECTION.id, data: { is_complete: true } },
      } as ReturnType<typeof useUpdateSection>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByTestId('section-editor-0')).toBeTruthy();
    });

    it('renders with draftMutation pending and error for matching section', () => {
      vi.mocked(useRequestAIDraft).mockReturnValue({
        mutate: vi.fn(),
        isPending: true,
        variables: BASE_SECTION.id,
        isError: true,
        error: new Error('Draft request failed'),
      } as ReturnType<typeof useRequestAIDraft>);
      renderWithQuery(<NarrativeSynthesisPage studyId={42} />);
      expect(screen.getByTestId('section-editor-0')).toBeTruthy();
    });
  });
});
