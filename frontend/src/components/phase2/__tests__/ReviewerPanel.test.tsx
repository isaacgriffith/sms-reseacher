/**
 * Tests for ReviewerPanel component.
 *
 * Mocks api.get (criteria) and api.post (decision submission).
 * Covers:
 * - Submit Decision heading renders
 * - Accept / Reject / Duplicate buttons rendered
 * - Submit button disabled when no decision selected
 * - Submit button disabled when reviewer ID not set
 * - Submit button enabled when decision + reviewer ID provided
 * - api.post called with correct payload on submit
 * - Override annotation textarea present
 * - Success and error states from mutation
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import { api } from '../../../services/api';
import ReviewerPanel from '../ReviewerPanel';

const mockApi = api as unknown as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const BASE_PROPS = { studyId: 1, candidateId: 42 };

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

    it('renders reviewer ID input', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      expect(screen.getByPlaceholderText(/reviewer id/i)).toBeTruthy();
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

    it('submit button is disabled when decision selected but no reviewer ID', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      const submitBtn = screen.getByRole('button', { name: /submit decision/i });
      expect(submitBtn).toHaveProperty('disabled', true);
    });

    it('submit button is enabled when decision and reviewer ID both set', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), {
        target: { value: '7' },
      });
      const submitBtn = screen.getByRole('button', { name: /submit decision/i });
      expect(submitBtn).toHaveProperty('disabled', false);
    });
  });

  describe('Decision submission', () => {
    it('calls api.post with reviewer_id, decision, and reasons on submit', async () => {
      mockApi.post.mockResolvedValue({ id: 99, decision: 'accepted', is_override: false });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), {
        target: { value: '5' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          expect.stringContaining('/decisions'),
          expect.objectContaining({
            reviewer_id: 5,
            decision: 'accepted',
            reasons: expect.any(Array),
          })
        );
      });
    });

    it('includes annotation text in reasons when override note is entered', async () => {
      mockApi.post.mockResolvedValue({ id: 100, decision: 'rejected', is_override: false });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), {
        target: { value: '3' },
      });
      fireEvent.change(screen.getByPlaceholderText(/optional annotation/i), {
        target: { value: 'Override note here' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const callBody = mockApi.post.mock.calls[0][1] as { reasons: object[] };
        expect(callBody.reasons).toContainEqual(
          expect.objectContaining({ text: 'Override note here' })
        );
      });
    });

    it('shows success message after successful submission', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted', is_override: false });
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), {
        target: { value: '1' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() =>
        expect(screen.getByText(/decision submitted/i)).toBeTruthy()
      );
    });

    it('shows error message when submission fails', async () => {
      mockApi.post.mockRejectedValue(new Error('Network error'));
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), {
        target: { value: '2' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() =>
        expect(screen.getByText(/failed to submit decision/i)).toBeTruthy()
      );
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

      await waitFor(() =>
        expect(screen.getByText('Must be peer-reviewed')).toBeTruthy()
      );
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

      await waitFor(() =>
        expect(screen.getByText(/inclusion criteria/i)).toBeTruthy()
      );
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

      await waitFor(() =>
        expect(screen.getByText(/exclusion criteria/i)).toBeTruthy()
      );
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

      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '7' } });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as { reasons: Array<{ criterion_type: string }> };
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

  describe('Reviewer ID input', () => {
    it('setting reviewer ID to empty string makes submit disabled', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      const reviewerInput = screen.getByPlaceholderText(/reviewer id/i);
      fireEvent.change(reviewerInput, { target: { value: '5' } });
      // Then clear it
      fireEvent.change(reviewerInput, { target: { value: '' } });

      const submitBtn = screen.getByRole('button', { name: /submit decision/i });
      expect((submitBtn as HTMLButtonElement).disabled).toBe(true);
    });
  });

  describe('onDecisionSubmitted callback', () => {
    it('calls onDecisionSubmitted callback after successful submission', async () => {
      const onSubmitted = vi.fn();
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(
        <ReviewerPanel {...BASE_PROPS} onDecisionSubmitted={onSubmitted} />
      );

      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '1' } });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        expect(onSubmitted).toHaveBeenCalledTimes(1);
      });
    });

    it('does not throw when onDecisionSubmitted is not provided', async () => {
      mockApi.post.mockResolvedValue({ id: 2, decision: 'rejected' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^rejected$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '2' } });

      expect(() =>
        fireEvent.click(screen.getByRole('button', { name: /submit decision/i }))
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

      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '1' } });
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
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '2' } });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as { reasons: Array<{ criterion_type: string; criterion_id: number; text: string }> };
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
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '1' } });
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
    it('submit disabled when reviewer ID set but no decision selected', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '5' } });
      const submitBtn = screen.getByRole('button', { name: /submit decision/i });
      expect((submitBtn as HTMLButtonElement).disabled).toBe(true);
    });

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

    it('deselecting decision (clicking again) with reviewerId entered makes submit disabled', () => {
      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '3' } });
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
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '1' } });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as { reasons: Array<{ criterion_type: string; criterion_id: number }> };
        expect(body.reasons).toContainEqual(
          expect.objectContaining({ criterion_type: 'inclusion', criterion_id: 7 })
        );
      });
    });
  });

  describe('Annotation in reasons', () => {
    it('does not include annotation reason when annotation textarea is empty', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '1' } });
      // Leave annotation empty
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as { reasons: Array<{ criterion_type: string }> };
        const annotationReason = body.reasons.find((r) => r.criterion_type === 'annotation');
        expect(annotationReason).toBeUndefined();
      });
    });

    it('does not include annotation reason when annotation is only whitespace', async () => {
      mockApi.post.mockResolvedValue({ id: 1, decision: 'accepted' });

      renderWithQuery(<ReviewerPanel {...BASE_PROPS} />);
      fireEvent.click(screen.getByRole('button', { name: /^accepted$/i }));
      fireEvent.change(screen.getByPlaceholderText(/reviewer id/i), { target: { value: '1' } });
      fireEvent.change(screen.getByPlaceholderText(/optional annotation/i), {
        target: { value: '   ' },
      });
      fireEvent.click(screen.getByRole('button', { name: /submit decision/i }));

      await waitFor(() => {
        const body = mockApi.post.mock.calls[0][1] as { reasons: Array<{ criterion_type: string }> };
        const annotationReason = body.reasons.find((r) => r.criterion_type === 'annotation');
        expect(annotationReason).toBeUndefined();
      });
    });
  });
});
