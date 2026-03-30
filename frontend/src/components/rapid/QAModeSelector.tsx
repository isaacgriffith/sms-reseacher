/**
 * QAModeSelector: three-option radio group for selecting the quality appraisal
 * mode in a Rapid Review study (feature 008).
 *
 * Renders inline explanations and consequences for each mode. Shows a
 * ThreatToValidityList preview for QA-related threats when a non-FULL
 * mode is selected.
 */

import { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormLabel from '@mui/material/FormLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Typography from '@mui/material/Typography';

import { useSetQAMode } from '../../hooks/rapid/useQAConfig';
import { useRRThreats } from '../../hooks/rapid/useRRProtocol';
import ThreatToValidityList from './ThreatToValidityList';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type QAMode = 'full' | 'peer_reviewed_only' | 'skipped';

interface QAModeConfig {
  value: QAMode;
  label: string;
  description: string;
  consequence: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const QA_MODE_CONFIGS: QAModeConfig[] = [
  {
    value: 'full',
    label: 'Full Quality Appraisal',
    description: 'Apply the standard quality checklist to all included papers.',
    consequence: 'All papers must be assessed before synthesis can begin.',
  },
  {
    value: 'peer_reviewed_only',
    label: 'Peer-Reviewed Venues Only',
    description: 'Automatically exclude papers from non-peer-reviewed venues.',
    consequence:
      'Non-peer-reviewed papers are excluded. This decision is recorded as a threat to validity.',
  },
  {
    value: 'skipped',
    label: 'Skip Quality Appraisal',
    description: 'No quality appraisal is performed for this Rapid Review.',
    consequence:
      'All included papers advance directly to synthesis. The omission is recorded as a threat to validity.',
  },
];

const QA_THREAT_TYPES = new Set(['QA_SKIPPED', 'QA_SIMPLIFIED']);

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/** Props for {@link QAModeSelector}. */
export interface QAModeSelectorProps {
  /** The Rapid Review study ID. */
  studyId: number;
  /** Currently saved quality appraisal mode. */
  currentMode: QAMode;
}

/**
 * Renders a radio group for selecting the quality appraisal mode.
 *
 * Calls the quality config API on save and shows an inline threat list when
 * a non-FULL mode is active.
 */
export default function QAModeSelector({ studyId, currentMode }: QAModeSelectorProps) {
  const [selectedMode, setSelectedMode] = useState<QAMode>(currentMode);
  const [saved, setSaved] = useState(false);

  const { data: threats = [] } = useRRThreats(studyId);
  const mutation = useSetQAMode(studyId);

  const qaThreats = threats.filter((t) => QA_THREAT_TYPES.has(t.threat_type));

  const handleSave = () => {
    mutation.mutate({ mode: selectedMode }, { onSuccess: () => setSaved(true) });
  };

  return (
    <Box>
      <FormControl component="fieldset" fullWidth>
        <FormLabel component="legend" sx={{ mb: 1.5, fontWeight: 600, color: 'text.primary' }}>
          Quality Appraisal Mode
        </FormLabel>
        <RadioGroup
          value={selectedMode}
          onChange={(e) => {
            setSelectedMode(e.target.value as QAMode);
            setSaved(false);
          }}
        >
          {QA_MODE_CONFIGS.map((cfg) => (
            <Box
              key={cfg.value}
              sx={{
                mb: 2,
                p: 1.5,
                border: '1px solid',
                borderColor: selectedMode === cfg.value ? 'primary.main' : '#e2e8f0',
                borderRadius: '0.5rem',
              }}
            >
              <FormControlLabel
                value={cfg.value}
                control={<Radio size="small" />}
                label={
                  <Typography variant="body2" fontWeight={600}>
                    {cfg.label}
                  </Typography>
                }
                sx={{ mb: 0.25 }}
              />
              <Typography variant="body2" sx={{ ml: 4, color: '#64748b' }}>
                {cfg.description}
              </Typography>
              {selectedMode === cfg.value && cfg.value !== 'full' && (
                <Typography
                  variant="caption"
                  sx={{ ml: 4, display: 'block', mt: 0.5, color: 'warning.dark' }}
                >
                  {cfg.consequence}
                </Typography>
              )}
            </Box>
          ))}
        </RadioGroup>
      </FormControl>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
        <Button
          variant="contained"
          size="small"
          onClick={handleSave}
          disabled={mutation.isPending}
          startIcon={mutation.isPending ? <CircularProgress size={14} /> : undefined}
        >
          Save Mode
        </Button>
        {saved && !mutation.isPending && (
          <Typography variant="caption" sx={{ color: 'success.main' }}>
            Saved
          </Typography>
        )}
      </Box>

      {mutation.isError && (
        <Alert severity="error" sx={{ mt: 1.5 }}>
          Failed to save quality appraisal mode. Please try again.
        </Alert>
      )}

      {selectedMode !== 'full' && qaThreats.length > 0 && (
        <Box sx={{ mt: 2.5 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            Quality Appraisal Threats to Validity
          </Typography>
          <ThreatToValidityList threats={qaThreats} />
        </Box>
      )}
    </Box>
  );
}
