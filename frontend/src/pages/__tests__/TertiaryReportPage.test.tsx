/**
 * Unit tests for TertiaryReportPage (feature 009).
 *
 * Covers:
 * - Loading state renders spinner.
 * - Error state renders error alert.
 * - Loaded state renders study name, section headings, and download buttons.
 * - Research questions list renders items.
 * - Download buttons trigger window.open.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TertiaryReportPage from '../TertiaryReportPage';

vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

import { api } from '../../services/api';

const mockApi = vi.mocked(api);

const REPORT_FIXTURE = {
  study_id: 1,
  study_name: 'Test Tertiary Study',
  generated_at: '2026-01-01T00:00:00Z',
  background: 'Background text.',
  review_questions: ['RQ1: What are the trends?', 'RQ2: What are the gaps?'],
  protocol_summary: 'Protocol summary text.',
  inclusion_exclusion_decisions: 'Inclusion criteria text.',
  quality_assessment_results: 'QA results text.',
  extracted_data: 'Extracted data text.',
  synthesis_results: 'Synthesis results text.',
  landscape_of_secondary_studies: {
    timeline_summary: 'Timeline: 2010–2023.',
    research_question_evolution: 'RQ evolution text.',
    synthesis_method_shifts: 'Synthesis method text.',
  },
  recommendations: 'Recommendations text.',
};

function makeWrapper(retry = false) {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry } },
  });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe('TertiaryReportPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading spinner initially', () => {
    mockApi.get.mockReturnValue(new Promise(() => {}));
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error alert on fetch failure', async () => {
    mockApi.get.mockRejectedValue(new Error('Network error'));
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    const alert = await screen.findByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert.textContent).toMatch(/Failed to load report/i);
  });

  it('renders study name after load', async () => {
    mockApi.get.mockResolvedValue(REPORT_FIXTURE);
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    expect(await screen.findByText('Test Tertiary Study')).toBeInTheDocument();
  });

  it('renders Background section', async () => {
    mockApi.get.mockResolvedValue(REPORT_FIXTURE);
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    await screen.findByText('Test Tertiary Study');
    expect(screen.getByText('Background text.')).toBeInTheDocument();
  });

  it('renders Research Questions section with items', async () => {
    mockApi.get.mockResolvedValue(REPORT_FIXTURE);
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    await screen.findByText('Test Tertiary Study');
    expect(screen.getByText('RQ1: What are the trends?')).toBeInTheDocument();
    expect(screen.getByText('RQ2: What are the gaps?')).toBeInTheDocument();
  });

  it('renders (none recorded) when review_questions is empty', async () => {
    mockApi.get.mockResolvedValue({ ...REPORT_FIXTURE, review_questions: [] });
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    await screen.findByText('Test Tertiary Study');
    expect(screen.getByText('(none recorded)')).toBeInTheDocument();
  });

  it('renders JSON, CSV, and Markdown download buttons', async () => {
    mockApi.get.mockResolvedValue(REPORT_FIXTURE);
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    await screen.findByText('Test Tertiary Study');
    expect(screen.getByRole('button', { name: /JSON/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /CSV/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Markdown/i })).toBeInTheDocument();
  });

  it('calls window.open on JSON download click', async () => {
    mockApi.get.mockResolvedValue(REPORT_FIXTURE);
    const openSpy = vi.spyOn(window, 'open').mockImplementation(() => null);
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    await screen.findByText('Test Tertiary Study');
    fireEvent.click(screen.getByRole('button', { name: /JSON/i }));
    expect(openSpy).toHaveBeenCalledWith(
      expect.stringContaining('format=json'),
      '_blank',
      'noopener,noreferrer',
    );
    openSpy.mockRestore();
  });

  it('renders Landscape of Secondary Studies section', async () => {
    mockApi.get.mockResolvedValue(REPORT_FIXTURE);
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    await screen.findByText('Test Tertiary Study');
    expect(screen.getByText(/Landscape of Secondary Studies/i)).toBeInTheDocument();
  });

  it('renders Recommendations section', async () => {
    mockApi.get.mockResolvedValue(REPORT_FIXTURE);
    render(<TertiaryReportPage studyId={1} />, { wrapper: makeWrapper() });
    await screen.findByText('Test Tertiary Study');
    expect(screen.getByText('Recommendations text.')).toBeInTheDocument();
  });
});
