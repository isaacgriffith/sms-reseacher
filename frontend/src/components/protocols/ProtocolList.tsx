/**
 * MUI List component displaying available research protocols (feature 010).
 *
 * Shows protocol name, study_type badge, and is_default_template indicator.
 * Used in ProtocolLibraryPage.
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import type { ProtocolListItem } from '../../services/protocols/protocolsApi';

interface ProtocolListProps {
  /** List of protocol items to render. */
  protocols: ProtocolListItem[];
  /** Called when a protocol item is selected. */
  onSelect?: (protocol: ProtocolListItem) => void;
  /** Called when the Copy button is clicked for a protocol. */
  onCopy?: (protocol: ProtocolListItem) => void;
  /** Called when the Assign button is clicked for a protocol. */
  onAssign?: (protocol: ProtocolListItem) => void;
  /** Called when the Export button is clicked for a protocol. */
  onExport?: (protocol: ProtocolListItem) => void;
}

/**
 * MUI List of research protocol items with optional Copy and Assign actions.
 *
 * @param props - Component props.
 * @returns MUI List element.
 */
export default function ProtocolList({
  protocols,
  onSelect,
  onCopy,
  onAssign,
  onExport,
}: ProtocolListProps) {
  if (protocols.length === 0) {
    return <Typography sx={{ color: 'text.secondary' }}>No protocols found.</Typography>;
  }

  return (
    <List disablePadding>
      {protocols.map((p) => (
        <ListItem
          key={p.id}
          disablePadding
          divider
          secondaryAction={
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {onExport && (
                <Button
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onExport(p);
                  }}
                >
                  Export
                </Button>
              )}
              {onAssign && (
                <Button
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onAssign(p);
                  }}
                >
                  Assign
                </Button>
              )}
              {onCopy && (
                <Button
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onCopy(p);
                  }}
                >
                  Copy
                </Button>
              )}
            </Box>
          }
        >
          <ListItemButton onClick={() => onSelect?.(p)}>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <span>{p.name}</span>
                  <Chip label={p.study_type} size="small" variant="outlined" />
                  {p.is_default_template && <Chip label="Default" size="small" color="success" />}
                </Box>
              }
              secondary={`Version ${p.version_id} · Updated ${new Date(p.updated_at).toLocaleDateString()}`}
            />
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
}
