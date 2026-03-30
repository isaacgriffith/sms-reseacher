/**
 * Unit tests for ThreatToValidityList component (feature 008).
 *
 * Covers empty state, rendering of threat chips and descriptions,
 * known label lookup, and source detail display.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ThreatToValidityList from '../ThreatToValidityList';
import type { Threat } from '../../../services/rapid/protocolApi';

// ---------------------------------------------------------------------------
// Fixture
// ---------------------------------------------------------------------------

function makeThreat(overrides: Partial<Threat>): Threat {
  return {
    id: 1,
    study_id: 42,
    threat_type: 'single_source',
    description: 'Only one database was searched.',
    source_detail: null,
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ThreatToValidityList', () => {
  it('renders empty message when threats array is empty', () => {
    render(<ThreatToValidityList threats={[]} />);
    expect(screen.getByText('No threats recorded yet.')).toBeTruthy();
  });

  it('renders a chip with the known label for single_source', () => {
    render(<ThreatToValidityList threats={[makeThreat({ threat_type: 'single_source' })]} />);
    expect(screen.getByText('Single Source')).toBeTruthy();
  });

  it('renders a chip with the known label for year_range', () => {
    render(<ThreatToValidityList threats={[makeThreat({ threat_type: 'year_range', id: 2 })]} />);
    expect(screen.getByText('Year Range')).toBeTruthy();
  });

  it('renders a chip with the known label for language', () => {
    render(<ThreatToValidityList threats={[makeThreat({ threat_type: 'language', id: 3 })]} />);
    expect(screen.getByText('Language')).toBeTruthy();
  });

  it('renders a chip with the known label for single_reviewer', () => {
    render(<ThreatToValidityList threats={[makeThreat({ threat_type: 'single_reviewer', id: 4 })]} />);
    expect(screen.getByText('Single Reviewer')).toBeTruthy();
  });

  it('falls back to raw threat_type when not in label map', () => {
    render(<ThreatToValidityList threats={[makeThreat({ threat_type: 'custom_unknown', id: 5 })]} />);
    expect(screen.getByText('custom_unknown')).toBeTruthy();
  });

  it('renders the threat description text', () => {
    const threat = makeThreat({ description: 'Only one database searched.' });
    render(<ThreatToValidityList threats={[threat]} />);
    expect(screen.getByText('Only one database searched.')).toBeTruthy();
  });

  it('renders source_detail when provided', () => {
    const threat = makeThreat({ source_detail: 'IEEE Xplore only' });
    render(<ThreatToValidityList threats={[threat]} />);
    expect(screen.getByText('IEEE Xplore only')).toBeTruthy();
  });

  it('does not render source_detail element when null', () => {
    const threat = makeThreat({ source_detail: null });
    render(<ThreatToValidityList threats={[threat]} />);
    expect(screen.queryByText('null')).toBeNull();
  });

  it('renders multiple threats', () => {
    const threats = [
      makeThreat({ id: 1, threat_type: 'single_source', description: 'Desc A' }),
      makeThreat({ id: 2, threat_type: 'language', description: 'Desc B' }),
    ];
    render(<ThreatToValidityList threats={threats} />);
    expect(screen.getByText('Desc A')).toBeTruthy();
    expect(screen.getByText('Desc B')).toBeTruthy();
    expect(screen.getByText('Single Source')).toBeTruthy();
    expect(screen.getByText('Language')).toBeTruthy();
  });

  it('renders known label for qa_skipped', () => {
    render(<ThreatToValidityList threats={[makeThreat({ threat_type: 'qa_skipped', id: 6 })]} />);
    expect(screen.getByText('QA Skipped')).toBeTruthy();
  });

  it('renders known label for context_restriction', () => {
    render(<ThreatToValidityList threats={[makeThreat({ threat_type: 'context_restriction', id: 7 })]} />);
    expect(screen.getByText('Context Restriction')).toBeTruthy();
  });
});
