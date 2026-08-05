import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('../api', () => ({
  api: {
    get: vi.fn(),
    put: vi.fn(),
    post: vi.fn(),
  },
  ApiError: class extends Error {
    status: number;
    detail: string;
    constructor(status: number, detail: string) {
      super(detail);
      this.status = status;
      this.detail = detail;
    }
  },
}));

import { api, ApiError } from '../api';
import {
  getPreferences,
  updateTheme,
  setup2fa,
  confirm2fa,
  disable2fa,
  regenerateBackupCodes,
  changePassword,
} from '../preferences';

describe('preferences service', () => {
  beforeEach(() => vi.clearAllMocks());

  it('getPreferences parses response', async () => {
    vi.mocked(api.get).mockResolvedValue({ theme_preference: 'dark', totp_enabled: false });
    const result = await getPreferences();
    expect(result).toEqual({ theme_preference: 'dark', totp_enabled: false });
  });

  it('updateTheme calls PUT', async () => {
    vi.mocked(api.put).mockResolvedValue({});
    await updateTheme('light');
    expect(api.put).toHaveBeenCalledWith('/api/v1/me/preferences/theme', { theme: 'light' });
  });

  it('setup2fa returns parsed data', async () => {
    vi.mocked(api.post).mockResolvedValue({
      qr_code_image: 'img',
      manual_key: 'key',
      issuer: 'iss',
    });
    const result = await setup2fa();
    expect(result.manual_key).toBe('key');
  });

  it('confirm2fa returns backup codes', async () => {
    vi.mocked(api.post).mockResolvedValue({ backup_codes: ['abc'] });
    const result = await confirm2fa('123456');
    expect(result.backup_codes).toEqual(['abc']);
  });

  it('disable2fa calls POST', async () => {
    vi.mocked(api.post).mockResolvedValue({});
    await disable2fa('pass', '123456');
    expect(api.post).toHaveBeenCalledWith('/api/v1/me/2fa/disable', {
      password: 'pass',
      totp_code: '123456',
    });
  });

  it('regenerateBackupCodes returns codes', async () => {
    vi.mocked(api.post).mockResolvedValue({ backup_codes: ['x', 'y'] });
    const result = await regenerateBackupCodes('pass', '123456');
    expect(result.backup_codes).toHaveLength(2);
  });

  it('changePassword calls PUT', async () => {
    vi.mocked(api.put).mockResolvedValue({ message: 'ok' });
    await changePassword('old', 'new');
    expect(api.put).toHaveBeenCalledWith('/api/v1/me/password', {
      current_password: 'old',
      new_password: 'new',
    });
  });

  it('changePassword rethrows ApiError with detail', async () => {
    vi.mocked(api.put).mockRejectedValue(new ApiError(400, 'wrong password'));
    await expect(changePassword('old', 'new')).rejects.toThrow('wrong password');
  });
});
