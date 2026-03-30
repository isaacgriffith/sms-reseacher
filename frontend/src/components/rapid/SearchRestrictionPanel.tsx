/**
 * SearchRestrictionPanel: checklist UI for configuring Rapid Review search
 * restrictions (year range, language, geography, study design).
 *
 * Each restriction type can be toggled on/off. When toggled on, a text field
 * for the source detail is shown. Saving calls the search-config endpoint
 * and refreshes the threat list.
 */

import { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import CircularProgress from '@mui/material/CircularProgress';
import FormControlLabel from '@mui/material/FormControlLabel';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import { useRRThreats } from '../../hooks/rapid/useRRProtocol';
import { useUpdateSearchConfig } from '../../hooks/rapid/useSearchConfig';
import ThreatToValidityList from './ThreatToValidityList';

interface RestrictionConfig {
  threatType: string;
  label: string;
  placeholder: string;
}

const RESTRICTION_CONFIGS: RestrictionConfig[] = [
  { threatType: 'YEAR_RANGE', label: 'Year Range', placeholder: 'e.g. 2015–2025' },
  { threatType: 'LANGUAGE', label: 'Language', placeholder: 'e.g. English only' },
  { threatType: 'GEOGRAPHY', label: 'Geography', placeholder: 'e.g. EU countries' },
  { threatType: 'STUDY_DESIGN', label: 'Study Design', placeholder: 'e.g. RCT only' },
];

interface RestrictionState {
  enabled: boolean;
  detail: string;
}

interface SearchRestrictionPanelProps {
  studyId: number;
}

export default function SearchRestrictionPanel({ studyId }: SearchRestrictionPanelProps) {
  const { data: threats = [] } = useRRThreats(studyId);
  const mutation = useUpdateSearchConfig(studyId);

  const [state, setState] = useState<Record<string, RestrictionState>>(() => {
    const initial: Record<string, RestrictionState> = {};
    for (const cfg of RESTRICTION_CONFIGS) {
      const existing = threats.find((t) => t.threat_type === cfg.threatType);
      initial[cfg.threatType] = {
        enabled: !!existing,
        detail: existing?.source_detail ?? '',
      };
    }
    return initial;
  });

  const [saved, setSaved] = useState(false);

  const handleToggle = (threatType: string) => {
    setState((prev) => ({
      ...prev,
      [threatType]: { ...prev[threatType], enabled: !prev[threatType].enabled },
    }));
    setSaved(false);
  };

  const handleDetailChange = (threatType: string, value: string) => {
    setState((prev) => ({
      ...prev,
      [threatType]: { ...prev[threatType], detail: value },
    }));
    setSaved(false);
  };

  const handleSave = () => {
    const restrictions = RESTRICTION_CONFIGS.filter((cfg) => state[cfg.threatType]?.enabled).map(
      (cfg) => ({
        type: cfg.threatType,
        source_detail: state[cfg.threatType]?.detail ?? '',
      }),
    );
    mutation.mutate(
      { restrictions },
      {
        onSuccess: () => setSaved(true),
      },
    );
  };

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
        Search Restrictions
      </Typography>
      <Typography variant="body2" sx={{ mb: 2, color: '#64748b' }}>
        Applying restrictions narrows the search and is automatically recorded as a threat to
        validity.
      </Typography>

      {RESTRICTION_CONFIGS.map((cfg) => (
        <Box key={cfg.threatType} sx={{ mb: 1.5 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={state[cfg.threatType]?.enabled ?? false}
                onChange={() => handleToggle(cfg.threatType)}
                size="small"
              />
            }
            label={cfg.label}
          />
          {state[cfg.threatType]?.enabled && (
            <TextField
              size="small"
              fullWidth
              placeholder={cfg.placeholder}
              value={state[cfg.threatType]?.detail ?? ''}
              onChange={(e) => handleDetailChange(cfg.threatType, e.target.value)}
              sx={{ mt: 0.5, ml: 4 }}
            />
          )}
        </Box>
      ))}

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
        <Button
          variant="contained"
          size="small"
          onClick={handleSave}
          disabled={mutation.isPending}
          startIcon={mutation.isPending ? <CircularProgress size={14} /> : undefined}
        >
          Save Restrictions
        </Button>
        {saved && !mutation.isPending && (
          <Typography variant="caption" sx={{ color: 'success.main' }}>
            Saved
          </Typography>
        )}
      </Box>

      {mutation.isError && (
        <Alert severity="error" sx={{ mt: 1.5 }}>
          Failed to save restrictions. Please try again.
        </Alert>
      )}

      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Active Threats to Validity
        </Typography>
        <ThreatToValidityList threats={threats} />
      </Box>
    </Box>
  );
}
