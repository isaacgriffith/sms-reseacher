/**
 * Unit tests for TertiaryProtocolForm component (feature 009, T045).
 *
 * Covers:
 * - Renders key input fields.
 * - Shows read-only alert when protocol status is "validated".
 * - Save button is absent in read-only mode.
 * - onSave is called with mapped data on valid submit.
 * - Validation error shown when research_questions is empty.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi } from 'vitest';
import TertiaryProtocolForm from '../TertiaryProtocolForm';
import type { TertiaryProtocol } from '../../../services/tertiary/protocolApi';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Build a complete TertiaryProtocol fixture.
 *
 * @param overrides - Partial fields to override.
 * @returns A complete {@link TertiaryProtocol} fixture.
 */
function makeProtocol(overrides: Partial<TertiaryProtocol> = {}): TertiaryProtocol {
  return {
    id: 1,
    study_id: 42,
    status: 'draft',
    background: 'Background text',
    research_questions: ['RQ1: What is the landscape of secondary studies on TDD?'],
    secondary_study_types: ['SLR', 'SMS'],
    inclusion_criteria: ['Must be a secondary study'],
    exclusion_criteria: ['Primary studies'],
    recency_cutoff_year: 2015,
    search_strategy: 'Search strategy text',
    quality_threshold: 0.6,
    synthesis_approach: 'narrative',
    dissemination_strategy: 'Journal publication',
    version_id: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

/**
 * Render TertiaryProtocolForm with standard props.
 *
 * @param protocol - Protocol data or null.
 * @param onSave - Mock save callback.
 * @returns Testing library render result.
 */
function renderForm(protocol: TertiaryProtocol | null = null, onSave = vi.fn()) {
  return render(<TertiaryProtocolForm protocol={protocol} onSave={onSave} />);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('TertiaryProtocolForm', () => {
  describe('Field rendering', () => {
    it('renders the background field', () => {
      renderForm();
      expect(screen.getByLabelText('background')).toBeInTheDocument();
    });

    it('renders the research_questions field', () => {
      renderForm();
      expect(screen.getByLabelText('research_questions')).toBeInTheDocument();
    });

    it('renders the search_strategy field', () => {
      renderForm();
      expect(screen.getByLabelText('search_strategy')).toBeInTheDocument();
    });

    it('renders the recency_cutoff_year field', () => {
      renderForm();
      expect(screen.getByLabelText('recency_cutoff_year')).toBeInTheDocument();
    });

    it('renders the inclusion_criteria field', () => {
      renderForm();
      expect(screen.getByLabelText('inclusion_criteria')).toBeInTheDocument();
    });

    it('renders the exclusion_criteria field', () => {
      renderForm();
      expect(screen.getByLabelText('exclusion_criteria')).toBeInTheDocument();
    });

    it('renders the quality_threshold slider', () => {
      renderForm();
      expect(screen.getByLabelText('quality_threshold')).toBeInTheDocument();
    });

    it('renders the Save Protocol button in draft mode', () => {
      renderForm();
      expect(screen.getByRole('button', { name: /save protocol/i })).toBeInTheDocument();
    });
  });

  describe('Read-only mode when validated', () => {
    it('shows a validated alert when status is "validated"', () => {
      renderForm(makeProtocol({ status: 'validated' }));
      expect(screen.getByText(/protocol validated/i)).toBeInTheDocument();
    });

    it('does not render Save Protocol button when validated', () => {
      renderForm(makeProtocol({ status: 'validated' }));
      expect(screen.queryByRole('button', { name: /save protocol/i })).toBeNull();
    });

    it('background field is disabled when validated', () => {
      renderForm(makeProtocol({ status: 'validated' }));
      const field = screen.getByLabelText('background');
      expect(field).toBeDisabled();
    });
  });

  describe('Initial values', () => {
    it('populates background from protocol prop', () => {
      renderForm(makeProtocol({ background: 'Initial background' }));
      const field = screen.getByLabelText('background') as HTMLTextAreaElement;
      expect(field.value).toBe('Initial background');
    });

    it('populates research_questions from protocol prop (joined by newline)', () => {
      renderForm(makeProtocol({ research_questions: ['RQ1', 'RQ2'] }));
      const field = screen.getByLabelText('research_questions') as HTMLTextAreaElement;
      expect(field.value).toContain('RQ1');
      expect(field.value).toContain('RQ2');
    });
  });

  describe('Validation errors', () => {
    it('shows error when research_questions is empty on submit', async () => {
      renderForm();
      // Clear the research_questions field.
      const rqField = screen.getByLabelText('research_questions');
      fireEvent.change(rqField, { target: { value: '' } });
      fireEvent.click(screen.getByRole('button', { name: /save protocol/i }));
      await waitFor(() => {
        expect(screen.getByText(/at least one research question/i)).toBeInTheDocument();
      });
    });

    it('unchecking a checkbox triggers the filter branch and shows error on submit', async () => {
      // Render with 'SLR' only so unchecking it leaves secondary_study_types empty.
      renderForm(makeProtocol({ secondary_study_types: ['SLR'] }));
      const slrCheckbox = screen.getByLabelText('SLR') as HTMLInputElement;
      expect(slrCheckbox.checked).toBe(true);
      // Uncheck SLR (filter branch) and also uncheck SMS if pre-checked.
      fireEvent.click(slrCheckbox);
      // Submit to trigger the secondary_study_types error display.
      fireEvent.click(screen.getByRole('button', { name: /save protocol/i }));
      await waitFor(() => {
        expect(
          screen.queryByText(/Select at least one secondary study type/i) ||
          screen.queryByText(/Select at least one type/i)
        ).not.toBeNull();
      });
    });

    it('checking an unchecked checkbox triggers the spread branch', () => {
      // Render with only SLR checked so RAPID_REVIEW is unchecked.
      renderForm(makeProtocol({ secondary_study_types: ['SLR'] }));
      const rapidCheckbox = screen.getByLabelText('RAPID REVIEW') as HTMLInputElement;
      expect(rapidCheckbox.checked).toBe(false);
      // Check it — this exercises the `[...field.value, opt]` branch (line 310).
      fireEvent.click(rapidCheckbox);
      expect(rapidCheckbox.checked).toBe(true);
    });
  });

  describe('onSave callback', () => {
    it('calls onSave with correct data on valid submit', async () => {
      const onSave = vi.fn();
      renderForm(makeProtocol(), onSave);

      // Ensure the RQ field has a value.
      const rqField = screen.getByLabelText('research_questions');
      fireEvent.change(rqField, { target: { value: 'RQ1: My question' } });
      fireEvent.click(screen.getByRole('button', { name: /save protocol/i }));

      await waitFor(() => {
        expect(onSave).toHaveBeenCalledTimes(1);
      });

      const payload = onSave.mock.calls[0][0];
      expect(Array.isArray(payload.research_questions)).toBe(true);
      expect(payload.research_questions).toContain('RQ1: My question');
    });
  });
});
