/**
 * Tests for CriteriaForm component.
 * Verifies add/remove criterion interactions for inclusion and exclusion lists.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

import { api } from '../../../services/api';
import CriteriaForm from '../CriteriaForm';

const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

const MOCK_INCLUSION = [
  { id: 1, study_id: 1, description: 'Must be peer-reviewed', order_index: 0 },
];
const MOCK_EXCLUSION = [
  { id: 2, study_id: 1, description: 'No grey literature', order_index: 0 },
];

describe('CriteriaForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders inclusion criteria section heading', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<CriteriaForm studyId={1} />);
      expect(screen.getByText(/inclusion criteria/i)).toBeTruthy();
    });

    it('renders exclusion criteria section heading', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<CriteriaForm studyId={1} />);
      const matches = screen.getAllByText(/exclusion criteria/i);
      expect(matches.length).toBeGreaterThan(0);
    });

    it('displays inclusion criteria items from API', async () => {
      mockApi.get
        .mockResolvedValueOnce(MOCK_INCLUSION)
        .mockResolvedValueOnce(MOCK_EXCLUSION);
      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Must be peer-reviewed')).toBeTruthy();
      });
    });

    it('displays exclusion criteria items from API', async () => {
      mockApi.get
        .mockResolvedValueOnce(MOCK_INCLUSION)
        .mockResolvedValueOnce(MOCK_EXCLUSION);
      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('No grey literature')).toBeTruthy();
      });
    });

    it('shows empty state message when no inclusion criteria', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => {
        const emptyMessages = screen.getAllByText(/no criteria added yet/i);
        expect(emptyMessages.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Add inclusion criterion', () => {
    it('calls api.post with correct URL and payload on Add', async () => {
      mockApi.get.mockResolvedValue([]);
      mockApi.post.mockResolvedValueOnce({
        id: 10, study_id: 1, description: 'Empirical studies only', order_index: 0,
      });

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: 'Empirical studies only' } });

      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      fireEvent.click(addButtons[0]);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/inclusion',
          expect.objectContaining({ description: 'Empirical studies only' }),
        );
      });
    });

    it('does not call api.post when input is empty', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      expect((addButtons[0] as HTMLButtonElement).disabled).toBe(true);
    });
  });

  describe('Add exclusion criterion', () => {
    it('calls api.post for exclusion with correct URL', async () => {
      mockApi.get.mockResolvedValue([]);
      mockApi.post.mockResolvedValueOnce({
        id: 11, study_id: 1, description: 'No duplicates', order_index: 0,
      });

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[1], { target: { value: 'No duplicates' } });

      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      fireEvent.click(addButtons[1]);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/exclusion',
          expect.objectContaining({ description: 'No duplicates' }),
        );
      });
    });
  });

  describe('Remove criterion', () => {
    it('calls api.delete with correct URL when remove button is clicked', async () => {
      mockApi.get
        .mockResolvedValueOnce(MOCK_INCLUSION)
        .mockResolvedValueOnce([]);
      mockApi.delete.mockResolvedValueOnce(undefined);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => {
        expect(screen.getByText('Must be peer-reviewed')).toBeTruthy();
      });

      const removeButton = screen.getByTitle('Remove');
      fireEvent.click(removeButton);

      await waitFor(() => {
        expect(mockApi.delete).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/inclusion/1',
        );
      });
    });
  });

  describe('Order index in POST body', () => {
    it('sends order_index equal to current inclusion list length', async () => {
      mockApi.get
        .mockResolvedValueOnce(MOCK_INCLUSION)  // inclusion list has 1 item
        .mockResolvedValueOnce([]);
      mockApi.post.mockResolvedValueOnce({
        id: 20, study_id: 1, description: 'New item', order_index: 1,
      });

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('Must be peer-reviewed'));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: 'New item' } });
      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      fireEvent.click(addButtons[0]);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/inclusion',
          expect.objectContaining({ order_index: 1 }),
        );
      });
    });

    it('sends order_index=0 when inclusion list is empty', async () => {
      mockApi.get.mockResolvedValue([]);
      mockApi.post.mockResolvedValueOnce({
        id: 21, study_id: 1, description: 'First item', order_index: 0,
      });

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: 'First item' } });
      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      fireEvent.click(addButtons[0]);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/inclusion',
          expect.objectContaining({ order_index: 0 }),
        );
      });
    });
  });

  describe('Keyboard interaction', () => {
    it('pressing Enter in inclusion input triggers add', async () => {
      mockApi.get.mockResolvedValue([]);
      mockApi.post.mockResolvedValueOnce({
        id: 30, study_id: 1, description: 'Enter key test', order_index: 0,
      });

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: 'Enter key test' } });
      fireEvent.keyDown(inputs[0], { key: 'Enter', code: 'Enter' });

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/inclusion',
          expect.objectContaining({ description: 'Enter key test' }),
        );
      });
    });

    it('pressing a non-Enter key does not trigger add', async () => {
      mockApi.get.mockResolvedValue([]);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: 'Some text' } });
      fireEvent.keyDown(inputs[0], { key: 'a', code: 'KeyA' });

      // Wait briefly to allow any async mutations to fire
      await new Promise((r) => setTimeout(r, 50));
      expect(mockApi.post).not.toHaveBeenCalled();
    });
  });

  describe('Whitespace trimming', () => {
    it('does not call api.post when input contains only whitespace', async () => {
      mockApi.get.mockResolvedValue([]);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: '   ' } });

      // Add button should be disabled (trimmed = empty)
      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      expect((addButtons[0] as HTMLButtonElement).disabled).toBe(true);
    });

    it('sends trimmed text when input has surrounding whitespace', async () => {
      mockApi.get.mockResolvedValue([]);
      mockApi.post.mockResolvedValueOnce({
        id: 31, study_id: 1, description: 'trimmed text', order_index: 0,
      });

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: '  trimmed text  ' } });
      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      fireEvent.click(addButtons[0]);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/inclusion',
          expect.objectContaining({ description: 'trimmed text' }),
        );
      });
    });
  });

  describe('Reorder buttons', () => {
    const TWO_ITEMS = [
      { id: 1, study_id: 1, description: 'First', order_index: 0 },
      { id: 2, study_id: 1, description: 'Second', order_index: 1 },
    ];

    it('Move Up button is disabled for first item', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('First'));

      const upButtons = screen.getAllByTitle('Move up');
      expect((upButtons[0] as HTMLButtonElement).disabled).toBe(true);
    });

    it('Move Down button is disabled for last item', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('Second'));

      const downButtons = screen.getAllByTitle('Move down');
      expect((downButtons[downButtons.length - 1] as HTMLButtonElement).disabled).toBe(true);
    });

    it('Move Up is enabled for second item', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('First'));

      const upButtons = screen.getAllByTitle('Move up');
      expect((upButtons[1] as HTMLButtonElement).disabled).toBe(false);
    });

    it('Move Down is enabled for first item', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('Second'));

      const downButtons = screen.getAllByTitle('Move down');
      expect((downButtons[0] as HTMLButtonElement).disabled).toBe(false);
    });

    it('clicking Move Down on first item swaps positions', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);

      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('First'));

      // Items should be First, Second in order
      let items = container.querySelectorAll('li span');
      const firstSpanBefore = Array.from(items).find(el => el.textContent === 'First');
      const secondSpanBefore = Array.from(items).find(el => el.textContent === 'Second');
      expect(firstSpanBefore).toBeTruthy();
      expect(secondSpanBefore).toBeTruthy();

      const downButtons = screen.getAllByTitle('Move down');
      fireEvent.click(downButtons[0]);

      // After click, Second should appear before First
      await waitFor(() => {
        const orderedItems = container.querySelectorAll('li span');
        const texts = Array.from(orderedItems)
          .map(el => el.textContent)
          .filter(t => t === 'First' || t === 'Second');
        expect(texts[0]).toBe('Second');
        expect(texts[1]).toBe('First');
      });
    });

    it('clicking Move Up on second item swaps positions', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);

      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('Second'));

      const upButtons = screen.getAllByTitle('Move up');
      fireEvent.click(upButtons[1]);

      await waitFor(() => {
        const orderedItems = container.querySelectorAll('li span');
        const texts = Array.from(orderedItems)
          .map(el => el.textContent)
          .filter(t => t === 'First' || t === 'Second');
        expect(texts[0]).toBe('Second');
        expect(texts[1]).toBe('First');
      });
    });
  });

  describe('Exclusion list reorder', () => {
    const TWO_EXC = [
      { id: 10, study_id: 1, description: 'ExcFirst', order_index: 0 },
      { id: 11, study_id: 1, description: 'ExcSecond', order_index: 1 },
    ];

    it('Move Up button is disabled for first exclusion item', async () => {
      mockApi.get
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(TWO_EXC);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('ExcFirst'));

      const upButtons = screen.getAllByTitle('Move up');
      // There should be 2 Move Up buttons (one for each item)
      expect((upButtons[0] as HTMLButtonElement).disabled).toBe(true);
    });

    it('Move Down button is disabled for last exclusion item', async () => {
      mockApi.get
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(TWO_EXC);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('ExcSecond'));

      const downButtons = screen.getAllByTitle('Move down');
      expect((downButtons[downButtons.length - 1] as HTMLButtonElement).disabled).toBe(true);
    });

    it('clicking Move Down on first exclusion item swaps positions', async () => {
      mockApi.get
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(TWO_EXC);

      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('ExcFirst'));

      const downButtons = screen.getAllByTitle('Move down');
      fireEvent.click(downButtons[0]);

      await waitFor(() => {
        const orderedItems = container.querySelectorAll('li span');
        const texts = Array.from(orderedItems)
          .map(el => el.textContent)
          .filter(t => t === 'ExcFirst' || t === 'ExcSecond');
        expect(texts[0]).toBe('ExcSecond');
        expect(texts[1]).toBe('ExcFirst');
      });
    });

    it('clicking Move Up on second exclusion item swaps positions', async () => {
      mockApi.get
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(TWO_EXC);

      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('ExcFirst'));

      const upButtons = screen.getAllByTitle('Move up');
      fireEvent.click(upButtons[upButtons.length - 1]);

      await waitFor(() => {
        const orderedItems = container.querySelectorAll('li span');
        const texts = Array.from(orderedItems)
          .map(el => el.textContent)
          .filter(t => t === 'ExcFirst' || t === 'ExcSecond');
        expect(texts[0]).toBe('ExcSecond');
        expect(texts[1]).toBe('ExcFirst');
      });
    });

    it('calls api.post for exclusion with order_index=current exclusion length', async () => {
      mockApi.get
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(TWO_EXC); // exclusion has 2 items
      mockApi.post.mockResolvedValueOnce({
        id: 50, study_id: 1, description: 'New excl', order_index: 2,
      });

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('ExcFirst'));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[1], { target: { value: 'New excl' } });
      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      fireEvent.click(addButtons[1]);

      await waitFor(() => {
        expect(mockApi.post).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/exclusion',
          expect.objectContaining({ order_index: 2 }),
        );
      });
    });
  });

  describe('Negative state: no criteria message', () => {
    it('"No criteria added yet" NOT shown when inclusion items exist', async () => {
      mockApi.get
        .mockResolvedValueOnce(MOCK_INCLUSION)
        .mockResolvedValueOnce([]);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('Must be peer-reviewed'));

      // Only the exclusion list is empty, so there should be exactly 1 "No criteria" message
      const noMessages = screen.getAllByText(/no criteria added yet/i);
      expect(noMessages.length).toBe(1);
    });

    it('"No criteria added yet" NOT shown when exclusion items exist', async () => {
      mockApi.get
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(MOCK_EXCLUSION);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('No grey literature'));

      // Only the inclusion list is empty
      const noMessages = screen.getAllByText(/no criteria added yet/i);
      expect(noMessages.length).toBe(1);
    });
  });

  describe('Enter key with empty input', () => {
    it('pressing Enter with empty inclusion input does not call api.post', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      // Input is empty; press Enter
      fireEvent.keyDown(inputs[0], { key: 'Enter', code: 'Enter' });

      // Wait briefly to allow any async mutations to fire
      await new Promise((r) => setTimeout(r, 50));
      expect(mockApi.post).not.toHaveBeenCalled();
    });

    it('pressing Enter with whitespace-only input does not call api.post', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: '   ' } });
      fireEvent.keyDown(inputs[0], { key: 'Enter', code: 'Enter' });

      // Wait briefly to allow any async mutations to fire
      await new Promise((r) => setTimeout(r, 50));
      expect(mockApi.post).not.toHaveBeenCalled();
    });
  });

  describe('Sort by order_index', () => {
    it('renders items sorted by order_index ascending', async () => {
      const unordered = [
        { id: 1, study_id: 1, description: 'Third', order_index: 2 },
        { id: 2, study_id: 1, description: 'First', order_index: 0 },
        { id: 3, study_id: 1, description: 'Second', order_index: 1 },
      ];
      mockApi.get
        .mockResolvedValueOnce(unordered)
        .mockResolvedValueOnce([]);

      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('Third'));

      const items = container.querySelectorAll('li span');
      const texts = Array.from(items)
        .map(el => el.textContent)
        .filter(t => ['First', 'Second', 'Third'].includes(t as string));
      expect(texts[0]).toBe('First');
      expect(texts[1]).toBe('Second');
      expect(texts[2]).toBe('Third');
    });

    it('renders exclusion items sorted by order_index ascending', async () => {
      const unorderedExclusion = [
        { id: 10, study_id: 1, description: 'ExcThird', order_index: 2 },
        { id: 11, study_id: 1, description: 'ExcFirst', order_index: 0 },
        { id: 12, study_id: 1, description: 'ExcSecond', order_index: 1 },
      ];
      mockApi.get
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(unorderedExclusion);

      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('ExcThird'));

      const items = container.querySelectorAll('li span');
      const texts = Array.from(items)
        .map(el => el.textContent)
        .filter(t => ['ExcFirst', 'ExcSecond', 'ExcThird'].includes(t as string));
      expect(texts[0]).toBe('ExcFirst');
      expect(texts[1]).toBe('ExcSecond');
      expect(texts[2]).toBe('ExcThird');
    });
  });

  describe('Button style states', () => {
    const TWO_ITEMS = [
      { id: 1, study_id: 1, description: 'First', order_index: 0 },
      { id: 2, study_id: 1, description: 'Second', order_index: 1 },
    ];

    it('Move Up button has not-allowed cursor for first item (disabled)', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);
      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('First'));

      const upButtons = container.querySelectorAll('button[title="Move up"]') as NodeListOf<HTMLButtonElement>;
      expect(upButtons[0].style.cursor).toBe('not-allowed');
    });

    it('Move Up button has pointer cursor for second item (enabled)', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);
      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('First'));

      const upButtons = container.querySelectorAll('button[title="Move up"]') as NodeListOf<HTMLButtonElement>;
      expect(upButtons[1].style.cursor).toBe('pointer');
    });

    it('Move Down button has pointer cursor for first item (enabled)', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);
      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('First'));

      const downButtons = container.querySelectorAll('button[title="Move down"]') as NodeListOf<HTMLButtonElement>;
      expect(downButtons[0].style.cursor).toBe('pointer');
    });

    it('Move Down button has not-allowed cursor for last item (disabled)', async () => {
      mockApi.get
        .mockResolvedValueOnce(TWO_ITEMS)
        .mockResolvedValueOnce([]);
      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('Second'));

      const downButtons = container.querySelectorAll('button[title="Move down"]') as NodeListOf<HTMLButtonElement>;
      expect(downButtons[downButtons.length - 1].style.cursor).toBe('not-allowed');
    });

    it('Add button has not-allowed cursor when input is empty', async () => {
      mockApi.get.mockResolvedValue([]);
      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const addButtons = container.querySelectorAll('button') as NodeListOf<HTMLButtonElement>;
      const addBtn = Array.from(addButtons).find(b => b.textContent === 'Add');
      expect(addBtn).toBeTruthy();
      expect(addBtn!.style.cursor).toBe('not-allowed');
    });

    it('Add button has pointer cursor when input has text', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: 'some text' } });

      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      expect((addButtons[0] as HTMLButtonElement).style.cursor).toBe('pointer');
    });

    it('Add button has 0.6 opacity when input is empty', async () => {
      mockApi.get.mockResolvedValue([]);
      const { container } = renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const addButtons = container.querySelectorAll('button') as NodeListOf<HTMLButtonElement>;
      const addBtn = Array.from(addButtons).find(b => b.textContent === 'Add');
      expect(addBtn!.style.opacity).toBe('0.6');
    });

    it('Add button has opacity 1 when input has text', async () => {
      mockApi.get.mockResolvedValue([]);
      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getAllByText(/no criteria added yet/i));

      const inputs = screen.getAllByPlaceholderText(/add criterion/i);
      fireEvent.change(inputs[0], { target: { value: 'some text' } });

      const addButtons = screen.getAllByRole('button', { name: /^add$/i });
      expect((addButtons[0] as HTMLButtonElement).style.opacity).toBe('1');
    });
  });

  describe('Exclusion deletion', () => {
    it('calls api.delete with exclusion URL when remove is clicked on exclusion item', async () => {
      mockApi.get
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(MOCK_EXCLUSION);
      mockApi.delete.mockResolvedValueOnce(undefined);

      renderWithQuery(<CriteriaForm studyId={1} />);
      await waitFor(() => screen.getByText('No grey literature'));

      const removeButton = screen.getByTitle('Remove');
      fireEvent.click(removeButton);

      await waitFor(() => {
        expect(mockApi.delete).toHaveBeenCalledWith(
          '/api/v1/studies/1/criteria/exclusion/2',
        );
      });
    });
  });
});
