import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import AgentWizard from '../AgentWizard';

const { mockCreateMutateAsync, mockSvgMutateAsync, mockSysMsgMutateAsync } = vi.hoisted(() => ({
  mockCreateMutateAsync: vi.fn().mockResolvedValue({ id: 'a1' }),
  mockSvgMutateAsync: vi.fn().mockResolvedValue({ svg: '<svg>icon</svg>' }),
  mockSysMsgMutateAsync: vi.fn().mockResolvedValue({ system_message_template: 'generated msg' }),
}));

vi.mock('../../../../services/agentsApi', () => ({
  useAgentTaskTypes: vi.fn().mockReturnValue({ data: ['screener', 'extractor'], isLoading: false }),
  useCreateAgent: vi.fn().mockReturnValue({
    mutateAsync: mockCreateMutateAsync,
    isPending: false,
    isError: false,
    error: null,
  }),
  useGeneratePersonaSvg: vi.fn().mockReturnValue({
    mutateAsync: mockSvgMutateAsync,
    isPending: false,
  }),
  useGenerateSystemMessage: vi.fn().mockReturnValue({
    mutateAsync: mockSysMsgMutateAsync,
    isPending: false,
    isError: false,
    error: null,
  }),
}));

vi.mock('../../../../services/providersApi', () => ({
  useProviders: vi.fn().mockReturnValue({
    data: [{ id: 'p1', display_name: 'OpenAI', provider_type: 'openai', is_enabled: true }],
    isLoading: false,
  }),
  useProviderModels: vi.fn().mockReturnValue({
    data: [{ id: 'm1', model_identifier: 'gpt-4', display_name: 'GPT-4', is_enabled: true }],
    isLoading: false,
  }),
}));

vi.mock('../SystemMessageEditor', () => ({
  default: ({ value, onChange, onUndo, canUndo }: { value: string; onChange: (v: string) => void; onUndo: () => void; canUndo: boolean }) =>
    React.createElement('div', { 'data-testid': 'sys-msg-editor' }, [
      React.createElement('textarea', {
        key: 'ta',
        'data-testid': 'sys-msg-textarea',
        value,
        onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => onChange(e.target.value),
      }),
      canUndo && React.createElement('button', { key: 'undo', onClick: onUndo }, 'Undo'),
    ]),
}));

function renderWizard() {
  const onClose = vi.fn();
  const result = render(React.createElement(AgentWizard, { open: true, onClose }));
  return { ...result, onClose };
}

async function selectTaskType() {
  // Open the Task Type dropdown and select 'screener'
  const selects = screen.getAllByRole('combobox');
  fireEvent.mouseDown(selects[0]);
  await waitFor(() => screen.getByRole('option', { name: 'screener' }));
  fireEvent.click(screen.getByRole('option', { name: 'screener' }));
}

async function advanceToStep(stepIndex: number) {
  if (stepIndex >= 1) {
    await selectTaskType();
    fireEvent.click(screen.getByText('Next'));
  }
  if (stepIndex >= 2) {
    // Step 1: Select provider and model
    const selects = screen.getAllByRole('combobox');
    fireEvent.mouseDown(selects[0]); // provider
    await waitFor(() => screen.getByRole('option', { name: 'OpenAI' }));
    fireEvent.click(screen.getByRole('option', { name: 'OpenAI' }));

    const modelSelects = screen.getAllByRole('combobox');
    fireEvent.mouseDown(modelSelects[1]); // model
    await waitFor(() => screen.getByRole('option', { name: 'GPT-4' }));
    fireEvent.click(screen.getByRole('option', { name: 'GPT-4' }));
    fireEvent.click(screen.getByText('Next'));
  }
  if (stepIndex >= 3) {
    // Step 2: Fill role & persona
    fireEvent.change(screen.getByLabelText('Role Name'), { target: { value: 'Reviewer' } });
    fireEvent.change(screen.getByLabelText('Persona Name'), { target: { value: 'Alice' } });
    fireEvent.click(screen.getByText('Next'));
  }
  if (stepIndex >= 4) {
    // Step 3: Skip SVG
    fireEvent.click(screen.getByText('Next'));
  }
}

describe('AgentWizard', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders step 0 with task type selection', () => {
    renderWizard();
    expect(screen.getByText('Create Agent')).toBeInTheDocument();
    expect(screen.getAllByText('Task Type').length).toBeGreaterThanOrEqual(1);
  });

  it('does not render when closed', () => {
    const onClose = vi.fn();
    render(React.createElement(AgentWizard, { open: false, onClose }));
    expect(screen.queryByText('Create Agent')).not.toBeInTheDocument();
  });

  it('Next is disabled when no task type selected', () => {
    renderWizard();
    expect(screen.getByText('Next')).toBeDisabled();
  });

  it('advances to step 1 (Model Selection) after selecting task type', async () => {
    renderWizard();
    await selectTaskType();
    fireEvent.click(screen.getByText('Next'));
    // Step 1 shows Provider and Model labels
    expect(screen.getByLabelText('Provider')).toBeInTheDocument();
    expect(screen.getByLabelText('Model')).toBeInTheDocument();
  });

  it('advances to step 2 (Role & Persona) with provider and model selected', async () => {
    renderWizard();
    await advanceToStep(2);
    expect(screen.getByLabelText('Role Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Persona Name')).toBeInTheDocument();
  });

  it('advances to step 3 (SVG) and can generate SVG', async () => {
    renderWizard();
    await advanceToStep(3);
    expect(screen.getByText('Generate SVG')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Generate SVG'));
    await waitFor(() => expect(mockSvgMutateAsync).toHaveBeenCalled());
  });

  it('advances to step 4 (System Message) and shows editor', async () => {
    renderWizard();
    await advanceToStep(4);
    expect(screen.getByTestId('sys-msg-editor')).toBeInTheDocument();
    expect(screen.getByText(/Generate System Message/)).toBeInTheDocument();
  });

  it('Back button works', async () => {
    renderWizard();
    await advanceToStep(1);
    // Now on step 1, click Back
    fireEvent.click(screen.getByText('Back'));
    // Should be back on step 0 with Task Type
    expect(screen.getAllByText('Task Type').length).toBeGreaterThanOrEqual(1);
  });

  it('Cancel button calls onClose', async () => {
    const { onClose } = renderWizard();
    fireEvent.click(screen.getByText('Cancel'));
    expect(onClose).toHaveBeenCalled();
  });

  it('Generate System Message button calls createAgent and generateSysMsg', async () => {
    renderWizard();
    await advanceToStep(4);
    fireEvent.click(screen.getByText(/Generate System Message/));
    await waitFor(() => expect(mockCreateMutateAsync).toHaveBeenCalled());
    await waitFor(() => expect(mockSysMsgMutateAsync).toHaveBeenCalledWith('a1'));
  });

  it('Save button on last step calls createAgent and closes', async () => {
    renderWizard();
    await advanceToStep(4);
    fireEvent.click(screen.getByText('Save'));
    await waitFor(() => expect(mockCreateMutateAsync).toHaveBeenCalled());
  });

  it('editing system message template dispatches SET_TEMPLATE', async () => {
    renderWizard();
    await advanceToStep(4);
    const textarea = screen.getByTestId('sys-msg-textarea');
    fireEvent.change(textarea, { target: { value: 'custom template' } });
    expect(textarea).toHaveValue('custom template');
  });
});
