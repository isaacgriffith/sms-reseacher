/**
 * Theme selector: Light / Dark / System toggle button group.
 * Reads and updates via ThemeContext.
 */

import Box from '@mui/material/Box';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import Typography from '@mui/material/Typography';

import type { ThemePreference } from '../../theme/ThemeContext';
import { useThemeContext } from '../../theme/ThemeContext';

const OPTIONS: { value: ThemePreference; label: string }[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System Default' },
];

export interface ThemeSelectorProps {
  /** Override for testing — if omitted, reads from ThemeContext. */
  value?: ThemePreference;
  /** Override for testing — if omitted, writes to ThemeContext. */
  onChange?: (pref: ThemePreference) => void;
}

export default function ThemeSelector({ value: valueProp, onChange: onChangeProp }: ThemeSelectorProps) {
  const { preference, setThemePreference } = useThemeContext();

  const current = valueProp ?? preference;
  const handleChange = onChangeProp ?? setThemePreference;

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        Choose how the application looks. "System Default" follows your OS setting.
      </Typography>
      <ToggleButtonGroup
        value={current}
        exclusive
        onChange={(_, newPref: ThemePreference | null) => {
          if (newPref !== null) handleChange(newPref);
        }}
        aria-label="theme preference"
        size="small"
      >
        {OPTIONS.map(({ value, label }) => (
          <ToggleButton key={value} value={value} aria-label={label}>
            {label}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </Box>
  );
}
