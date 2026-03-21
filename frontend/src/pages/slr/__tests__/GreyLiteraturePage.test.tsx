/**
 * Unit tests for GreyLiteraturePage (feature 007, T094).
 *
 * Covers:
 * - Renders page heading.
 * - Renders description text.
 * - Renders the GreyLiteraturePanel.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import GreyLiteraturePage from '../GreyLiteraturePage';

vi.mock('../../../components/slr/GreyLiteraturePanel', () => ({
  default: ({ studyId }: { studyId: number }) => (
    <div data-testid="grey-literature-panel" data-study-id={studyId} />
  ),
}));

function renderPage(studyId = 42) {
  const qc = new QueryClient();
  render(
    <QueryClientProvider client={qc}>
      <GreyLiteraturePage studyId={studyId} />
    </QueryClientProvider>,
  );
}

describe('GreyLiteraturePage', () => {
  it('renders the page heading', () => {
    renderPage();
    expect(screen.getByText(/grey literature sources/i)).toBeInTheDocument();
  });

  it('renders a descriptive text', () => {
    renderPage();
    expect(screen.getByText(/technical reports|dissertations/i)).toBeInTheDocument();
  });

  it('renders the GreyLiteraturePanel with correct studyId', () => {
    renderPage(99);
    const panel = screen.getByTestId('grey-literature-panel');
    expect(panel).toBeInTheDocument();
    expect(panel.getAttribute('data-study-id')).toBe('99');
  });

  it('renders within the grey-literature-page container', () => {
    renderPage();
    expect(screen.getByTestId('grey-literature-page')).toBeInTheDocument();
  });
});
