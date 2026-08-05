import { describe, it, expect, vi } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import React from 'react';
import { ThemeProvider, useThemeContext } from '../ThemeContext';

vi.mock('../../hooks/useColorMode', () => ({
  useColorMode: vi.fn().mockReturnValue('light'),
}));

vi.mock('../../services/auth', () => ({
  useAuthStore: vi.fn((selector: (s: { user: null }) => unknown) => selector({ user: null })),
  updateUserFields: vi.fn(),
}));

vi.mock('../../services/preferences', () => ({
  updateTheme: vi.fn().mockResolvedValue(undefined),
}));

function Consumer() {
  const { mode, preference, setThemePreference } = useThemeContext();
  return React.createElement('div', null, [
    React.createElement('span', { key: 'mode', 'data-testid': 'mode' }, mode),
    React.createElement('span', { key: 'pref', 'data-testid': 'pref' }, preference),
    React.createElement(
      'button',
      { key: 'btn', onClick: () => setThemePreference('dark') },
      'Switch',
    ),
  ]);
}

describe('ThemeProvider', () => {
  it('provides mode and preference', () => {
    render(
      React.createElement(ThemeProvider, {
        initialPreference: 'light',
        children: React.createElement(Consumer),
      }),
    );
    expect(screen.getByTestId('mode').textContent).toBe('light');
    expect(screen.getByTestId('pref').textContent).toBe('light');
  });

  it('calls setThemePreference', async () => {
    const { updateUserFields } = await import('../../services/auth');
    render(React.createElement(ThemeProvider, null, React.createElement(Consumer)));
    act(() => {
      screen.getByText('Switch').click();
    });
    expect(updateUserFields).toHaveBeenCalledWith({ themePreference: 'dark' });
  });
});

describe('useThemeContext', () => {
  it('throws outside provider', () => {
    expect(() => {
      render(React.createElement(Consumer));
    }).toThrow('useThemeContext must be used within a ThemeProvider');
  });
});
