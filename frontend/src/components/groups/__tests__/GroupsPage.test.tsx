import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import GroupsPage from '../GroupsPage';
import { api } from '../../../services/api';

vi.mock('../../../services/api', () => ({
  api: { get: vi.fn(), post: vi.fn() },
  ApiError: class extends Error {
    detail: string;
    constructor(_s: number, d: string) {
      super(d);
      this.detail = d;
    }
  },
}));

vi.mock('../GroupCard', () => ({
  default: ({ group }: { group: { name: string } }) =>
    React.createElement('div', { 'data-testid': 'group-card' }, group.name),
}));

const mockApi = vi.mocked(api);

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    React.createElement(QueryClientProvider, { client: qc }, React.createElement(GroupsPage)),
  );
}

describe('GroupsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state', () => {
    mockApi.get.mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/Loading groups/)).toBeInTheDocument();
  });

  it('shows error state', async () => {
    mockApi.get.mockRejectedValue(new Error('fail'));
    renderPage();
    await waitFor(() => expect(screen.getByText(/Failed to load groups/)).toBeInTheDocument());
  });

  it('shows empty state', async () => {
    mockApi.get.mockResolvedValue([]);
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/not a member of any research groups/)).toBeInTheDocument(),
    );
  });

  it('shows group cards', async () => {
    mockApi.get.mockResolvedValue([{ id: 1, name: 'Group A', role: 'owner', study_count: 3 }]);
    renderPage();
    await waitFor(() => expect(screen.getByText('Group A')).toBeInTheDocument());
  });

  it('toggles create form', async () => {
    mockApi.get.mockResolvedValue([]);
    renderPage();
    await waitFor(() => expect(screen.getByText('New Group')).toBeInTheDocument());
    fireEvent.click(screen.getByText('New Group'));
    expect(screen.getByPlaceholderText('Group name')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Cancel'));
    expect(screen.queryByPlaceholderText('Group name')).not.toBeInTheDocument();
  });

  it('creates a new group', async () => {
    mockApi.get.mockResolvedValue([]);
    mockApi.post.mockResolvedValue({ id: 2, name: 'New' });
    renderPage();
    await waitFor(() => expect(screen.getByText('New Group')).toBeInTheDocument());
    fireEvent.click(screen.getByText('New Group'));
    fireEvent.change(screen.getByPlaceholderText('Group name'), {
      target: { value: 'My Group' },
    });
    fireEvent.submit(screen.getByPlaceholderText('Group name').closest('form')!);
    await waitFor(() => expect(mockApi.post).toHaveBeenCalled());
  });
});
