/**
 * Tests for ForestPlotViewer component (feature 007, T079).
 *
 * Covers:
 * - Renders SVG content when forestPlotSvg is provided.
 * - Shows skeleton when isLoading is true.
 * - Shows empty state when forestPlotSvg is null and not loading.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ForestPlotViewer from '../ForestPlotViewer';

describe('ForestPlotViewer', () => {
  describe('Loading state', () => {
    it('shows skeleton when isLoading is true', () => {
      render(<ForestPlotViewer forestPlotSvg={null} isLoading />);
      expect(screen.getByTestId('forest-plot-skeleton')).toBeInTheDocument();
      expect(screen.queryByTestId('forest-plot-empty')).not.toBeInTheDocument();
      expect(screen.queryByTestId('forest-plot-svg')).not.toBeInTheDocument();
    });

    it('skeleton has accessible label', () => {
      render(<ForestPlotViewer forestPlotSvg={null} isLoading />);
      expect(screen.getByLabelText(/loading forest plot/i)).toBeInTheDocument();
    });
  });

  describe('Empty state', () => {
    it('shows empty state when forestPlotSvg is null and not loading', () => {
      render(<ForestPlotViewer forestPlotSvg={null} />);
      expect(screen.getByTestId('forest-plot-empty')).toBeInTheDocument();
      expect(screen.queryByTestId('forest-plot-skeleton')).not.toBeInTheDocument();
    });

    it('empty state contains helpful text', () => {
      render(<ForestPlotViewer forestPlotSvg={null} />);
      expect(screen.getByTestId('forest-plot-empty')).toHaveTextContent(/no forest plot/i);
    });
  });

  describe('SVG rendering', () => {
    it('renders the SVG box when forestPlotSvg is provided', () => {
      const svg = '<svg><rect width="100" height="100"/></svg>';
      render(<ForestPlotViewer forestPlotSvg={svg} />);
      const box = screen.getByTestId('forest-plot-svg');
      expect(box).toBeInTheDocument();
      expect(box.innerHTML).toContain('<svg>');
    });

    it('does not show skeleton or empty state when SVG is provided', () => {
      const svg = '<svg>test</svg>';
      render(<ForestPlotViewer forestPlotSvg={svg} />);
      expect(screen.queryByTestId('forest-plot-skeleton')).not.toBeInTheDocument();
      expect(screen.queryByTestId('forest-plot-empty')).not.toBeInTheDocument();
    });
  });

  describe('Default props', () => {
    it('isLoading defaults to false — shows empty state for null svg', () => {
      render(<ForestPlotViewer forestPlotSvg={null} />);
      expect(screen.getByTestId('forest-plot-empty')).toBeInTheDocument();
    });
  });
});
