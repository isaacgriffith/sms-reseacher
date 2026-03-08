/**
 * ChartGallery: displays a grid of all generated classification SVG charts,
 * plus a publications-by-year bar chart. Each chart has a download button.
 */

interface Chart {
  id: number;
  chart_type: string;
  version: number;
  svg_content: string | null;
}

interface ChartGalleryProps {
  studyId: number;
  charts: Chart[];
}

const CHART_LABELS: Record<string, string> = {
  venue: 'Venue',
  author: 'Author',
  locale: 'Author Locale',
  institution: 'Institution',
  year: 'Publication Year',
  subtopic: 'Subtopic / Keyword',
  research_type: 'Research Type',
  research_method: 'Research Method',
};

export default function ChartGallery({ studyId, charts }: ChartGalleryProps) {
  if (charts.length === 0) {
    return (
      <div style={emptyStyle}>
        No charts generated yet. Click <strong>Generate Results</strong> to build them.
      </div>
    );
  }

  return (
    <div>
      <div style={gridStyle}>
        {charts.map((chart) => (
          <ChartCard key={chart.id} studyId={studyId} chart={chart} />
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// ChartCard
// ---------------------------------------------------------------------------

interface ChartCardProps {
  studyId: number;
  chart: Chart;
}

function ChartCard({ studyId, chart }: ChartCardProps) {
  const label = CHART_LABELS[chart.chart_type] ?? chart.chart_type.replace(/_/g, ' ');

  const handleDownload = () => {
    if (!chart.svg_content) return;
    const blob = new Blob([chart.svg_content], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${chart.chart_type}_v${chart.version}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const svgSrc = chart.svg_content
    ? `/api/v1/studies/${studyId}/results/charts/${chart.id}/svg`
    : null;

  return (
    <div style={cardStyle}>
      <div style={cardHeaderStyle}>
        <span style={cardTitleStyle}>{label}</span>
        <button
          onClick={handleDownload}
          disabled={!chart.svg_content}
          style={chart.svg_content ? downloadBtnStyle : disabledBtnStyle}
          title="Download SVG"
        >
          ↓ SVG
        </button>
      </div>

      <div style={chartContainerStyle}>
        {svgSrc ? (
          <img
            src={svgSrc}
            alt={`${label} chart`}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        ) : (
          <div style={{ color: '#9ca3af', fontSize: '0.8125rem' }}>No data</div>
        )}
      </div>

      <div style={{ marginTop: '0.375rem', fontSize: '0.6875rem', color: '#9ca3af' }}>
        v{chart.version}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const gridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
  gap: '1rem',
};

const cardStyle: React.CSSProperties = {
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
  padding: '0.875rem',
  background: '#fff',
};

const cardHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '0.625rem',
};

const cardTitleStyle: React.CSSProperties = {
  fontSize: '0.8125rem',
  fontWeight: 600,
  color: '#374151',
  textTransform: 'capitalize' as const,
};

const chartContainerStyle: React.CSSProperties = {
  height: '160px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: '#f8fafc',
  borderRadius: '0.375rem',
  overflow: 'hidden',
};

const downloadBtnStyle: React.CSSProperties = {
  padding: '0.125rem 0.5rem',
  background: '#eff6ff',
  color: '#2563eb',
  border: '1px solid #bfdbfe',
  borderRadius: '0.25rem',
  cursor: 'pointer',
  fontSize: '0.6875rem',
  fontWeight: 600,
};

const disabledBtnStyle: React.CSSProperties = {
  ...downloadBtnStyle,
  background: '#f1f5f9',
  color: '#9ca3af',
  border: '1px solid #e2e8f0',
  cursor: 'not-allowed',
};

const emptyStyle: React.CSSProperties = {
  padding: '2rem',
  textAlign: 'center',
  color: '#6b7280',
  fontSize: '0.875rem',
  border: '1px dashed #d1d5db',
  borderRadius: '0.5rem',
};
