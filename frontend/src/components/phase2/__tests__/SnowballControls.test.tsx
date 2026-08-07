/**
 * Tests for SnowballControls.
 *
 * Closes the frontend half of G22: `run_snowball` was a registered ARQ job with
 * no enqueue site and no control, so backward and forward snowballing had never
 * run for a user. An endpoint alone does not make it reachable (Principle X).
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
import SnowballControls from '../SnowballControls';

const mockApi = api as unknown as {
  post: ReturnType<typeof vi.fn>;
};

describe('SnowballControls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('offers both snowball directions', () => {
    render(<SnowballControls studyId={1} onJobStarted={vi.fn()} />);

    expect(screen.getByRole('button', { name: /backward/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /forward/i })).toBeInTheDocument();
  });

  it('posts the backward direction when backward is clicked', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'job-1', search_execution_id: 5, seed_count: 3 });

    render(<SnowballControls studyId={7} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /backward/i }));

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/studies/7/snowball', {
        direction: 'backward',
      });
    });
  });

  it('posts the forward direction when forward is clicked', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'job-2', search_execution_id: 6, seed_count: 1 });

    render(<SnowballControls studyId={7} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /forward/i }));

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/studies/7/snowball', {
        direction: 'forward',
      });
    });
  });

  it('hands the started job id to the progress panel via onJobStarted', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'job-9', search_execution_id: 5, seed_count: 2 });
    const onJobStarted = vi.fn();

    render(<SnowballControls studyId={1} onJobStarted={onJobStarted} />);
    fireEvent.click(screen.getByRole('button', { name: /backward/i }));

    await waitFor(() => {
      expect(onJobStarted).toHaveBeenCalledWith('job-9');
    });
  });

  it('reports how many seed papers the run started from', async () => {
    mockApi.post.mockResolvedValue({ job_id: 'job-1', search_execution_id: 5, seed_count: 4 });

    render(<SnowballControls studyId={1} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /backward/i }));

    expect(await screen.findByText(/4 seed papers/i)).toBeInTheDocument();
  });

  /**
   * The 409 is an expected outcome, not an exception: the study already has an
   * automated pass running. Swallowing it leaves a button that does nothing.
   */
  it('shows why a run was refused when another pass is in flight', async () => {
    mockApi.post.mockRejectedValue(
      new ApiError(409, 'Another automated pass is already running for this study.'),
    );

    render(<SnowballControls studyId={1} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /backward/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/already running/i);
  });

  it('shows why a run was refused when the study has no accepted papers', async () => {
    mockApi.post.mockRejectedValue(
      new ApiError(422, 'No seed papers to snowball from. Accept at least one paper.'),
    );

    render(<SnowballControls studyId={1} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /forward/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/no seed papers/i);
  });

  it('does not start a job when the request was refused', async () => {
    mockApi.post.mockRejectedValue(new ApiError(409, 'Another automated pass is running.'));
    const onJobStarted = vi.fn();

    render(<SnowballControls studyId={1} onJobStarted={onJobStarted} />);
    fireEvent.click(screen.getByRole('button', { name: /backward/i }));

    await screen.findByRole('alert');
    expect(onJobStarted).not.toHaveBeenCalled();
  });

  it('clears a previous refusal when a later run succeeds', async () => {
    mockApi.post.mockRejectedValueOnce(new ApiError(409, 'Another automated pass is running.'));
    render(<SnowballControls studyId={1} onJobStarted={vi.fn()} />);

    fireEvent.click(screen.getByRole('button', { name: /backward/i }));
    await screen.findByRole('alert');

    mockApi.post.mockResolvedValue({ job_id: 'job-3', search_execution_id: 7, seed_count: 1 });
    fireEvent.click(screen.getByRole('button', { name: /backward/i }));

    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  it('disables both directions while a run is being started', async () => {
    let resolvePost: (v: unknown) => void = () => {};
    mockApi.post.mockReturnValue(
      new Promise((resolve) => {
        resolvePost = resolve;
      }),
    );

    render(<SnowballControls studyId={1} onJobStarted={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /backward/i }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /forward/i })).toBeDisabled();
    });

    resolvePost({ job_id: 'job-1', search_execution_id: 1, seed_count: 1 });
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /forward/i })).not.toBeDisabled();
    });
  });
});
