/**
 * Unit tests for BriefingPreview component (feature 008).
 *
 * Covers rendering of title, summary, findings, target audience, threats,
 * reference to complementary material, and institution logos sections.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import BriefingPreview from '../BriefingPreview';
import type { BriefingDetail } from '../../../services/rapid/briefingApi';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const BASE_BRIEFING: BriefingDetail = {
  id: 1,
  study_id: 42,
  version_number: 1,
  status: 'draft',
  title: 'Rapid Review Briefing v1',
  generated_at: '2026-01-01T00:00:00Z',
  pdf_available: true,
  html_available: false,
  summary: 'This is a summary of the evidence.',
  findings: { '0': 'Finding for RQ0', '1': 'Finding for RQ1' },
  target_audience: 'Healthcare practitioners',
  reference_complementary: 'See companion full systematic review.',
  institution_logos: [],
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('BriefingPreview', () => {
  it('renders the briefing title', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} />);
    expect(screen.getByText('Rapid Review Briefing v1')).toBeTruthy();
  });

  it('renders the Summary section when summary is provided', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} />);
    expect(screen.getByText('Summary')).toBeTruthy();
    expect(screen.getByText('This is a summary of the evidence.')).toBeTruthy();
  });

  it('does not render Summary section when summary is null', () => {
    const briefing: BriefingDetail = { ...BASE_BRIEFING, summary: null };
    render(<BriefingPreview briefing={briefing} />);
    expect(screen.queryByText('Summary')).toBeNull();
  });

  it('renders Findings section with per-RQ entries', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} />);
    expect(screen.getByText('Findings')).toBeTruthy();
    expect(screen.getByText('Finding for RQ0')).toBeTruthy();
    expect(screen.getByText('Finding for RQ1')).toBeTruthy();
  });

  it('renders RQ labels for each finding', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} />);
    expect(screen.getByText('RQ 0')).toBeTruthy();
    expect(screen.getByText('RQ 1')).toBeTruthy();
  });

  it('does not render Findings section when findings is empty', () => {
    const briefing: BriefingDetail = { ...BASE_BRIEFING, findings: {} };
    render(<BriefingPreview briefing={briefing} />);
    expect(screen.queryByText('Findings')).toBeNull();
  });

  it('renders Target Audience section when provided', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} />);
    expect(screen.getByText('Target Audience')).toBeTruthy();
    expect(screen.getByText('Healthcare practitioners')).toBeTruthy();
  });

  it('does not render Target Audience when null', () => {
    const briefing: BriefingDetail = { ...BASE_BRIEFING, target_audience: null };
    render(<BriefingPreview briefing={briefing} />);
    expect(screen.queryByText('Target Audience')).toBeNull();
  });

  it('renders threats chips inside Target Audience when threats provided', () => {
    const threats = [
      { threat_type: 'Selection', description: 'Publication bias', source_detail: null },
    ];
    render(<BriefingPreview briefing={BASE_BRIEFING} threats={threats} />);
    expect(screen.getByText('Threats to Validity')).toBeTruthy();
    expect(screen.getByText('Selection: Publication bias')).toBeTruthy();
  });

  it('does not render Threats to Validity section when threats prop is omitted', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} />);
    expect(screen.queryByText('Threats to Validity')).toBeNull();
  });

  it('does not render Threats to Validity section when threats array is empty', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} threats={[]} />);
    expect(screen.queryByText('Threats to Validity')).toBeNull();
  });

  it('renders Reference to Complementary Material when provided', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} />);
    expect(screen.getByText('Reference to Complementary Material')).toBeTruthy();
    expect(screen.getByText('See companion full systematic review.')).toBeTruthy();
  });

  it('does not render Reference to Complementary Material when null', () => {
    const briefing: BriefingDetail = { ...BASE_BRIEFING, reference_complementary: null };
    render(<BriefingPreview briefing={briefing} />);
    expect(screen.queryByText('Reference to Complementary Material')).toBeNull();
  });

  it('renders Institution Logos section when logos are present', () => {
    const briefing: BriefingDetail = { ...BASE_BRIEFING, institution_logos: ['/logos/univ.png'] };
    render(<BriefingPreview briefing={briefing} />);
    expect(screen.getByText('Institution Logos')).toBeTruthy();
    expect(screen.getByText('/logos/univ.png')).toBeTruthy();
  });

  it('does not render Institution Logos section when logos array is empty', () => {
    render(<BriefingPreview briefing={BASE_BRIEFING} />);
    expect(screen.queryByText('Institution Logos')).toBeNull();
  });

  it('renders multiple threats as separate chips', () => {
    const threats = [
      { threat_type: 'Internal', description: 'Confounding', source_detail: null },
      { threat_type: 'External', description: 'Generalisability', source_detail: 'Study A' },
    ];
    render(<BriefingPreview briefing={BASE_BRIEFING} threats={threats} />);
    expect(screen.getByText('Internal: Confounding')).toBeTruthy();
    expect(screen.getByText('External: Generalisability')).toBeTruthy();
  });
});
