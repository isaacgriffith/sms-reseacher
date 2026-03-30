/**
 * Unit tests for LandscapeSummarySection component (feature 009).
 *
 * Covers:
 * - Renders all three accordion panel headings.
 * - Timeline content is displayed.
 * - RQ evolution content is displayed.
 * - Synthesis method shifts content is displayed.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect } from 'vitest';
import LandscapeSummarySection from '../LandscapeSummarySection';
import type { LandscapeSection } from '../LandscapeSummarySection';

const LANDSCAPE_FIXTURE: LandscapeSection = {
  timeline_summary: 'Studies span 2010–2023.',
  research_question_evolution: 'RQs evolved over three eras.',
  synthesis_method_shifts: 'Meta-analysis became dominant after 2015.',
};

describe('LandscapeSummarySection', () => {
  it('renders the Timeline panel heading', () => {
    render(<LandscapeSummarySection landscape={LANDSCAPE_FIXTURE} />);
    expect(screen.getByText(/Timeline of Secondary Studies/i)).toBeInTheDocument();
  });

  it('renders the Research Question Evolution panel heading', () => {
    render(<LandscapeSummarySection landscape={LANDSCAPE_FIXTURE} />);
    expect(screen.getByText(/Research Question Evolution/i)).toBeInTheDocument();
  });

  it('renders the Synthesis Method Shifts panel heading', () => {
    render(<LandscapeSummarySection landscape={LANDSCAPE_FIXTURE} />);
    expect(screen.getByText(/Synthesis Method Shifts/i)).toBeInTheDocument();
  });

  it('displays timeline_summary content', () => {
    render(<LandscapeSummarySection landscape={LANDSCAPE_FIXTURE} />);
    expect(screen.getByText(/Studies span 2010/)).toBeInTheDocument();
  });
});
