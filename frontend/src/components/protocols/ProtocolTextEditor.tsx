/**
 * YAML text editor pane for the dual-pane protocol editor (feature 010).
 *
 * Provides a controlled textarea for editing protocol YAML.
 * Changes are dispatched via the debounced SET_YAML action from useProtocolEditor
 * so graph state stays in sync after a 300ms pause.
 */

import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import Typography from '@mui/material/Typography';

interface ProtocolTextEditorProps {
  /** Current YAML text value (controlled). */
  value: string;
  /** Called on every keystroke with the new raw text (debounce is caller's responsibility). */
  onChange: (yaml: string) => void;
  /** Optional parse error message to display below the textarea. */
  parseError: string | null;
}

/**
 * Monospace textarea YAML editor for the protocol dual-pane editor.
 *
 * @param props - Component props.
 * @returns MUI-styled textarea with optional error alert.
 */
export default function ProtocolTextEditor({
  value,
  onChange,
  parseError,
}: ProtocolTextEditorProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        YAML Editor
      </Typography>
      <Box
        component="textarea"
        value={value}
        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => onChange(e.target.value)}
        spellCheck={false}
        sx={{
          flex: 1,
          fontFamily: 'monospace',
          fontSize: 13,
          p: 1,
          border: '1px solid',
          borderColor: parseError ? 'error.main' : 'divider',
          borderRadius: 1,
          resize: 'none',
          outline: 'none',
          background: '#fafafa',
          width: '100%',
          boxSizing: 'border-box',
          '&:focus': { borderColor: 'primary.main' },
        }}
      />
      {parseError && (
        <Alert severity="error" sx={{ mt: 0.5, py: 0, fontSize: 12 }}>
          {parseError}
        </Alert>
      )}
    </Box>
  );
}
