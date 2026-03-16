/**
 * Tests for TwoFactorSettings status/enable/disable/regenerate panel.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import TwoFactorSettings from './TwoFactorSettings';
import * as prefs from '../../services/preferences';

function wrap(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

beforeEach(() => {
  vi.restoreAllMocks();
});

describe('TwoFactorSettings — disabled state', () => {
  it('shows Disabled chip and Enable 2FA button', () => {
    wrap(<TwoFactorSettings totpEnabled={false} onStatusChange={vi.fn()} />);
    expect(screen.getByText('Disabled')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /enable 2fa/i })).toBeInTheDocument();
  });
});

describe('TwoFactorSettings — enabled state', () => {
  it('shows Enabled chip', () => {
    wrap(<TwoFactorSettings totpEnabled={true} onStatusChange={vi.fn()} />);
    expect(screen.getByText('Enabled')).toBeInTheDocument();
  });

  it('calls disable2fa and onStatusChange on successful disable', async () => {
    const onStatusChange = vi.fn();
    vi.spyOn(prefs, 'disable2fa').mockResolvedValue(undefined);
    wrap(<TwoFactorSettings totpEnabled={true} onStatusChange={onStatusChange} />);

    const [pwField] = screen.getAllByLabelText(/current password/i);
    const [codeField] = screen.getAllByLabelText(/authenticator code/i);
    fireEvent.change(pwField, { target: { value: 'Password123!' } });
    fireEvent.change(codeField, { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: /disable 2fa/i }));

    await waitFor(() => expect(prefs.disable2fa).toHaveBeenCalledWith('Password123!', '123456'));
    expect(onStatusChange).toHaveBeenCalledOnce();
  });

  it('shows error when disable fails', async () => {
    vi.spyOn(prefs, 'disable2fa').mockRejectedValue(new Error('Invalid TOTP code'));
    wrap(<TwoFactorSettings totpEnabled={true} onStatusChange={vi.fn()} />);

    const [pwField] = screen.getAllByLabelText(/current password/i);
    const [codeField] = screen.getAllByLabelText(/authenticator code/i);
    fireEvent.change(pwField, { target: { value: 'Password123!' } });
    fireEvent.change(codeField, { target: { value: '000000' } });
    fireEvent.click(screen.getByRole('button', { name: /disable 2fa/i }));

    await waitFor(() =>
      expect(screen.getAllByText(/invalid totp code/i).length).toBeGreaterThan(0),
    );
  });

  it('shows new backup codes after regeneration', async () => {
    vi.spyOn(prefs, 'regenerateBackupCodes').mockResolvedValue({
      backup_codes: ['NEWCODE0001', 'NEWCODE0002'],
    });
    wrap(<TwoFactorSettings totpEnabled={true} onStatusChange={vi.fn()} />);

    const pwFields = screen.getAllByLabelText(/current password/i);
    const codeFields = screen.getAllByLabelText(/authenticator code/i);
    // Use second form (regen)
    fireEvent.change(pwFields[1], { target: { value: 'Password123!' } });
    fireEvent.change(codeFields[1], { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: /regenerate codes/i }));

    await waitFor(() =>
      expect(screen.getByText('NEWCODE0001')).toBeInTheDocument(),
    );
  });
});
