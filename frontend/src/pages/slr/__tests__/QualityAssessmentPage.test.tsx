/**
 * Unit tests for QualityAssessmentPage (feature 007, T057).
 *
 * Covers:
 * - Renders the "Checklist Setup" tab by default.
 * - Renders the "Score Papers" tab button.
 * - Switching tabs changes the active panel.
 * - QualityChecklistEditor is rendered in the Checklist Setup tab.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import QualityAssessmentPage from '../QualityAssessmentPage';

vi.mock('../../../components/slr/QualityChecklistEditor', () => ({
  default: ({ studyId }: { studyId: number }) => (
    <div data-testid="quality-checklist-editor" data-study-id={studyId} />
  ),
}));

function renderPage(studyId = 42, reviewerId = 1) {
  const qc = new QueryClient();
  render(
    <QueryClientProvider client={qc}>
      <QualityAssessmentPage studyId={studyId} reviewerId={reviewerId} />
    </QueryClientProvider>,
  );
}

describe('QualityAssessmentPage', () => {
  it('renders the Quality Assessment heading', () => {
    renderPage();
    expect(screen.getByText(/quality assessment/i)).toBeInTheDocument();
  });

  it('renders the Checklist Setup tab', () => {
    renderPage();
    expect(screen.getByRole('tab', { name: /checklist setup/i })).toBeInTheDocument();
  });

  it('renders the Score Papers tab', () => {
    renderPage();
    expect(screen.getByRole('tab', { name: /score papers/i })).toBeInTheDocument();
  });

  it('renders QualityChecklistEditor in the first tab by default', () => {
    renderPage(77);
    expect(screen.getByTestId('quality-checklist-editor')).toBeInTheDocument();
    expect(screen.getByTestId('quality-checklist-editor').getAttribute('data-study-id')).toBe('77');
  });

  it('switches to Score Papers tab when clicked', () => {
    renderPage();
    const scorePapersTab = screen.getByRole('tab', { name: /score papers/i });
    fireEvent.click(scorePapersTab);
    expect(screen.getByText(/select an accepted paper/i)).toBeInTheDocument();
  });
});
