/**
 * SystemMessageEditor — multiline template editor for Jinja2 system message
 * templates.  Lists available `{{ variable }}` placeholders as helper text
 * and exposes an Undo button.
 *
 * Wrapped with React.memo + forwardRef so parents can programmatically focus
 * the textarea via useImperativeHandle.
 */

import React, { useRef, useImperativeHandle } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

/** Available Jinja2 template variables for the system message. */
const AVAILABLE_VARS = [
  '{{ role_name }}',
  '{{ role_description }}',
  '{{ persona_name }}',
  '{{ persona_description }}',
  '{{ domain }}',
  '{{ study_type }}',
];

/** Props for {@link SystemMessageEditor}. */
interface SystemMessageEditorProps {
  /** Current template string value. */
  value: string;
  /** Called when the user edits the template. */
  onChange: (val: string) => void;
  /** Called when the user clicks the Undo button. */
  onUndo: () => void;
  /** Whether an undo action is available. */
  canUndo: boolean;
  /** Optional label for the text field. */
  label?: string;
  /** Whether the editor is in a disabled state. */
  disabled?: boolean;
}

/** Imperative handle exposed to parent components. */
export interface SystemMessageEditorHandle {
  /** Programmatically focus the textarea. */
  focus: () => void;
}

/**
 * System message template editor with variable helper and undo support.
 *
 * @param props - {@link SystemMessageEditorProps}
 * @param ref   - Optional ref forwarded to {@link SystemMessageEditorHandle}.
 */
const SystemMessageEditor = React.memo(
  React.forwardRef<SystemMessageEditorHandle, SystemMessageEditorProps>(
    function SystemMessageEditor(
      { value, onChange, onUndo, canUndo, label = 'System Message Template', disabled = false },
      ref,
    ) {
      const inputRef = useRef<HTMLTextAreaElement>(null);

      useImperativeHandle(ref, () => ({
        focus: () => {
          inputRef.current?.focus();
        },
      }));

      return (
        <Box>
          <TextField
            label={label}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            multiline
            minRows={6}
            fullWidth
            disabled={disabled}
            inputRef={inputRef}
            inputProps={{ 'aria-label': label }}
          />
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Available variables: {AVAILABLE_VARS.join(', ')}
            </Typography>
            <Button
              size="small"
              variant="outlined"
              onClick={onUndo}
              disabled={!canUndo || disabled}
            >
              Undo
            </Button>
          </Box>
        </Box>
      );
    },
  ),
);

export default SystemMessageEditor;
