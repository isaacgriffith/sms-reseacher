/**
 * Side navigation: avatar, Research Groups link, phase nav for active study.
 */
// @ts-nocheck


import { NavLink, useNavigate } from 'react-router-dom';
import { clearSession, useAuthStore } from '../../services/auth';

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
    <nav
      style={{
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
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            background: '#2563eb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: '0.875rem',
            flexShrink: 0,
          }}
        >
          {initials}
        </div>
        <span style={{ fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {user?.displayName ?? 'Unknown'}
        </span>
      </div>

      {/* Navigation links */}
      <ul style={{ listStyle: 'none', padding: 0, margin: 0, flex: 1 }}>
        <li style={{ marginBottom: '0.5rem' }}>
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
            })}
          >
            Research Groups
          </NavLink>
        </li>
      </ul>


      {/* Logout */}
      <button
        onClick={handleLogout}
        style={{
          padding: '0.5rem 0.75rem',
          background: 'transparent',
          border: '1px solid #475569',
          borderRadius: '0.375rem',
          color: '#cbd5e1',
          cursor: 'pointer',
          fontSize: '0.875rem',
          textAlign: 'left',
        }}
      >
        Sign out
      </button>
    </nav>
  );
}
