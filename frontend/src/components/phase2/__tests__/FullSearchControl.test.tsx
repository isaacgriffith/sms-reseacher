/**
 * Tests for FullSearchControl.
 *
 * Extracted from `renderSearchAndScreen`, where the click handler caught every
 * error and discarded it. That became a real defect once the in-flight guard
 * landed: `POST /studies/{id}/searches` now answers 409 while another
 * automated pass is running, and swallowing it leaves a button that does
 * nothing precisely when the user most needs to know why.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
  // Mirrors the real ApiError signature: (status, detail).
  ApiError: class ApiError extends Error {
    status: number;
    detail: string;
    constructor(status: number, detail: string) {
      super(detail);
      this.name = 'ApiError';
      this.status = status;
      this.detail = detail;
    }
  },
}));

import { api, ApiError } from '../../../services/api';
import FullSearchControl from '../FullSearchControl';

const mockApi = api as unknown as {
  post: ReturnType<typeof vi.fn>;
};

describe('FullSearchControl', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('posts the databases and phase tag the search job expects', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'job-1', search_execution_id: 3 });

    render(<FullSearchControl studyId={4} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/studies/4/searches', {
        databases: ['acm', 'ieee', 'scopus'],
        phase_tag: 'initial-search',
      });
    });
  });

  it('hands the started job id to the progress panel', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'job-7', search_execution_id: 3 });
    const onJobStarted = vi.fn();

    render(<FullSearchControl studyId={1} onJobStarted={onJobStarted} />);
    fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

    await waitFor(() => {
      expect(onJobStarted).toHaveBeenCalledWith('job-7');
    });
  });

  /**
   * The regression this file exists for: the old handler discarded this.
   */
  it('shows why a search was refused when another pass is in flight', async () => {
    mockApi.post.mockRejectedValue(
      new ApiError(409, 'Another automated pass is already running for this study.'),
    );

    render(<FullSearchControl studyId={1} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/already running/i);
  });

  it('shows why a search was refused when no search string exists', async () => {
    mockApi.post.mockRejectedValue(
      new ApiError(422, 'No search string found for this study. Create one first.'),
    );

    render(<FullSearchControl studyId={1} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/no search string/i);
  });

  it('does not start a job when the request was refused', async () => {
    mockApi.post.mockRejectedValue(new ApiError(409, 'Another automated pass is running.'));
    const onJobStarted = vi.fn();

    render(<FullSearchControl studyId={1} onJobStarted={onJobStarted} />);
    fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

    await screen.findByRole('alert');
    expect(onJobStarted).not.toHaveBeenCalled();
  });

  it('clears a previous refusal when a later search succeeds', async () => {
    mockApi.post.mockRejectedValueOnce(new ApiError(409, 'Another automated pass is running.'));
    render(<FullSearchControl studyId={1} onJobStarted={vi.fn()} />);

    fireEvent.click(screen.getByRole('button', { name: /run full search/i }));
    await screen.findByRole('alert');

    mockApi.post.mockResolvedValue({ job_id: 'job-2', search_execution_id: 4 });
    fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  it('disables the button while a search is being started', async () => {
    let resolvePost: (v: unknown) => void = () => {};
    mockApi.post.mockReturnValue(
      new Promise((resolve) => {
        resolvePost = resolve;
      }),
    );

    render(<FullSearchControl studyId={1} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /run full search/i }));

    await waitFor(() => {
      expect(screen.getByRole('button')).toBeDisabled();
    });

    resolvePost({ job_id: 'job-1', search_execution_id: 1 });
    await waitFor(() => {
      expect(screen.getByRole('button')).not.toBeDisabled();
    });
  });
});
