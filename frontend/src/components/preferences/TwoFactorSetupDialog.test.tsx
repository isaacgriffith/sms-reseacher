/**
 * Tests for TwoFactorSetupDialog multi-step flow.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import TwoFactorSetupDialog from './TwoFactorSetupDialog';
import * as prefs from '../../services/preferences';

const SETUP_DATA: prefs.TotpSetupData = {
  qr_code_image: 'abc123',
  manual_key: 'JBSWY3DPEHPK3PXP',
  issuer: 'SMS Researcher',
};

function wrap(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

beforeEach(() => {
  vi.restoreAllMocks();
});

describe('TwoFactorSetupDialog', () => {
  it('shows Enable 2FA button initially', () => {
    wrap(<TwoFactorSetupDialog onEnabled={vi.fn()} />);
    expect(screen.getByRole('button', { name: /enable 2fa/i })).toBeInTheDocument();
  });

  it('opens QR step after setup mutation succeeds', async () => {
    vi.spyOn(prefs, 'setup2fa').mockResolvedValue(SETUP_DATA);
    wrap(<TwoFactorSetupDialog onEnabled={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /enable 2fa/i }));
    await waitFor(() =>
      expect(screen.getByAltText('TOTP QR code')).toBeInTheDocument(),
    );
    expect(screen.getByLabelText('manual key')).toHaveTextContent(SETUP_DATA.manual_key);
  });

  it('advances to code entry on Next', async () => {
    vi.spyOn(prefs, 'setup2fa').mockResolvedValue(SETUP_DATA);
    wrap(<TwoFactorSetupDialog onEnabled={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /enable 2fa/i }));
    await waitFor(() => screen.getByAltText('TOTP QR code'));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByLabelText(/authentication code/i)).toBeInTheDocument();
  });

  it('shows backup codes after confirm mutation succeeds', async () => {
    vi.spyOn(prefs, 'setup2fa').mockResolvedValue(SETUP_DATA);
    vi.spyOn(prefs, 'confirm2fa').mockResolvedValue({ backup_codes: ['AAAA111111', 'BBBB222222'] });
    wrap(<TwoFactorSetupDialog onEnabled={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /enable 2fa/i }));
    await waitFor(() => screen.getByAltText('TOTP QR code'));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    const input = screen.getByLabelText(/authentication code/i);
    fireEvent.change(input, { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: /verify/i }));
    await waitFor(() =>
      expect(screen.getByText('AAAA111111')).toBeInTheDocument(),
    );
  });

  it('calls onEnabled and closes dialog after acknowledging backup codes', async () => {
    const onEnabled = vi.fn();
    vi.spyOn(prefs, 'setup2fa').mockResolvedValue(SETUP_DATA);
    vi.spyOn(prefs, 'confirm2fa').mockResolvedValue({ backup_codes: ['AAAA111111'] });
    wrap(<TwoFactorSetupDialog onEnabled={onEnabled} />);
    fireEvent.click(screen.getByRole('button', { name: /enable 2fa/i }));
    await waitFor(() => screen.getByAltText('TOTP QR code'));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    const input = screen.getByLabelText(/authentication code/i);
    fireEvent.change(input, { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: /verify/i }));
    await waitFor(() => screen.getByText('AAAA111111'));
    fireEvent.click(screen.getByRole('button', { name: /i have saved/i }));
    expect(onEnabled).toHaveBeenCalledOnce();
  });

  it('shows error message when confirm fails', async () => {
    vi.spyOn(prefs, 'setup2fa').mockResolvedValue(SETUP_DATA);
    vi.spyOn(prefs, 'confirm2fa').mockRejectedValue(new Error('Invalid TOTP code'));
    wrap(<TwoFactorSetupDialog onEnabled={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /enable 2fa/i }));
    await waitFor(() => screen.getByAltText('TOTP QR code'));
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    const input = screen.getByLabelText(/authentication code/i);
    fireEvent.change(input, { target: { value: '000000' } });
    fireEvent.click(screen.getByRole('button', { name: /verify/i }));
    await waitFor(() =>
      expect(screen.getByText(/invalid totp code/i)).toBeInTheDocument(),
    );
  });
});
