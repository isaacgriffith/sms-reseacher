/**
 * Form component for building conditional protocol edge conditions (feature 010).
 *
 * Renders output_name selector, operator selector, and numeric value input.
 * Null condition means unconditional edge (all fields optional).
 */

import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useForm, useWatch, Controller } from 'react-hook-form';
import type { EdgeCondition } from '../../services/protocols/protocolsApi';

const OPERATORS = ['gt', 'gte', 'lt', 'lte', 'eq', 'neq'] as const;

interface EdgeConditionBuilderProps {
  /** Available output names from the source node. */
  sourceOutputNames: string[];
  /** Current condition value (null = unconditional). */
  value: EdgeCondition | null;
  /** Called when condition changes. */
  onChange: (condition: EdgeCondition | null) => void;
}

interface ConditionForm {
  conditional: boolean;
  output_name: string;
  operator: string;
  value: string;
}

/**
 * Form for building an optional edge condition triple.
 *
 * @param props - Component props.
 * @returns Condition builder form.
 */
export default function EdgeConditionBuilder({
  sourceOutputNames,
  value,
  onChange,
}: EdgeConditionBuilderProps) {
  const { control, register, handleSubmit } = useForm<ConditionForm>({
    defaultValues: {
      conditional: value !== null,
      output_name: value?.output_name ?? sourceOutputNames[0] ?? '',
      operator: value?.operator ?? 'gte',
      value: value?.value?.toString() ?? '0',
    },
  });
  const isConditional = useWatch({ control, name: 'conditional' });

  function onApply(data: ConditionForm) {
    if (!data.conditional) {
      onChange(null);
      return;
    }
    onChange({
      output_name: data.output_name,
      operator: data.operator,
      value: parseFloat(data.value),
    });
  }

  return (
    <Box
      component="form"
      onBlur={handleSubmit(onApply)}
      sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}
    >
      <FormControlLabel
        control={
          <Controller
            name="conditional"
            control={control}
            render={({ field }) => <Checkbox {...field} checked={field.value} size="small" />}
          />
        }
        label={<Typography variant="caption">Conditional edge</Typography>}
      />
      {isConditional && (
        <>
          <Controller
            name="output_name"
            control={control}
            render={({ field }) => (
              <Select {...field} size="small" displayEmpty>
                {sourceOutputNames.map((n) => (
                  <MenuItem key={n} value={n}>
                    {n}
                  </MenuItem>
                ))}
                {sourceOutputNames.length === 0 && <MenuItem value="">— no outputs —</MenuItem>}
              </Select>
            )}
          />
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
          <TextField label="Value" size="small" type="number" {...register('value')} />
        </>
      )}
    </Box>
  );
}
