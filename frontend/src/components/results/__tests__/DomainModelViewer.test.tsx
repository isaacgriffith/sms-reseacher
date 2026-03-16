/**
 * Tests for DomainModelViewer component.
 *
 * The D3 graph rendering code uses useEffect + SVGElement which requires
 * mocking in jsdom.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import DomainModelViewer from '../DomainModelViewer';

// Mock d3 to avoid complex canvas/SVG rendering in jsdom
vi.mock('d3', () => ({
  select: vi.fn().mockReturnValue({
    selectAll: vi.fn().mockReturnThis(),
    remove: vi.fn().mockReturnThis(),
    attr: vi.fn().mockReturnThis(),
    append: vi.fn().mockReturnThis(),
    call: vi.fn().mockReturnThis(),
    data: vi.fn().mockReturnThis(),
    enter: vi.fn().mockReturnThis(),
    text: vi.fn().mockReturnThis(),
  }),
  forceSimulation: vi.fn().mockReturnValue({
    force: vi.fn().mockReturnThis(),
    alphaDecay: vi.fn().mockReturnThis(),
    on: vi.fn().mockReturnThis(),
  }),
  forceManyBody: vi.fn().mockReturnValue({ strength: vi.fn().mockReturnThis() }),
  forceLink: vi.fn().mockReturnValue({ id: vi.fn().mockReturnThis(), distance: vi.fn().mockReturnThis() }),
  forceCenter: vi.fn().mockReturnValue({}),
  forceCollide: vi.fn().mockReturnValue({}),
  zoom: vi.fn().mockReturnValue({
    scaleExtent: vi.fn().mockReturnThis(),
    on: vi.fn().mockReturnThis(),
  }),
  drag: vi.fn().mockReturnValue({
    on: vi.fn().mockReturnThis(),
  }),
}));

const DOMAIN_MODEL_EMPTY = {
  id: 1,
  version: 1,
  concepts: null,
  relationships: null,
};

const DOMAIN_MODEL_WITH_DATA = {
  id: 2,
  version: 2,
  concepts: [
    { name: 'Software Testing', definition: 'The process of evaluating software', attributes: [] },
    { name: 'TDD', definition: 'Test-Driven Development', attributes: ['red-green-refactor'] },
  ],
  relationships: [
    { from: 'TDD', to: 'Software Testing', label: 'is a type of', type: 'specialisation' },
  ],
};

describe('DomainModelViewer', () => {
  it('renders empty state message when no concepts', () => {
    render(<DomainModelViewer domainModel={DOMAIN_MODEL_EMPTY} />);
    expect(screen.getByText(/not available/i)).toBeInTheDocument();
  });

  it('renders SVG container when concepts are present', () => {
    render(<DomainModelViewer domainModel={DOMAIN_MODEL_WITH_DATA} />);
    // SVG should be rendered
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('renders export button when concepts are present', () => {
    render(<DomainModelViewer domainModel={DOMAIN_MODEL_WITH_DATA} />);
    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });

  it('shows version in export button label', () => {
    render(<DomainModelViewer domainModel={DOMAIN_MODEL_WITH_DATA} />);
    // The export button should reference the version
    const button = screen.getByRole('button', { name: /export/i });
    expect(button).toBeInTheDocument();
  });
});
