import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import AppShell from '../AppShell';

vi.mock('react-router-dom', () => ({
  Outlet: () => React.createElement('div', { 'data-testid': 'outlet' }, 'outlet'),
}));

vi.mock('../SideNav', () => ({
  default: () => React.createElement('nav', { 'data-testid': 'sidenav' }, 'nav'),
}));

describe('AppShell', () => {
  it('renders SideNav and Outlet', () => {
    render(React.createElement(AppShell));
    expect(screen.getByTestId('sidenav')).toBeInTheDocument();
    expect(screen.getByTestId('outlet')).toBeInTheDocument();
  });
});
