/**
 * ChartGallery: displays a grid of all generated classification SVG charts,
 * plus a publications-by-year bar chart. Each chart has a download button.
 */

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';

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
      <Box
        sx={{
          padding: '2rem',
          textAlign: 'center',
          color: '#6b7280',
          fontSize: '0.875rem',
          border: '1px dashed #d1d5db',
          borderRadius: '0.5rem',
        }}
      >
        No charts generated yet. Click <strong>Generate Results</strong> to build them.
      </Box>
    );
  }

  return (
    <Box>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '1rem',
        }}
      >
        {charts.map((chart) => (
          <ChartCard key={chart.id} studyId={studyId} chart={chart} />
        ))}
      </Box>
    </Box>
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
    <Paper variant="outlined" sx={{ border: '1px solid #e2e8f0', borderRadius: '0.5rem', padding: '0.875rem', background: '#fff' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.625rem' }}>
        <Typography component="span" sx={{ fontSize: '0.8125rem', fontWeight: 600, color: '#374151', textTransform: 'capitalize' }}>{label}</Typography>
        <Button
          variant="outlined"
          size="small"
          onClick={handleDownload}
          disabled={!chart.svg_content}
          title="Download SVG"
          sx={{
            padding: '0.125rem 0.5rem',
            fontSize: '0.6875rem',
            fontWeight: 600,
            background: chart.svg_content ? '#eff6ff' : '#f1f5f9',
            color: chart.svg_content ? '#2563eb' : '#9ca3af',
            borderColor: chart.svg_content ? '#bfdbfe' : '#e2e8f0',
          }}
        >
          ↓ SVG
        </Button>
      </Box>

      <Box
        sx={{
          height: '160px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#f8fafc',
          borderRadius: '0.375rem',
          overflow: 'hidden',
        }}
      >
        {svgSrc ? (
          <img
            src={svgSrc}
            alt={`${label} chart`}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        ) : (
          <Typography sx={{ color: '#9ca3af', fontSize: '0.8125rem' }}>No data</Typography>
        )}
      </Box>

      <Typography sx={{ marginTop: '0.375rem', fontSize: '0.6875rem', color: '#9ca3af' }}>
        v{chart.version}
      </Typography>
    </Paper>
  );
}
