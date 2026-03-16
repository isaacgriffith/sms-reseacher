/**
 * Login page: left-1/3 login form, right-2/3 product infographic.
 * Redirects to /groups on success. Handles optional TOTP second step.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { ApiError } from '../../services/api';
import { loginUser } from '../../services/api';
import { setSession } from '../../services/auth';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';

interface LoginForm {
  email: string;
  password: string;
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  // TOTP second-step state
  const [partialToken, setPartialToken] = useState<string | null>(null);
  const [totpCode, setTotpCode] = useState('');
  const [totpPending, setTotpPending] = useState(false);

  const {
    register,
    handleSubmit,
    getValues,
    formState: { isSubmitting, errors },
  } = useForm<LoginForm>();

  // Step 1: credentials
  const onSubmit = async (data: LoginForm) => {
    setError(null);
    try {
      const result = await loginUser(data.email, data.password);
      if (result.type === 'totp_required') {
        setPartialToken(result.partial_token);
        return;
      }
      setSession(result.access_token, {
        id: result.user_id,
        email: data.email,
        displayName: result.display_name,
      });
      navigate('/groups', { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'An unexpected error occurred');
    }
  };

  // Step 2: TOTP code
  const onTotpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setTotpPending(true);
    try {
      const response = await fetch('/api/v1/auth/login/totp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ partial_token: partialToken, totp_code: totpCode }),
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const detail = (data as { detail?: string }).detail ?? response.statusText;
        if (response.status === 429) {
          setError(`Account temporarily locked. ${detail}`);
        } else {
          setError(detail);
        }
        return;
      }
      const data = await response.json() as {
        access_token: string;
        user_id: number;
        display_name: string;
      };
      setSession(data.access_token, {
        id: data.user_id,
        email: getValues('email'),
        displayName: data.display_name,
      });
      navigate('/groups', { replace: true });
    } catch {
      setError('An unexpected error occurred');
    } finally {
      setTotpPending(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Left panel — login form */}
      <Box
        sx={{
          width: '33%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '2rem',
          boxSizing: 'border-box',
          background: '#ffffff',
        }}
      >
        <Typography variant="h4" sx={{ marginBottom: '0.5rem' }}>SMS Researcher</Typography>
        <Typography sx={{ color: '#666', marginBottom: '2rem' }}>
          {partialToken ? 'Enter your authentication code' : 'Sign in to your account'}
        </Typography>

        {!partialToken ? (
          <Box component="form" onSubmit={handleSubmit(onSubmit)}>
            <Box sx={{ marginBottom: '1rem' }}>
              <TextField
                id="email"
                type="email"
                label="Email"
                fullWidth
                size="small"
                error={!!errors.email}
                helperText={errors.email?.message}
                {...register('email', { required: 'Email is required' })}
              />
            </Box>

            <Box sx={{ marginBottom: '1.5rem' }}>
              <TextField
                id="password"
                type="password"
                label="Password"
                fullWidth
                size="small"
                error={!!errors.password}
                helperText={errors.password?.message}
                {...register('password', { required: 'Password is required' })}
              />
            </Box>

            {error && (
              <Alert severity="error" sx={{ marginBottom: '1rem' }}>{error}</Alert>
            )}

            <Button
              type="submit"
              variant="contained"
              disabled={isSubmitting}
              fullWidth
              sx={{ padding: '0.75rem', fontSize: '1rem' }}
            >
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </Button>
          </Box>
        ) : (
          <Box component="form" onSubmit={(e) => void onTotpSubmit(e)}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Open your authenticator app and enter the 6-digit code for SMS Researcher.
              You can also enter a 10-character backup code.
            </Typography>

            <TextField
              label="Authentication code"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              fullWidth
              size="small"
              inputProps={{ maxLength: 10, autoComplete: 'one-time-code' }}
              autoFocus
              sx={{ mb: 1.5 }}
            />

            {error && (
              <Alert severity="error" sx={{ marginBottom: '1rem' }}>{error}</Alert>
            )}

            <Button
              type="submit"
              variant="contained"
              disabled={totpPending || totpCode.length < 6}
              fullWidth
              sx={{ padding: '0.75rem', fontSize: '1rem' }}
            >
              {totpPending ? 'Verifying…' : 'Verify'}
            </Button>

            <Button
              variant="text"
              size="small"
              onClick={() => { setPartialToken(null); setError(null); setTotpCode(''); }}
              sx={{ mt: 1 }}
            >
              Back to sign in
            </Button>
          </Box>
        )}
      </Box>

      {/* Right panel — product infographic */}
      <Box
        sx={{
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
        <Typography variant="h4" sx={{ fontSize: '2rem', marginBottom: '1rem' }}>Systematic Mapping Studies</Typography>
        <Typography sx={{ fontSize: '1.125rem', textAlign: 'center', maxWidth: '480px', lineHeight: 1.6 }}>
          AI-augmented research automation — guide your team through study scoping, database
          search, paper screening, data extraction, and publication-ready visualisations.
        </Typography>
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
      </Box>
    </Box>
  );
}
