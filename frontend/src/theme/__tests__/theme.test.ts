/**
 * Unit tests for createAppTheme.
 */

import { describe, it, expect } from 'vitest';
import { createAppTheme } from '../theme';

describe('createAppTheme', () => {
  it('creates a light theme', () => {
    const theme = createAppTheme('light');
    expect(theme.palette.mode).toBe('light');
    expect(theme.palette.primary.main).toBe('#1976d2');
    expect(theme.palette.secondary.main).toBe('#9c27b0');
  });

  it('creates a dark theme', () => {
    const theme = createAppTheme('dark');
    expect(theme.palette.mode).toBe('dark');
    expect(theme.palette.primary.main).toBe('#1976d2');
  });

  it('returns different theme objects for different modes', () => {
    const light = createAppTheme('light');
    const dark = createAppTheme('dark');
    expect(light.palette.mode).not.toBe(dark.palette.mode);
  });
});
