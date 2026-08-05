import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import PasswordChangeForm from '../PasswordChangeForm';

vi.mock('../../../services/api', () => ({
  api: { post: vi.fn().mockResolvedValue({}) },
  ApiError: class extends Error {
    detail: string;
    constructor(_s: number, d: string) {
      super(d);
      this.detail = d;
    }
  },
}));

describe('PasswordChangeForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all password fields', () => {
    render(React.createElement(PasswordChangeForm));
    expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
    expect(screen.getByLabelText('New password')).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm new password/i)).toBeInTheDocument();
  });

  it('renders the change password button', () => {
    render(React.createElement(PasswordChangeForm));
    expect(screen.getByRole('button', { name: /change password/i })).toBeInTheDocument();
  });
});
