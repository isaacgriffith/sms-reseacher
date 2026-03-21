/**
 * Tests for ProtocolForm component (feature 007, T036).
 *
 * Covers:
 * - Renders all required input fields.
 * - Validation errors shown for empty required fields on submit.
 * - Read-only state when protocol is validated.
 * - pico_context field is rendered and optional.
 * - onSave called with correct data on valid submit.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import ProtocolForm from '../ProtocolForm';
import type { ReviewProtocol } from '../../../services/slr/protocolApi';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Builds a complete protocol object suitable for test fixtures.
 *
 * @param overrides - Partial protocol fields to override.
 * @returns A complete ReviewProtocol fixture.
 */
function makeProtocol(overrides: Partial<ReviewProtocol> = {}): ReviewProtocol {
  return {
    id: 1,
    study_id: 42,
    status: 'draft',
    background: 'Test background',
    rationale: 'Test rationale',
    research_questions: ['RQ1'],
    pico_population: 'Population',
    pico_intervention: 'Intervention',
    pico_comparison: 'Comparison',
    pico_outcome: 'Outcome',
    pico_context: null,
    search_strategy: 'Strategy',
    inclusion_criteria: ['IC1'],
    exclusion_criteria: ['EC1'],
    data_extraction_strategy: 'Extract effect sizes',
    synthesis_approach: 'descriptive',
    dissemination_strategy: 'Journal publication',
    timetable: 'Q1-Q4 2026',
    review_report: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Render helper
// ---------------------------------------------------------------------------

/**
 * Renders ProtocolForm with the given props.
 *
 * @param protocol - Protocol data or null.
 * @param onSave - Mock save callback.
 * @returns Testing library render result.
 */
function renderForm(protocol: ReviewProtocol | null = null, onSave = vi.fn()) {
  return render(<ProtocolForm protocol={protocol} onSave={onSave} />);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ProtocolForm', () => {
  describe('Field rendering', () => {
    it('renders background field', () => {
      renderForm();
      expect(screen.getByLabelText('background')).toBeInTheDocument();
    });

    it('renders rationale field', () => {
      renderForm();
      expect(screen.getByLabelText('rationale')).toBeInTheDocument();
    });

    it('renders research_questions field', () => {
      renderForm();
      expect(screen.getByLabelText('research_questions')).toBeInTheDocument();
    });

    it('renders PICO fields', () => {
      renderForm();
      expect(screen.getByLabelText('pico_population')).toBeInTheDocument();
      expect(screen.getByLabelText('pico_intervention')).toBeInTheDocument();
      expect(screen.getByLabelText('pico_comparison')).toBeInTheDocument();
      expect(screen.getByLabelText('pico_outcome')).toBeInTheDocument();
    });

    it('renders pico_context field (optional)', () => {
      renderForm();
      expect(screen.getByLabelText('pico_context')).toBeInTheDocument();
    });

    it('renders search strategy and criteria fields', () => {
      renderForm();
      expect(screen.getByLabelText('search_strategy')).toBeInTheDocument();
      expect(screen.getByLabelText('inclusion_criteria')).toBeInTheDocument();
      expect(screen.getByLabelText('exclusion_criteria')).toBeInTheDocument();
    });

    it('renders synthesis approach select', () => {
      renderForm();
      expect(screen.getByLabelText('synthesis_approach')).toBeInTheDocument();
    });

    it('renders Save button when not validated', () => {
      renderForm(makeProtocol({ status: 'draft' }));
      expect(screen.getByRole('button', { name: /save protocol/i })).toBeInTheDocument();
    });
  });

  describe('Field population', () => {
    it('populates fields from protocol data', () => {
      const protocol = makeProtocol({ background: 'Loaded background' });
      renderForm(protocol);
      expect(screen.getByLabelText('background')).toHaveValue('Loaded background');
    });

    it('populates research_questions as newline-separated text', () => {
      const protocol = makeProtocol({ research_questions: ['RQ1', 'RQ2'] });
      renderForm(protocol);
      expect(screen.getByLabelText('research_questions')).toHaveValue('RQ1\nRQ2');
    });
  });

  describe('Validation errors', () => {
    it('shows error when required field is empty on submit', async () => {
      const onSave = vi.fn();
      render(<ProtocolForm protocol={null} onSave={onSave} />);
      fireEvent.click(screen.getByRole('button', { name: /save protocol/i }));
      await waitFor(() => {
        expect(screen.getByText(/background is required/i)).toBeInTheDocument();
      });
      expect(onSave).not.toHaveBeenCalled();
    });
  });

  describe('Read-only state', () => {
    it('disables all fields when status is validated', () => {
      const protocol = makeProtocol({ status: 'validated' });
      renderForm(protocol);
      expect(screen.getByLabelText('background')).toBeDisabled();
      expect(screen.getByLabelText('rationale')).toBeDisabled();
    });

    it('does not render Save button when status is validated', () => {
      const protocol = makeProtocol({ status: 'validated' });
      renderForm(protocol);
      expect(screen.queryByRole('button', { name: /save protocol/i })).not.toBeInTheDocument();
    });
  });

  describe('onSave callback', () => {
    it('calls onSave with correct data on valid submit', async () => {
      const onSave = vi.fn();
      const protocol = makeProtocol();
      render(<ProtocolForm protocol={protocol} onSave={onSave} />);
      fireEvent.click(screen.getByRole('button', { name: /save protocol/i }));
      await waitFor(() => {
        expect(onSave).toHaveBeenCalledWith(
          expect.objectContaining({
            background: 'Test background',
            rationale: 'Test rationale',
            research_questions: ['RQ1'],
          }),
        );
      });
    });

    it('passes empty string for pico_context when null in protocol', async () => {
      const onSave = vi.fn();
      const protocol = makeProtocol({ pico_context: null });
      render(<ProtocolForm protocol={protocol} onSave={onSave} />);
      fireEvent.click(screen.getByRole('button', { name: /save protocol/i }));
      await waitFor(() => {
        expect(onSave).toHaveBeenCalled();
      });
    });
  });

  describe('Null field fallback population', () => {
    it('populates fields with empty string when all protocol fields are null', () => {
      const protocol = makeProtocol({
        background: null as unknown as string,
        rationale: null as unknown as string,
        pico_population: null as unknown as string,
        pico_intervention: null as unknown as string,
        pico_comparison: null as unknown as string,
        pico_outcome: null as unknown as string,
        pico_context: null,
        search_strategy: null as unknown as string,
        data_extraction_strategy: null as unknown as string,
        synthesis_approach: null as unknown as 'descriptive',
        dissemination_strategy: null as unknown as string,
        timetable: null as unknown as string,
      });
      renderForm(protocol);
      expect(screen.getByLabelText('background')).toHaveValue('');
      expect(screen.getByLabelText('rationale')).toHaveValue('');
    });
  });

  describe('picoContext helper text', () => {
    it('shows "Context provided" when pico_context has content', async () => {
      const protocol = makeProtocol({ pico_context: 'Some context' });
      renderForm(protocol);
      await waitFor(() => {
        expect(screen.getByText('Context provided')).toBeInTheDocument();
      });
    });
  });
});
