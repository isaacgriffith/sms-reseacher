/**
 * Side navigation: avatar, Research Groups link, phase nav for active study.
 */

import { NavLink, useNavigate } from 'react-router-dom';
import { clearSession, useAuthStore } from '../../services/auth';
import Box from '@mui/material/Box';
import Avatar from '@mui/material/Avatar';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Button from '@mui/material/Button';

export default function SideNav() {
  const user = useAuthStore((s) => s.user);
  const navigate = useNavigate();

  const handleLogout = () => {
    clearSession();
    navigate('/login', { replace: true });
  };

  const initials = user?.displayName
    ? user.displayName
        .split(' ')
        .map((n) => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase()
    : '?';

  return (
    <Box
      component="nav"
      sx={{
        width: '220px',
        minHeight: '100vh',
        background: '#1e293b',
        color: '#f8fafc',
        display: 'flex',
        flexDirection: 'column',
        padding: '1rem',
        boxSizing: 'border-box',
        flexShrink: 0,
      }}
    >
      {/* Avatar + name */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
        <Avatar
          sx={{
            width: 40,
            height: 40,
            background: '#2563eb',
            fontWeight: 700,
            fontSize: '0.875rem',
            flexShrink: 0,
          }}
        >
          {initials}
        </Avatar>
        <Typography sx={{ fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {user?.displayName ?? 'Unknown'}
        </Typography>
      </Box>

      {/* Navigation links */}
      <List sx={{ listStyle: 'none', padding: 0, margin: 0, flex: 1 }}>
        <ListItem sx={{ marginBottom: '0.5rem', padding: 0 }}>
          <NavLink
            to="/groups"
            style={({ isActive }) => ({
              display: 'block',
              padding: '0.5rem 0.75rem',
              borderRadius: '0.375rem',
              color: isActive ? '#fff' : '#cbd5e1',
              background: isActive ? '#334155' : 'transparent',
              textDecoration: 'none',
              fontSize: '0.9375rem',
              width: '100%',
            })}
          >
            Research Groups
          </NavLink>
        </ListItem>
        <ListItem sx={{ marginBottom: '0.5rem', padding: 0 }}>
          <NavLink
            to="/preferences"
            style={({ isActive }) => ({
              display: 'block',
              padding: '0.5rem 0.75rem',
              borderRadius: '0.375rem',
              color: isActive ? '#fff' : '#cbd5e1',
              background: isActive ? '#334155' : 'transparent',
              textDecoration: 'none',
              fontSize: '0.9375rem',
              width: '100%',
            })}
          >
            Preferences
          </NavLink>
        </ListItem>
        <ListItem sx={{ marginBottom: '0.5rem', padding: 0 }}>
          <NavLink
            to="/api-docs"
            style={({ isActive }) => ({
              display: 'block',
              padding: '0.5rem 0.75rem',
              borderRadius: '0.375rem',
              color: isActive ? '#fff' : '#cbd5e1',
              background: isActive ? '#334155' : 'transparent',
              textDecoration: 'none',
              fontSize: '0.9375rem',
              width: '100%',
            })}
          >
            API Docs
          </NavLink>
        </ListItem>
      </List>


      {/* Logout */}
      <Button
        onClick={handleLogout}
        variant="outlined"
        sx={{
          padding: '0.5rem 0.75rem',
          border: '1px solid #475569',
          color: '#cbd5e1',
          fontSize: '0.875rem',
          textAlign: 'left',
          justifyContent: 'flex-start',
          '&:hover': { border: '1px solid #cbd5e1' },
        }}
      >
        Sign out
      </Button>
    </Box>
  );
}
