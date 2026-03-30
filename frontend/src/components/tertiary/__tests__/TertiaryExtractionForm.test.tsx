/**
 * Unit tests for TertiaryExtractionForm component (feature 009, T045).
 *
 * Covers:
 * - Renders key extraction fields.
 * - Shows AI pre-fill banner when extraction_status is "ai_complete".
 * - No AI banner for "pending" status.
 * - Calls onSave with extraction_status set to "human_reviewed" on submit.
 * - Populates initial values from the extraction prop.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi } from 'vitest';
import TertiaryExtractionForm from '../TertiaryExtractionForm';
import type { TertiaryExtraction } from '../../../services/tertiary/extractionApi';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Build a TertiaryExtraction fixture.
 *
 * @param overrides - Partial fields to override.
 * @returns A complete {@link TertiaryExtraction} fixture.
 */
function makeExtraction(overrides: Partial<TertiaryExtraction> = {}): TertiaryExtraction {
  return {
    id: 1,
    candidate_paper_id: 42,
    paper_title: 'A Mapping Study on TDD',
    secondary_study_type: 'SLR',
    research_questions_addressed: ['RQ1: Effect of TDD'],
    databases_searched: ['ACM DL', 'IEEE Xplore'],
    study_period_start: 2010,
    study_period_end: 2020,
    primary_study_count: 25,
    synthesis_approach_used: 'narrative',
    key_findings: 'TDD improves code quality.',
    research_gaps: 'Long-term effects unclear.',
    reviewer_quality_rating: 0.75,
    extraction_status: 'pending',
    extracted_by_agent: null,
    validated_by_reviewer_id: null,
    version_id: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

/**
 * Render TertiaryExtractionForm with standard props.
 *
 * @param extraction - Extraction record to pass.
 * @param onSave - Mock save callback.
 * @returns Testing library render result.
 */
function renderForm(extraction: TertiaryExtraction = makeExtraction(), onSave = vi.fn()) {
  return render(
    <TertiaryExtractionForm extraction={extraction} isSaving={false} onSave={onSave} />,
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('TertiaryExtractionForm', () => {
  describe('Field rendering', () => {
    it('renders the key_findings field', () => {
      renderForm();
      expect(screen.getByLabelText('Key Findings')).toBeInTheDocument();
    });

    it('renders the research_gaps field', () => {
      renderForm();
      expect(screen.getByLabelText('Research Gaps')).toBeInTheDocument();
    });

    it('renders the synthesis_approach_used field', () => {
      renderForm();
      expect(screen.getByLabelText('Synthesis Approach Used')).toBeInTheDocument();
    });

    it('renders the Save Extraction button', () => {
      renderForm();
      expect(screen.getByRole('button', { name: /save extraction/i })).toBeInTheDocument();
    });
  });

  describe('AI pre-fill banner', () => {
    it('shows AI pre-filled banner when status is "ai_complete"', () => {
      renderForm(makeExtraction({ extraction_status: 'ai_complete' }));
      expect(screen.getByText(/ai pre-filled/i)).toBeInTheDocument();
    });

    it('does not show AI banner when status is "pending"', () => {
      renderForm(makeExtraction({ extraction_status: 'pending' }));
      expect(screen.queryByText(/ai pre-filled/i)).toBeNull();
    });

    it('does not show AI banner when status is "human_reviewed"', () => {
      renderForm(makeExtraction({ extraction_status: 'human_reviewed' }));
      expect(screen.queryByText(/ai pre-filled/i)).toBeNull();
    });
  });

  describe('Initial values', () => {
    it('populates key_findings from extraction prop', () => {
      renderForm(makeExtraction({ key_findings: 'TDD improves quality significantly.' }));
      const field = screen.getByLabelText('Key Findings') as HTMLTextAreaElement;
      expect(field.value).toContain('TDD improves quality');
    });

    it('populates research_gaps from extraction prop', () => {
      renderForm(makeExtraction({ research_gaps: 'Long-term data missing.' }));
      const field = screen.getByLabelText('Research Gaps') as HTMLTextAreaElement;
      expect(field.value).toContain('Long-term data missing');
    });
  });

  describe('Null value rendering', () => {
    it('renders without crashing when numeric fields are null', () => {
      renderForm(makeExtraction({
        study_period_start: null,
        study_period_end: null,
        primary_study_count: null,
      }));
      expect(screen.getByLabelText('Key Findings')).toBeInTheDocument();
    });

    it('shows quality rating numeric value when reviewer_quality_rating is provided', () => {
      renderForm(makeExtraction({ reviewer_quality_rating: 0.80 }));
      expect(screen.getByText(/Reviewer Quality Rating/)).toHaveTextContent('0.80');
    });

    it('defaults reviewer_quality_rating to 0.50 when null is passed', () => {
      renderForm(makeExtraction({ reviewer_quality_rating: null }));
      // The form default sets it to 0.5 when null, so the watch returns 0.5.
      expect(screen.getByText(/Reviewer Quality Rating/)).toHaveTextContent('0.50');
    });

    it('renders without crashing when text fields are null', () => {
      renderForm(makeExtraction({
        synthesis_approach_used: null,
        key_findings: null,
        research_gaps: null,
      }));
      expect(screen.getByLabelText('Key Findings')).toBeInTheDocument();
    });
  });

  describe('onSave callback', () => {
    it('calls onSave with extraction_status set to "human_reviewed" on submit', async () => {
      const onSave = vi.fn();
      renderForm(makeExtraction(), onSave);

      fireEvent.click(screen.getByRole('button', { name: /save extraction/i }));

      await waitFor(() => {
        expect(onSave).toHaveBeenCalledTimes(1);
      });

      const payload = onSave.mock.calls[0][0];
      expect(payload.extraction_status).toBe('human_reviewed');
    });

    it('converts empty optional fields to null on submit', async () => {
      const onSave = vi.fn();
      renderForm(makeExtraction({ research_gaps: '', synthesis_approach_used: '' }), onSave);

      // Clear key_findings to test another || null branch.
      const keyFindingsField = screen.getByLabelText('Key Findings') as HTMLTextAreaElement;
      fireEvent.change(keyFindingsField, { target: { value: '' } });

      fireEvent.click(screen.getByRole('button', { name: /save extraction/i }));

      await waitFor(() => {
        expect(onSave).toHaveBeenCalledTimes(1);
      });

      const payload = onSave.mock.calls[0][0];
      expect(payload.research_gaps).toBeNull();
    });

    it('converts empty secondary_study_type to null on submit', async () => {
      const onSave = vi.fn();
      renderForm(makeExtraction({ secondary_study_type: '' }), onSave);
      fireEvent.click(screen.getByRole('button', { name: /save extraction/i }));
      await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1));
      expect(onSave.mock.calls[0][0].secondary_study_type).toBeNull();
    });
  });

  describe('isSaving state', () => {
    it('shows "Saving…" text when isSaving is true', () => {
      render(
        <TertiaryExtractionForm extraction={makeExtraction()} isSaving={true} onSave={vi.fn()} />,
      );
      expect(screen.getByRole('button', { name: /saving…/i })).toBeInTheDocument();
    });
  });
});
