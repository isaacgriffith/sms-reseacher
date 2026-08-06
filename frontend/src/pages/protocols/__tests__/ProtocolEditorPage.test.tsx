import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import ProtocolEditorPage from '../ProtocolEditorPage';
import { useProtocolDetail, useUpdateProtocol } from '../../../hooks/protocols/useProtocol';

const { mockNavigate, mockMutate, mockDispatch, mockDispatchYaml } = vi.hoisted(() => ({
  mockNavigate: vi.fn(),
  mockMutate: vi.fn(),
  mockDispatch: vi.fn(),
  mockDispatchYaml: vi.fn(),
}));

vi.mock('react-router-dom', () => ({
  useParams: vi.fn().mockReturnValue({ id: '1' }),
  useNavigate: () => mockNavigate,
}));
vi.mock('../../../hooks/protocols/useProtocol', () => ({
  useProtocolDetail: vi.fn().mockReturnValue({
    data: {
      id: 1,
      name: 'Test Protocol',
      study_type: 'sms',
      is_default_template: false,
      owner_user_id: 1,
      version_id: 1,
      description: null,
      nodes: [
        {
          id: 1,
          task_id: 't1',
          task_type: 'search',
          label: 'Search',
          description: 'Run search',
          is_required: true,
          position_x: 100,
          position_y: 200,
          inputs: [],
          outputs: [],
          quality_gates: [],
          assignees: [],
        },
      ],
      edges: [],
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
    isLoading: false,
    error: null,
  }),
  useUpdateProtocol: vi.fn().mockReturnValue({
    mutate: (...args: unknown[]) => mockMutate(...args),
    isPending: false,
    isError: false,
  }),
}));

vi.mock('../../../hooks/protocols/useProtocolEditor', () => ({
  useProtocolEditor: vi.fn().mockReturnValue({
    graph: {
      nodes: [
        {
          id: 1,
          task_id: 't1',
          task_type: 'search',
          label: 'Search',
          description: 'Run search',
          is_required: true,
          position_x: 100,
          position_y: 200,
          inputs: [],
          outputs: [],
          quality_gates: [],
          assignees: [],
        },
      ],
      edges: [],
    },
    yamlText: 'name: Test\n',
    yamlError: null,
    selectedNode: null,
    dispatch: mockDispatch,
    dispatchYamlDebounced: mockDispatchYaml,
  }),
}));

let graphCallbacks: Record<string, (...args: unknown[]) => void> = {};
vi.mock('../../../components/protocols/ProtocolGraph', () => ({
  default: ({ onNodeClick, onNodeMove }: Record<string, unknown>) => {
    graphCallbacks = { onNodeClick, onNodeMove } as Record<string, (...args: unknown[]) => void>;
    return React.createElement('div', { 'data-testid': 'protocol-graph' });
  },
}));

let textEditorCallbacks: Record<string, (...args: unknown[]) => void> = {};
vi.mock('../../../components/protocols/ProtocolTextEditor', () => ({
  default: ({ onChange }: Record<string, unknown>) => {
    textEditorCallbacks = { onChange } as Record<string, (...args: unknown[]) => void>;
    return React.createElement('div', { 'data-testid': 'protocol-text-editor' });
  },
}));

let nodePanelCallbacks: Record<string, (...args: unknown[]) => void> = {};
vi.mock('../../../components/protocols/ProtocolNodePanel', () => ({
  default: ({ onClose, onSave }: Record<string, unknown>) => {
    nodePanelCallbacks = { onClose, onSave } as Record<string, (...args: unknown[]) => void>;
    return null;
  },
}));

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    React.createElement(
      QueryClientProvider,
      { client: qc },
      React.createElement(ProtocolEditorPage),
    ),
  );
}

describe('ProtocolEditorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    graphCallbacks = {};
    textEditorCallbacks = {};
    nodePanelCallbacks = {};
    vi.mocked(useProtocolDetail).mockReturnValue({
      data: {
        id: 1,
        name: 'Test Protocol',
        study_type: 'sms',
        is_default_template: false,
        owner_user_id: 1,
        version_id: 1,
        description: null,
        nodes: [
          {
            id: 1,
            task_id: 't1',
            task_type: 'search',
            label: 'Search',
            description: 'Run search',
            is_required: true,
            position_x: 100,
            position_y: 200,
            inputs: [],
            outputs: [],
            quality_gates: [],
            assignees: [],
          },
        ],
        edges: [],
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useProtocolDetail>);
    vi.mocked(useUpdateProtocol).mockReturnValue({
      mutate: (...args: unknown[]) => mockMutate(...args),
      isPending: false,
      isError: false,
    } as ReturnType<typeof useUpdateProtocol>);
  });

  it('renders the editor page with graph and text editor', () => {
    renderPage();
    expect(screen.getByTestId('protocol-graph')).toBeInTheDocument();
    expect(screen.getByTestId('protocol-text-editor')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    vi.mocked(useProtocolDetail).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as ReturnType<typeof useProtocolDetail>);
    renderPage();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error state', () => {
    vi.mocked(useProtocolDetail).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('fail'),
    } as ReturnType<typeof useProtocolDetail>);
    renderPage();
    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  });

  it('calls save mutation on Save click', () => {
    renderPage();
    fireEvent.click(screen.getByText('Save'));
    expect(mockMutate).toHaveBeenCalled();
  });

  it('confirms the save in place instead of navigating away', () => {
    vi.mocked(useUpdateProtocol).mockReturnValue({
      mutate: (...args: unknown[]) => mockMutate(...args),
      isPending: false,
      isError: false,
      isSuccess: true,
    } as ReturnType<typeof useUpdateProtocol>);

    renderPage();

    // /protocols/:id is both the view and the edit route, so a successful save
    // shows a confirmation rather than a navigation.
    expect(screen.getByText(/protocol saved/i)).toBeInTheDocument();
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('navigates back on Discard click', () => {
    renderPage();
    fireEvent.click(screen.getByText('Discard'));
    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });

  it('dispatches on node click', () => {
    renderPage();
    graphCallbacks.onNodeClick({ task_id: 't1', label: 'Search' });
    expect(mockDispatch).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'SELECT_NODE', payload: { task_id: 't1' } }),
    );
  });

  it('dispatches on node move', () => {
    renderPage();
    graphCallbacks.onNodeMove('t1', 150, 250);
    expect(mockDispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'UPDATE_NODE',
        payload: { task_id: 't1', position_x: 150, position_y: 250 },
      }),
    );
  });

  it('calls dispatchYamlDebounced on text editor change', () => {
    renderPage();
    textEditorCallbacks.onChange('new yaml');
    expect(mockDispatchYaml).toHaveBeenCalledWith('new yaml');
  });

  it('dispatches UPDATE_NODE on node panel save', () => {
    renderPage();
    nodePanelCallbacks.onSave({ task_id: 't1', label: 'Updated' });
    expect(mockDispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'UPDATE_NODE',
        payload: { task_id: 't1', label: 'Updated' },
      }),
    );
  });
});
