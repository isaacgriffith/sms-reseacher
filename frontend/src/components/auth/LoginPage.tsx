/**
 * Login page: left-1/3 login form, right-2/3 product infographic.
 * Redirects to /groups on success.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { api, ApiError } from '../../services/api';
import { setSession } from '../../services/auth';

interface LoginForm {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  display_name: string;
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { isSubmitting, errors },
  } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    setError(null);
    try {
      const resp = await api.post<LoginResponse>(
        '/api/v1/auth/login',
        { email: data.email, password: data.password },
        false,
      );
      setSession(resp.access_token, {
        id: resp.user_id,
        email: data.email,
        displayName: resp.display_name,
      });
      navigate('/groups', { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('An unexpected error occurred');
      }
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Left panel — login form */}
      <div
        style={{
          width: '33%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '2rem',
          boxSizing: 'border-box',
          background: '#ffffff',
        }}
      >
        <h1 style={{ marginBottom: '0.5rem' }}>SMS Researcher</h1>
        <p style={{ color: '#666', marginBottom: '2rem' }}>Sign in to your account</p>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="email" style={{ display: 'block', marginBottom: '0.25rem' }}>
              Email
            </label>
            <input
              id="email"
              type="email"
              style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
              {...register('email', { required: 'Email is required' })}
            />
            {errors.email && (
              <span style={{ color: 'red', fontSize: '0.875rem' }}>{errors.email.message}</span>
            )}
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="password" style={{ display: 'block', marginBottom: '0.25rem' }}>
              Password
            </label>
            <input
              id="password"
              type="password"
              style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
              {...register('password', { required: 'Password is required' })}
            />
            {errors.password && (
              <span style={{ color: 'red', fontSize: '0.875rem' }}>{errors.password.message}</span>
            )}
          </div>

          {error && (
            <p style={{ color: 'red', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '0.75rem',
              background: '#2563eb',
              color: '#fff',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              fontSize: '1rem',
            }}
          >
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>

      {/* Right panel — product infographic */}
      <div
        style={{
          width: '67%',
          background: 'linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          padding: '3rem',
          boxSizing: 'border-box',
        }}
      >
        <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Systematic Mapping Studies</h2>
        <p style={{ fontSize: '1.125rem', textAlign: 'center', maxWidth: '480px', lineHeight: 1.6 }}>
          AI-augmented research automation — guide your team through study scoping, database
          search, paper screening, data extraction, and publication-ready visualisations.
        </p>
        <ul
          style={{
            marginTop: '2rem',
            listStyle: 'none',
            padding: 0,
            fontSize: '1rem',
            lineHeight: 2,
          }}
        >
          <li>✓ PICO/C study scoping with AI suggestions</li>
          <li>✓ Search string builder with test-retest recall</li>
          <li>✓ Automated paper screening &amp; snowball sampling</li>
          <li>✓ Structured data extraction with audit trail</li>
          <li>✓ SVG charts &amp; interactive domain model</li>
        </ul>
      </div>
    </div>
  );
}
