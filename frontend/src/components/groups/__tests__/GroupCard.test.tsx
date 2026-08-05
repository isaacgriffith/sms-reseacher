import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';
import GroupCard from '../GroupCard';

describe('GroupCard', () => {
  it('renders group name and study count', () => {
    render(
      React.createElement(
        MemoryRouter,
        null,
        React.createElement(GroupCard, {
          group: { id: 1, name: 'Test Group', role: 'admin', study_count: 3 },
        }),
      ),
    );
    expect(screen.getByText('Test Group')).toBeInTheDocument();
    expect(screen.getByText('3 studies')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
  });

  it('renders singular study for count 1', () => {
    render(
      React.createElement(
        MemoryRouter,
        null,
        React.createElement(GroupCard, {
          group: { id: 2, name: 'Solo Group', role: 'member', study_count: 1 },
        }),
      ),
    );
    expect(screen.getByText('1 study')).toBeInTheDocument();
  });
});
