/**
 * PICO/C form with variant selector, text areas per component,
 * and "Refine with AI" button.
 */

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { api, ApiError } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

interface PICOData {
  variant: string;
  population: string;
  intervention: string;
  comparison: string;
  outcome: string;
  context: string;
}

interface PICOComponent {
  id: number;
  study_id: number;
  variant: string;
  population: string | null;
  intervention: string | null;
  comparison: string | null;
  outcome: string | null;
  context: string | null;
  extra_fields: Record<string, unknown> | null;
  ai_suggestions: Record<string, string[]> | null;
  updated_at: string;
}

interface Props {
  studyId: number;
}

const VARIANTS = ['PICO', 'PICOS', 'PICOT', 'SPIDER', 'PCC'];

const COMPONENT_LABELS: Record<string, string> = {
  population: 'Population',
  intervention: 'Intervention / Phenomenon of Interest',
  comparison: 'Comparison',
  outcome: 'Outcome',
  context: 'Context / Setting',
};

export default function PICOForm({ studyId }: Props) {
  const [pico, setPico] = useState<PICOComponent | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [refining, setRefining] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<Record<string, string[]>>({});

  const { register, handleSubmit, watch, reset } = useForm<PICOData>({
    defaultValues: { variant: 'PICO' },
  });

  const variant = watch('variant');

  useEffect(() => {
    api
      .get<PICOComponent>(`/api/v1/studies/${studyId}/pico`)
      .then((data) => {
        setPico(data);
        reset({
          variant: data.variant,
          population: data.population ?? '',
          intervention: data.intervention ?? '',
          comparison: data.comparison ?? '',
          outcome: data.outcome ?? '',
          context: data.context ?? '',
        });
        if (data.ai_suggestions) setSuggestions(data.ai_suggestions);
      })
      .catch(() => {
        /* 404 means not yet created — that's fine */
      })
      .finally(() => setLoading(false));
  }, [studyId]);

  const onSubmit = handleSubmit(async (data) => {
    setSaveError(null);
    setSaving(true);
    try {
      const saved = await api.put<PICOComponent>(`/api/v1/studies/${studyId}/pico`, {
        variant: data.variant,
        population: data.population || null,
        intervention: data.intervention || null,
        comparison: data.comparison || null,
        outcome: data.outcome || null,
        context: data.context || null,
      });
      setPico(saved);
    } catch (err) {
      setSaveError(err instanceof ApiError ? err.detail : 'Failed to save PICO/C');
    } finally {
      setSaving(false);
    }
  });

  const handleRefine = async (component: string) => {
    setRefining(component);
    try {
      const result = await api.post<{ suggestions: string[] }>(
        `/api/v1/studies/${studyId}/pico/refine`,
        { component },
      );
      setSuggestions((s) => ({ ...s, [component]: result.suggestions }));
    } catch {
      // ignore — suggestions stay empty
    } finally {
      setRefining(null);
    }
  };

  if (loading) return <Typography>Loading PICO/C…</Typography>;

  return (
    <Box>
      <Typography variant="h6" sx={{ margin: '0 0 1rem' }}>PICO/C Framework</Typography>

      <form onSubmit={onSubmit}>
        {/* Variant selector */}
        <Box sx={{ marginBottom: '1.5rem' }}>
          <Typography component="label" sx={{ display: 'block', fontWeight: 500, marginBottom: '0.5rem' }}>
            Framework variant
          </Typography>
          <Box sx={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {VARIANTS.map((v) => (
              <label
                key={v}
                style={{
                  padding: '0.375rem 0.875rem',
                  border: `2px solid ${variant === v ? '#2563eb' : '#e2e8f0'}`,
                  borderRadius: '9999px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  background: variant === v ? '#eff6ff' : '#fff',
                  color: variant === v ? '#1d4ed8' : '#374151',
                }}
              >
                <input type="radio" value={v} {...register('variant')} style={{ display: 'none' }} />
                {v}
              </label>
            ))}
          </Box>
        </Box>

        {/* Component fields */}
        {Object.entries(COMPONENT_LABELS).map(([key, label]) => (
          <Box key={key} sx={{ marginBottom: '1.25rem' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
              <Typography component="label" sx={{ fontWeight: 500, fontSize: '0.9rem' }}>{label}</Typography>
              <Button
                type="button"
                variant="outlined"
                size="small"
                onClick={() => handleRefine(key)}
                disabled={refining === key}
                sx={{
                  padding: '0.2rem 0.6rem',
                  fontSize: '0.75rem',
                  borderColor: '#2563eb',
                  color: '#2563eb',
                }}
              >
                {refining === key ? 'Refining…' : '✨ Refine with AI'}
              </Button>
            </Box>
            <textarea
              rows={3}
              style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box', borderRadius: '0.25rem', border: '1px solid #cbd5e1', resize: 'vertical' }}
              {...register(key as keyof PICOData)}
            />
            {suggestions[key] && suggestions[key].length > 0 && (
              <Box sx={{ marginTop: '0.5rem', padding: '0.75rem', background: '#f0f9ff', borderRadius: '0.375rem', fontSize: '0.875rem' }}>
                <Typography sx={{ margin: '0 0 0.5rem', fontWeight: 500, color: '#0369a1' }}>AI suggestions:</Typography>
                <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                  {suggestions[key].map((s, i) => <li key={i} style={{ marginBottom: '0.25rem' }}>{s}</li>)}
                </ul>
              </Box>
            )}
          </Box>
        ))}

        {saveError && <Typography sx={{ color: 'red', fontSize: '0.875rem' }}>{saveError}</Typography>}

        <Button
          type="submit"
          variant="contained"
          disabled={saving}
          sx={{ padding: '0.625rem 1.5rem', fontSize: '1rem' }}
        >
          {saving ? 'Saving…' : pico ? 'Update PICO/C' : 'Save PICO/C'}
        </Button>

        {pico && (
          <Typography component="span" sx={{ marginLeft: '0.75rem', color: '#16a34a', fontSize: '0.875rem' }}>
            ✓ Saved — Phase 2 unlocked
          </Typography>
        )}
      </form>
    </Box>
  );
}
