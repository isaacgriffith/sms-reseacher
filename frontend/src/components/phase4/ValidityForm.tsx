/**
 * ValidityForm: six text areas for the study validity discussion dimensions.
 *
 * - Auto-saves each field on blur using react-hook-form register + onBlur.
 * - "Generate with AI" button enqueues the validity prefill ARQ job.
 *
 * ⚠️ Principle IX compliance: uses register() + onBlur for auto-save.
 *    The watch() function from useForm() is NOT imported or called.
 *    If cross-field reactive logic is needed, use useWatch() on specific fields only.
 */

import { useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { api } from '../../services/api';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ValidityFormValues {
  descriptive: string;
  theoretical: string;
  generalizability_internal: string;
  generalizability_external: string;
  interpretive: string;
  repeatability: string;
}

interface ValidityData {
  descriptive: string | null;
  theoretical: string | null;
  generalizability_internal: string | null;
  generalizability_external: string | null;
  interpretive: string | null;
  repeatability: string | null;
}

interface ValidityFormProps {
  studyId: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DIMS: Array<{ field: keyof ValidityFormValues; label: string; hint: string }> = [
  {
    field: 'descriptive',
    label: 'Descriptive Validity',
    hint: 'Accuracy of observations — does extracted data faithfully represent the papers?',
  },
  {
    field: 'theoretical',
    label: 'Theoretical Validity',
    hint: 'Accuracy of interpretation — does the conceptual model reflect the phenomena?',
  },
  {
    field: 'generalizability_internal',
    label: 'Generalizability (Internal)',
    hint: 'Do the conclusions apply to all papers in the corpus, not just a subset?',
  },
  {
    field: 'generalizability_external',
    label: 'Generalizability (External)',
    hint: 'Do the conclusions extend beyond the included papers to the broader domain?',
  },
  {
    field: 'interpretive',
    label: 'Interpretive Validity',
    hint: 'Are the conclusions logically supported by the evidence in the data?',
  },
  {
    field: 'repeatability',
    label: 'Repeatability',
    hint: 'Could another researcher replicate this study and reach similar conclusions?',
  },
];

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function ValidityForm({ studyId }: ValidityFormProps) {
  const { register, reset, formState } = useForm<ValidityFormValues>({
    defaultValues: {
      descriptive: '',
      theoretical: '',
      generalizability_internal: '',
      generalizability_external: '',
      interpretive: '',
      repeatability: '',
    },
  });

  const savingRef = useRef<Record<string, boolean>>({});
  const errorRef = useRef<string | null>(null);
  const generatingRef = useRef(false);

  // Load existing validity data on mount
  useEffect(() => {
    let cancelled = false;
    api
      .get<ValidityData>(`/api/v1/studies/${studyId}/validity`)
      .then((data) => {
        if (!cancelled) {
          reset({
            descriptive: data.descriptive ?? '',
            theoretical: data.theoretical ?? '',
            generalizability_internal: data.generalizability_internal ?? '',
            generalizability_external: data.generalizability_external ?? '',
            interpretive: data.interpretive ?? '',
            repeatability: data.repeatability ?? '',
          });
        }
      })
      .catch(() => {
        // Silently ignore load errors — form starts empty
      });
    return () => { cancelled = true; };
  }, [studyId, reset]);

  /**
   * Auto-save a single field on blur.
   * Called by each textarea's onBlur handler (wired via register).
   */
  const saveField = async (field: keyof ValidityFormValues, value: string) => {
    if (savingRef.current[field]) return;
    savingRef.current[field] = true;
    try {
      await api.patch(`/api/v1/studies/${studyId}/validity`, { [field]: value });
    } catch (err: unknown) {
      errorRef.current = err instanceof Error ? err.message : 'Save failed';
    } finally {
      savingRef.current[field] = false;
    }
  };

  const handleGenerate = async () => {
    if (generatingRef.current) return;
    generatingRef.current = true;
    try {
      await api.post(`/api/v1/studies/${studyId}/validity/generate`, {});
      // Reload after short delay to pick up AI-generated text
      setTimeout(async () => {
        try {
          const data = await api.get<ValidityData>(`/api/v1/studies/${studyId}/validity`);
          reset({
            descriptive: data.descriptive ?? '',
            theoretical: data.theoretical ?? '',
            generalizability_internal: data.generalizability_internal ?? '',
            generalizability_external: data.generalizability_external ?? '',
            interpretive: data.interpretive ?? '',
            repeatability: data.repeatability ?? '',
          });
        } catch {
          // Ignore reload errors
        }
        generatingRef.current = false;
      }, 3000);
    } catch (err: unknown) {
      errorRef.current = err instanceof Error ? err.message : 'Failed to start AI generation';
      generatingRef.current = false;
    }
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h2 style={headingStyle}>Validity Discussion</h2>
        <button
          style={generateBtnStyle}
          onClick={handleGenerate}
          aria-label="Generate with AI"
          type="button"
        >
          Generate with AI
        </button>
      </div>

      <p style={subheadStyle}>
        Document potential threats to validity across six dimensions.
        Changes are saved automatically when you leave each field.
      </p>

      {/* Six text area fields */}
      <form>
        {DIMS.map(({ field, label, hint }) => {
          const fieldProps = register(field, {
            onBlur: (e) => saveField(field, e.target.value),
          });
          return (
            <div key={field} style={fieldGroupStyle}>
              <label htmlFor={field} style={labelStyle}>
                {label}
              </label>
              <p style={hintStyle}>{hint}</p>
              <textarea
                {...fieldProps}
                id={field}
                rows={5}
                style={textareaStyle}
                placeholder={`Describe ${label.toLowerCase()} threats and mitigations…`}
              />
              {formState.errors[field] && (
                <p style={{ color: '#dc2626', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                  {formState.errors[field]?.message}
                </p>
              )}
            </div>
          );
        })}
      </form>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const containerStyle: React.CSSProperties = {
  padding: '1.25rem',
  background: '#fff',
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
};

const headingStyle: React.CSSProperties = {
  margin: 0,
  fontSize: '1.125rem',
  fontWeight: 700,
  color: '#111827',
};

const subheadStyle: React.CSSProperties = {
  fontSize: '0.875rem',
  color: '#6b7280',
  marginBottom: '1.5rem',
  marginTop: 0,
};

const fieldGroupStyle: React.CSSProperties = {
  marginBottom: '1.25rem',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontWeight: 600,
  fontSize: '0.875rem',
  color: '#374151',
  marginBottom: '0.25rem',
};

const hintStyle: React.CSSProperties = {
  margin: '0 0 0.375rem',
  fontSize: '0.75rem',
  color: '#9ca3af',
};

const textareaStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.5rem 0.75rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  color: '#111827',
  resize: 'vertical',
  lineHeight: 1.5,
  boxSizing: 'border-box',
};

const generateBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  background: '#7c3aed',
  color: '#fff',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 600,
};
