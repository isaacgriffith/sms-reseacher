import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import ProtocolList from '../ProtocolList';

const PROTOCOLS = [
  {
    id: 1,
    name: 'SMS Default',
    study_type: 'sms',
    is_default_template: true,
    owner_user_id: null,
    version_id: 2,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Custom SLR',
    study_type: 'slr',
    is_default_template: false,
    owner_user_id: 1,
    version_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

describe('ProtocolList', () => {
  it('shows empty message when no protocols', () => {
    render(React.createElement(ProtocolList, { protocols: [] }));
    expect(screen.getByText('No protocols found.')).toBeInTheDocument();
  });

  it('renders protocol items with names and badges', () => {
    render(React.createElement(ProtocolList, { protocols: PROTOCOLS }));
    expect(screen.getByText('SMS Default')).toBeInTheDocument();
    expect(screen.getByText('Custom SLR')).toBeInTheDocument();
    expect(screen.getByText('sms')).toBeInTheDocument();
    expect(screen.getByText('Default')).toBeInTheDocument();
  });

  it('calls onSelect when item clicked', () => {
    const onSelect = vi.fn();
    render(React.createElement(ProtocolList, { protocols: PROTOCOLS, onSelect }));
    fireEvent.click(screen.getByText('SMS Default'));
    expect(onSelect).toHaveBeenCalledWith(PROTOCOLS[0]);
  });

  it('shows and calls onCopy button', () => {
    const onCopy = vi.fn();
    render(React.createElement(ProtocolList, { protocols: PROTOCOLS, onCopy }));
    const copyBtns = screen.getAllByText('Copy');
    fireEvent.click(copyBtns[0]);
    expect(onCopy).toHaveBeenCalledWith(PROTOCOLS[0]);
  });

  it('shows and calls onAssign button', () => {
    const onAssign = vi.fn();
    render(React.createElement(ProtocolList, { protocols: PROTOCOLS, onAssign }));
    const assignBtns = screen.getAllByText('Assign');
    fireEvent.click(assignBtns[0]);
    expect(onAssign).toHaveBeenCalledWith(PROTOCOLS[0]);
  });

  it('shows and calls onExport button', () => {
    const onExport = vi.fn();
    render(React.createElement(ProtocolList, { protocols: PROTOCOLS, onExport }));
    const exportBtns = screen.getAllByText('Export');
    fireEvent.click(exportBtns[0]);
    expect(onExport).toHaveBeenCalledWith(PROTOCOLS[0]);
  });
});
