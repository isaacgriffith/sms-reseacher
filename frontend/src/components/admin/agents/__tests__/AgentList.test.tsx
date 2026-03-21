/**
 * Unit tests for AgentList component.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import AgentList from '../AgentList';
import type { AgentSummary } from '../../../../types/agent';

const AGENT: AgentSummary = {
  id: '00000000-0000-0000-0000-000000000001',
  task_type: 'screener',
  role_name: 'Reviewer',
  persona_name: 'Alice',
  model_id: '00000000-0000-0000-0000-000000000002',
  provider_id: '00000000-0000-0000-0000-000000000003',
  model_display_name: 'GPT-4',
  provider_display_name: 'OpenAI',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('AgentList', () => {
  it('renders table headers', () => {
    render(<AgentList agents={[]} onEdit={vi.fn()} />);
    expect(screen.getByText('Task Type')).toBeInTheDocument();
    expect(screen.getByText('Role Name')).toBeInTheDocument();
  });

  it('shows empty state when no agents', () => {
    render(<AgentList agents={[]} onEdit={vi.fn()} />);
    expect(screen.getByText('No agents found.')).toBeInTheDocument();
  });

  it('renders an agent row', () => {
    render(<AgentList agents={[AGENT]} onEdit={vi.fn()} />);
    expect(screen.getByText('screener')).toBeInTheDocument();
    expect(screen.getByText('Reviewer')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders inactive chip for inactive agents', () => {
    render(<AgentList agents={[{ ...AGENT, is_active: false }]} onEdit={vi.fn()} />);
    expect(screen.getByText('Inactive')).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', () => {
    const onEdit = vi.fn();
    render(<AgentList agents={[AGENT]} onEdit={onEdit} />);
    fireEvent.click(screen.getByRole('button', { name: /edit agent/i }));
    expect(onEdit).toHaveBeenCalledWith(AGENT);
  });
});
