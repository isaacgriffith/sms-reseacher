/**
 * Card representing a single research group.
 */

import { useNavigate } from 'react-router-dom';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';

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
    <Card
      onClick={() => navigate(`/groups/${group.id}/studies`)}
      sx={{
        cursor: 'pointer',
        transition: 'box-shadow 0.15s',
        '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.1)' },
      }}
      variant="outlined"
    >
      <CardContent sx={{ padding: '1.25rem' }}>
        <Typography variant="h6" sx={{ margin: '0 0 0.5rem', fontSize: '1.125rem' }}>{group.name}</Typography>
        <Typography sx={{ margin: '0 0 0.25rem', color: '#475569', fontSize: '0.875rem' }}>
          {group.study_count} {group.study_count === 1 ? 'study' : 'studies'}
        </Typography>
        <Chip
          label={group.role}
          size="small"
          sx={{
            background: group.role === 'admin' ? '#dbeafe' : '#f1f5f9',
            color: group.role === 'admin' ? '#1d4ed8' : '#475569',
            fontSize: '0.75rem',
            fontWeight: 600,
            textTransform: 'capitalize',
            height: 'auto',
            padding: '0.125rem 0',
          }}
        />
      </CardContent>
    </Card>
  );
}
