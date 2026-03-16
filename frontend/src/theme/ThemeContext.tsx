import React, { createContext, useCallback, useContext, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import type { PaletteMode } from '@mui/material';

import { useColorMode } from '../hooks/useColorMode';
import { updateUserFields, useAuthStore } from '../services/auth';
import { updateTheme } from '../services/preferences';
import { createAppTheme } from './theme';

/** The three-way user preference stored in the database. */
export type ThemePreference = 'light' | 'dark' | 'system';

interface ThemeContextValue {
  /** Resolved MUI palette mode in use right now ('light' | 'dark'). */
  mode: PaletteMode;
  /** The user's raw three-way preference. */
  preference: ThemePreference;
  /** Persist and apply a new theme preference. */
  setThemePreference: (pref: ThemePreference) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

interface ThemeProviderProps {
  /** Fallback preference before the user is authenticated. */
  initialPreference?: ThemePreference;
  children: React.ReactNode;
}

/**
 * Wraps the application with an MUI ThemeProvider and CssBaseline.
 *
 * Reads `theme_preference` from the auth store (stored on login via `/auth/me`).
 * Falls back to `initialPreference` when no user is authenticated.
 * `setThemePreference` persists to `PUT /api/v1/me/preferences/theme` and
 * updates the local auth store so the preference survives page refresh.
 *
 * @param props - Component props.
 */
export function ThemeProvider({ initialPreference = 'light', children }: ThemeProviderProps) {
  const storedPref = useAuthStore((s) => s.user?.themePreference);
  const preference: ThemePreference = storedPref ?? initialPreference;

  const mode = useColorMode(preference);
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  const setThemePreference = useCallback((pref: ThemePreference) => {
    updateUserFields({ themePreference: pref });
    // Best-effort API persist; ignore errors (e.g. unauthenticated)
    updateTheme(pref).catch(() => undefined);
  }, []);

  const value = useMemo<ThemeContextValue>(
    () => ({ mode, preference, setThemePreference }),
    [mode, preference, setThemePreference],
  );

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
}

/**
 * Returns the current theme context value.
 *
 * @throws {Error} If called outside of a {@link ThemeProvider}.
 */
export function useThemeContext(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error('useThemeContext must be used within a ThemeProvider');
  }
  return ctx;
}
