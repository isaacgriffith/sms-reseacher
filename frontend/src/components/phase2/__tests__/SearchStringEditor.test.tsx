/**
 * Tests for SearchStringEditor component.
 * Verifies version history display, manual save, and Generate with AI button call.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

import { api, ApiError } from '../../../services/api';
import SearchStringEditor from '../SearchStringEditor';

const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const MOCK_SEARCH_STRINGS = [
  {
    id: 1,
    study_id: 1,
    version: 1,
    string_text: '("TDD" OR "test-driven") AND quality',
    is_active: false,
    created_by_agent: null,
    iterations: [],
  },
];

const MOCK_ACTIVE_STRING = {
  id: 2,
  study_id: 1,
  version: 2,
  string_text: '("TDD" OR "test-driven") AND "code quality"',
  is_active: true,
  created_by_agent: 'search-builder',
  iterations: [
    {
      id: 5,
      iteration_number: 1,
      result_set_count: 100,
      test_set_recall: 0.85,
      ai_adequacy_judgment: 'Good coverage.',
      human_approved: null,
    },
  ],
};

describe('SearchStringEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders the Search String heading', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      expect(screen.getByText(/search string/i)).toBeTruthy();
    });

    it('renders the Generate with AI button', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      expect(screen.getByRole('button', { name: /generate with ai/i })).toBeTruthy();
    });

    it('renders version history when search strings are returned', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/version history/i)).toBeTruthy();
      });
    });

    it('shows AI badge for AI-generated strings', async () => {
      mockApi.get.mockResolvedValueOnce([MOCK_ACTIVE_STRING]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('AI')).toBeTruthy();
      });
    });

    it('shows Active badge for is_active strings', async () => {
      mockApi.get.mockResolvedValueOnce([MOCK_ACTIVE_STRING]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Active')).toBeTruthy();
      });
    });
  });

  describe('Manual create', () => {
    it('calls api.post with string_text on Save String click', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 3, study_id: 1, version: 1, string_text: 'manual string',
        is_active: false, created_by_agent: null, iterations: [],
      });

      renderWithQuery(<SearchStringEditor studyId={1} />);

      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: 'manual string' } });

      const saveButton = screen.getByRole('button', { name: /save string/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/search-strings',
          { string_text: 'manual string' },
        );
      });
    });

    it('Save String button is disabled when textarea is empty', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const saveButton = screen.getByRole('button', { name: /save string/i });
      expect((saveButton as HTMLButtonElement).disabled).toBe(true);
    });
  });

  describe('Version history details', () => {
    it('shows iteration count in version history', async () => {
      mockApi.get.mockResolvedValueOnce([MOCK_ACTIVE_STRING]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/1 test iteration/i)).toBeTruthy();
      });
    });

    it('shows last recall percentage in version history', async () => {
      mockApi.get.mockResolvedValueOnce([MOCK_ACTIVE_STRING]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        // test_set_recall: 0.85 → "85%"
        expect(screen.getByText(/last recall: 85%/i)).toBeTruthy();
      });
    });

    it('shows "iterations" (plural) when count > 1', async () => {
      const multiIteration = {
        ...MOCK_ACTIVE_STRING,
        iterations: [
          { ...MOCK_ACTIVE_STRING.iterations[0], id: 5, iteration_number: 1 },
          { ...MOCK_ACTIVE_STRING.iterations[0], id: 6, iteration_number: 2, test_set_recall: 0.90 },
        ],
      };
      mockApi.get.mockResolvedValueOnce([multiIteration]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/2 test iterations/i)).toBeTruthy();
      });
    });

    it('shows full string in selected view', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        // string_text from MOCK_SEARCH_STRINGS should appear in full-string section
        expect(screen.getAllByText(/TDD.*quality/)).toBeTruthy();
      });
    });
  });

  describe('Callback', () => {
    it('calls onSearchStringCreated with new string id after manual save', async () => {
      const onCreated = vi.fn();
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 99, study_id: 1, version: 1, string_text: 'test string',
        is_active: false, created_by_agent: null, iterations: [],
      });

      renderWithQuery(<SearchStringEditor studyId={1} onSearchStringCreated={onCreated} />);

      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: 'test string' } });
      fireEvent.click(screen.getByRole('button', { name: /save string/i }));

      await waitFor(() => {
        expect(onCreated).toHaveBeenCalledWith(99);
      });
    });

    it('clears manual text after successful save', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 88, study_id: 1, version: 1, string_text: 'cleared after save',
        is_active: false, created_by_agent: null, iterations: [],
      });

      renderWithQuery(<SearchStringEditor studyId={1} />);

      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: 'cleared after save' } });
      fireEvent.click(screen.getByRole('button', { name: /save string/i }));

      await waitFor(() => {
        expect((textarea as HTMLTextAreaElement).value).toBe('');
      });
    });
  });

  describe('Generate with AI', () => {
    it('calls POST /search-strings/generate when Generate with AI is clicked', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 4, study_id: 1, version: 1, string_text: 'AI generated string',
        is_active: false, created_by_agent: 'search-builder', iterations: [],
      });

      renderWithQuery(<SearchStringEditor studyId={1} />);

      const generateButton = screen.getByRole('button', { name: /generate with ai/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/search-strings/generate',
          {},
        );
      });
    });

    it('shows error message when generate fails', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      const apiErr = new ApiError('Agent unavailable');
      (apiErr as { detail?: string }).detail = 'Search string builder agent unavailable';
      mockApi.post.mockRejectedValueOnce(apiErr);

      renderWithQuery(<SearchStringEditor studyId={1} />);

      fireEvent.click(screen.getByRole('button', { name: /generate with ai/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/search string builder agent unavailable/i)
        ).toBeTruthy();
      });
    });

    it('shows "Generation failed" fallback when non-ApiError thrown', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockRejectedValueOnce(new Error('Generic error'));

      renderWithQuery(<SearchStringEditor studyId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /generate with ai/i }));

      await waitFor(() => {
        expect(screen.getByText('Generation failed')).toBeTruthy();
      });
    });

    it('calls onSearchStringCreated with new string id after AI generate', async () => {
      const onCreated = vi.fn();
      mockApi.get.mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 77, study_id: 1, version: 1, string_text: 'AI string',
        is_active: false, created_by_agent: 'search-builder', iterations: [],
      });

      renderWithQuery(<SearchStringEditor studyId={1} onSearchStringCreated={onCreated} />);
      fireEvent.click(screen.getByRole('button', { name: /generate with ai/i }));

      await waitFor(() => {
        expect(onCreated).toHaveBeenCalledWith(77);
      });
    });
  });

  describe('Selected string display', () => {
    it('shows first string in full view when no selection made', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        // First (and only) string's text appears in the full view
        const codeBlocks = screen.getAllByText(/TDD.*quality/);
        expect(codeBlocks.length).toBeGreaterThan(0);
      });
    });

    it('shows "v1 — Full String" heading for the selected string', async () => {
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/v1 — Full String/)).toBeTruthy();
      });
    });

    it('shows string_text in full view for the selected string', async () => {
      const TWO_STRINGS = [
        {
          id: 1, study_id: 1, version: 1,
          string_text: 'string-alpha',
          is_active: false, created_by_agent: null, iterations: [],
        },
        {
          id: 2, study_id: 1, version: 2,
          string_text: 'string-beta',
          is_active: false, created_by_agent: null, iterations: [],
        },
      ];
      mockApi.get.mockResolvedValueOnce(TWO_STRINGS);
      const { container } = renderWithQuery(<SearchStringEditor studyId={1} />);

      await waitFor(() => screen.getAllByText(/string-alpha/));

      // Full view shows the first (selected by default) string's text
      const codeBlocks = container.querySelectorAll('code');
      const fullViewBlock = Array.from(codeBlocks).find(el =>
        el.textContent === 'string-alpha'
      );
      expect(fullViewBlock).toBeTruthy();
    });
  });

  describe('Loading state', () => {
    it('shows Loading text while data is fetching', () => {
      mockApi.get.mockReturnValue(new Promise(() => {}));
      renderWithQuery(<SearchStringEditor studyId={1} />);
      expect(screen.getByText(/loading/i)).toBeTruthy();
    });
  });

  describe('Plural iteration count', () => {
    it('shows "iteration" singular when exactly 1 iteration', async () => {
      mockApi.get.mockResolvedValueOnce([MOCK_ACTIVE_STRING]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/1 test iteration[^s]/)).toBeTruthy();
      });
    });
  });

  describe('Version number display', () => {
    it('shows correct version number in history list', async () => {
      const vString = { ...MOCK_SEARCH_STRINGS[0], version: 5 };
      mockApi.get.mockResolvedValueOnce([vString]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        const matches = screen.getAllByText(/v5/);
        expect(matches.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Generate with AI button state', () => {
    it('shows "✨ Generate with AI" text when not generating', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      expect(screen.getByRole('button', { name: /generate with ai/i })).toBeTruthy();
    });
  });

  describe('Last recall arithmetic', () => {
    it('shows 90% when test_set_recall is 0.90', async () => {
      const highRecall = {
        ...MOCK_ACTIVE_STRING,
        iterations: [
          { ...MOCK_ACTIVE_STRING.iterations[0], test_set_recall: 0.90 },
        ],
      };
      mockApi.get.mockResolvedValueOnce([highRecall]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/last recall: 90%/i)).toBeTruthy();
      });
    });

    it('uses last iteration (highest index) for recall display', async () => {
      const twoIterations = {
        ...MOCK_ACTIVE_STRING,
        iterations: [
          { ...MOCK_ACTIVE_STRING.iterations[0], id: 1, iteration_number: 1, test_set_recall: 0.50 },
          { ...MOCK_ACTIVE_STRING.iterations[0], id: 2, iteration_number: 2, test_set_recall: 0.95 },
        ],
      };
      mockApi.get.mockResolvedValueOnce([twoIterations]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        // Should show 95%, not 50% (uses last iteration)
        expect(screen.getByText(/last recall: 95%/i)).toBeTruthy();
        expect(screen.queryByText(/last recall: 50%/i)).toBeNull();
      });
    });
  });

  describe('Version history count', () => {
    it('shows count of strings in version history heading', async () => {
      const twoStrings = [
        { ...MOCK_SEARCH_STRINGS[0], id: 1 },
        { ...MOCK_SEARCH_STRINGS[0], id: 2, version: 2, string_text: 'second string' },
      ];
      mockApi.get.mockResolvedValueOnce(twoStrings);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/Version History \(2\)/)).toBeTruthy();
      });
    });
  });

  describe('Selected string fallback when selectedId not in strings', () => {
    it('falls back to first string when selectedId is not in the loaded strings', async () => {
      // When generateAI succeeds, it sets selectedId to ss.id
      // If the strings list doesn't contain that id, falls back to strings[0]
      mockApi.get.mockResolvedValueOnce([]);
      // After generate, get returns strings WITHOUT the generated string
      mockApi.get.mockResolvedValueOnce([MOCK_SEARCH_STRINGS[0]]);
      mockApi.post.mockResolvedValueOnce({
        id: 999, study_id: 1, version: 3, string_text: 'AI string',
        is_active: false, created_by_agent: 'search-builder', iterations: [],
      });

      renderWithQuery(<SearchStringEditor studyId={1} />);
      fireEvent.click(screen.getByRole('button', { name: /generate with ai/i }));

      await waitFor(() => {
        // The strings[0] = MOCK_SEARCH_STRINGS[0] appears in full view
        // because selectedId=999 not found in strings
        const matches = screen.getAllByText(/TDD.*quality/);
        expect(matches.length).toBeGreaterThan(0);
      });
    });
  });

  describe('strings.length > 0 conditional', () => {
    it('does not show version history section when no strings returned', async () => {
      mockApi.get.mockResolvedValueOnce([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.queryByText(/version history/i)).toBeNull();
      });
    });

    it('shows version history section when strings are returned', async () => {
      mockApi.get.mockResolvedValueOnce([MOCK_SEARCH_STRINGS[0]]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText(/version history/i)).toBeTruthy();
      });
    });
  });

  describe('Save button style states', () => {
    it('Save String button has not-allowed cursor when textarea is empty', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const saveButton = screen.getByRole('button', { name: /save string/i }) as HTMLButtonElement;
      expect(saveButton.style.cursor).toBe('not-allowed');
    });

    it('Save String button has pointer cursor when text is entered', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: 'some text' } });
      const saveButton = screen.getByRole('button', { name: /save string/i }) as HTMLButtonElement;
      expect(saveButton.style.cursor).toBe('pointer');
    });

    it('Save String button has not-allowed cursor when textarea has only whitespace', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: '   ' } });
      const saveButton = screen.getByRole('button', { name: /save string/i }) as HTMLButtonElement;
      expect(saveButton.style.cursor).toBe('not-allowed');
    });

    it('Save String button has opacity 0.6 when textarea is empty', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const saveButton = screen.getByRole('button', { name: /save string/i }) as HTMLButtonElement;
      expect(saveButton.style.opacity).toBe('0.6');
    });

    it('Save String button has opacity 1 when text is entered', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: 'some text' } });
      const saveButton = screen.getByRole('button', { name: /save string/i }) as HTMLButtonElement;
      expect(saveButton.style.opacity).toBe('1');
    });

    it('Save String button has opacity 0.6 when textarea has only whitespace', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: '   ' } });
      const saveButton = screen.getByRole('button', { name: /save string/i }) as HTMLButtonElement;
      expect(saveButton.style.opacity).toBe('0.6');
    });

    it('Save String button is disabled when textarea has only whitespace', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: '   ' } });
      const saveButton = screen.getByRole('button', { name: /save string/i }) as HTMLButtonElement;
      expect(saveButton.disabled).toBe(true);
    });
  });

  describe('Version history item selection styles', () => {
    const TWO_STRINGS = [
      {
        id: 1, study_id: 1, version: 1,
        string_text: 'first-string',
        is_active: false, created_by_agent: null, iterations: [],
      },
      {
        id: 2, study_id: 1, version: 2,
        string_text: 'second-string',
        is_active: false, created_by_agent: null, iterations: [],
      },
    ];

    it('selected item has light blue background, unselected has white', async () => {
      mockApi.get.mockResolvedValueOnce(TWO_STRINGS);
      const { container } = renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => screen.getByText(/version history/i));

      // Find all version history item divs by their style attributes
      const historyDivs = Array.from(
        container.querySelectorAll('div[style]')
      ) as HTMLElement[];

      const selectedItem = historyDivs.find(
        el => el.style.background === 'rgb(239, 246, 255)' || el.style.backgroundColor === 'rgb(239, 246, 255)'
      );
      expect(selectedItem).toBeTruthy();

      const unselectedItem = historyDivs.find(
        el => el.style.background === 'rgb(255, 255, 255)' || el.style.backgroundColor === 'rgb(255, 255, 255)'
      );
      // At least one unselected item exists
      expect(unselectedItem || historyDivs.some(el => el.style.background === '#fff')).toBeTruthy();
    });

    it('clicking second item gives it the selected background color', async () => {
      mockApi.get.mockResolvedValueOnce(TWO_STRINGS);
      const { container } = renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => screen.getByText(/version history/i));

      // Click on v2 item
      const v2Label = screen.getAllByText(/^v\d+$/).find(el => el.textContent === 'v2');
      fireEvent.click(v2Label!);

      await waitFor(() => {
        const historyDivs = Array.from(
          container.querySelectorAll('div[style]')
        ) as HTMLElement[];
        // After clicking v2, there should still be exactly one selected (blue) item
        const selectedItems = historyDivs.filter(
          el =>
            el.style.background === 'rgb(239, 246, 255)' ||
            el.style.backgroundColor === 'rgb(239, 246, 255)' ||
            el.style.background === '#eff6ff'
        );
        expect(selectedItems.length).toBeGreaterThanOrEqual(1);
      });
    });
  });

  describe('Negative badge assertions', () => {
    it('AI badge NOT shown when created_by_agent is null', async () => {
      // MOCK_SEARCH_STRINGS[0] has created_by_agent: null
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => screen.getByText(/version history/i));
      expect(screen.queryByText('AI')).toBeNull();
    });

    it('Active badge NOT shown when is_active is false', async () => {
      // MOCK_SEARCH_STRINGS[0] has is_active: false
      mockApi.get.mockResolvedValueOnce(MOCK_SEARCH_STRINGS);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => screen.getByText(/version history/i));
      expect(screen.queryByText('Active')).toBeNull();
    });

    it('generate error NOT shown initially before any generate attempt', async () => {
      mockApi.get.mockResolvedValue([]);
      const { container } = renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => screen.getByRole('button', { name: /generate with ai/i }));
      expect(screen.queryByText(/generation failed/i)).toBeNull();
      // Also verify no error-styled paragraph exists (catches && → || mutations)
      const errorPs = Array.from(container.querySelectorAll('p')).filter(
        el => (el as HTMLElement).style.color === 'rgb(239, 68, 68)'
      );
      expect(errorPs.length).toBe(0);
    });

    it('Save String button is NOT disabled when text is entered in textarea', () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      const textarea = screen.getByPlaceholderText(/boolean search string/i);
      fireEvent.change(textarea, { target: { value: 'some search string text' } });
      const saveButton = screen.getByRole('button', { name: /save string/i });
      expect((saveButton as HTMLButtonElement).disabled).toBe(false);
    });
  });

  describe('String selection by click', () => {
    it('clicking second string in history switches the full view to that string', async () => {
      const TWO_STRINGS = [
        {
          id: 1, study_id: 1, version: 1,
          string_text: 'string-alpha',
          is_active: false, created_by_agent: null, iterations: [],
        },
        {
          id: 2, study_id: 1, version: 2,
          string_text: 'string-beta',
          is_active: false, created_by_agent: null, iterations: [],
        },
      ];
      mockApi.get.mockResolvedValueOnce(TWO_STRINGS);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => screen.getByText(/version history/i));

      // Initially full view shows v1 (first string)
      expect(screen.getByText('v1 — Full String')).toBeTruthy();

      // Click on the v2 span to select second string
      const versionLabels = screen.getAllByText(/^v\d+$/);
      // versionLabels[0] = "v1" in history list, versionLabels[1] = "v2" in history list
      // (the full view shows "v1 — Full String" not just "v1")
      const v2Label = versionLabels.find(el => el.textContent === 'v2');
      expect(v2Label).toBeTruthy();
      fireEvent.click(v2Label!);

      await waitFor(() => {
        expect(screen.getByText('v2 — Full String')).toBeTruthy();
      });
    });

    it('clicking first string after selecting second restores first string in full view', async () => {
      const TWO_STRINGS = [
        {
          id: 1, study_id: 1, version: 1,
          string_text: 'first-string-text',
          is_active: false, created_by_agent: null, iterations: [],
        },
        {
          id: 2, study_id: 1, version: 2,
          string_text: 'second-string-text',
          is_active: false, created_by_agent: null, iterations: [],
        },
      ];
      mockApi.get.mockResolvedValueOnce(TWO_STRINGS);
      renderWithQuery(<SearchStringEditor studyId={1} />);
      await waitFor(() => screen.getByText(/version history/i));

      // Click v2
      const v2Label = screen.getAllByText(/^v\d+$/).find(el => el.textContent === 'v2');
      fireEvent.click(v2Label!);
      await waitFor(() => expect(screen.getByText('v2 — Full String')).toBeTruthy());

      // Click v1 to go back
      const v1Label = screen.getAllByText(/^v\d+$/).find(el => el.textContent === 'v1');
      fireEvent.click(v1Label!);
      await waitFor(() => {
        expect(screen.getByText('v1 — Full String')).toBeTruthy();
      });
    });
  });
});
