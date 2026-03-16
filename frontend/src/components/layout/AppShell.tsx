/**
 * Application shell: side navigation + main content outlet.
 */

import { Outlet } from 'react-router-dom';
import SideNav from './SideNav';
import Box from '@mui/material/Box';

export default function AppShell() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <SideNav />
      <Box component="main" sx={{ flex: 1, padding: '2rem', boxSizing: 'border-box', overflowY: 'auto' }}>
        <Outlet />
      </Box>
    </Box>
  );
}
