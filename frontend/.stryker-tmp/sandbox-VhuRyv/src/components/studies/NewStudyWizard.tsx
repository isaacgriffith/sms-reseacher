/**
 * Multi-step wizard for creating a new study.
 * Steps: (1) Name+Type, (2) Assign members, (3) Configure reviewers,
 *        (4) Motivation+Objectives+Questions, (5) PICO/C variant selector
 *
 * Principle IX.5: >3 related useState → useReducer with typed WizardAction
 * Principle IX: useWatch replaces watch() for form-field subscriptions
 */
// @ts-nocheck


import { useReducer } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { api, ApiError } from '../../services/api';

interface ReviewerConfig {
  type: 'human' | 'ai_agent';
  user_id?: number;
  agent_name?: string;
  agent_config?: Record<string, unknown>;
}

interface WizardData {
  name: string;
  topic: string;
  study_type: string;
  motivation: string;
  research_objectives: string;
  research_questions: string;
  snowball_threshold: number;
  pico_variant: string;
}

interface Props {
  groupId: number;
  onClose: () => void;
  onCreated: (studyId: number) => void;
}

// ---------------------------------------------------------------------------
// Wizard state — useReducer replaces the 5 useState calls (Principle IX.5)
// ---------------------------------------------------------------------------

interface WizardState {
  step: number;
  reviewers: ReviewerConfig[];
  newAgentName: string;
  submitError: string | null;
  isSubmitting: boolean;
}

type WizardAction =
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'ADD_REVIEWER'; payload: ReviewerConfig }
  | { type: 'REMOVE_REVIEWER'; payload: number }
  | { type: 'SET_NEW_AGENT_NAME'; payload: string }
  | { type: 'SUBMIT_START' }
  | { type: 'SUBMIT_ERROR'; payload: string }
  | { type: 'SUBMIT_RESET' };

const INITIAL_STATE: WizardState = {
  step: 1,
  reviewers: [{ type: 'ai_agent', agent_name: 'screener-v2' }],
  newAgentName: '',
  submitError: null,
  isSubmitting: false,
};

function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'NEXT_STEP':
      return { ...state, step: state.step + 1 };
    case 'PREV_STEP':
      return { ...state, step: state.step - 1 };
    case 'ADD_REVIEWER':
      return {
        ...state,
        reviewers: [...state.reviewers, action.payload],
        newAgentName: '',
      };
    case 'REMOVE_REVIEWER':
      return {
        ...state,
        reviewers: state.reviewers.filter((_, i) => i !== action.payload),
      };
    case 'SET_NEW_AGENT_NAME':
      return { ...state, newAgentName: action.payload };
    case 'SUBMIT_START':
      return { ...state, submitError: null, isSubmitting: true };
    case 'SUBMIT_ERROR':
      return { ...state, submitError: action.payload, isSubmitting: false };
    case 'SUBMIT_RESET':
      return { ...state, submitError: null, isSubmitting: false };
    default:
      return state;
  }
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const STUDY_TYPES = ['SMS', 'SLR', 'Tertiary', 'Rapid'];
const PICO_VARIANTS = ['PICO', 'PICOS', 'PICOT', 'SPIDER', 'PCC'];
const TOTAL_STEPS = 5;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function NewStudyWizard({ groupId, onClose, onCreated }: Props) {
  const [state, dispatch] = useReducer(wizardReducer, INITIAL_STATE);
  const { step, reviewers, newAgentName, submitError, isSubmitting } = state;

  const {
    register,
    handleSubmit,
    control,
    trigger,
    formState: { errors },
  } = useForm<WizardData>({
    defaultValues: {
      study_type: 'SMS',
      pico_variant: 'PICO',
      snowball_threshold: 5,
    },
  });

  // Principle IX: useWatch replaces watch() for form-field subscriptions
  const selectedPicoVariant = useWatch({ control, name: 'pico_variant' });

  const addAiReviewer = () => {
    if (!newAgentName.trim()) return;
    dispatch({
      type: 'ADD_REVIEWER',
      payload: { type: 'ai_agent', agent_name: newAgentName.trim() },
    });
  };

  const removeReviewer = (idx: number) => {
    dispatch({ type: 'REMOVE_REVIEWER', payload: idx });
  };

  const onSubmit = handleSubmit(async (data) => {
    dispatch({ type: 'SUBMIT_START' });
    try {
      const body = {
        name: data.name,
        topic: data.topic,
        study_type: data.study_type,
        motivation: data.motivation || null,
        research_objectives: data.research_objectives
          ? data.research_objectives.split('\n').map((s) => s.trim()).filter(Boolean)
          : [],
        research_questions: data.research_questions
          ? data.research_questions.split('\n').map((s) => s.trim()).filter(Boolean)
          : [],
        member_ids: [],
        reviewers,
        snowball_threshold: data.snowball_threshold,
      };

      const study = await api.post<{ id: number }>(`/api/v1/groups/${groupId}/studies`, body);
      onCreated(study.id);
    } catch (err) {
      dispatch({
        type: 'SUBMIT_ERROR',
        payload: err instanceof ApiError ? err.detail : 'Failed to create study',
      });
    }
  });

  const panelStyle: React.CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  };

  const dialogStyle: React.CSSProperties = {
    background: '#fff',
    borderRadius: '0.5rem',
    padding: '2rem',
    width: '560px',
    maxHeight: '85vh',
    overflowY: 'auto',
    boxSizing: 'border-box',
  };

  const fieldStyle: React.CSSProperties = { marginBottom: '1rem' };
  const labelStyle: React.CSSProperties = { display: 'block', marginBottom: '0.25rem', fontWeight: 500, fontSize: '0.9rem' };
  const inputStyle: React.CSSProperties = { width: '100%', padding: '0.5rem', boxSizing: 'border-box', borderRadius: '0.25rem', border: '1px solid #cbd5e1' };
  const errorStyle: React.CSSProperties = { color: 'red', fontSize: '0.8125rem' };

  return (
    <div style={panelStyle} onClick={onClose}>
      <div style={dialogStyle} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.25rem' }}>New Study</h2>
            <p style={{ margin: '0.25rem 0 0', color: '#64748b', fontSize: '0.875rem' }}>
              Step {step} of {TOTAL_STEPS}
            </p>
          </div>
          <button onClick={onClose} aria-label="Close" style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#64748b' }}>×</button>
        </div>

        {/* Progress bar */}
        <div style={{ height: 4, background: '#e2e8f0', borderRadius: 2, marginBottom: '1.5rem' }}>
          <div style={{ height: '100%', width: `${(step / TOTAL_STEPS) * 100}%`, background: '#2563eb', borderRadius: 2, transition: 'width 0.3s' }} />
        </div>

        <form onSubmit={onSubmit}>
          {/* Step 1: Name + Type */}
          {step === 1 && (
            <div>
              <h3 style={{ margin: '0 0 1rem' }}>Study Name & Type</h3>
              <div style={fieldStyle}>
                <label style={labelStyle}>Study name *</label>
                <input style={inputStyle} placeholder="Study name" {...register('name', { required: 'Name is required' })} />
                {errors.name && <span style={errorStyle}>{errors.name.message}</span>}
              </div>
              <div style={fieldStyle}>
                <label style={labelStyle}>Topic *</label>
                <input style={inputStyle} placeholder="Brief topic description" {...register('topic', { required: 'Topic is required' })} />
                {errors.topic && <span style={errorStyle}>{errors.topic.message}</span>}
              </div>
              <div style={fieldStyle}>
                <label style={labelStyle}>Study type *</label>
                <select style={inputStyle} {...register('study_type')}>
                  {STUDY_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div style={fieldStyle}>
                <label style={labelStyle}>Snowball threshold</label>
                <input type="number" min={1} max={50} style={inputStyle} {...register('snowball_threshold', { valueAsNumber: true })} />
              </div>
            </div>
          )}

          {/* Step 2: Assign members (simplified — IDs only) */}
          {step === 2 && (
            <div>
              <h3 style={{ margin: '0 0 1rem' }}>Assign Members</h3>
              <p style={{ color: '#64748b', fontSize: '0.875rem' }}>
                You are automatically added as the study lead. Additional members can be invited after creation via the group member management page.
              </p>
            </div>
          )}

          {/* Step 3: Configure reviewers */}
          {step === 3 && (
            <div>
              <h3 style={{ margin: '0 0 1rem' }}>Configure Reviewers</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1rem' }}>
                {reviewers.map((r, i) => (
                  <li key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0', borderBottom: '1px solid #e2e8f0' }}>
                    <span style={{ fontSize: '0.875rem' }}>
                      {r.type === 'ai_agent' ? `🤖 ${r.agent_name}` : `👤 User ${r.user_id}`}
                    </span>
                    <button type="button" onClick={() => removeReviewer(i)} style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer' }}>Remove</button>
                  </li>
                ))}
              </ul>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <input
                  value={newAgentName}
                  onChange={(e) => dispatch({ type: 'SET_NEW_AGENT_NAME', payload: e.target.value })}
                  placeholder="Agent name (e.g. screener-v2)"
                  style={{ flex: 1, ...inputStyle }}
                />
                <button type="button" onClick={addAiReviewer} style={{ padding: '0.5rem 0.75rem', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer', whiteSpace: 'nowrap' }}>+ AI Reviewer</button>
              </div>
            </div>
          )}

          {/* Step 4: Motivation + Objectives + Questions */}
          {step === 4 && (
            <div>
              <h3 style={{ margin: '0 0 1rem' }}>Research Context</h3>
              <div style={fieldStyle}>
                <label style={labelStyle}>Motivation</label>
                <textarea rows={3} style={{ ...inputStyle, resize: 'vertical' }} placeholder="Why is this study needed?" {...register('motivation')} />
              </div>
              <div style={fieldStyle}>
                <label style={labelStyle}>Research objectives (one per line)</label>
                <textarea rows={4} style={{ ...inputStyle, resize: 'vertical' }} placeholder="RO1: Identify…&#10;RO2: Characterise…" {...register('research_objectives')} />
              </div>
              <div style={fieldStyle}>
                <label style={labelStyle}>Research questions (one per line)</label>
                <textarea rows={4} style={{ ...inputStyle, resize: 'vertical' }} placeholder="RQ1: What…&#10;RQ2: How…" {...register('research_questions')} />
              </div>
            </div>
          )}

          {/* Step 5: PICO/C variant */}
          {step === 5 && (
            <div>
              <h3 style={{ margin: '0 0 1rem' }}>PICO/C Framework</h3>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginBottom: '1rem' }}>
                Choose the framework variant. You can fill in the components after the study is created.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
                {PICO_VARIANTS.map((v) => (
                  <label key={v} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem', border: `2px solid ${selectedPicoVariant === v ? '#2563eb' : '#e2e8f0'}`, borderRadius: '0.375rem', cursor: 'pointer', fontSize: '0.875rem' }}>
                    <input type="radio" value={v} {...register('pico_variant')} style={{ accentColor: '#2563eb' }} />
                    {v}
                  </label>
                ))}
              </div>

              {submitError && (
                <p style={{ color: 'red', marginTop: '1rem', fontSize: '0.875rem' }}>{submitError}</p>
              )}
            </div>
          )}

          {/* Navigation */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem' }}>
            <button
              type="button"
              onClick={() => dispatch({ type: 'PREV_STEP' })}
              disabled={step === 1}
              style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid #cbd5e1', borderRadius: '0.375rem', cursor: step === 1 ? 'not-allowed' : 'pointer', color: '#64748b' }}
            >
              Back
            </button>
            {step < TOTAL_STEPS ? (
              <button
                type="button"
                onClick={async () => {
                  if (step === 1) {
                    const valid = await trigger(['name', 'topic']);
                    if (!valid) return;
                  }
                  dispatch({ type: 'NEXT_STEP' });
                }}
                style={{ padding: '0.5rem 1.25rem', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' }}
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                disabled={isSubmitting}
                style={{ padding: '0.5rem 1.25rem', background: '#16a34a', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: isSubmitting ? 'not-allowed' : 'pointer' }}
              >
                {isSubmitting ? 'Creating…' : 'Create Study'}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
