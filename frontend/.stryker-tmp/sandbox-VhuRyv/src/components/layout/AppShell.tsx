/**
 * Application shell: side navigation + main content outlet.
 */
// @ts-nocheck


import { Outlet } from 'react-router-dom';
import SideNav from './SideNav';

export default function AppShell() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <SideNav />
      <main style={{ flex: 1, padding: '2rem', boxSizing: 'border-box', overflowY: 'auto' }}>
        <Outlet />
      </main>
    </div>
  );
}
