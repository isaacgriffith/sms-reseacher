import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';

import ThemeSelector from './ThemeSelector';
import * as ThemeContextModule from '../../theme/ThemeContext';

// Stub ThemeContext so ThemeSelector can render without a real ThemeProvider
const stubCtx = {
  mode: 'light' as const,
  preference: 'light' as const,
  setThemePreference: vi.fn(),
};

vi.spyOn(ThemeContextModule, 'useThemeContext').mockReturnValue(stubCtx);

// ThemeSelector accepts optional `value` / `onChange` props that override context
describe('ThemeSelector', () => {
  it('renders all three option labels', () => {
    render(<ThemeSelector value="light" onChange={vi.fn()} />);
    expect(screen.getByRole('button', { name: /^Light$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Dark$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /System Default/i })).toBeInTheDocument();
  });

  it('highlights the active preference via aria-pressed', () => {
    render(<ThemeSelector value="dark" onChange={vi.fn()} />);
    expect(screen.getByRole('button', { name: /^Dark$/i })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: /^Light$/i })).toHaveAttribute('aria-pressed', 'false');
  });

  it('calls onChange with "dark" when Dark is clicked', async () => {
    const onChange = vi.fn();
    render(<ThemeSelector value="light" onChange={onChange} />);
    await userEvent.click(screen.getByRole('button', { name: /^Dark$/i }));
    expect(onChange).toHaveBeenCalledWith('dark');
  });

  it('calls onChange with "system" when System Default is clicked', async () => {
    const onChange = vi.fn();
    render(<ThemeSelector value="light" onChange={onChange} />);
    await userEvent.click(screen.getByRole('button', { name: /System Default/i }));
    expect(onChange).toHaveBeenCalledWith('system');
  });

  it('does not call onChange when already-selected option is clicked', async () => {
    const onChange = vi.fn();
    render(<ThemeSelector value="light" onChange={onChange} />);
    await userEvent.click(screen.getByRole('button', { name: /^Light$/i }));
    expect(onChange).not.toHaveBeenCalled();
  });
});
