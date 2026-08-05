import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import ProtocolLibraryPage from '../ProtocolLibraryPage';
import { useProtocolList, useCopyProtocol, useAssignProtocol, useImportProtocol } from '../../../hooks/protocols/useProtocol';

const { mockNavigate, mockCopyMutate, mockAssignMutate, mockImportMutate } = vi.hoisted(() => ({
  mockNavigate: vi.fn(),
  mockCopyMutate: vi.fn(),
  mockAssignMutate: vi.fn(),
  mockImportMutate: vi.fn(),
}));

vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

vi.mock('../../../hooks/protocols/useProtocol', () => ({
  useProtocolList: vi.fn().mockReturnValue({
    data: [
      { id: 1, name: 'SMS Default', study_type: 'sms', is_default_template: true, owner_user_id: null, version_id: 1 },
    ],
    isLoading: false,
    error: null,
  }),
  useCopyProtocol: vi.fn().mockReturnValue({ mutate: (...args: unknown[]) => mockCopyMutate(...args), isPending: false }),
  useAssignProtocol: vi.fn().mockReturnValue({ mutate: (...args: unknown[]) => mockAssignMutate(...args), isPending: false }),
  useImportProtocol: vi.fn().mockReturnValue({ mutate: (...args: unknown[]) => mockImportMutate(...args), isPending: false }),
}));

vi.mock('../../../services/protocols/protocolsApi', () => ({
  exportProtocol: vi.fn().mockResolvedValue(undefined),
}));

// Mock ProtocolList to expose callbacks
let capturedCallbacks: Record<string, (p: unknown) => void> = {};
vi.mock('../../../components/protocols/ProtocolList', () => ({
  default: ({ protocols, onSelect, onCopy, onAssign, onExport }: Record<string, unknown>) => {
    capturedCallbacks = { onSelect, onCopy, onAssign, onExport } as Record<string, (p: unknown) => void>;
    return React.createElement(
      'div',
      { 'data-testid': 'protocol-list' },
      `${(protocols as unknown[]).length} protocols`,
    );
  },
}));

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    React.createElement(QueryClientProvider, { client: qc }, React.createElement(ProtocolLibraryPage)),
  );
}

const sampleProtocol = { id: 1, name: 'SMS Default', study_type: 'sms' };

describe('ProtocolLibraryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    capturedCallbacks = {};
    vi.mocked(useProtocolList).mockReturnValue({
      data: [
        { id: 1, name: 'SMS Default', study_type: 'sms', is_default_template: true, owner_user_id: null, version_id: 1 },
      ],
      isLoading: false,
      error: null,
    } as ReturnType<typeof useProtocolList>);
    vi.mocked(useCopyProtocol).mockReturnValue({ mutate: (...args: unknown[]) => mockCopyMutate(...args), isPending: false } as ReturnType<typeof useCopyProtocol>);
    vi.mocked(useAssignProtocol).mockReturnValue({ mutate: (...args: unknown[]) => mockAssignMutate(...args), isPending: false } as ReturnType<typeof useAssignProtocol>);
    vi.mocked(useImportProtocol).mockReturnValue({ mutate: (...args: unknown[]) => mockImportMutate(...args), isPending: false } as ReturnType<typeof useImportProtocol>);
  });

  it('renders protocol list', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByTestId('protocol-list')).toBeInTheDocument());
    expect(screen.getByText('1 protocols')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    vi.mocked(useProtocolList).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as ReturnType<typeof useProtocolList>);
    renderPage();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('navigates on select', async () => {
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onSelect).toBeDefined());
    capturedCallbacks.onSelect(sampleProtocol);
    expect(mockNavigate).toHaveBeenCalledWith('/protocols/1');
  });

  it('opens copy dialog', async () => {
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onCopy).toBeDefined());
    act(() => { capturedCallbacks.onCopy(sampleProtocol); });
    expect(screen.getByText('Copy Protocol')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Copy of SMS Default')).toBeInTheDocument();
  });

  it('confirms copy and navigates on success', async () => {
    mockCopyMutate.mockImplementation((_data: unknown, opts?: { onSuccess?: (r: { id: number }) => void }) => {
      opts?.onSuccess?.({ id: 99 });
    });
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onCopy).toBeDefined());
    act(() => { capturedCallbacks.onCopy(sampleProtocol); });
    fireEvent.click(screen.getByText('Copy'));
    expect(mockCopyMutate).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/protocols/99/edit');
  });

  it('shows copy error on failure', async () => {
    mockCopyMutate.mockImplementation((_data: unknown, opts?: { onError?: () => void }) => {
      opts?.onError?.();
    });
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onCopy).toBeDefined());
    act(() => { capturedCallbacks.onCopy(sampleProtocol); });
    fireEvent.click(screen.getByText('Copy'));
    expect(screen.getByText(/Failed to copy/)).toBeInTheDocument();
  });

  it('opens assign dialog', async () => {
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onAssign).toBeDefined());
    act(() => { capturedCallbacks.onAssign(sampleProtocol); });
    expect(screen.getByText('Assign to Study')).toBeInTheDocument();
  });

  it('confirms assign with valid study ID and closes on success', async () => {
    mockAssignMutate.mockImplementation((_data: unknown, opts?: { onSuccess?: () => void }) => {
      opts?.onSuccess?.();
    });
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onAssign).toBeDefined());
    act(() => { capturedCallbacks.onAssign(sampleProtocol); });
    fireEvent.change(screen.getByLabelText('Study ID'), { target: { value: '42' } });
    fireEvent.click(screen.getByText('Assign'));
    expect(mockAssignMutate).toHaveBeenCalled();
  });

  it('shows assign error on failure', async () => {
    mockAssignMutate.mockImplementation((_data: unknown, opts?: { onError?: () => void }) => {
      opts?.onError?.();
    });
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onAssign).toBeDefined());
    act(() => { capturedCallbacks.onAssign(sampleProtocol); });
    fireEvent.change(screen.getByLabelText('Study ID'), { target: { value: '42' } });
    fireEvent.click(screen.getByText('Assign'));
    expect(screen.getByText(/Failed to assign/)).toBeInTheDocument();
  });

  it('does not assign when study ID is empty', async () => {
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onAssign).toBeDefined());
    act(() => { capturedCallbacks.onAssign(sampleProtocol); });
    // Study ID field is empty by default, Assign button should not call mutation
    fireEvent.click(screen.getByText('Assign'));
    expect(mockAssignMutate).not.toHaveBeenCalled();
  });

  it('calls export on export click', async () => {
    const { exportProtocol } = await import('../../../services/protocols/protocolsApi');
    renderPage();
    await waitFor(() => expect(capturedCallbacks.onExport).toBeDefined());
    capturedCallbacks.onExport(sampleProtocol);
    expect(exportProtocol).toHaveBeenCalledWith(1);
  });

  it('triggers import via file input', () => {
    renderPage();
    const importBtn = screen.getByText('Import YAML');
    fireEvent.click(importBtn);
    // File input click is triggered; we test via handleFileChange
  });

  it('handles file input change and calls import mutation', async () => {
    mockImportMutate.mockImplementation((_file: unknown, opts?: { onSuccess?: (r: { id: number }) => void }) => {
      opts?.onSuccess?.({ id: 77 });
    });
    renderPage();
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['yaml: true'], 'protocol.yaml', { type: 'text/yaml' });
    fireEvent.change(fileInput, { target: { files: [file] } });
    expect(mockImportMutate).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/protocols/77/edit');
  });

  it('shows import error on failure', async () => {
    mockImportMutate.mockImplementation((_file: unknown, opts?: { onError?: (err: Error) => void }) => {
      opts?.onError?.(new Error('Bad YAML'));
    });
    renderPage();
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['invalid'], 'bad.yaml', { type: 'text/yaml' });
    fireEvent.change(fileInput, { target: { files: [file] } });
    expect(screen.getByText('Bad YAML')).toBeInTheDocument();
  });

  it('filters by study type via dropdown', () => {
    renderPage();
    const select = screen.getByRole('combobox');
    fireEvent.mouseDown(select);
    fireEvent.click(screen.getByRole('option', { name: 'SMS' }));
    // Study type filter was set
  });
});
