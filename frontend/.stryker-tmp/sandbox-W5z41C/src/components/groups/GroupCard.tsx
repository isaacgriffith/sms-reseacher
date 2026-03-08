/**
 * Card representing a single research group.
 */
// @ts-nocheck


import { useNavigate } from 'react-router-dom';

export interface GroupSummary {
  id: number;
  name: string;
  role: string;
  study_count: number;
}

interface GroupCardProps {
  group: GroupSummary;
}

export default function GroupCard({ group }: GroupCardProps) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/groups/${group.id}/studies`)}
      style={{
        padding: '1.25rem',
        border: '1px solid #e2e8f0',
        borderRadius: '0.5rem',
        cursor: 'pointer',
        background: '#fff',
        transition: 'box-shadow 0.15s',
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLDivElement).style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLDivElement).style.boxShadow = 'none';
      }}
    >
      <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.125rem' }}>{group.name}</h3>
      <p style={{ margin: '0 0 0.25rem', color: '#475569', fontSize: '0.875rem' }}>
        {group.study_count} {group.study_count === 1 ? 'study' : 'studies'}
      </p>
      <span
        style={{
          display: 'inline-block',
          padding: '0.125rem 0.5rem',
          background: group.role === 'admin' ? '#dbeafe' : '#f1f5f9',
          color: group.role === 'admin' ? '#1d4ed8' : '#475569',
          borderRadius: '9999px',
          fontSize: '0.75rem',
          fontWeight: 600,
          textTransform: 'capitalize',
        }}
      >
        {group.role}
      </span>
    </div>
  );
}
