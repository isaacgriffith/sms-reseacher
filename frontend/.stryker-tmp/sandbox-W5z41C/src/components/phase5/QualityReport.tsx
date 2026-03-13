/**
 * QualityReport: displays a quality evaluation report with rubric score cards,
 * per-rubric justification text, and a prioritised recommendation list.
 */
// @ts-nocheck


import { useState } from 'react';
import { api } from '../../services/api';

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
    <div style={{ marginTop: '0.375rem' }}>
      <div style={{ height: '6px', background: '#e2e8f0', borderRadius: '9999px', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: '9999px', transition: 'width 0.3s' }} />
      </div>
    </div>
  );
}

function RubricCard({ rubric, report }: { rubric: typeof RUBRICS[number]; report: QualityReportData }) {
  const score = report[rubric.key] as number;
  const detail = report.rubric_details?.[rubric.rubricKey];
  return (
    <div style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontWeight: 600, fontSize: '0.875rem', color: '#374151' }}>{rubric.name}</span>
        <span style={scoreBadgeStyle(score, rubric.max)}>
          {score}/{rubric.max}
        </span>
      </div>
      <ScoreBar score={score} max={rubric.max} />
      {detail?.justification && (
        <p style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: '#6b7280', lineHeight: 1.5 }}>
          {detail.justification}
        </p>
      )}
    </div>
  );
}

function RecommendationList({ recommendations }: { recommendations: Recommendation[] }) {
  if (!recommendations.length) {
    return <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>No recommendations — all rubrics scored well.</p>;
  }
  const sorted = [...recommendations].sort((a, b) => a.priority - b.priority);
  return (
    <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
      {sorted.map((rec, i) => (
        <li key={i} style={recItemStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={priorityBadgeStyle(rec.priority)}>{PRIORITY_LABELS[rec.priority] ?? `P${rec.priority}`}</span>
            <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
              {rec.target_rubric.replace(/_/g, ' ')}
            </span>
          </div>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#374151' }}>{rec.action}</p>
          <button style={actionBtnStyle} onClick={() => alert(`Action: ${rec.action}`)}>
            Address
          </button>
        </li>
      ))}
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
    <div style={containerStyle}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2 style={headingStyle}>Quality Evaluation</h2>
          {selectedReport && (
            <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
              Version {selectedReport.version} — Total: {selectedReport.total_score}/11
            </span>
          )}
        </div>
        <button
          style={generating ? disabledBtnStyle : primaryBtnStyle}
          disabled={generating}
          onClick={handleGenerate}
          aria-label="Run Evaluation"
        >
          {generating ? 'Evaluating…' : 'Run Evaluation'}
        </button>
      </div>

      {/* Error */}
      {error && <p style={{ color: '#dc2626', fontSize: '0.875rem', marginBottom: '0.75rem' }}>{error}</p>}

      {/* Version picker */}
      {summaries.length > 1 && (
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ fontSize: '0.8125rem', color: '#6b7280', marginRight: '0.5rem' }}>
            Report version:
          </label>
          <select
            style={selectStyle}
            onChange={(e) => loadDetail(Number(e.target.value))}
            value={selectedReport?.id ?? ''}
          >
            {summaries.map((s) => (
              <option key={s.id} value={s.id}>
                v{s.version} — {s.total_score}/11 ({new Date(s.generated_at).toLocaleDateString()})
              </option>
            ))}
          </select>
        </div>
      )}

      {loading && <p style={{ color: '#6b7280' }}>Loading…</p>}

      {selectedReport && (
        <>
          {/* Rubric score cards */}
          <section aria-label="Rubric scores">
            <h3 style={sectionHeadingStyle}>Rubric Scores</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
              {RUBRICS.map((rubric) => (
                <RubricCard key={rubric.key} rubric={rubric} report={selectedReport} />
              ))}
            </div>
          </section>

          {/* Recommendations */}
          <section aria-label="Recommendations" style={{ marginTop: '1.5rem' }}>
            <h3 style={sectionHeadingStyle}>Improvement Recommendations</h3>
            <RecommendationList recommendations={selectedReport.recommendations ?? []} />
          </section>
        </>
      )}

      {!loading && !selectedReport && summaries.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem 0', color: '#9ca3af' }}>
          <p>No quality evaluations yet.</p>
          <p style={{ fontSize: '0.875rem' }}>Click "Run Evaluation" to score this study.</p>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const containerStyle: React.CSSProperties = {
  padding: '1.25rem',
  background: '#fff',
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
};

const headingStyle: React.CSSProperties = {
  margin: 0,
  fontSize: '1.125rem',
  fontWeight: 700,
  color: '#111827',
};

const sectionHeadingStyle: React.CSSProperties = {
  fontSize: '0.9375rem',
  fontWeight: 600,
  color: '#374151',
  margin: '0 0 0.75rem',
};

const cardStyle: React.CSSProperties = {
  border: '1px solid #e2e8f0',
  borderRadius: '0.375rem',
  padding: '0.75rem 1rem',
};

const scoreBadgeStyle = (score: number, max: number): React.CSSProperties => {
  const pct = max > 0 ? score / max : 0;
  const bg = pct >= 0.67 ? '#dcfce7' : pct >= 0.34 ? '#fef9c3' : '#fee2e2';
  const color = pct >= 0.67 ? '#16a34a' : pct >= 0.34 ? '#b45309' : '#dc2626';
  return { fontWeight: 700, fontSize: '0.875rem', padding: '0.125rem 0.5rem', borderRadius: '9999px', background: bg, color };
};

const recItemStyle: React.CSSProperties = {
  border: '1px solid #e2e8f0',
  borderRadius: '0.375rem',
  padding: '0.75rem 1rem',
};

const priorityBadgeStyle = (priority: number): React.CSSProperties => {
  const colors: Record<number, [string, string]> = {
    1: ['#fee2e2', '#dc2626'],
    2: ['#fef9c3', '#b45309'],
    3: ['#f0fdf4', '#16a34a'],
  };
  const [bg, color] = colors[priority] ?? ['#f3f4f6', '#6b7280'];
  return { fontSize: '0.6875rem', fontWeight: 700, padding: '0.125rem 0.5rem', borderRadius: '9999px', background: bg, color };
};

const actionBtnStyle: React.CSSProperties = {
  marginTop: '0.5rem',
  padding: '0.25rem 0.75rem',
  fontSize: '0.75rem',
  fontWeight: 600,
  background: 'transparent',
  border: '1px solid #d1d5db',
  borderRadius: '0.25rem',
  cursor: 'pointer',
  color: '#374151',
};

const primaryBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 600,
};

const disabledBtnStyle: React.CSSProperties = { ...primaryBtnStyle, background: '#93c5fd', cursor: 'not-allowed' };

const selectStyle: React.CSSProperties = {
  padding: '0.25rem 0.5rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.25rem',
  fontSize: '0.8125rem',
};
