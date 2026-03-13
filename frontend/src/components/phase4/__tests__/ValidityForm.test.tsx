/**
 * Tests for ValidityForm component.
 *
 * Mocks api.get / api.patch / api.post to verify:
 * - All six validity text areas are rendered
 * - Each text area has the correct label
 * - Auto-save on blur calls api.patch with the field value
 * - "Generate with AI" button calls api.post /validity/generate
 * - Existing data is loaded and pre-fills the form
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

import { api } from '../../../services/api';
import ValidityForm from '../ValidityForm';

const STUDY_ID = 5;
const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  patch: ReturnType<typeof vi.fn>;
};

const EMPTY_VALIDITY = {
  descriptive: null,
  theoretical: null,
  generalizability_internal: null,
  generalizability_external: null,
  interpretive: null,
  repeatability: null,
};

const POPULATED_VALIDITY = {
  descriptive: 'Data was extracted by two independent reviewers.',
  theoretical: 'Classifications were grounded in established frameworks.',
  generalizability_internal: 'All included papers were treated consistently.',
  generalizability_external: 'Four major databases were searched.',
  interpretive: 'Patterns were validated through inter-rater agreement.',
  repeatability: 'Search strings are documented in the appendix.',
};

describe('ValidityForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.get.mockResolvedValue(EMPTY_VALIDITY);
    mockApi.patch.mockResolvedValue(EMPTY_VALIDITY);
    mockApi.post.mockResolvedValue({ job_id: 'vp-job-001', study_id: STUDY_ID });
  });

  describe('text areas', () => {
    it('renders six validity text areas', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() => {
        const textareas = screen.getAllByRole('textbox');
        expect(textareas.length).toBe(6);
      });
    });

    it('renders Descriptive Validity label', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByLabelText(/descriptive validity/i)).toBeTruthy()
      );
    });

    it('renders Theoretical Validity label', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByLabelText(/theoretical validity/i)).toBeTruthy()
      );
    });

    it('renders Generalizability (Internal) label', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByLabelText(/generalizability.*internal/i)).toBeTruthy()
      );
    });

    it('renders Generalizability (External) label', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByLabelText(/generalizability.*external/i)).toBeTruthy()
      );
    });

    it('renders Interpretive Validity label', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByLabelText(/interpretive validity/i)).toBeTruthy()
      );
    });

    it('renders Repeatability label', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByLabelText(/repeatability/i)).toBeTruthy()
      );
    });
  });

  describe('auto-save on blur', () => {
    it('calls api.patch with field value when textarea loses focus', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() => screen.getByLabelText(/descriptive validity/i));

      const textarea = screen.getByLabelText(/descriptive validity/i) as HTMLTextAreaElement;
      fireEvent.change(textarea, { target: { value: 'New descriptive text' } });
      fireEvent.blur(textarea);

      await waitFor(() =>
        expect(mockApi.patch).toHaveBeenCalledWith(
          `/api/v1/studies/${STUDY_ID}/validity`,
          { descriptive: 'New descriptive text' }
        )
      );
    });

    it('does not call api.patch on focus (only on blur)', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() => screen.getByLabelText(/theoretical validity/i));

      const textarea = screen.getByLabelText(/theoretical validity/i);
      fireEvent.focus(textarea);

      expect(mockApi.patch).not.toHaveBeenCalled();
    });
  });

  describe('Generate with AI button', () => {
    it('renders the Generate with AI button', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() =>
        expect(screen.getByRole('button', { name: /generate with ai/i })).toBeTruthy()
      );
    });

    it('calls api.post /validity/generate when clicked', async () => {
      render(<ValidityForm studyId={STUDY_ID} />);
      await waitFor(() => screen.getByRole('button', { name: /generate with ai/i }));

      fireEvent.click(screen.getByRole('button', { name: /generate with ai/i }));

      await waitFor(() =>
        expect(mockApi.post).toHaveBeenCalledWith(
          `/api/v1/studies/${STUDY_ID}/validity/generate`,
          {}
        )
      );
    });
  });

  describe('pre-fill from existing data', () => {
    it('loads and displays existing validity text', async () => {
      mockApi.get.mockResolvedValue(POPULATED_VALIDITY);
      render(<ValidityForm studyId={STUDY_ID} />);

      await waitFor(() => {
        const textarea = screen.getByLabelText(/descriptive validity/i) as HTMLTextAreaElement;
        expect(textarea.value).toBe('Data was extracted by two independent reviewers.');
      });
    });

    it('pre-fills all six dimensions from API response', async () => {
      mockApi.get.mockResolvedValue(POPULATED_VALIDITY);
      render(<ValidityForm studyId={STUDY_ID} />);

      await waitFor(() => {
        const textareas = screen.getAllByRole('textbox') as HTMLTextAreaElement[];
        const values = textareas.map((t) => t.value).filter(Boolean);
        expect(values.length).toBe(6);
      });
    });
  });
});
