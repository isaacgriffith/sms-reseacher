import { createTheme, Theme } from '@mui/material/styles';
import type { PaletteMode } from '@mui/material';

/**
 * Creates an MUI Theme for the given palette mode.
 *
 * @param mode - `'light'` or `'dark'` — determines the colour scheme.
 * @returns A fully configured MUI {@link Theme}.
 */
export function createAppTheme(mode: PaletteMode): Theme {
  return createTheme({
    palette: {
      mode,
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#9c27b0',
      },
    },
    typography: {
      fontFamily: [
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
      ].join(','),
    },
  });
}
