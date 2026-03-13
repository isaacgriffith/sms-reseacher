/**
 * Tests for PICOForm component.
 * Verifies variant selector rendering, form field visibility, and API call shapes.
 */
// @ts-nocheck


import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    put: vi.fn(),
    post: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

import { api } from '../../../services/api';
import PICOForm from '../PICOForm';

const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  put: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
};

const MOCK_PICO = {
  id: 1,
  study_id: 1,
  variant: 'PICO',
  population: 'Software engineers',
  intervention: 'TDD',
  comparison: 'No TDD',
  outcome: 'Code quality',
  context: null,
  extra_fields: null,
  ai_suggestions: null,
  updated_at: '2026-01-01T00:00:00Z',
};

describe('PICOForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Loading state', () => {
    it('fetches PICO data on mount', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_PICO);
      render(<PICOForm studyId={1} />);
      await waitFor(() => {
        expect(mockApi.get).toHaveBeenCalledWith('/api/v1/studies/1/pico');
      });
    });

    it('renders form fields after data loads', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_PICO);
      render(<PICOForm studyId={1} />);
      await waitFor(() => {
        expect(screen.getByDisplayValue('Software engineers')).toBeTruthy();
      });
    });
  });

  describe('Variant selector', () => {
    it('renders variant selector with all options', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_PICO);
      const { container } = render(<PICOForm studyId={1} />);
      await waitFor(() => screen.getByDisplayValue('Software engineers'));

      // Variant selector uses visually-hidden radio inputs inside styled labels
      const variantRadios = container.querySelectorAll('input[type="radio"]') as NodeListOf<HTMLInputElement>;
      expect(variantRadios.length).toBeGreaterThan(0);
      // PICO is the default variant
      const picoRadio = Array.from(variantRadios).find((r) => r.value === 'PICO');
      expect(picoRadio).toBeTruthy();
    });
  });

  describe('Save action', () => {
    it('calls PUT /pico with form data on save', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_PICO);
      mockApi.put.mockResolvedValueOnce({ ...MOCK_PICO, population: 'Devs' });
      render(<PICOForm studyId={1} />);

      await waitFor(() => screen.getByDisplayValue('Software engineers'));

      // Update population
      const populationField = screen.getByDisplayValue('Software engineers');
      fireEvent.change(populationField, { target: { value: 'Devs' } });

      // After loading existing PICO, button shows "Update PICO/C"
      const saveButton = screen.getByRole('button', { name: /pico/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockApi.put).toHaveBeenCalledWith(
          '/api/v1/studies/1/pico',
          expect.objectContaining({ population: 'Devs' }),
        );
      });
    });
  });

  describe('Refine with AI', () => {
    it('renders Refine with AI button', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_PICO);
      render(<PICOForm studyId={1} />);
      await waitFor(() => screen.getByDisplayValue('Software engineers'));
      const refineButtons = screen.getAllByRole('button', { name: /refine/i });
      expect(refineButtons.length).toBeGreaterThan(0);
    });
  });
});
