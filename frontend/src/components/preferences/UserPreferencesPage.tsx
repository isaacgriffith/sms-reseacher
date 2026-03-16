/**
 * User preferences page with tabs for Password, Theme, and Two-Factor Authentication.
 */

import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';

import PasswordChangeForm from './PasswordChangeForm';
import ThemeSelector from './ThemeSelector';
import TwoFactorSettings from './TwoFactorSettings';
import { getPreferences } from '../../services/preferences';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export interface UserPreferencesPageProps {
  initialTab?: number;
}

export default function UserPreferencesPage({ initialTab = 0 }: UserPreferencesPageProps) {
  const [tab, setTab] = useState(initialTab);
  const queryClient = useQueryClient();

  const { data: prefs, isLoading } = useQuery({
    queryKey: ['preferences'],
    queryFn: getPreferences,
  });

  const handleTotpStatusChange = () => {
    void queryClient.invalidateQueries({ queryKey: ['preferences'] });
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        Preferences
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tab} onChange={(_, v: number) => setTab(v)} aria-label="preferences tabs">
          <Tab label="Password" />
          <Tab label="Theme" />
          <Tab label="Two-Factor Authentication" />
        </Tabs>
      </Box>

      <TabPanel value={tab} index={0}>
        <PasswordChangeForm />
      </TabPanel>

      <TabPanel value={tab} index={1}>
        <ThemeSelector />
      </TabPanel>

      <TabPanel value={tab} index={2}>
        {isLoading ? (
          <CircularProgress size={24} />
        ) : (
          <TwoFactorSettings
            totpEnabled={prefs?.totp_enabled ?? false}
            onStatusChange={handleTotpStatusChange}
          />
        )}
      </TabPanel>
    </Box>
  );
}
