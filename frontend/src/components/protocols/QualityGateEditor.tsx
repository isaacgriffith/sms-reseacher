/**
 * Form component for creating and editing quality gate configurations (feature 010).
 *
 * Supports MetricThreshold, CompletionCheck, and HumanSignOff gate types,
 * rendering the appropriate config fields per gate type using useWatch.
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useForm, useWatch, Controller } from 'react-hook-form';
import type { QualityGate } from '../../services/protocols/protocolsApi';

const GATE_TYPES = ['metric_threshold', 'completion_check', 'human_sign_off'] as const;
const OPERATORS = ['gt', 'gte', 'lt', 'lte', 'eq', 'neq'] as const;

interface QualityGateEditorProps {
  /** Existing gates on the node. */
  gates: QualityGate[];
  /** Called when a gate is added or updated. */
  onChange: (gates: QualityGate[]) => void;
}

interface GateForm {
  gate_type: string;
  metric_name: string;
  operator: string;
  threshold: string;
  description: string;
  required_role: string;
  prompt: string;
}

/**
 * Editor for quality gates attached to a protocol node.
 *
 * @param props - Component props.
 * @returns Gate list with inline add-gate form.
 */
export default function QualityGateEditor({ gates, onChange }: QualityGateEditorProps) {
  const { control, handleSubmit, reset, register } = useForm<GateForm>({
    defaultValues: {
      gate_type: 'completion_check',
      operator: 'gte',
      threshold: '0',
      metric_name: '',
      description: '',
      required_role: 'study_admin',
      prompt: '',
    },
  });
  const gateType = useWatch({ control, name: 'gate_type' });

  function onAdd(data: GateForm) {
    let config: Record<string, unknown> = {};
    if (data.gate_type === 'metric_threshold') {
      config = {
        gate_type: data.gate_type,
        metric_name: data.metric_name,
        operator: data.operator,
        threshold: parseFloat(data.threshold),
      };
    } else if (data.gate_type === 'completion_check') {
      config = { gate_type: data.gate_type, description: data.description };
    } else {
      config = {
        gate_type: data.gate_type,
        required_role: data.required_role,
        prompt: data.prompt,
      };
    }
    const newGate: QualityGate = { id: Date.now(), gate_type: data.gate_type, config };
    onChange([...gates, newGate]);
    reset();
  }

  function removeGate(id: number) {
    onChange(gates.filter((g) => g.id !== id));
  }

  return (
    <Box>
      {gates.map((g) => (
        <Box key={g.id} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
          <Typography variant="caption" sx={{ flex: 1 }}>
            {g.gate_type}: {JSON.stringify(g.config).slice(0, 60)}
          </Typography>
          <IconButton size="small" onClick={() => removeGate(g.id)} aria-label="remove gate">
            ✕
          </IconButton>
        </Box>
      ))}
      <Box
        component="form"
        onSubmit={handleSubmit(onAdd)}
        sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 1 }}
      >
        <Controller
          name="gate_type"
          control={control}
          render={({ field }) => (
            <Select {...field} size="small" displayEmpty>
              {GATE_TYPES.map((t) => (
                <MenuItem key={t} value={t}>
                  {t}
                </MenuItem>
              ))}
            </Select>
          )}
        />
        {gateType === 'metric_threshold' && (
          <>
            <TextField label="Metric name" size="small" {...register('metric_name')} />
            <Controller
              name="operator"
              control={control}
              render={({ field }) => (
                <Select {...field} size="small">
                  {OPERATORS.map((o) => (
                    <MenuItem key={o} value={o}>
                      {o}
                    </MenuItem>
                  ))}
                </Select>
              )}
            />
            <TextField label="Threshold" size="small" type="number" {...register('threshold')} />
          </>
        )}
        {gateType === 'completion_check' && (
          <TextField label="Description" size="small" {...register('description')} />
        )}
        {gateType === 'human_sign_off' && (
          <>
            <TextField label="Required role" size="small" {...register('required_role')} />
            <TextField label="Prompt" size="small" {...register('prompt')} />
          </>
        )}
        <Button type="submit" size="small" variant="outlined">
          Add Gate
        </Button>
      </Box>
    </Box>
  );
}
