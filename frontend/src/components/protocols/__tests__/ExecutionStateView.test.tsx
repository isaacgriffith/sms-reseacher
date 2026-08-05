import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import ExecutionStateView from '../ExecutionStateView';
import { useExecutionState } from '../../../hooks/protocols/useExecutionState';

vi.mock('../../../hooks/protocols/useExecutionState', () => ({
  useExecutionState: vi.fn().mockReturnValue({
    data: {
      tasks: [
        { node_id: 1, task_id: 't1', task_type: 'search', label: 'Search', status: 'active', gate_failure_detail: null },
        { node_id: 2, task_id: 't2', task_type: 'screening', label: 'Screen', status: 'complete', gate_failure_detail: null },
      ],
    },
    isLoading: false,
    error: null,
  }),
  useCompleteTask: vi.fn().mockReturnValue({ mutate: vi.fn(), isPending: false }),
  useApproveTask: vi.fn().mockReturnValue({ mutate: vi.fn(), isPending: false }),
}));

function renderView(props?: Record<string, unknown>) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    React.createElement(
      QueryClientProvider,
      { client: qc },
      React.createElement(ExecutionStateView, { studyId: 1, isAdmin: true, ...props }),
    ),
  );
}

describe('ExecutionStateView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useExecutionState).mockReturnValue({
      data: {
        tasks: [
          { node_id: 1, task_id: 't1', task_type: 'search', label: 'Search', status: 'active', gate_failure_detail: null },
          { node_id: 2, task_id: 't2', task_type: 'screening', label: 'Screen', status: 'complete', gate_failure_detail: null },
        ],
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useExecutionState>);
  });

  it('renders task cards', () => {
    renderView();
    expect(screen.getByText('Search')).toBeInTheDocument();
    expect(screen.getByText('Screen')).toBeInTheDocument();
  });

  it('shows Mark Complete button for active tasks when admin', () => {
    renderView();
    expect(screen.getByText('Mark Complete')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    vi.mocked(useExecutionState).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as ReturnType<typeof useExecutionState>);
    renderView();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows empty state', () => {
    vi.mocked(useExecutionState).mockReturnValue({
      data: { tasks: [] },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useExecutionState>);
    renderView();
    expect(screen.getByText('No tasks found.')).toBeInTheDocument();
  });
});
