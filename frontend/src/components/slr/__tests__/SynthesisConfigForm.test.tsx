/**
 * Tests for SynthesisConfigForm component (feature 007, T080).
 *
 * Covers:
 * - Renders with approach radio buttons.
 * - Selecting meta_analysis shows model_type field.
 * - Selecting qualitative hides meta-analysis fields.
 * - Submit calls onSubmit with correct data.
 * - Validation error shown when approach is not selected and form is submitted.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SynthesisConfigForm from '../SynthesisConfigForm';

function renderForm(onSubmit = vi.fn()) {
  const qc = new QueryClient();
  render(
    <QueryClientProvider client={qc}>
      <SynthesisConfigForm studyId={1} onSubmit={onSubmit} />
    </QueryClientProvider>,
  );
  return { onSubmit };
}

describe('SynthesisConfigForm', () => {
  describe('Rendering', () => {
    it('renders all three approach radio buttons', () => {
      renderForm();
      expect(screen.getByLabelText(/meta-analysis/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/descriptive/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/qualitative/i)).toBeInTheDocument();
    });

    it('renders Run Synthesis button', () => {
      renderForm();
      expect(screen.getByTestId('synthesis-submit')).toBeInTheDocument();
    });
  });

  describe('Conditional fields', () => {
    it('shows model_type select after selecting meta_analysis', async () => {
      renderForm();
      await userEvent.click(screen.getByLabelText(/meta-analysis/i));
      await waitFor(() => {
        expect(screen.getByLabelText(/model type/i, { selector: '[role="combobox"]' })).toBeInTheDocument();
      });
    });

    it('hides model_type select after switching to qualitative', async () => {
      renderForm();
      await userEvent.click(screen.getByLabelText(/meta-analysis/i));
      await userEvent.click(screen.getByLabelText(/qualitative/i));
      await waitFor(() => {
        expect(screen.queryByLabelText(/model type/i, { selector: '[role="combobox"]' })).not.toBeInTheDocument();
      });
    });

    it('shows theme fields when qualitative is selected', async () => {
      renderForm();
      await userEvent.click(screen.getByLabelText(/qualitative/i));
      await waitFor(() => {
        expect(screen.getByTestId('qualitative-themes-label')).toBeInTheDocument();
      });
    });
  });

  describe('Submission', () => {
    it('calls onSubmit with approach when a valid approach is selected', async () => {
      const onSubmit = vi.fn();
      renderForm(onSubmit);
      await userEvent.click(screen.getByLabelText(/qualitative/i));
      await userEvent.click(screen.getByTestId('synthesis-submit'));
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith(
          expect.objectContaining({ approach: 'qualitative' }),
          expect.anything(),
        );
      });
    });
  });

  describe('Validation', () => {
    it('does not call onSubmit without selecting an approach', async () => {
      const onSubmit = vi.fn();
      renderForm(onSubmit);
      await userEvent.click(screen.getByTestId('synthesis-submit'));
      // give a tick for the async validation
      await waitFor(() => {
        expect(onSubmit).not.toHaveBeenCalled();
      });
    });
  });

  describe('Disabled state', () => {
    it('disables submit button when isSubmitting is true', () => {
      const qc = new QueryClient();
      render(
        <QueryClientProvider client={qc}>
          <SynthesisConfigForm studyId={1} onSubmit={vi.fn()} isSubmitting />
        </QueryClientProvider>,
      );
      expect(screen.getByTestId('synthesis-submit')).toBeDisabled();
    });
  });
});
