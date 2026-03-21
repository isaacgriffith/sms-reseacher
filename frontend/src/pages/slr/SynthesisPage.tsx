/**
 * SynthesisPage — Phase 5 data synthesis for SLR studies.
 *
 * Manages configuration of new synthesis runs and browsing of past results.
 * Polls for status changes while a result is pending or running.
 *
 * @module SynthesisPage
 */

import React, { useReducer } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import SynthesisConfigForm, { type SynthesisFormData } from '../../components/slr/SynthesisConfigForm';
import ForestPlotViewer from '../../components/slr/ForestPlotViewer';
import FunnelPlotViewer from '../../components/slr/FunnelPlotViewer';
import {
  useSynthesisResults,
  useStartSynthesis,
  useSynthesisResult,
} from '../../hooks/slr/useSynthesis';
import type { SynthesisResult } from '../../services/slr/synthesisApi';

// ---------------------------------------------------------------------------
// State management
// ---------------------------------------------------------------------------

type PageMode = 'config' | 'results';

interface PageState {
  mode: PageMode;
  selectedResultId: number | null;
}

type PageAction =
  | { type: 'SELECT_RESULT'; id: number }
  | { type: 'SHOW_CONFIG' };

function pageReducer(state: PageState, action: PageAction): PageState {
  switch (action.type) {
    case 'SELECT_RESULT':
      return { mode: 'results', selectedResultId: action.id };
    case 'SHOW_CONFIG':
      return { mode: 'config', selectedResultId: null };
    default:
      return state;
  }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const STATUS_COLOR: Record<string, 'default' | 'warning' | 'primary' | 'success' | 'error'> = {
  pending: 'warning',
  running: 'primary',
  completed: 'success',
  failed: 'error',
};

interface ResultsListProps {
  results: SynthesisResult[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}

/** Renders the list of past synthesis results. */
function ResultsList({ results, selectedId, onSelect }: ResultsListProps) {
  if (results.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" data-testid="synthesis-empty">
        No synthesis runs yet. Use the form above to start one.
      </Typography>
    );
  }
  return (
    <Table size="small" aria-label="Synthesis results">
      <TableHead>
        <TableRow>
          <TableCell>ID</TableCell>
          <TableCell>Approach</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Created</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {results.map((r) => (
          <TableRow
            key={r.id}
            selected={r.id === selectedId}
            hover
            onClick={() => onSelect(r.id)}
            sx={{ cursor: 'pointer' }}
          >
            <TableCell>{r.id}</TableCell>
            <TableCell>{r.approach}</TableCell>
            <TableCell>
              <Chip
                label={r.status}
                color={STATUS_COLOR[r.status] ?? 'default'}
                size="small"
              />
            </TableCell>
            <TableCell>{new Date(r.created_at).toLocaleString()}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

interface ResultDetailProps {
  synthesisId: number;
}

/** Loads and renders a selected synthesis result with plots and themes. */
function ResultDetail({ synthesisId }: ResultDetailProps) {
  const { data: result, isLoading } = useSynthesisResult(synthesisId);

  if (isLoading || !result) {
    return <CircularProgress size={20} aria-label="Loading result" />;
  }

  const isInProgress = result.status === 'pending' || result.status === 'running';

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        Result #{result.id} — {result.approach}
      </Typography>

      {isInProgress && (
        <Alert severity="info" sx={{ mb: 1 }}>
          Synthesis is {result.status}. Polling for updates…
        </Alert>
      )}

      {result.status === 'failed' && (
        <Alert severity="error" sx={{ mb: 1 }}>
          {result.error_message ?? 'Synthesis failed.'}
        </Alert>
      )}

      {result.status === 'completed' && (
        <>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 2 }}>
            <Box>
              <Typography variant="caption">Forest Plot</Typography>
              <ForestPlotViewer forestPlotSvg={result.forest_plot_svg ?? null} />
            </Box>
            <Box>
              <Typography variant="caption">Funnel Plot</Typography>
              <FunnelPlotViewer funnelPlotSvg={result.funnel_plot_svg ?? null} />
            </Box>
          </Box>

          {result.qualitative_themes && (
            <QualitativeThemesTable themes={result.qualitative_themes} />
          )}

          {result.sensitivity_analysis && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                Sensitivity Analysis
              </Typography>
              <pre style={{ fontSize: '0.75rem', overflowX: 'auto' }}>
                {JSON.stringify(result.sensitivity_analysis, null, 2)}
              </pre>
            </Box>
          )}
        </>
      )}
    </Box>
  );
}

interface QualitativeThemesTableProps {
  themes: Record<string, unknown>;
}

/** Renders qualitative theme mapping as a simple table. */
function QualitativeThemesTable({ themes }: QualitativeThemesTableProps) {
  const themeMap = (themes as { themes?: Record<string, number[]> }).themes ?? {};
  const entries = Object.entries(themeMap);
  if (entries.length === 0) return null;

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>Themes</Typography>
      <Table size="small" aria-label="Qualitative themes">
        <TableHead>
          <TableRow>
            <TableCell>Theme</TableCell>
            <TableCell>Paper IDs</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {entries.map(([name, ids]) => (
            <TableRow key={name}>
              <TableCell>{name}</TableCell>
              <TableCell>{(ids as number[]).join(', ')}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface SynthesisPageProps {
  /** Integer study ID from the parent page. */
  studyId: number;
}

/**
 * SynthesisPage composes the synthesis configuration form with a list of
 * past synthesis results and detail view for completed runs.
 *
 * @param props - {@link SynthesisPageProps}
 */
export default function SynthesisPage({ studyId }: SynthesisPageProps) {
  const [state, dispatch] = useReducer(pageReducer, {
    mode: 'config',
    selectedResultId: null,
  });

  const { data: listData, isLoading: listLoading } = useSynthesisResults(studyId);
  const startMutation = useStartSynthesis(studyId);

  function handleSubmit(data: SynthesisFormData) {
    const parameters = _buildParameters(data);
    startMutation.mutate(
      { approach: data.approach, parameters },
      {
        onSuccess: (result) => {
          dispatch({ type: 'SELECT_RESULT', id: result.id });
        },
      },
    );
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Data Synthesis
      </Typography>

      <SynthesisConfigForm
        studyId={studyId}
        onSubmit={handleSubmit}
        isSubmitting={startMutation.isPending}
      />

      {startMutation.isError && (
        <Alert severity="error" sx={{ mt: 1 }}>
          {(startMutation.error as Error).message}
        </Alert>
      )}

      <Divider sx={{ my: 3 }} />

      <Typography variant="subtitle2" sx={{ mb: 1 }}>Past Synthesis Runs</Typography>

      {listLoading ? (
        <CircularProgress size={20} />
      ) : (
        <ResultsList
          results={listData?.results ?? []}
          selectedId={state.selectedResultId}
          onSelect={(id) => dispatch({ type: 'SELECT_RESULT', id })}
        />
      )}

      {state.selectedResultId !== null && (
        <ResultDetail synthesisId={state.selectedResultId} />
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

function _buildParameters(data: SynthesisFormData): Record<string, unknown> {
  if (data.approach === 'meta_analysis') {
    return {
      model_type: data.model_type ?? 'auto',
      heterogeneity_threshold: data.heterogeneity_threshold ?? 0.1,
      confidence_interval: data.confidence_interval ?? 0.95,
      papers: (data.papers ?? []).map((p) => ({
        label: p.label,
        effect_size: p.effect_size,
        se: p.se ?? 0,
        ci_lower: p.ci_lower ?? 0,
        ci_upper: p.ci_upper ?? 0,
        weight: p.weight ?? 1.0,
      })),
    };
  }
  if (data.approach === 'descriptive') {
    return {
      papers: (data.papers ?? []).map((p) => ({
        label: p.label,
        effect_size: p.effect_size,
        ci_lower: p.ci_lower ?? 0,
        ci_upper: p.ci_upper ?? 0,
        weight: p.weight ?? 1.0,
        sample_size: p.sample_size,
        unit: p.unit,
      })),
    };
  }
  // qualitative
  return {
    themes: (data.themes ?? []).map((t) => ({
      theme_name: t.theme_name,
      paper_ids: t.paper_ids_text
        .split(',')
        .map((s) => parseInt(s.trim(), 10))
        .filter((n) => !Number.isNaN(n)),
    })),
  };
}
