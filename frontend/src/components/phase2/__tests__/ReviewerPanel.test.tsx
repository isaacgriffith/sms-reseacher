/**
 * Tests for ReviewerPanel component.
 *
 * Mocks api.get (criteria) and api.post (decision submission).
 * Covers:
 * - Submit Decision heading renders
 * - Accept / Reject / Duplicate buttons rendered
 * - Submit button disabled when no decision selected
 * - Submit button enabled once a decision is chosen (TFIX4: no reviewer id entry required)
 * - api.post called with correct payload on submit, and never with reviewer_id (TFIX4)
 * - Override annotation textarea present
 * - Success and error states from mutation
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../../services/api')>();
  return {
    ...actual,
    api: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

import { api, ApiError } from '../../../services/api';
import ReviewerPanel from '../ReviewerPanel';

const mockApi = api as unknown as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const BASE_PROPS = { studyId: 1, candidateId: 42, observedStatus: 'pending' };

describe('ReviewerPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.get.mockResolvedValue([]);
    mockApi.post.mockResolvedValue({});
  });

  describe('Rendering', () => {
    it('renders "Submit Decision" heading', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.getByRole('heading', { name: /submit decision/i })).toBeTruthy();
    });

    it('renders accepted button', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.getByRole('button', { name: /^accepted$/i })).toBeTruthy();
    });

    it('renders rejected button', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.getByRole('button', { name: /^rejected$/i })).toBeTruthy();
    });

    it('renders duplicate button', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.getByRole('button', { name: /^duplicate$/i })).toBeTruthy();
    });

    it('does not render a reviewer ID input (TFIX4: reviewer resolved from session)', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.queryByPlaceholderText(/reviewer id/i)).toBeNull();
      expect(screen.queryByText(/^reviewer id$/i)).toBeNull();
    });

    it('renders override annotation textarea', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.getByPlaceholderText(/optional annotation/i)).toBeTruthy();
    });
  });

  describe('Submit button state', () => {
    it('submit button is disabled when no decision selected', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      const submitBtn = screen.getByRole('button', { name: /submit decision/i });
      expect(submitBtn).toHaveProperty('disabled', true);
    });

    it('submit button is enabled once a decision is chosen, with no reviewer id entered anywhere', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      const submitBtn = screen.getByRole('button', { name: /submit decision/i });
      expect(submitBtn).toHaveProperty('disabled', false);
    });
  });

  describe('Decision submission', () => {
    it('calls api.post with decision and reasons, and never with reviewer_id, on submit', async () => {
      mockApi.post.mockResolvedValue({ id: 99, decision: 'accepted', is_override: false });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          expect.stringContaining('/decisions'),
          expect.objectContaining({
            decision: 'accepted',
            reasons: expect.any(Array),
          }),
        );
      });

      const body = mockApi.post.mock.calls[0][1] as Record<string, unknown>;
      expect(body).not.toHaveProperty('reviewer_id');
    });

    it('sends annotation text as its own top-level field, not inside reasons, when override note is entered', async () => {
      mockApi.post.mockResolvedValue({ id: 100, decision: 'rejected', is_override: false });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));
      fireEvent.change(screen.getByPlaceholderText(/optional annotation/i), {
        target: { value: 'Override note here' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const callBody = mockApi.post.mock.calls[0][1] as {
          annotation: string | null;
          reasons: Array<{ criterion_type?: string }>;
        };
        expect(callBody.annotation).toBe('Override note here');
        // TFIX3 regression guard: the annotation must never be smuggled into `reasons`
        // as a fake criterion again.
        expect(callBody.reasons.find((r) => r.criterion_type === 'annotation')).toBeUndefined();
      });
    });

    it('shows success message after successful submission', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted', is_override: false });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => expect(screen.getByText(/decision submitted/i)).toBeTruthy());
    });

    it('shows error message when submission fails', async () => {
      mockApi.post.mockRejectedValue(new Error('Network error'));
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => expect(screen.getByText(/failed to submit decision/i)).toBeTruthy());
    });
  });

  describe('Criteria selector', () => {
    it('shows inclusion criteria checkboxes when decision selected and criteria loaded', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('inclusion')) {
          return Promise.resolve([{ id: 1, description: 'Must be peer-reviewed', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));

      await waitFor(() => expect(screen.getByText('Must be peer-reviewed')).toBeTruthy());
    });

    it('shows "Inclusion Criteria" group label when criteria are available', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('inclusion')) {
          return Promise.resolve([{ id: 1, description: 'Peer-reviewed', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));

      await waitFor(() => expect(screen.getByText(/inclusion criteria/i)).toBeTruthy());
    });

    it('shows "Exclusion Criteria" group label when exclusion criteria available', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('exclusion')) {
          return Promise.resolve([{ id: 5, description: 'No grey lit', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));

      await waitFor(() => expect(screen.getByText(/exclusion criteria/i)).toBeTruthy());
    });

    it('includes criterion type exclusion in reasons when exclusion criterion selected', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('exclusion')) {
          return Promise.resolve([{ id: 5, description: 'No grey lit', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });
      mockApi.post.mockResolvedValue({ id: 1, decision: 'rejected' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));

      await waitFor(() => screen.getByText('No grey lit'));
      fireEvent.click(screen.getByLabelText('No grey lit'));

      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as {
          reasons: Array<{ criterion_type: string }>;
        };
        const excReason = body.reasons.find((r) => r.criterion_type === 'exclusion');
        expect(excReason).toBeTruthy();
      });
    });

    it('does not show criteria section when no criteria available', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));

      await waitFor(() => screen.getByRole('button', { name: /submit decision/i }));
      // No "Reasons (select criteria)" label when criteria are empty
      expect(screen.queryByText(/reasons \(select criteria\)/i)).toBeNull();
    });
  });

  describe('Decision toggle', () => {
    it('clicking same decision button again deselects it (Submit becomes disabled)', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      // Select accepted
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      // Click again to deselect
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));

      const submitBtn = screen.getByRole('button', { name: /submit decision/i });
      expect((submitBtn as HTMLButtonElement).disabled).toBe(true);
    });
  });

  describe('onDecisionSubmitted callback', () => {
    it('calls onDecisionSubmitted callback after successful submission', async () => {
      const onSubmitted = vi.fn();
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} onDecisionSubmitted={onSubmitted} />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        expect(onSubmitted).toHaveBeenCalledTimes(1);
      });
    });

    it('does not throw when onDecisionSubmitted is not provided', async () => {
      mockApi.post.mockResolvedValue({ id: 2, decision: 'rejected' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));

      expect(() =>
        fireEvent.click(screen.getByRole('button', { name: /submit decision/i })),
      ).not.toThrow();
    });
  });

  describe('Criteria checkbox toggle', () => {
    it('toggling a criterion on then off removes it from reasons', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('inclusion')) {
          return Promise.resolve([{ id: 3, description: 'Peer reviewed', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      await waitFor(() => screen.getByText('Peer reviewed'));

      // Toggle the checkbox on
      fireEvent.click(screen.getByLabelText('Peer reviewed'));
      // Toggle it back off
      fireEvent.click(screen.getByLabelText('Peer reviewed'));

      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as { reasons: object[] };
        expect(body.reasons).toHaveLength(0);
      });
    });

    it('toggling a criterion on adds it to reasons with criterion type', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('inclusion')) {
          return Promise.resolve([{ id: 4, description: 'Must use RCT', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      await waitFor(() => screen.getByText('Must use RCT'));

      fireEvent.click(screen.getByLabelText('Must use RCT'));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as {
          reasons: Array<{ criterion_type: string; criterion_id: number; text: string }>;
        };
        expect(body.reasons).toHaveLength(1);
        expect(body.reasons[0]).toMatchObject({
          criterion_id: 4,
          criterion_type: 'inclusion',
          text: 'Must use RCT',
        });
      });
    });

    it('sends duplicate decision with reasons', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'duplicate' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^duplicate$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          expect.stringContaining('/decisions'),
          expect.objectContaining({ decision: 'duplicate' }),
        );
      });
    });
  });

  describe('Negative state assertions', () => {
    it('error message NOT shown initially before any submission', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.queryByText(/failed to submit/i)).toBeNull();
    });

    it('success message NOT shown initially before any submission', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.queryByText(/decision submitted/i)).toBeNull();
    });

    it('"Inclusion Criteria" group NOT shown when only exclusion criteria loaded', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('exclusion')) {
          return Promise.resolve([{ id: 5, description: 'No grey lit', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));
      await waitFor(() => screen.getByText('No grey lit'));
      expect(screen.queryByText('Inclusion Criteria')).toBeNull();
    });

    it('"Exclusion Criteria" group NOT shown when only inclusion criteria loaded', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('inclusion')) {
          return Promise.resolve([{ id: 2, description: 'Peer reviewed', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      await waitFor(() => screen.getByText('Peer reviewed'));
      expect(screen.queryByText('Exclusion Criteria')).toBeNull();
    });

    it('deselecting decision (clicking again) makes submit disabled', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      // Deselect by clicking same button again
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      const submitBtn = screen.getByRole('button', { name: /submit decision/i });
      expect((submitBtn as HTMLButtonElement).disabled).toBe(true);
    });
  });

  describe('Criterion type accuracy', () => {
    it('includes criterion_type "inclusion" for inclusion criterion', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('inclusion')) {
          return Promise.resolve([{ id: 7, description: 'Must be RCT', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      await waitFor(() => screen.getByText('Must be RCT'));
      fireEvent.click(screen.getByLabelText('Must be RCT'));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as {
          reasons: Array<{ criterion_type: string; criterion_id: number }>;
        };
        expect(body.reasons).toContainEqual(
          expect.objectContaining({ criterion_type: 'inclusion', criterion_id: 7 }),
        );
      });
    });
  });

  describe('Annotation field (TFIX3: dedicated column, not a fake criterion)', () => {
    it('sends annotation as null (not "") when annotation textarea is empty', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      // Leave annotation empty
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as { annotation: string | null };
        expect(body.annotation).toBeNull();
      });
    });

    it('sends annotation as null when annotation is only whitespace', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/optional annotation/i), {
        target: { value: '   ' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as { annotation: string | null };
        expect(body.annotation).toBeNull();
      });
    });

    it('never includes an entry with criterion_type "annotation" in reasons, regardless of annotation text', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/optional annotation/i), {
        target: { value: 'Some free-text note' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as {
          annotation: string | null;
          reasons: Array<{ criterion_type?: string }>;
        };
        expect(body.annotation).toBe('Some free-text note');
        expect(body.reasons.some((r) => r.criterion_type === 'annotation')).toBe(false);
      });
    });
  });

  describe('observed_status / overrides_decision_id (contract T017)', () => {
    it('sends observed_status from the observedStatus prop', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} observedStatus="pending" />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          expect.stringContaining('/decisions'),
          expect.objectContaining({ observed_status: 'pending' }),
        );
      });
    });

    it('sends overrides_decision_id when the prop is set', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted', is_override: true });
      renderWithQuery(
        <ReviewerPanel {...BASE_PROPS} observedStatus="pending" overridesDecisionId={9} />,
      );

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          expect.stringContaining('/decisions'),
          expect.objectContaining({ overrides_decision_id: 9 }),
        );
      });
    });

    it('does not send overrides_decision_id when the prop is not set', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} observedStatus="pending" />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as Record<string, unknown>;
        expect(body.overrides_decision_id).toBeUndefined();
      });
    });
  });

  describe('409 conflict handling (FR-022, FR-025)', () => {
    it('shows a re-confirmation prompt on 409 stale_state, not the generic failure message', async () => {
      mockApi.post.mockRejectedValueOnce(
        new ApiError(409, {
          error: 'stale_state',
          observed_status: 'pending',
          current_status: 'accepted',
        } as unknown as string),
      );
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} observedStatus="pending" />);

      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => expect(screen.getByText(/status is now/i)).toBeTruthy());
      expect(screen.queryByText(/^failed to submit decision/i)).toBeNull();
    });

    it('resubmits with the updated status when the stale-state prompt is confirmed', async () => {
      mockApi.post.mockRejectedValueOnce(
        new ApiError(409, {
          error: 'stale_state',
          observed_status: 'pending',
          current_status: 'accepted',
        } as unknown as string),
      );
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} observedStatus="pending" />);

      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));
      await waitFor(() => expect(screen.getByText(/status is now/i)).toBeTruthy());

      mockApi.post.mockResolvedValueOnce({ id: 2, decision: 'rejected' });
      fireEvent.click(screen.getByRole('button', { name: /confirm and resubmit/i }));

      await waitFor(() => {
        const lastCall = mockApi.post.mock.calls.at(-1);
        expect(lastCall?.[1]).toMatchObject({ observed_status: 'accepted' });
      });
    });

    it('shows an override prompt on 409 unacknowledged_prior_decision', async () => {
      mockApi.post.mockRejectedValueOnce(
        new ApiError(409, {
          error: 'unacknowledged_prior_decision',
          prior_decision: { id: 9, decision: 'rejected' },
        } as unknown as string),
      );
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} observedStatus="pending" />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => expect(screen.getByText(/already recorded/i)).toBeTruthy());
    });

    it('resubmits with overrides_decision_id when the override prompt is confirmed', async () => {
      mockApi.post.mockRejectedValueOnce(
        new ApiError(409, {
          error: 'unacknowledged_prior_decision',
          prior_decision: { id: 9, decision: 'rejected' },
        } as unknown as string),
      );
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} observedStatus="pending" />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));
      await waitFor(() => expect(screen.getByText(/already recorded/i)).toBeTruthy());

      mockApi.post.mockResolvedValueOnce({ id: 10, decision: 'accepted', is_override: true });
      fireEvent.click(screen.getByRole('button', { name: /confirm override/i }));

      await waitFor(() => {
        const lastCall = mockApi.post.mock.calls.at(-1);
        expect(lastCall?.[1]).toMatchObject({ overrides_decision_id: 9 });
      });
    });

    it('keeps entered reasons and annotation visible after a stale_state 409', async () => {
      mockApi.get.mockImplementation((url: string) => {
        if (url.includes('inclusion')) {
          return Promise.resolve([{ id: 1, description: 'Peer-reviewed', order_index: 0 }]);
        }
        return Promise.resolve([]);
      });
      mockApi.post.mockRejectedValueOnce(
        new ApiError(409, {
          error: 'stale_state',
          observed_status: 'pending',
          current_status: 'accepted',
        } as unknown as string),
      );
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} observedStatus="pending" />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      await waitFor(() => screen.getByText('Peer-reviewed'));
      fireEvent.click(screen.getByLabelText('Peer-reviewed'));
      fireEvent.change(screen.getByPlaceholderText(/optional annotation/i), {
        target: { value: 'Keep me around' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => expect(screen.getByText(/status is now/i)).toBeTruthy());
      expect((screen.getByLabelText('Peer-reviewed') as HTMLInputElement).checked).toBe(true);
      expect(
        (screen.getByPlaceholderText(/optional annotation/i) as HTMLTextAreaElement).value,
      ).toBe('Keep me around');

      // The annotation must survive the re-confirmation resubmit as its own field (FR-025),
      // and must not reappear inside reasons as a fake criterion.
      mockApi.post.mockResolvedValueOnce({ id: 2, decision: 'accepted' });
      fireEvent.click(screen.getByRole('button', { name: /confirm and resubmit/i }));

      await waitFor(() => {
        const lastCall = mockApi.post.mock.calls.at(-1);
        const body = lastCall?.[1] as {
          annotation: string | null;
          reasons: Array<{ criterion_type?: string }>;
        };
        expect(body.annotation).toBe('Keep me around');
        expect(body.reasons.some((r) => r.criterion_type === 'annotation')).toBe(false);
      });
    });
  });
});
