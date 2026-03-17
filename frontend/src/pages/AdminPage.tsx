/**
 * AdminPage: admin dashboard with System, Providers, and Models tabs.
 *
 * - System tab: health dashboard and job retry UI.
 * - Providers tab: provider list with add/edit/delete/refresh actions.
 * - Models tab: model enable/disable table scoped to a selected provider.
 *
 * Redirects non-admins to /groups with an access-denied message.
 * State is managed via useReducer as there are more than 3 related items.
 */

import { useReducer } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api, ApiError } from '../services/api';
import ServiceHealthPanel from '../components/admin/ServiceHealthPanel';
import JobRetryPanel from '../components/admin/JobRetryPanel';
import ProviderList from '../components/admin/providers/ProviderList';
import ProviderForm from '../components/admin/providers/ProviderForm';
import ModelList from '../components/admin/models/ModelList';
import AgentList from '../components/admin/agents/AgentList';
import AgentForm from '../components/admin/agents/AgentForm';
import AgentWizard from '../components/admin/agents/AgentWizard';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Divider from '@mui/material/Divider';
import MenuItem from '@mui/material/MenuItem';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useProviders, useDeleteProvider, useRefreshModels } from '../services/providersApi';
import { useAgents, useAgent } from '../services/agentsApi';
import type { Provider } from '../types/provider';
import type { AgentSummary } from '../types/agent';

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

interface AdminState {
  selectedTab: number;
  editingProvider: Provider | null;
  showProviderForm: boolean;
  selectedProviderId: string;
  showAgentWizard: boolean;
  editingAgentId: string | null;
}

type AdminAction =
  | { type: 'SET_TAB'; tab: number }
  | { type: 'OPEN_CREATE_PROVIDER' }
  | { type: 'OPEN_EDIT_PROVIDER'; provider: Provider }
  | { type: 'CLOSE_PROVIDER_FORM' }
  | { type: 'SET_PROVIDER_ID'; id: string }
  | { type: 'TOGGLE_AGENT_WIZARD' }
  | { type: 'OPEN_EDIT_AGENT'; agentId: string }
  | { type: 'CLOSE_AGENT_FORM' };

function adminReducer(state: AdminState, action: AdminAction): AdminState {
  switch (action.type) {
    case 'SET_TAB':
      return { ...state, selectedTab: action.tab };
    case 'OPEN_CREATE_PROVIDER':
      return { ...state, showProviderForm: true, editingProvider: null };
    case 'OPEN_EDIT_PROVIDER':
      return { ...state, showProviderForm: true, editingProvider: action.provider };
    case 'CLOSE_PROVIDER_FORM':
      return { ...state, showProviderForm: false, editingProvider: null };
    case 'SET_PROVIDER_ID':
      return { ...state, selectedProviderId: action.id };
    case 'TOGGLE_AGENT_WIZARD':
      return { ...state, showAgentWizard: !state.showAgentWizard };
    case 'OPEN_EDIT_AGENT':
      return { ...state, editingAgentId: action.agentId };
    case 'CLOSE_AGENT_FORM':
      return { ...state, editingAgentId: null };
    default:
      return state;
  }
}

const initialState: AdminState = {
  selectedTab: 0,
  editingProvider: null,
  showProviderForm: false,
  selectedProviderId: '',
  showAgentWizard: false,
  editingAgentId: null,
};

// ---------------------------------------------------------------------------
// Admin access check
// ---------------------------------------------------------------------------

/** Probes admin access by attempting to fetch the health endpoint. */
function useAdminAccess() {
  return useQuery<unknown>({
    queryKey: ['admin', 'access-check'],
    queryFn: () => api.get('/api/v1/admin/health'),
    retry: false,
  });
}

// ---------------------------------------------------------------------------
// Sub-panels
// ---------------------------------------------------------------------------

interface ProvidersTabProps {
  state: AdminState;
  dispatch: React.Dispatch<AdminAction>;
}

function ProvidersTab({ state, dispatch }: ProvidersTabProps) {
  const { data: providers = [], isLoading } = useProviders();
  const deleteMutation = useDeleteProvider();
  const refreshMutation = useRefreshModels();

  const handleDelete = (id: string) => {
    if (window.confirm('Delete this provider? This cannot be undone.')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
        <Button variant="contained" size="small" onClick={() => dispatch({ type: 'OPEN_CREATE_PROVIDER' })}>
          Add Provider
        </Button>
      </Box>
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={24} />
        </Box>
      ) : (
        <ProviderList
          providers={providers}
          onEdit={(p) => dispatch({ type: 'OPEN_EDIT_PROVIDER', provider: p })}
          onDelete={handleDelete}
          onRefresh={(id) => refreshMutation.mutate(id)}
        />
      )}

      <Dialog
        open={state.showProviderForm}
        onClose={() => dispatch({ type: 'CLOSE_PROVIDER_FORM' })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {state.editingProvider ? 'Edit Provider' : 'Add Provider'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <ProviderForm
              provider={state.editingProvider ?? undefined}
              onSuccess={() => dispatch({ type: 'CLOSE_PROVIDER_FORM' })}
              onCancel={() => dispatch({ type: 'CLOSE_PROVIDER_FORM' })}
            />
          </Box>
        </DialogContent>
      </Dialog>
    </Box>
  );
}

interface ModelsTabProps {
  state: AdminState;
  dispatch: React.Dispatch<AdminAction>;
}

function ModelsTab({ state, dispatch }: ModelsTabProps) {
  const { data: providers = [] } = useProviders();

  return (
    <Box>
      <TextField
        select
        label="Select Provider"
        value={state.selectedProviderId}
        onChange={(e) => dispatch({ type: 'SET_PROVIDER_ID', id: e.target.value })}
        size="small"
        sx={{ minWidth: 240, mb: 2 }}
      >
        {providers.map((p) => (
          <MenuItem key={p.id} value={p.id}>
            {p.display_name} ({p.provider_type})
          </MenuItem>
        ))}
      </TextField>

      {state.selectedProviderId ? (
        <ModelList providerId={state.selectedProviderId} />
      ) : (
        <Typography color="text.secondary">Select a provider above to view its models.</Typography>
      )}
    </Box>
  );
}

interface AgentsTabProps {
  state: AdminState;
  dispatch: React.Dispatch<AdminAction>;
}

function AgentsTab({ state, dispatch }: AgentsTabProps) {
  const { data: agents = [], isLoading } = useAgents();
  const { data: editingAgent } = useAgent(state.editingAgentId);

  const handleEdit = (agent: AgentSummary) => {
    dispatch({ type: 'OPEN_EDIT_AGENT', agentId: agent.id });
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
        <Button
          variant="contained"
          size="small"
          onClick={() => dispatch({ type: 'TOGGLE_AGENT_WIZARD' })}
        >
          Create Agent
        </Button>
      </Box>
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={24} />
        </Box>
      ) : (
        <AgentList agents={agents} onEdit={handleEdit} />
      )}
      <AgentWizard
        open={state.showAgentWizard}
        onClose={() => dispatch({ type: 'TOGGLE_AGENT_WIZARD' })}
      />
      <Dialog
        open={!!state.editingAgentId && !!editingAgent}
        onClose={() => dispatch({ type: 'CLOSE_AGENT_FORM' })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Agent</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {editingAgent && (
              <AgentForm
                agent={editingAgent}
                onSuccess={() => dispatch({ type: 'CLOSE_AGENT_FORM' })}
                onCancel={() => dispatch({ type: 'CLOSE_AGENT_FORM' })}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

/** Full-page admin dashboard with System, Providers, and Models tabs. */
export default function AdminPage() {
  const navigate = useNavigate();
  const { isLoading, error } = useAdminAccess();
  const [state, dispatch] = useReducer(adminReducer, initialState);

  if (isLoading) {
    return (
      <Box sx={{ padding: '2rem', color: '#64748b' }}>
        Checking access…
      </Box>
    );
  }

  if (error instanceof ApiError && error.status === 403) {
    return (
      <Box sx={{ padding: '2rem' }}>
        <Typography variant="h5" sx={{ color: '#dc2626', marginBottom: '0.5rem' }}>403 Forbidden</Typography>
        <Typography sx={{ color: '#4b5563' }}>
          You do not have admin access. Only group administrators may view this page.
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate('/groups')}
          sx={{ marginTop: '1rem', padding: '0.5rem 1rem' }}
        >
          Back to Groups
        </Button>
      </Box>
    );
  }

  return (
    <Container maxWidth="md" sx={{ padding: '1.5rem' }}>
      <Typography variant="h5" sx={{ marginTop: 0, marginBottom: '1.5rem', fontSize: '1.375rem', color: '#111827' }}>
        Admin Dashboard
      </Typography>

      <Tabs
        value={state.selectedTab}
        onChange={(_, v: number) => dispatch({ type: 'SET_TAB', tab: v })}
        sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
      >
        <Tab label="System" />
        <Tab label="Providers" />
        <Tab label="Models" />
        <Tab label="Agents" />
      </Tabs>

      {state.selectedTab === 0 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <ServiceHealthPanel />
          <Divider />
          <JobRetryPanel />
        </Box>
      )}

      {state.selectedTab === 1 && (
        <ProvidersTab state={state} dispatch={dispatch} />
      )}

      {state.selectedTab === 2 && (
        <ModelsTab state={state} dispatch={dispatch} />
      )}

      {state.selectedTab === 3 && (
        <AgentsTab state={state} dispatch={dispatch} />
      )}
    </Container>
  );
}
