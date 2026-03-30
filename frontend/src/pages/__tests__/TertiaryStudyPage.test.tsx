/**
 * Unit tests for TertiaryStudyPage (feature 009).
 *
 * Covers:
 * - Renders phase tab bar.
 * - Phase 1 (Protocol) renders when active.
 * - Phase 2 (Search & Import) renders when selected.
 * - Locked phases are disabled.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TertiaryStudyPage from '../TertiaryStudyPage';

// Mock all hooks and sub-components to keep tests fast.
vi.mock('../../hooks/tertiary/useProtocol', () => ({
  useTertiaryProtocol: vi.fn(() => ({ data: null, isLoading: false, error: null })),
  useUpdateTertiaryProtocol: vi.fn(() => ({ mutate: vi.fn(), isPending: false, isError: false })),
  useValidateTertiaryProtocol: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
    isError: false,
    isSuccess: false,
  })),
}));

vi.mock('../../hooks/tertiary/useExtractions', () => ({
  useExtractions: vi.fn(() => ({ data: [], isLoading: false, error: null })),
  useUpdateExtraction: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useAiAssist: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

vi.mock('../../hooks/tertiary/useSeedImports', () => ({
  useSeedImports: vi.fn(() => ({ data: [], isLoading: false, error: null })),
  useGroupStudies: vi.fn(() => ({ data: [], isLoading: false })),
  useCreateSeedImport: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

vi.mock('../../services/slr/synthesisApi', () => ({
  startSynthesis: vi.fn(),
  listSynthesisResults: vi.fn().mockResolvedValue([]),
}));

vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn().mockReturnValue(new Promise(() => {})),
    post: vi.fn(),
  },
}));

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

const ALL_UNLOCKED = new Set([1, 2, 3, 4, 5]);
const ONLY_PHASE_1 = new Set([1]);

describe('TertiaryStudyPage', () => {
  it('renders phase tab labels', () => {
    render(
      <TertiaryStudyPage studyId={1} unlockedPhases={ALL_UNLOCKED} groupId={10} />,
      { wrapper: makeWrapper() },
    );
    expect(screen.getByRole('button', { name: /Phase 1.*Protocol/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Phase 2.*Search/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Phase 3.*Screening/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Phase 4.*Quality/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Phase 5.*Synthesis/i })).toBeInTheDocument();
  });

  it('shows Phase 1 content by default', () => {
    render(
      <TertiaryStudyPage studyId={1} unlockedPhases={ALL_UNLOCKED} groupId={10} />,
      { wrapper: makeWrapper() },
    );
    expect(screen.getByText(/Tertiary Study Protocol/i)).toBeInTheDocument();
  });

  it('switches to Phase 2 when tab is clicked', () => {
    render(
      <TertiaryStudyPage studyId={1} unlockedPhases={ALL_UNLOCKED} groupId={10} />,
      { wrapper: makeWrapper() },
    );
    fireEvent.click(screen.getByRole('button', { name: /Phase 2.*Search/i }));
    expect(screen.getAllByText(/Search & Import/i).length).toBeGreaterThanOrEqual(1);
  });

  it('renders Validate Protocol button in Phase 1', () => {
    render(
      <TertiaryStudyPage studyId={1} unlockedPhases={ONLY_PHASE_1} groupId={10} />,
      { wrapper: makeWrapper() },
    );
    expect(screen.getByRole('button', { name: /Validate Protocol/i })).toBeInTheDocument();
  });

  it('does not switch to locked phase when clicked', () => {
    render(
      <TertiaryStudyPage studyId={1} unlockedPhases={ONLY_PHASE_1} groupId={10} />,
      { wrapper: makeWrapper() },
    );
    // Phase 2 is locked, clicking it should not change the active phase
    fireEvent.click(screen.getByRole('button', { name: /Phase 2.*Search/i }));
    // Phase 1 content should still be visible
    expect(screen.getByText(/Tertiary Study Protocol/i)).toBeInTheDocument();
  });


});
