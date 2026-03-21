/**
 * Unit tests for LoginPage component.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';
import { loginUser, ApiError } from '../../../services/api';
import { setSession } from '../../../services/auth';

vi.mock('../../../services/api', () => ({
  loginUser: vi.fn(),
  ApiError: class ApiError extends Error {
    detail: string;
    constructor(detail: string) {
      super(detail);
      this.detail = detail;
    }
  },
}));
vi.mock('../../../services/auth', () => ({ setSession: vi.fn() }));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderLogin() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

describe('LoginPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders sign-in form', () => {
    renderLogin();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('navigates to /groups on successful login', async () => {
    vi.mocked(loginUser).mockResolvedValue({
      type: 'token',
      access_token: 'tok',
      user_id: 1,
      display_name: 'Alice',
    } as Awaited<ReturnType<typeof loginUser>>);
    renderLogin();
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form')!);
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/groups', { replace: true }));
    expect(setSession).toHaveBeenCalled();
  });

  it('shows error message on failed login', async () => {
    const ApiErrorClass = (await import('../../../services/api')).ApiError as typeof ApiError;
    vi.mocked(loginUser).mockRejectedValue(new ApiErrorClass('Invalid credentials'));
    renderLogin();
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrong' } });
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form')!);
    await waitFor(() => expect(screen.getByText('Invalid credentials')).toBeInTheDocument());
  });

  it('shows TOTP form when totp_required', async () => {
    vi.mocked(loginUser).mockResolvedValue({
      type: 'totp_required',
      partial_token: 'partial-tok',
    } as Awaited<ReturnType<typeof loginUser>>);
    renderLogin();
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form')!);
    await waitFor(() =>
      expect(screen.getByLabelText(/authentication code/i)).toBeInTheDocument(),
    );
  });

  it('shows error for unexpected non-api errors', async () => {
    vi.mocked(loginUser).mockRejectedValue(new Error('Network failure'));
    renderLogin();
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form')!);
    await waitFor(() =>
      expect(screen.getByText(/an unexpected error occurred/i)).toBeInTheDocument(),
    );
  });

  it('navigates to /groups after successful TOTP verification', async () => {
    vi.mocked(loginUser).mockResolvedValue({
      type: 'totp_required',
      partial_token: 'partial-tok',
    } as Awaited<ReturnType<typeof loginUser>>);
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: 'full-tok',
        user_id: 1,
        display_name: 'Alice',
      }),
    });
    vi.stubGlobal('fetch', mockFetch);
    renderLogin();
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form')!);
    await waitFor(() => expect(screen.getByLabelText(/authentication code/i)).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText(/authentication code/i), {
      target: { value: '123456' },
    });
    fireEvent.submit(screen.getByRole('button', { name: /verify/i }).closest('form')!);
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/groups', { replace: true }));
    vi.unstubAllGlobals();
  });

  it('shows error when TOTP verification fails', async () => {
    vi.mocked(loginUser).mockResolvedValue({
      type: 'totp_required',
      partial_token: 'partial-tok',
    } as Awaited<ReturnType<typeof loginUser>>);
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      json: async () => ({ detail: 'Invalid code' }),
    });
    vi.stubGlobal('fetch', mockFetch);
    renderLogin();
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form')!);
    await waitFor(() => expect(screen.getByLabelText(/authentication code/i)).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText(/authentication code/i), {
      target: { value: '999999' },
    });
    fireEvent.submit(screen.getByRole('button', { name: /verify/i }).closest('form')!);
    await waitFor(() => expect(screen.getByText('Invalid code')).toBeInTheDocument());
    vi.unstubAllGlobals();
  });

  it('shows account locked message on 429 TOTP response', async () => {
    vi.mocked(loginUser).mockResolvedValue({
      type: 'totp_required',
      partial_token: 'partial-tok',
    } as Awaited<ReturnType<typeof loginUser>>);
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
      statusText: 'Too Many Requests',
      json: async () => ({ detail: 'Too many attempts' }),
    });
    vi.stubGlobal('fetch', mockFetch);
    renderLogin();
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form')!);
    await waitFor(() => expect(screen.getByLabelText(/authentication code/i)).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText(/authentication code/i), {
      target: { value: '999999' },
    });
    fireEvent.submit(screen.getByRole('button', { name: /verify/i }).closest('form')!);
    await waitFor(() => expect(screen.getByText(/account temporarily locked/i)).toBeInTheDocument());
    vi.unstubAllGlobals();
  });

  it('goes back to sign-in form from TOTP screen', async () => {
    vi.mocked(loginUser).mockResolvedValue({
      type: 'totp_required',
      partial_token: 'partial-tok',
    } as Awaited<ReturnType<typeof loginUser>>);
    renderLogin();
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form')!);
    await waitFor(() => expect(screen.getByText(/back to sign in/i)).toBeInTheDocument());
    fireEvent.click(screen.getByText(/back to sign in/i));
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });
});
