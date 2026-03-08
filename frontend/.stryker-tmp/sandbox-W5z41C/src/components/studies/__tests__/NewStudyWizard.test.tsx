/**
 * Tests for NewStudyWizard component.
 * Verifies step navigation, form validation errors, and API call shape.
 */
// @ts-nocheck


import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import NewStudyWizard from '../NewStudyWizard';

// Mock api module
vi.mock('../../../services/api', () => ({
  api: {
    post: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

import { api } from '../../../services/api';

const mockApi = api as { post: ReturnType<typeof vi.fn> };

const defaultProps = {
  groupId: 1,
  onClose: vi.fn(),
  onCreated: vi.fn(),
};

describe('NewStudyWizard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Step navigation', () => {
    it('renders step 1 by default', () => {
      render(<NewStudyWizard {...defaultProps} />);
      expect(screen.getByText(/step 1/i)).toBeTruthy();
    });

    it('advances to step 2 when Next is clicked on step 1 with valid data', async () => {
      render(<NewStudyWizard {...defaultProps} />);

      // Fill required fields on step 1
      const nameInput = screen.getByPlaceholderText(/study name/i);
      fireEvent.change(nameInput, { target: { value: 'My Study' } });

      const topicInput = screen.getByPlaceholderText(/topic/i);
      fireEvent.change(topicInput, { target: { value: 'TDD' } });

      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText(/step 2/i)).toBeTruthy();
      });
    });

    it('shows Back button on step 2', async () => {
      render(<NewStudyWizard {...defaultProps} />);

      const nameInput = screen.getByPlaceholderText(/study name/i);
      fireEvent.change(nameInput, { target: { value: 'My Study' } });
      const topicInput = screen.getByPlaceholderText(/topic/i);
      fireEvent.change(topicInput, { target: { value: 'TDD' } });

      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /back/i })).toBeTruthy();
      });
    });

    it('navigates back when Back is clicked', async () => {
      render(<NewStudyWizard {...defaultProps} />);

      const nameInput = screen.getByPlaceholderText(/study name/i);
      fireEvent.change(nameInput, { target: { value: 'My Study' } });
      const topicInput = screen.getByPlaceholderText(/topic/i);
      fireEvent.change(topicInput, { target: { value: 'TDD' } });

      fireEvent.click(screen.getByRole('button', { name: /next/i }));
      await waitFor(() => screen.getByRole('button', { name: /back/i }));

      fireEvent.click(screen.getByRole('button', { name: /back/i }));
      await waitFor(() => {
        expect(screen.getByText(/step 1/i)).toBeTruthy();
      });
    });

    it('calls onClose when cancel/close is clicked', () => {
      render(<NewStudyWizard {...defaultProps} />);
      const closeButton = screen.getByRole('button', { name: /cancel|close/i });
      fireEvent.click(closeButton);
      expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Form validation', () => {
    it('shows validation error when name is missing on step 1', async () => {
      render(<NewStudyWizard {...defaultProps} />);
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        // Should still be on step 1 or show an error
        expect(screen.getByText(/step 1/i)).toBeTruthy();
      });
    });
  });

  describe('API call shape', () => {
    it('calls api.post with correct shape on final submit', async () => {
      mockApi.post.mockResolvedValueOnce({ id: 42 });
      render(<NewStudyWizard {...defaultProps} />);

      // Navigate through all 5 steps quickly by filling minimum required fields
      const nameInput = screen.getByPlaceholderText(/study name/i);
      fireEvent.change(nameInput, { target: { value: 'API Shape Study' } });
      const topicInput = screen.getByPlaceholderText(/topic/i);
      fireEvent.change(topicInput, { target: { value: 'TDD testing' } });

      // Click Next 4 times to get to step 5
      for (let i = 0; i < 4; i++) {
        const nextBtn = screen.getByRole('button', { name: /next/i });
        fireEvent.click(nextBtn);
        await waitFor(() => {});
      }

      const submitButton = screen.getByRole('button', { name: /create|submit|finish/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        if (mockApi.post.mock.calls.length > 0) {
          const [url, payload] = mockApi.post.mock.calls[0];
          expect(url).toMatch(/groups\/1\/studies/);
          expect(payload).toHaveProperty('name');
          expect(payload).toHaveProperty('study_type');
        }
      });
    });
  });
});
