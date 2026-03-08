/**
 * Tests for DiffViewer component.
 *
 * Mocks api.patch (resolution PATCH calls).
 * Covers (T152):
 * - Renders two-column diff table with your_version and current_version
 * - Highlights rows where values differ
 * - "Keep Mine" resubmits PATCH with current_version.version_id and your field values
 * - "Keep Theirs" calls onResolved without a PATCH
 * - "Merge" resubmits with current_version.version_id, preferring your non-null values
 * - "Cancel" calls onDismiss without a PATCH
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../../services/api', () => ({
  api: {
    patch: vi.fn(),
  },
}));

import { api } from '../../../services/api';
import DiffViewer from '../DiffViewer';

const mockApi = api as unknown as {
  patch: ReturnType<typeof vi.fn>;
};

const CONFLICT_PAYLOAD = {
  error: 'conflict',
  your_version: {
    version_id: 1,
    research_type: 'evaluation',
    venue_type: 'conference',
    venue_name: 'ICSE 2023',
    summary: 'My summary',
    keywords: ['TDD'],
  },
  current_version: {
    version_id: 2,
    research_type: 'evaluation',
    venue_type: 'journal',
    venue_name: 'TSE',
    summary: 'Their summary',
    keywords: ['agile'],
  },
};

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe('DiffViewer', () => {
  const onResolved = vi.fn();
  const onDismiss = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    onResolved.mockReset();
    onDismiss.mockReset();
  });

  describe('Rendering', () => {
    it('renders the conflict heading', () => {
      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );
      expect(screen.getByText(/conflict detected/i)).toBeTruthy();
    });

    it('renders Your Version and Current Version column headers', () => {
      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );
      expect(screen.getByText(/your version/i)).toBeTruthy();
      expect(screen.getByText(/current version/i)).toBeTruthy();
    });

    it('shows your venue_name value in the diff', () => {
      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );
      expect(screen.getByText('ICSE 2023')).toBeTruthy();
    });

    it('shows the current venue_name value in the diff', () => {
      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );
      expect(screen.getByText('TSE')).toBeTruthy();
    });

    it('renders Keep Mine, Keep Theirs, Merge, and Cancel buttons', () => {
      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );
      expect(screen.getByRole('button', { name: /keep mine/i })).toBeTruthy();
      expect(screen.getByRole('button', { name: /keep theirs/i })).toBeTruthy();
      expect(screen.getByRole('button', { name: /merge/i })).toBeTruthy();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeTruthy();
    });
  });

  describe('Keep Mine', () => {
    it('calls api.patch with current_version.version_id and your field values', async () => {
      mockApi.patch.mockResolvedValueOnce({});

      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /keep mine/i }));

      await waitFor(() => {
        expect(mockApi.patch).toHaveBeenCalledTimes(1);
        const [url, body] = mockApi.patch.mock.calls[0];
        expect(url).toBe('/api/v1/studies/1/extractions/1');
        // Must use current_version.version_id (2), not the stale one (1)
        expect(body.version_id).toBe(2);
        // Must include your venue_type
        expect(body.venue_type).toBe('conference');
      });
    });

    it('calls onResolved after successful patch', async () => {
      mockApi.patch.mockResolvedValueOnce({});

      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /keep mine/i }));

      await waitFor(() => {
        expect(onResolved).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Keep Theirs', () => {
    it('calls onResolved without calling api.patch', async () => {
      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /keep theirs/i }));

      await waitFor(() => {
        expect(onResolved).toHaveBeenCalledTimes(1);
        expect(mockApi.patch).not.toHaveBeenCalled();
      });
    });
  });

  describe('Merge', () => {
    it('calls api.patch with current_version.version_id', async () => {
      mockApi.patch.mockResolvedValueOnce({});

      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /merge/i }));

      await waitFor(() => {
        expect(mockApi.patch).toHaveBeenCalledTimes(1);
        const [, body] = mockApi.patch.mock.calls[0];
        expect(body.version_id).toBe(2);
      });
    });

    it('prefers your non-null values in the merged payload', async () => {
      mockApi.patch.mockResolvedValueOnce({});

      const payload = {
        ...CONFLICT_PAYLOAD,
        your_version: {
          ...CONFLICT_PAYLOAD.your_version,
          venue_name: 'My Venue',
        },
        current_version: {
          ...CONFLICT_PAYLOAD.current_version,
          venue_name: 'Their Venue',
        },
      };

      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={payload}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /merge/i }));

      await waitFor(() => {
        const [, body] = mockApi.patch.mock.calls[0];
        expect(body.venue_name).toBe('My Venue');
      });
    });
  });

  describe('Cancel', () => {
    it('calls onDismiss without calling api.patch', async () => {
      renderWithQuery(
        <DiffViewer
          studyId={1}
          extractionId={1}
          conflict={CONFLICT_PAYLOAD}
          onResolved={onResolved}
          onDismiss={onDismiss}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /cancel/i }));

      await waitFor(() => {
        expect(onDismiss).toHaveBeenCalledTimes(1);
        expect(mockApi.patch).not.toHaveBeenCalled();
      });
    });
  });
});
