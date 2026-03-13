/**
 * ChartGallery: displays a grid of all generated classification SVG charts,
 * plus a publications-by-year bar chart. Each chart has a download button.
 */
// @ts-nocheck
function stryNS_9fa48() {
  var g = typeof globalThis === 'object' && globalThis && globalThis.Math === Math && globalThis || new Function("return this")();
  var ns = g.__stryker__ || (g.__stryker__ = {});
  if (ns.activeMutant === undefined && g.process && g.process.env && g.process.env.__STRYKER_ACTIVE_MUTANT__) {
    ns.activeMutant = g.process.env.__STRYKER_ACTIVE_MUTANT__;
  }
  function retrieveNS() {
    return ns;
  }
  stryNS_9fa48 = retrieveNS;
  return retrieveNS();
}
stryNS_9fa48();
function stryCov_9fa48() {
  var ns = stryNS_9fa48();
  var cov = ns.mutantCoverage || (ns.mutantCoverage = {
    static: {},
    perTest: {}
  });
  function cover() {
    var c = cov.static;
    if (ns.currentTestId) {
      c = cov.perTest[ns.currentTestId] = cov.perTest[ns.currentTestId] || {};
    }
    var a = arguments;
    for (var i = 0; i < a.length; i++) {
      c[a[i]] = (c[a[i]] || 0) + 1;
    }
  }
  stryCov_9fa48 = cover;
  cover.apply(null, arguments);
}
function stryMutAct_9fa48(id) {
  var ns = stryNS_9fa48();
  function isActive(id) {
    if (ns.activeMutant === id) {
      if (ns.hitCount !== void 0 && ++ns.hitCount > ns.hitLimit) {
        throw new Error('Stryker: Hit count limit reached (' + ns.hitCount + ')');
      }
      return true;
    }
    return false;
  }
  stryMutAct_9fa48 = isActive;
  return isActive(id);
}
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
  research_method: 'Research Method'
};
export default function ChartGallery({
  studyId,
  charts
}: ChartGalleryProps) {
  if (stryMutAct_9fa48("1517")) {
    {}
  } else {
    stryCov_9fa48("1517");
    if (stryMutAct_9fa48("1520") ? charts.length !== 0 : stryMutAct_9fa48("1519") ? false : stryMutAct_9fa48("1518") ? true : (stryCov_9fa48("1518", "1519", "1520"), charts.length === 0)) {
      if (stryMutAct_9fa48("1521")) {
        {}
      } else {
        stryCov_9fa48("1521");
        return <div style={emptyStyle}>
        No charts generated yet. Click <strong>Generate Results</strong> to build them.
      </div>;
      }
    }
    return <div>
      <div style={gridStyle}>
        {charts.map(stryMutAct_9fa48("1522") ? () => undefined : (stryCov_9fa48("1522"), chart => <ChartCard key={chart.id} studyId={studyId} chart={chart} />))}
      </div>
    </div>;
  }
}

// ---------------------------------------------------------------------------
// ChartCard
// ---------------------------------------------------------------------------

interface ChartCardProps {
  studyId: number;
  chart: Chart;
}
function ChartCard({
  studyId,
  chart
}: ChartCardProps) {
  if (stryMutAct_9fa48("1523")) {
    {}
  } else {
    stryCov_9fa48("1523");
    const label = stryMutAct_9fa48("1524") ? CHART_LABELS[chart.chart_type] && chart.chart_type.replace(/_/g, ' ') : (stryCov_9fa48("1524"), CHART_LABELS[chart.chart_type] ?? chart.chart_type.replace(/_/g, ' '));
    const handleDownload = () => {
      if (stryMutAct_9fa48("1526")) {
        {}
      } else {
        stryCov_9fa48("1526");
        if (stryMutAct_9fa48("1529") ? false : stryMutAct_9fa48("1528") ? true : stryMutAct_9fa48("1527") ? chart.svg_content : (stryCov_9fa48("1527", "1528", "1529"), !chart.svg_content)) return;
        const blob = new Blob(stryMutAct_9fa48("1530") ? [] : (stryCov_9fa48("1530"), [chart.svg_content]), {
          type: 'image/svg+xml'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${chart.chart_type}_v${chart.version}.svg`;
        a.click();
        URL.revokeObjectURL(url);
      }
    };
    const svgSrc = chart.svg_content ? `/api/v1/studies/${studyId}/results/charts/${chart.id}/svg` : null;
    return <div style={cardStyle}>
      <div style={cardHeaderStyle}>
        <span style={cardTitleStyle}>{label}</span>
        <button onClick={handleDownload} disabled={stryMutAct_9fa48("1536") ? chart.svg_content : (stryCov_9fa48("1536"), !chart.svg_content)} style={chart.svg_content ? downloadBtnStyle : disabledBtnStyle} title="Download SVG">
          ↓ SVG
        </button>
      </div>

      <div style={chartContainerStyle}>
        {svgSrc ? <img src={svgSrc} alt={`${label} chart`} style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain'
        }} /> : <div style={{
          color: '#9ca3af',
          fontSize: '0.8125rem'
        }}>No data</div>}
      </div>

      <div style={{
        marginTop: '0.375rem',
        fontSize: '0.6875rem',
        color: '#9ca3af'
      }}>
        v{chart.version}
      </div>
    </div>;
  }
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const gridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
  gap: '1rem'
};
const cardStyle: React.CSSProperties = {
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
  padding: '0.875rem',
  background: '#fff'
};
const cardHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '0.625rem'
};
const cardTitleStyle: React.CSSProperties = {
  fontSize: '0.8125rem',
  fontWeight: 600,
  color: '#374151',
  textTransform: 'capitalize' as const
};
const chartContainerStyle: React.CSSProperties = {
  height: '160px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: '#f8fafc',
  borderRadius: '0.375rem',
  overflow: 'hidden'
};
const downloadBtnStyle: React.CSSProperties = {
  padding: '0.125rem 0.5rem',
  background: '#eff6ff',
  color: '#2563eb',
  border: '1px solid #bfdbfe',
  borderRadius: '0.25rem',
  cursor: 'pointer',
  fontSize: '0.6875rem',
  fontWeight: 600
};
const disabledBtnStyle: React.CSSProperties = {
  ...downloadBtnStyle,
  background: '#f1f5f9',
  color: '#9ca3af',
  border: '1px solid #e2e8f0',
  cursor: 'not-allowed'
};
const emptyStyle: React.CSSProperties = {
  padding: '2rem',
  textAlign: 'center',
  color: '#6b7280',
  fontSize: '0.875rem',
  border: '1px dashed #d1d5db',
  borderRadius: '0.5rem'
};