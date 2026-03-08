/**
 * Tests for ChartGallery component.
 *
 * Verifies:
 * - Renders empty-state message when charts array is empty
 * - Renders an <img> element for each chart that has svg_content
 * - img src points to the correct SVG API endpoint
 * - Download button is present and enabled when svg_content exists
 * - Download button is disabled when svg_content is null
 * - Chart type labels are displayed in human-readable form
 */
// @ts-nocheck


import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// jsdom does not implement URL.createObjectURL — provide a stub
if (!URL.createObjectURL) {
  URL.createObjectURL = vi.fn().mockReturnValue('blob:stub');
  URL.revokeObjectURL = vi.fn();
}

import ChartGallery from '../ChartGallery';

const STUDY_ID = 42;

function makeChart(overrides: Partial<{
  id: number;
  chart_type: string;
  version: number;
  svg_content: string | null;
}> = {}) {
  return {
    id: overrides.id ?? 1,
    chart_type: overrides.chart_type ?? 'venue',
    version: overrides.version ?? 1,
    svg_content: overrides.svg_content !== undefined ? overrides.svg_content : '<svg/>',
  };
}

describe('ChartGallery', () => {
  describe('empty state', () => {
    it('shows empty-state message when charts array is empty', () => {
      render(<ChartGallery studyId={STUDY_ID} charts={[]} />);
      expect(screen.getByText(/no charts generated yet/i)).toBeTruthy();
    });

    it('does not render any img when charts is empty', () => {
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={[]} />);
      expect(container.querySelectorAll('img').length).toBe(0);
    });
  });

  describe('chart rendering', () => {
    it('renders one img per chart that has svg_content', () => {
      const charts = [
        makeChart({ id: 1, chart_type: 'venue', svg_content: '<svg/>' }),
        makeChart({ id: 2, chart_type: 'year', svg_content: '<svg/>' }),
        makeChart({ id: 3, chart_type: 'author', svg_content: null }),
      ];
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      // Only 2 charts have svg_content — each gets an <img>
      expect(container.querySelectorAll('img').length).toBe(2);
    });

    it('sets img src to the SVG API endpoint', () => {
      const charts = [makeChart({ id: 7, chart_type: 'research_type', svg_content: '<svg/>' })];
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      const img = container.querySelector('img') as HTMLImageElement;
      expect(img.getAttribute('src')).toBe(
        `/api/v1/studies/${STUDY_ID}/results/charts/7/svg`
      );
    });

    it('shows chart type label for each chart', () => {
      const charts = [makeChart({ id: 1, chart_type: 'research_method', svg_content: '<svg/>' })];
      render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      // Label maps research_method → "Research Method" (capitalized, not lowercase)
      expect(screen.getByText('Research Method')).toBeTruthy();
    });

    it('falls back to replace-underscore label for unknown chart types', () => {
      const charts = [makeChart({ id: 1, chart_type: 'custom_type', svg_content: '<svg/>' })];
      render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      // Unknown chart type: 'custom_type' → 'custom type' via replace
      expect(screen.getByText('custom type')).toBeTruthy();
    });

    it('shows "No data" placeholder when svg_content is null', () => {
      const charts = [makeChart({ id: 1, chart_type: 'venue', svg_content: null })];
      render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      expect(screen.getByText('No data')).toBeTruthy();
    });

    it('does not show "No data" when svg_content is present', () => {
      const charts = [makeChart({ id: 1, chart_type: 'venue', svg_content: '<svg/>' })];
      render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      expect(screen.queryByText('No data')).toBeNull();
    });

    it('displays version number', () => {
      const charts = [makeChart({ id: 1, chart_type: 'venue', version: 3, svg_content: '<svg/>' })];
      render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      expect(screen.getByText(/v3/)).toBeTruthy();
    });
  });

  describe('download button', () => {
    it('download button is enabled when svg_content is present', () => {
      const charts = [makeChart({ id: 1, svg_content: '<svg/>' })];
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      const btn = container.querySelector('button') as HTMLButtonElement;
      expect(btn.disabled).toBe(false);
    });

    it('download button is disabled when svg_content is null', () => {
      const charts = [makeChart({ id: 1, svg_content: null })];
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      const btn = container.querySelector('button') as HTMLButtonElement;
      expect(btn.disabled).toBe(true);
    });

    it('clicking download button does not throw when svg_content is present', () => {
      // Mock URL.createObjectURL so jsdom does not throw
      const createSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test');
      const revokeSpy = vi.spyOn(URL, 'revokeObjectURL').mockReturnValue(undefined);

      const charts = [makeChart({ id: 1, chart_type: 'venue', svg_content: '<svg/>' })];
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      const btn = container.querySelector('button') as HTMLButtonElement;
      expect(() => fireEvent.click(btn)).not.toThrow();

      createSpy.mockRestore();
      revokeSpy.mockRestore();
    });

    it('calls URL.createObjectURL when download button clicked with svg_content', () => {
      const createSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test');
      vi.spyOn(URL, 'revokeObjectURL').mockReturnValue(undefined);

      const charts = [makeChart({ id: 1, chart_type: 'venue', svg_content: '<svg>content</svg>' })];
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      const btn = container.querySelector('button') as HTMLButtonElement;
      fireEvent.click(btn);

      expect(createSpy).toHaveBeenCalledTimes(1);
      createSpy.mockRestore();
    });

    it('does not call URL.createObjectURL when svg_content is null', () => {
      const createSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test');

      const charts = [makeChart({ id: 1, chart_type: 'venue', svg_content: null })];
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      const btn = container.querySelector('button') as HTMLButtonElement;
      fireEvent.click(btn);

      expect(createSpy).not.toHaveBeenCalled();
      createSpy.mockRestore();
    });
  });

  describe('multiple chart types', () => {
    it('renders all 8 known chart types if provided', () => {
      const types = ['venue', 'author', 'locale', 'institution', 'year', 'subtopic', 'research_type', 'research_method'];
      const charts = types.map((t, i) => makeChart({ id: i + 1, chart_type: t, svg_content: '<svg/>' }));
      const { container } = render(<ChartGallery studyId={STUDY_ID} charts={charts} />);
      expect(container.querySelectorAll('img').length).toBe(8);
    });
  });
});
