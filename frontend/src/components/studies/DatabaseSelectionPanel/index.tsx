/**
 * DatabaseSelectionPanel: Per-study academic database index toggle UI.
 *
 * Groups database indices into Primary / General / Supplementary categories,
 * shows credential warning badges for unconfigured subscription databases,
 * and presents a SciHub acknowledgment dialog when SciHub is toggled on.
 *
 * Toggle state is managed with `useReducer` per Constitution Principle IX
 * (>3 related state values → useReducer).
 */

import React, { useReducer } from 'react';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

import {
  DatabaseSelectionItem,
  useStudyDatabaseSelection,
} from '../../../hooks/useStudyDatabaseSelection';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for the DatabaseSelectionPanel component. */
export interface DatabaseSelectionPanelProps {
  /** Integer study ID whose database selection is being managed. */
  studyId: number;
}

// ---------------------------------------------------------------------------
// Database index groupings and display names
// ---------------------------------------------------------------------------

type IndexGroup = 'Primary' | 'General' | 'Supplementary';

const INDEX_GROUP: Record<string, IndexGroup> = {
  semantic_scholar: 'Primary',
  ieee_xplore: 'Primary',
  scopus: 'Primary',
  acm_dl: 'General',
  web_of_science: 'General',
  inspec: 'General',
  science_direct: 'Supplementary',
  springer_link: 'Supplementary',
  google_scholar: 'Supplementary',
};

const INDEX_DISPLAY_NAME: Record<string, string> = {
  semantic_scholar: 'Semantic Scholar',
  ieee_xplore: 'IEEE Xplore',
  scopus: 'Scopus',
  acm_dl: 'ACM Digital Library',
  web_of_science: 'Web of Science',
  inspec: 'Inspec',
  science_direct: 'ScienceDirect',
  springer_link: 'SpringerLink',
  google_scholar: 'Google Scholar',
};

const GROUPS: IndexGroup[] = ['Primary', 'General', 'Supplementary'];

// ---------------------------------------------------------------------------
// Reducer
// ---------------------------------------------------------------------------

interface ToggleState {
  selections: Record<string, boolean>;
  snowball_enabled: boolean;
  scihub_enabled: boolean;
  scihub_acknowledged: boolean;
  scihub_dialog_open: boolean;
}

type ToggleAction =
  | { type: 'TOGGLE_INDEX'; index: string }
  | { type: 'TOGGLE_SNOWBALL' }
  | { type: 'TOGGLE_SCIHUB' }
  | { type: 'ACKNOWLEDGE_SCIHUB' }
  | { type: 'DISMISS_SCIHUB_DIALOG' }
  | { type: 'INIT'; data: ToggleState };

function toggleReducer(state: ToggleState, action: ToggleAction): ToggleState {
  switch (action.type) {
    case 'INIT':
      return action.data;
    case 'TOGGLE_INDEX':
      return {
        ...state,
        selections: {
          ...state.selections,
          [action.index]: !state.selections[action.index],
        },
      };
    case 'TOGGLE_SNOWBALL':
      return { ...state, snowball_enabled: !state.snowball_enabled };
    case 'TOGGLE_SCIHUB':
      if (!state.scihub_enabled) {
        // Opening SciHub: show acknowledgment dialog first
        return { ...state, scihub_dialog_open: true };
      }
      return { ...state, scihub_enabled: false, scihub_acknowledged: false };
    case 'ACKNOWLEDGE_SCIHUB':
      return {
        ...state,
        scihub_enabled: true,
        scihub_acknowledged: true,
        scihub_dialog_open: false,
      };
    case 'DISMISS_SCIHUB_DIALOG':
      return { ...state, scihub_dialog_open: false };
    default:
      return state;
  }
}

function initToggleState(items: DatabaseSelectionItem[]): ToggleState {
  const selections: Record<string, boolean> = {};
  for (const item of items) {
    selections[item.database_index] = item.is_enabled;
  }
  return {
    selections,
    snowball_enabled: false,
    scihub_enabled: false,
    scihub_acknowledged: false,
    scihub_dialog_open: false,
  };
}

// ---------------------------------------------------------------------------
// Index toggle row
// ---------------------------------------------------------------------------

interface IndexRowProps {
  item: DatabaseSelectionItem;
  enabled: boolean;
  onToggle: () => void;
}

/** Renders a single database index toggle with credential warning if needed. */
function IndexRow({ item, enabled, onToggle }: IndexRowProps) {
  const displayName = INDEX_DISPLAY_NAME[item.database_index] ?? item.database_index;
  const showWarning = item.requires_credential && !item.credential_configured;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 0.5 }}>
      <FormControlLabel
        control={<Switch checked={enabled} onChange={onToggle} size="small" />}
        label={displayName}
        sx={{ flex: 1 }}
      />
      {showWarning && (
        <Tooltip title="API key not configured — configure in Admin → Search Integrations">
          <WarningAmberIcon
            fontSize="small"
            color="warning"
            aria-label="credential not configured"
          />
        </Tooltip>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

/**
 * Panel for configuring which academic database indices a study searches.
 *
 * @param props - {@link DatabaseSelectionPanelProps}
 */
export default function DatabaseSelectionPanel({
  studyId,
}: DatabaseSelectionPanelProps) {
  const { data, isLoading, updateSelection } = useStudyDatabaseSelection(studyId);

  const [state, dispatch] = useReducer(
    toggleReducer,
    data?.selections ? initToggleState(data.selections) : {
      selections: {},
      snowball_enabled: false,
      scihub_enabled: false,
      scihub_acknowledged: false,
      scihub_dialog_open: false,
    }
  );

  // Initialise reducer state when data loads (only once)
  React.useEffect(() => {
    if (data?.selections) {
      dispatch({ type: 'INIT', data: initToggleState(data.selections) });
    }
  }, [data]);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
        <CircularProgress size={20} />
        <Typography variant="body2">Loading database selection…</Typography>
      </Box>
    );
  }

  if (!data) {
    return null;
  }

  const handleSave = () => {
    const selections = data.selections.map((item) => ({
      database_index: item.database_index,
      is_enabled: state.selections[item.database_index] ?? item.is_enabled,
    }));
    updateSelection.mutate({
      selections,
      snowball_enabled: state.snowball_enabled,
      scihub_enabled: state.scihub_enabled,
      scihub_acknowledged: state.scihub_acknowledged,
    });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Database Search Configuration
      </Typography>

      {GROUPS.map((group) => {
        const groupItems = (data.selections ?? []).filter(
          (item) => (INDEX_GROUP[item.database_index] ?? 'Supplementary') === group
        );
        if (groupItems.length === 0) return null;

        return (
          <Box key={group} component="section" sx={{ mb: 2 }}>
            <Typography
              variant="subtitle2"
              color="text.secondary"
              sx={{ mb: 0.5 }}
            >
              {group}
            </Typography>
            {groupItems.map((item) => (
              <IndexRow
                key={item.database_index}
                item={item}
                enabled={state.selections[item.database_index] ?? item.is_enabled}
                onToggle={() =>
                  dispatch({ type: 'TOGGLE_INDEX', index: item.database_index })
                }
              />
            ))}
          </Box>
        );
      })}

      <Box sx={{ mt: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={updateSelection.isPending}
        >
          {updateSelection.isPending ? 'Saving…' : 'Save'}
        </Button>
      </Box>

      {/* SciHub acknowledgment dialog */}
      <Dialog open={state.scihub_dialog_open}>
        <DialogTitle>Enable SciHub Access?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            SciHub provides access to papers that may be behind paywalls.
            Use of SciHub may not be legal in all jurisdictions. By enabling
            SciHub for this study you acknowledge that you are solely
            responsible for compliance with applicable copyright law.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => dispatch({ type: 'DISMISS_SCIHUB_DIALOG' })}>
            Cancel
          </Button>
          <Button
            color="warning"
            onClick={() => dispatch({ type: 'ACKNOWLEDGE_SCIHUB' })}
          >
            I Acknowledge — Enable SciHub
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
