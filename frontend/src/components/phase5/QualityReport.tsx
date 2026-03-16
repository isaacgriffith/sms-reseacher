/**
 * QualityReport: displays a quality evaluation report with rubric score cards,
 * per-rubric justification text, and a prioritised recommendation list.
 */

import { useState } from 'react';
import { api } from '../../services/api';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface RubricDetail {
  score: number;
  justification: string;
}

interface Recommendation {
  priority: number;
  action: string;
  target_rubric: string;
}

export interface QualityReportData {
  id: number;
  study_id: number;
  version: number;
  score_need_for_review: number;
  score_search_strategy: number;
  score_search_evaluation: number;
  score_extraction_classification: number;
  score_study_validity: number;
  total_score: number;
  rubric_details: Record<string, RubricDetail> | null;
  recommendations: Recommendation[] | null;
  generated_at: string;
}

interface QualityReportSummary {
  id: number;
  version: number;
  total_score: number;
  generated_at: string;
}

interface QualityReportProps {
  studyId: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RUBRICS: Array<{ key: keyof QualityReportData; name: string; max: number; rubricKey: string }> = [
  { key: 'score_need_for_review', name: 'Need for Review', max: 2, rubricKey: 'need_for_review' },
  { key: 'score_search_strategy', name: 'Search Strategy', max: 2, rubricKey: 'search_strategy' },
  { key: 'score_search_evaluation', name: 'Search Evaluation', max: 3, rubricKey: 'search_evaluation' },
  { key: 'score_extraction_classification', name: 'Extraction & Classification', max: 3, rubricKey: 'extraction_classification' },
  { key: 'score_study_validity', name: 'Study Validity', max: 1, rubricKey: 'study_validity' },
];

const PRIORITY_LABELS: Record<number, string> = { 1: 'High', 2: 'Medium', 3: 'Low' };

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ScoreBar({ score, max }: { score: number; max: number }) {
  const pct = max > 0 ? (score / max) * 100 : 0;
  const color = pct >= 67 ? '#16a34a' : pct >= 34 ? '#d97706' : '#dc2626';
  return (
    <Box sx={{ marginTop: '0.375rem' }}>
      <Box sx={{ height: '6px', background: '#e2e8f0', borderRadius: '9999px', overflow: 'hidden' }}>
        <Box sx={{ height: '100%', width: `${pct}%`, background: color, borderRadius: '9999px', transition: 'width 0.3s' }} />
      </Box>
    </Box>
  );
}

function RubricCard({ rubric, report }: { rubric: typeof RUBRICS[number]; report: QualityReportData }) {
  const score = report[rubric.key] as number;
  const detail = report.rubric_details?.[rubric.rubricKey];
  const pct = rubric.max > 0 ? score / rubric.max : 0;
  const bg = pct >= 0.67 ? '#dcfce7' : pct >= 0.34 ? '#fef9c3' : '#fee2e2';
  const color = pct >= 0.67 ? '#16a34a' : pct >= 0.34 ? '#b45309' : '#dc2626';
  return (
    <Paper variant="outlined" sx={{ border: '1px solid #e2e8f0', borderRadius: '0.375rem', padding: '0.75rem 1rem' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography component="span" sx={{ fontWeight: 600, fontSize: '0.875rem', color: '#374151' }}>{rubric.name}</Typography>
        <Typography component="span" sx={{ fontWeight: 700, fontSize: '0.875rem', padding: '0.125rem 0.5rem', borderRadius: '9999px', background: bg, color }}>
          {score}/{rubric.max}
        </Typography>
      </Box>
      <ScoreBar score={score} max={rubric.max} />
      {detail?.justification && (
        <Typography sx={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: '#6b7280', lineHeight: 1.5 }}>
          {detail.justification}
        </Typography>
      )}
    </Paper>
  );
}

function RecommendationList({ recommendations }: { recommendations: Recommendation[] }) {
  if (!recommendations.length) {
    return <Typography sx={{ color: '#6b7280', fontSize: '0.875rem' }}>No recommendations — all rubrics scored well.</Typography>;
  }
  const sorted = [...recommendations].sort((a, b) => a.priority - b.priority);
  const priorityColors: Record<number, [string, string]> = {
    1: ['#fee2e2', '#dc2626'],
    2: ['#fef9c3', '#b45309'],
    3: ['#f0fdf4', '#16a34a'],
  };
  return (
    <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
      {sorted.map((rec, i) => {
        const [bg, color] = priorityColors[rec.priority] ?? ['#f3f4f6', '#6b7280'];
        return (
          <li key={i}>
            <Paper variant="outlined" sx={{ border: '1px solid #e2e8f0', borderRadius: '0.375rem', padding: '0.75rem 1rem' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                <Typography component="span" sx={{ fontSize: '0.6875rem', fontWeight: 700, padding: '0.125rem 0.5rem', borderRadius: '9999px', background: bg, color }}>
                  {PRIORITY_LABELS[rec.priority] ?? `P${rec.priority}`}
                </Typography>
                <Typography component="span" sx={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                  {rec.target_rubric.replace(/_/g, ' ')}
                </Typography>
              </Box>
              <Typography sx={{ margin: 0, fontSize: '0.875rem', color: '#374151' }}>{rec.action}</Typography>
              <Button
                variant="outlined"
                size="small"
                sx={{ marginTop: '0.5rem', fontSize: '0.75rem', fontWeight: 600, color: '#374151', borderColor: '#d1d5db', padding: '0.25rem 0.75rem' }}
                onClick={() => alert(`Action: ${rec.action}`)}
              >
                Address
              </Button>
            </Paper>
          </li>
        );
      })}
    </ol>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function QualityReport({ studyId }: QualityReportProps) {
  const [summaries, setSummaries] = useState<QualityReportSummary[]>([]);
  const [selectedReport, setSelectedReport] = useState<QualityReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<QualityReportSummary[]>(`/api/v1/studies/${studyId}/quality-reports`);
      setSummaries(data);
      if (data.length > 0) {
        await loadDetail(data[0].id);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load quality reports');
    } finally {
      setLoading(false);
    }
  };

  const loadDetail = async (reportId: number) => {
    try {
      const detail = await api.get<QualityReportData>(`/api/v1/studies/${studyId}/quality-reports/${reportId}`);
      setSelectedReport(detail);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load report details');
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      await api.post(`/api/v1/studies/${studyId}/quality-reports`, {});
      await loadReports();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start quality evaluation');
    } finally {
      setGenerating(false);
    }
  };

  // Load on first render
  useState(() => { loadReports(); });

  return (
    <Paper variant="outlined" sx={{ padding: '1.25rem', background: '#fff', border: '1px solid #e2e8f0', borderRadius: '0.5rem' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <Box>
          <Typography variant="h5" sx={{ margin: 0, fontSize: '1.125rem', fontWeight: 700, color: '#111827' }}>Quality Evaluation</Typography>
          {selectedReport && (
            <Typography component="span" sx={{ fontSize: '0.75rem', color: '#9ca3af' }}>
              Version {selectedReport.version} — Total: {selectedReport.total_score}/11
            </Typography>
          )}
        </Box>
        <Button
          variant="contained"
          disabled={generating}
          onClick={handleGenerate}
          aria-label="Run Evaluation"
          sx={{
            background: generating ? '#93c5fd' : '#2563eb',
            fontSize: '0.875rem',
            fontWeight: 600,
          }}
        >
          {generating ? 'Evaluating…' : 'Run Evaluation'}
        </Button>
      </Box>

      {/* Error */}
      {error && <Typography sx={{ color: '#dc2626', fontSize: '0.875rem', marginBottom: '0.75rem' }}>{error}</Typography>}

      {/* Version picker */}
      {summaries.length > 1 && (
        <Box sx={{ marginBottom: '1rem' }}>
          <Typography component="label" sx={{ fontSize: '0.8125rem', color: '#6b7280', marginRight: '0.5rem' }}>
            Report version:
          </Typography>
          <select
            style={{
              padding: '0.25rem 0.5rem',
              border: '1px solid #d1d5db',
              borderRadius: '0.25rem',
              fontSize: '0.8125rem',
            }}
            onChange={(e) => loadDetail(Number(e.target.value))}
            value={selectedReport?.id ?? ''}
          >
            {summaries.map((s) => (
              <option key={s.id} value={s.id}>
                v{s.version} — {s.total_score}/11 ({new Date(s.generated_at).toLocaleDateString()})
              </option>
            ))}
          </select>
        </Box>
      )}

      {loading && <Typography sx={{ color: '#6b7280' }}>Loading…</Typography>}

      {selectedReport && (
        <>
          {/* Rubric score cards */}
          <Box component="section" aria-label="Rubric scores">
            <Typography variant="subtitle1" sx={{ fontSize: '0.9375rem', fontWeight: 600, color: '#374151', margin: '0 0 0.75rem' }}>Rubric Scores</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
              {RUBRICS.map((rubric) => (
                <RubricCard key={rubric.key} rubric={rubric} report={selectedReport} />
              ))}
            </Box>
          </Box>

          {/* Recommendations */}
          <Box component="section" aria-label="Recommendations" sx={{ marginTop: '1.5rem' }}>
            <Typography variant="subtitle1" sx={{ fontSize: '0.9375rem', fontWeight: 600, color: '#374151', margin: '0 0 0.75rem' }}>Improvement Recommendations</Typography>
            <RecommendationList recommendations={selectedReport.recommendations ?? []} />
          </Box>
        </>
      )}

      {!loading && !selectedReport && summaries.length === 0 && (
        <Box sx={{ textAlign: 'center', padding: '2rem 0', color: '#9ca3af' }}>
          <Typography>No quality evaluations yet.</Typography>
          <Typography sx={{ fontSize: '0.875rem' }}>Click "Run Evaluation" to score this study.</Typography>
        </Box>
      )}
    </Paper>
  );
}
