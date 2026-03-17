/**
 * AgentWizard — 5-step MUI Stepper for creating a new Agent record.
 *
 * Steps:
 * 1. Task Type
 * 2. Model Selection (Provider → Model)
 * 3. Role & Persona
 * 4. Persona SVG (optional)
 * 5. System Message
 */

import { useReducer } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import MenuItem from '@mui/material/MenuItem';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Stepper from '@mui/material/Stepper';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import SystemMessageEditor from './SystemMessageEditor';
import { useAgentTaskTypes, useCreateAgent, useGeneratePersonaSvg, useGenerateSystemMessage } from '../../../services/agentsApi';
import { useProviders, useProviderModels } from '../../../services/providersApi';

const DEFAULT_TEMPLATE =
  'You are {{ persona_name }}. Your role is {{ role_name }}: {{ role_description }}. You are working on a {{ study_type }} in {{ domain }}.';

const STEPS = ['Task Type', 'Model Selection', 'Role & Persona', 'Persona SVG', 'System Message'];

interface WizardState {
  step: number;
  task_type: string;
  provider_id: string;
  model_id: string;
  role_name: string;
  role_description: string;
  persona_name: string;
  persona_description: string;
  persona_svg: string | null;
  system_message_template: string;
  generatedSvg: string | null;
  savedAgentId: string | null;
}

type WizardAction =
  | { type: 'SET_STEP'; step: number }
  | { type: 'SET_TASK_TYPE'; value: string }
  | { type: 'SET_PROVIDER'; value: string }
  | { type: 'SET_MODEL'; value: string }
  | { type: 'SET_FIELD'; field: keyof WizardState; value: string }
  | { type: 'SET_SVG'; value: string | null }
  | { type: 'SET_TEMPLATE'; value: string }
  | { type: 'SET_SAVED_AGENT'; id: string };

function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, step: action.step };
    case 'SET_TASK_TYPE':
      return { ...state, task_type: action.value };
    case 'SET_PROVIDER':
      return { ...state, provider_id: action.value, model_id: '' };
    case 'SET_MODEL':
      return { ...state, model_id: action.value };
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value };
    case 'SET_SVG':
      return { ...state, generatedSvg: action.value, persona_svg: action.value };
    case 'SET_TEMPLATE':
      return { ...state, system_message_template: action.value };
    case 'SET_SAVED_AGENT':
      return { ...state, savedAgentId: action.id };
    default:
      return state;
  }
}

const initialState: WizardState = {
  step: 0,
  task_type: '',
  provider_id: '',
  model_id: '',
  role_name: '',
  role_description: '',
  persona_name: '',
  persona_description: '',
  persona_svg: null,
  system_message_template: DEFAULT_TEMPLATE,
  generatedSvg: null,
  savedAgentId: null,
};

/** Props for {@link AgentWizard}. */
interface AgentWizardProps {
  /** Whether the wizard dialog is open. */
  open: boolean;
  /** Called when the dialog should be closed. */
  onClose: () => void;
}

/**
 * Multi-step agent creation wizard.
 *
 * @param props - {@link AgentWizardProps}
 */
export default function AgentWizard({ open, onClose }: AgentWizardProps) {
  const [state, dispatch] = useReducer(wizardReducer, initialState);

  const { data: taskTypes = [] } = useAgentTaskTypes();
  const { data: providers = [] } = useProviders();
  const { data: models = [] } = useProviderModels(state.provider_id);

  const createAgent = useCreateAgent();
  const generateSvg = useGeneratePersonaSvg();
  const generateSysMsg = useGenerateSystemMessage();

  const isLastStep = state.step === STEPS.length - 1;

  function handleNext() {
    dispatch({ type: 'SET_STEP', step: state.step + 1 });
  }

  function handleBack() {
    dispatch({ type: 'SET_STEP', step: state.step - 1 });
  }

  async function handleGenerateSvg() {
    const result = await generateSvg.mutateAsync({
      persona_name: state.persona_name,
      persona_description: state.persona_description,
    });
    dispatch({ type: 'SET_SVG', value: result.svg });
  }

  async function handleGenerateAndSave() {
    const template = state.system_message_template || DEFAULT_TEMPLATE;
    const agent = await createAgent.mutateAsync({
      task_type: state.task_type as Parameters<typeof createAgent.mutateAsync>[0]['task_type'],
      role_name: state.role_name,
      role_description: state.role_description,
      persona_name: state.persona_name,
      persona_description: state.persona_description,
      system_message_template: template,
      model_id: state.model_id,
      provider_id: state.provider_id,
      persona_svg: state.persona_svg,
    });
    dispatch({ type: 'SET_SAVED_AGENT', id: agent.id });
    const result = await generateSysMsg.mutateAsync(agent.id);
    dispatch({ type: 'SET_TEMPLATE', value: result.system_message_template });
  }

  async function handleSave() {
    await createAgent.mutateAsync({
      task_type: state.task_type as Parameters<typeof createAgent.mutateAsync>[0]['task_type'],
      role_name: state.role_name,
      role_description: state.role_description,
      persona_name: state.persona_name,
      persona_description: state.persona_description,
      system_message_template: state.system_message_template || DEFAULT_TEMPLATE,
      model_id: state.model_id,
      provider_id: state.provider_id,
      persona_svg: state.persona_svg,
    });
    onClose();
  }

  const isBusy =
    createAgent.isPending || generateSvg.isPending || generateSysMsg.isPending;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create Agent</DialogTitle>
      <DialogContent>
        <Stepper activeStep={state.step} sx={{ mb: 3 }}>
          {STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {state.step === 0 && (
          <TextField
            select
            label="Task Type"
            value={state.task_type}
            onChange={(e) => dispatch({ type: 'SET_TASK_TYPE', value: e.target.value })}
            fullWidth
          >
            {taskTypes.map((t) => (
              <MenuItem key={t} value={t}>{t}</MenuItem>
            ))}
          </TextField>
        )}

        {state.step === 1 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              label="Provider"
              value={state.provider_id}
              onChange={(e) => dispatch({ type: 'SET_PROVIDER', value: e.target.value })}
              fullWidth
            >
              {providers.map((p) => (
                <MenuItem key={p.id} value={p.id}>{p.display_name}</MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Model"
              value={state.model_id}
              onChange={(e) => dispatch({ type: 'SET_MODEL', value: e.target.value })}
              fullWidth
              disabled={!state.provider_id}
            >
              {models.filter((m) => m.is_enabled).map((m) => (
                <MenuItem key={m.id} value={m.id}>{m.display_name}</MenuItem>
              ))}
            </TextField>
          </Box>
        )}

        {state.step === 2 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField label="Role Name" value={state.role_name} onChange={(e) => dispatch({ type: 'SET_FIELD', field: 'role_name', value: e.target.value })} fullWidth />
            <TextField label="Role Description" value={state.role_description} onChange={(e) => dispatch({ type: 'SET_FIELD', field: 'role_description', value: e.target.value })} multiline minRows={3} fullWidth />
            <TextField label="Persona Name" value={state.persona_name} onChange={(e) => dispatch({ type: 'SET_FIELD', field: 'persona_name', value: e.target.value })} fullWidth />
            <TextField label="Persona Description" value={state.persona_description} onChange={(e) => dispatch({ type: 'SET_FIELD', field: 'persona_description', value: e.target.value })} multiline minRows={3} fullWidth />
          </Box>
        )}

        {state.step === 3 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Button variant="outlined" onClick={handleGenerateSvg} disabled={isBusy || !state.persona_name}>
              {generateSvg.isPending ? <CircularProgress size={20} /> : 'Generate SVG'}
            </Button>
            {state.generatedSvg && (
              <Box dangerouslySetInnerHTML={{ __html: state.generatedSvg }} sx={{ width: 100, height: 100 }} />
            )}
            <Typography variant="caption" color="text.secondary">
              SVG generation is optional — you can skip this step.
            </Typography>
          </Box>
        )}

        {state.step === 4 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <SystemMessageEditor
              value={state.system_message_template}
              onChange={(val) => dispatch({ type: 'SET_TEMPLATE', value: val })}
              onUndo={() => dispatch({ type: 'SET_TEMPLATE', value: DEFAULT_TEMPLATE })}
              canUndo={state.system_message_template !== DEFAULT_TEMPLATE}
              disabled={isBusy}
            />
            <Button variant="outlined" onClick={handleGenerateAndSave} disabled={isBusy || !state.role_name || !state.model_id}>
              {isBusy ? <CircularProgress size={20} /> : 'Generate System Message (saves agent)'}
            </Button>
            {(createAgent.isError || generateSysMsg.isError) && (
              <Typography color="error" variant="caption">
                {String((createAgent.error ?? generateSysMsg.error) ?? 'An error occurred')}
              </Typography>
            )}
          </Box>
        )}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button onClick={handleBack} disabled={state.step === 0 || isBusy}>
            Back
          </Button>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button onClick={onClose} disabled={isBusy}>Cancel</Button>
            {isLastStep ? (
              <Button variant="contained" onClick={handleSave} disabled={isBusy || !state.role_name || !state.model_id}>
                {createAgent.isPending ? <CircularProgress size={20} /> : 'Save'}
              </Button>
            ) : (
              <Button variant="contained" onClick={handleNext} disabled={state.step === 0 && !state.task_type || state.step === 1 && !state.model_id}>
                Next
              </Button>
            )}
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
