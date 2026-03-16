/**
 * useColorMode — resolves a ThemePreference to a live MUI PaletteMode.
 *
 * For 'system', registers a matchMedia listener that re-fires whenever the
 * OS dark-mode preference changes and cleans up on unmount or pref change.
 */

import { useEffect, useState } from 'react';

import type { PaletteMode } from '@mui/material';

import type { ThemePreference } from '../theme/ThemeContext';

function resolvePref(pref: ThemePreference): PaletteMode {
  if (pref === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return pref;
}

/**
 * Returns the resolved MUI {@link PaletteMode} for the given preference.
 *
 * When `themePref` is `'system'`, the hook listens for OS-level
 * `prefers-color-scheme` changes and updates reactively.
 *
 * @param themePref - The user's stored three-way preference.
 * @returns `'light'` or `'dark'`.
 */
export function useColorMode(themePref: ThemePreference): PaletteMode {
  const [mode, setMode] = useState<PaletteMode>(() => resolvePref(themePref));

  useEffect(() => {
    setMode(resolvePref(themePref));

    if (themePref !== 'system') return;

    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => setMode(e.matches ? 'dark' : 'light');
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [themePref]);

  return mode;
}
