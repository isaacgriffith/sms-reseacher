/**
 * Unit tests for TertiaryQAGuidancePanel component (feature 009).
 *
 * Covers:
 * - Renders the info banner heading.
 * - Renders all six QA dimension accordion labels.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect } from 'vitest';
import TertiaryQAGuidancePanel from '../TertiaryQAGuidancePanel';

describe('TertiaryQAGuidancePanel', () => {
  it('renders the secondary-study QA heading', () => {
    render(<TertiaryQAGuidancePanel />);
    expect(screen.getByText(/Secondary-Study Quality Assessment/i)).toBeInTheDocument();
  });

  it('renders the guidance description text', () => {
    render(<TertiaryQAGuidancePanel />);
    expect(screen.getByText(/six mandatory dimensions/i)).toBeInTheDocument();
  });

  it('renders Protocol Documentation Completeness dimension', () => {
    render(<TertiaryQAGuidancePanel />);
    expect(screen.getByText(/Protocol Documentation Completeness/i)).toBeInTheDocument();
  });

  it('renders Search Strategy Adequacy dimension', () => {
    render(<TertiaryQAGuidancePanel />);
    expect(screen.getByText(/Search Strategy Adequacy/i)).toBeInTheDocument();
  });

  it('renders Inclusion / Exclusion Criteria Clarity dimension', () => {
    render(<TertiaryQAGuidancePanel />);
    expect(screen.getByText(/Inclusion \/ Exclusion Criteria Clarity/i)).toBeInTheDocument();
  });

  it('renders Quality Assessment Approach dimension', () => {
    render(<TertiaryQAGuidancePanel />);
    expect(screen.getByText(/Quality Assessment Approach/i)).toBeInTheDocument();
  });

  it('renders Synthesis Method Appropriateness dimension', () => {
    render(<TertiaryQAGuidancePanel />);
    expect(screen.getByText(/Synthesis Method Appropriateness/i)).toBeInTheDocument();
  });

  it('renders Validity Threats Discussion dimension', () => {
    render(<TertiaryQAGuidancePanel />);
    expect(screen.getByText(/Validity Threats Discussion/i)).toBeInTheDocument();
  });

  it('renders six accordion items', () => {
    render(<TertiaryQAGuidancePanel />);
    const items = screen.getAllByRole('button');
    expect(items.length).toBeGreaterThanOrEqual(6);
  });
});
