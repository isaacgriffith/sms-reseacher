import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import AgentForm from '../AgentForm';

vi.mock('../../../../services/agentsApi', () => ({
  useUpdateAgent: vi.fn().mockReturnValue({ mutateAsync: vi.fn(), isPending: false }),
  useGenerateSystemMessage: vi.fn().mockReturnValue({ mutateAsync: vi.fn(), isPending: false }),
  useUndoSystemMessage: vi.fn().mockReturnValue({ mutateAsync: vi.fn(), isPending: false }),
}));

vi.mock('../../../../services/providersApi', () => ({
  useProviderModels: vi.fn().mockReturnValue({ data: [], isLoading: false }),
}));

vi.mock('../SystemMessageEditor', () => ({
  default: ({ value }: { value: string }) =>
    React.createElement('div', { 'data-testid': 'sys-msg-editor' }, value),
}));

const mockAgent = {
  id: '00000000-0000-0000-0000-000000000001',
  task_type: 'screener' as const,
  role_name: 'Reviewer',
  persona_name: 'Alice',
  model_id: '00000000-0000-0000-0000-000000000002',
  provider_id: '00000000-0000-0000-0000-000000000003',
  model_display_name: 'GPT-4',
  provider_display_name: 'OpenAI',
  is_active: true,
  role_description: 'Reviews papers.',
  persona_description: 'Diligent.',
  persona_svg: null,
  system_message_template: 'You are a reviewer.',
  system_message_undo_buffer: null,
  version_id: 1,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('AgentForm', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders agent details in form', () => {
    render(
      React.createElement(AgentForm, {
        agent: mockAgent,
        onSuccess: vi.fn(),
        onCancel: vi.fn(),
      }),
    );
    expect(screen.getByDisplayValue('Reviewer')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Alice')).toBeInTheDocument();
  });

  it('renders system message editor', () => {
    render(
      React.createElement(AgentForm, {
        agent: mockAgent,
        onSuccess: vi.fn(),
        onCancel: vi.fn(),
      }),
    );
    expect(screen.getByTestId('sys-msg-editor')).toBeInTheDocument();
  });
});
