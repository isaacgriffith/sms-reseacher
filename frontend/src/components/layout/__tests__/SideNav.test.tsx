/**
 * Unit tests for SideNav component.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import SideNav from '../SideNav';
import { useAuthStore, clearSession } from '../../../services/auth';

vi.mock('../../../services/auth', () => ({
  useAuthStore: vi.fn(),
  clearSession: vi.fn(),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

describe('SideNav', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuthStore).mockReturnValue({ displayName: 'Alice Smith' });
  });

  it('renders navigation links', () => {
    render(
      <MemoryRouter>
        <SideNav />
      </MemoryRouter>,
    );
    expect(screen.getByText('Research Groups')).toBeInTheDocument();
    expect(screen.getByText('Preferences')).toBeInTheDocument();
    expect(screen.getByText('API Docs')).toBeInTheDocument();
  });

  it('shows user initials in avatar', () => {
    render(
      <MemoryRouter>
        <SideNav />
      </MemoryRouter>,
    );
    expect(screen.getByText('AS')).toBeInTheDocument();
  });

  it('shows display name', () => {
    render(
      <MemoryRouter>
        <SideNav />
      </MemoryRouter>,
    );
    expect(screen.getByText('Alice Smith')).toBeInTheDocument();
  });

  it('shows ? when no user', () => {
    vi.mocked(useAuthStore).mockReturnValue(null);
    render(
      <MemoryRouter>
        <SideNav />
      </MemoryRouter>,
    );
    expect(screen.getByText('?')).toBeInTheDocument();
  });

  it('renders active style for matching route', () => {
    vi.mocked(useAuthStore).mockReturnValue({ displayName: 'Alice' });
    // Render at /groups so the Research Groups link is active
    render(
      <MemoryRouter initialEntries={['/groups']}>
        <SideNav />
      </MemoryRouter>,
    );
    expect(screen.getByText('Research Groups')).toBeInTheDocument();
  });

  it('calls clearSession and navigates on sign out', () => {
    render(
      <MemoryRouter>
        <SideNav />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByRole('button', { name: /sign out/i }));
    expect(clearSession).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true });
  });
});
