/**
 * Tests for QualityChecklistEditor component (feature 007, T059).
 *
 * Covers:
 * - Renders the checklist name input field.
 * - Clicking "Add Item" adds a new item row.
 * - Clicking "Remove" removes an item row.
 * - Submitting an empty form shows a validation error.
 * - Valid submit calls useUpsertChecklist mutate.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import QualityChecklistEditor from '../QualityChecklistEditor';

// ---------------------------------------------------------------------------
// Mock the hook
// ---------------------------------------------------------------------------

const mockMutate = vi.fn();
const mockUseUpsertChecklist = vi.fn(() => ({
  mutate: mockMutate,
  isPending: false,
}));
const mockUseChecklist = vi.fn(() => ({
  data: undefined,
  isLoading: false,
}));

vi.mock('../../../hooks/slr/useQualityAssessment', () => ({
  useChecklist: (...args: unknown[]) => mockUseChecklist(...args),
  useUpsertChecklist: (...args: unknown[]) => mockUseUpsertChecklist(...args),
}));

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

function renderEditor(studyId = 1) {
  return render(<QualityChecklistEditor studyId={studyId} />);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('QualityChecklistEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseChecklist.mockReturnValue({ data: undefined, isLoading: false });
    mockUseUpsertChecklist.mockReturnValue({ mutate: mockMutate, isPending: false });
  });

  it('renders checklist name input', () => {
    renderEditor();
    expect(screen.getByLabelText('checklist-name')).toBeInTheDocument();
  });

  it('adds a new item row when "Add Item" is clicked', async () => {
    renderEditor();
    const addBtn = screen.getByRole('button', { name: /add item/i });
    fireEvent.click(addBtn);
    await waitFor(() => {
      expect(screen.getByLabelText('item-question-0')).toBeInTheDocument();
    });
  });

  it('removes an item row when "Remove" is clicked', async () => {
    renderEditor();
    // Add an item first
    fireEvent.click(screen.getByRole('button', { name: /add item/i }));
    await waitFor(() => {
      expect(screen.getByLabelText('item-question-0')).toBeInTheDocument();
    });
    // Remove it
    fireEvent.click(screen.getByRole('button', { name: /remove-item-0/i }));
    await waitFor(() => {
      expect(screen.queryByLabelText('item-question-0')).not.toBeInTheDocument();
    });
  });

  it('shows validation error when name is empty on submit', async () => {
    renderEditor();
    fireEvent.click(screen.getByRole('button', { name: /save checklist/i }));
    await waitFor(() => {
      expect(screen.getByText(/checklist name is required/i)).toBeInTheDocument();
    });
    expect(mockMutate).not.toHaveBeenCalled();
  });

  it('calls mutate with correct data on valid submit', async () => {
    renderEditor();
    fireEvent.change(screen.getByLabelText('checklist-name'), {
      target: { value: 'My Checklist' },
    });
    fireEvent.click(screen.getByRole('button', { name: /save checklist/i }));
    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        expect.objectContaining({ name: 'My Checklist' }),
      );
    });
  });
});
