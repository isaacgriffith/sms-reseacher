/**
 * Tests for ExtractionView component.
 *
 * Mocks api.get (fetch extraction) and api.patch (update extraction).
 * Covers (T152):
 * - Renders extraction fields from API
 * - Shows validation status badge
 * - Clicking Edit on a field shows the input
 * - Saving a field triggers api.patch with the correct version_id
 * - 409 conflict response calls onConflict with the conflict payload
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    patch: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    status: number;
    detail: unknown;
    constructor(status: number, detail: unknown) {
      super(String(detail));
      this.name = 'ApiError';
      this.status = status;
      this.detail = detail;
    }
  },
}));

import { api, ApiError } from '../../../services/api';
import ExtractionView from '../ExtractionView';

const mockApi = api as unknown as {
  get: ReturnType<typeof vi.fn>;
  patch: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const MOCK_EXTRACTION = {
  id: 1,
  candidate_paper_id: 42,
  research_type: 'evaluation',
  venue_type: 'conference',
  venue_name: 'ICSE 2023',
  author_details: [{ name: 'Alice', institution: 'MIT', locale: 'US' }],
  summary: 'An empirical study of TDD adoption.',
  open_codings: [{ code: 'productivity', definition: 'speed', evidence_quote: 'faster' }],
  keywords: ['TDD', 'agile'],
  question_data: { RQ1: 'Teams adopted TDD in 60% of cases' },
  extraction_status: 'ai_complete',
  version_id: 1,
  extracted_by_agent: 'ExtractorAgent',
  conflict_flag: false,
  created_at: '2026-03-12T00:00:00Z',
  updated_at: '2026-03-12T00:00:00Z',
  audit_history: [],
};

describe('ExtractionView', () => {
  const onConflict = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    onConflict.mockReset();
  });

  describe('Rendering', () => {
    it('renders extraction status badge', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        const badges = screen.getAllByText(/ai complete/i);
        expect(badges.length).toBeGreaterThan(0);
      });
    });

    it('renders venue name from API data', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText('ICSE 2023')).toBeTruthy();
      });
    });

    it('renders paper summary', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText(/empirical study of TDD/i)).toBeTruthy();
      });
    });

    it('renders keyword tags', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText('TDD')).toBeTruthy();
        expect(screen.getByText('agile')).toBeTruthy();
      });
    });

    it('renders conflict badge when conflict_flag is true', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, conflict_flag: true });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText(/conflict/i)).toBeTruthy();
      });
    });

    it('does not show conflict badge when conflict_flag is false', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, conflict_flag: false });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        // status badge exists but 'Conflict' badge should not
        expect(screen.queryByText(/^Conflict$/i)).toBeNull();
      });
    });
  });

  describe('Inline editing', () => {
    it('clicking Edit shows an input field for venue_type', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText('conference'));

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[0]);

      await waitFor(() => {
        // An input or select should now be visible
        const inputs = screen.queryAllByRole('textbox');
        const selects = screen.queryAllByRole('combobox');
        expect(inputs.length + selects.length).toBeGreaterThan(0);
      });
    });

    it('clicking Cancel after Edit hides the input', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText('conference'));

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[0]);

      await waitFor(() => screen.getByRole('button', { name: /cancel/i }));
      fireEvent.click(screen.getByRole('button', { name: /cancel/i }));

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /cancel/i })).toBeNull();
      });
    });
  });

  describe('Loading and error states', () => {
    it('shows "Loading extraction…" while data is loading', () => {
      // Never resolves → stays loading
      mockApi.get.mockReturnValue(new Promise(() => {}));
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      expect(screen.getByText(/loading extraction/i)).toBeTruthy();
    });

    it('shows "Failed to load extraction" on API error', async () => {
      mockApi.get.mockRejectedValueOnce(new Error('Network error'));
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText(/failed to load extraction/i)).toBeTruthy();
      });
    });
  });

  describe('Conditional field rendering', () => {
    it('shows em-dash (—) when venue_type is empty string', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, venue_type: '' });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getAllByText('—').length).toBeGreaterThan(0);
      });
    });

    it('shows em-dash (—) when venue_name is null', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, venue_name: null });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getAllByText('—').length).toBeGreaterThan(0);
      });
    });

    it('shows em-dash (—) when summary is null', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, summary: null });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getAllByText('—').length).toBeGreaterThan(0);
      });
    });

    it('shows extracted_by_agent attribution when set', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText(/extracted by: ExtractorAgent/i)).toBeTruthy();
      });
    });

    it('does not show agent attribution when extracted_by_agent is null', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, extracted_by_agent: null });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText(/data extraction/i));
      expect(screen.queryByText(/extracted by/i)).toBeNull();
    });

    it('shows version_id in agent attribution line', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, version_id: 7 });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText(/version 7/i)).toBeTruthy();
      });
    });

    it('shows "No open codings yet." when open_codings is null', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, open_codings: null });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText(/no open codings yet/i)).toBeTruthy();
      });
    });

    it('shows "No open codings yet." when open_codings is empty array', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, open_codings: [] });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText(/no open codings yet/i)).toBeTruthy();
      });
    });

    it('shows open coding code when open_codings has entries', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText('productivity')).toBeTruthy();
      });
    });

    it('shows evidence_quote in blockquote when present', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText('faster')).toBeTruthy();
      });
    });

    it('does not show blockquote when evidence_quote is empty string', async () => {
      const extractionNoQuote = {
        ...MOCK_EXTRACTION,
        open_codings: [{ code: 'test-code', definition: 'test-def', evidence_quote: '' }],
      };
      mockApi.get.mockResolvedValueOnce(extractionNoQuote);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText('test-code'));
      expect(screen.queryByRole('blockquote')).toBeNull();
    });

    it('renders question_data table when question_data has entries', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText('RQ1')).toBeTruthy();
        expect(screen.getByText('Teams adopted TDD in 60% of cases')).toBeTruthy();
      });
    });

    it('does not render question_data section when question_data is null', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, question_data: null });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText(/data extraction/i));
      expect(screen.queryByText('RQ1')).toBeNull();
    });

    it('does not render question_data section when question_data is empty object', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, question_data: {} });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText(/data extraction/i));
      expect(screen.queryByText('RQ1')).toBeNull();
    });

    it('shows em-dash for null question answer', async () => {
      const extractionNullAnswer = {
        ...MOCK_EXTRACTION,
        question_data: { RQ_null: null },
      };
      mockApi.get.mockResolvedValueOnce(extractionNullAnswer);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText('RQ_null')).toBeTruthy();
        expect(screen.getAllByText('—').length).toBeGreaterThan(0);
      });
    });

    it('shows string representation of non-null question answer', async () => {
      const extractionNumAnswer = {
        ...MOCK_EXTRACTION,
        question_data: { RQ_num: 42 },
      };
      mockApi.get.mockResolvedValueOnce(extractionNumAnswer);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText('42')).toBeTruthy();
      });
    });

    it('shows em-dash (—) for keywords when keywords is null', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, keywords: null });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getAllByText('—').length).toBeGreaterThan(0);
      });
    });

    it('shows keywords as tag spans when present', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => {
        expect(screen.getByText('TDD')).toBeTruthy();
        expect(screen.getByText('agile')).toBeTruthy();
      });
    });
  });

  describe('Save error handling', () => {
    it('shows "Save failed" message on non-409 patch error', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      mockApi.patch.mockRejectedValueOnce(new Error('Server error'));

      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText('conference'));

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[0]);
      await waitFor(() => screen.getByRole('button', { name: /save/i }));
      fireEvent.click(screen.getByRole('button', { name: /save/i }));

      await waitFor(() => {
        expect(screen.getByText(/save failed/i)).toBeTruthy();
      });
    });

    it('does not show "Save failed" message on 409 conflict error', async () => {
      const conflictDetail = {
        error: 'conflict',
        your_version: { version_id: 1, venue_type: 'conference' },
        current_version: { version_id: 2, venue_type: 'journal' },
      };
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      const err = new ApiError(409, conflictDetail);
      mockApi.patch.mockRejectedValueOnce(err);

      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText('conference'));

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[0]);
      await waitFor(() => screen.getByRole('button', { name: /save/i }));
      fireEvent.click(screen.getByRole('button', { name: /save/i }));

      await waitFor(() => onConflict.mock.calls.length > 0);
      expect(screen.queryByText(/save failed/i)).toBeNull();
    });
  });

  describe('Edit mode pre-populated values', () => {
    it('edit mode for venue_name shows current value in input', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText('ICSE 2023'));

      // Click Edit on Venue Name (third Edit button — Research Type, Venue Type, Venue Name)
      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[2]); // Venue Name

      await waitFor(() => {
        const inputs = screen.queryAllByRole('textbox') as HTMLInputElement[];
        const venueNameInput = inputs.find(el => el.defaultValue === 'ICSE 2023');
        expect(venueNameInput).toBeTruthy();
      });
    });

    it('edit mode for summary shows current value in textarea', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText(/empirical study of TDD/i));

      // Click Edit on Summary (4th Edit button)
      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[3]); // Summary

      await waitFor(() => {
        const textareas = screen.queryAllByRole('textbox') as HTMLTextAreaElement[];
        const summaryArea = textareas.find(el =>
          el.defaultValue?.includes('empirical study of TDD')
        );
        expect(summaryArea).toBeTruthy();
      });
    });

    it('edit mode for venue_name shows empty input when venue_name is null', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, venue_name: null });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getAllByText('—'));

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[2]); // Venue Name

      await waitFor(() => {
        const inputs = screen.queryAllByRole('textbox') as HTMLInputElement[];
        // When venue_name is null, defaultValue should be '' (empty string)
        const emptyInput = inputs.find(el => el.defaultValue === '');
        expect(emptyInput).toBeTruthy();
      });
    });

    it('Conflict badge NOT shown initially when conflict_flag is false', async () => {
      mockApi.get.mockResolvedValueOnce({ ...MOCK_EXTRACTION, conflict_flag: false });
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText(/data extraction/i));
      expect(screen.queryByText('Conflict')).toBeNull();
    });

    it('Save failed message NOT shown before any edit attempt', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText(/data extraction/i));
      expect(screen.queryByText(/save failed/i)).toBeNull();
    });
  });

  describe('PATCH with version_id', () => {
    it('saving a field calls api.patch with the extraction version_id', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      mockApi.patch.mockResolvedValueOnce({ ...MOCK_EXTRACTION, venue_type: 'journal', version_id: 2 });

      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText('conference'));

      // Click Edit for the first field (Research Type)
      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[0]);

      await waitFor(() => screen.getByRole('button', { name: /save/i }));
      fireEvent.click(screen.getByRole('button', { name: /save/i }));

      await waitFor(() => {
        expect(mockApi.patch).toHaveBeenCalledTimes(1);
        const [url, body] = mockApi.patch.mock.calls[0];
        expect(url).toBe('/api/v1/studies/1/extractions/1');
        expect(body.version_id).toBe(1);
      });
    });

    it('409 response calls onConflict with the conflict payload', async () => {
      const conflictDetail = {
        error: 'conflict',
        your_version: { version_id: 1, venue_type: 'conference' },
        current_version: { version_id: 2, venue_type: 'journal' },
      };

      mockApi.get.mockResolvedValueOnce(MOCK_EXTRACTION);
      // Simulate ApiError with 409 status
      const err = new ApiError(409, conflictDetail);
      mockApi.patch.mockRejectedValueOnce(err);

      renderWithQuery(
        <ExtractionView studyId={1} extractionId={1} onConflict={onConflict} />
      );
      await waitFor(() => screen.getByText('conference'));

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      fireEvent.click(editButtons[0]);

      await waitFor(() => screen.getByRole('button', { name: /save/i }));
      fireEvent.click(screen.getByRole('button', { name: /save/i }));

      await waitFor(() => {
        expect(onConflict).toHaveBeenCalledTimes(1);
        expect(onConflict).toHaveBeenCalledWith(conflictDetail);
      });
    });
  });
});
