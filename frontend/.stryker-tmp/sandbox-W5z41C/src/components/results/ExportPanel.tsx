/**
 * ExportPanel: lets the researcher select an export format, trigger the ARQ
 * export job, poll for completion via the jobs endpoint, and download the result.
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
import { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
interface ExportJob {
  job_id: string;
  study_id: number;
}
interface JobStatus {
  id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress_pct: number;
  progress_detail: {
    download_url?: string;
    size_bytes?: number;
    format?: string;
  } | null;
  error_message: string | null;
}
interface ExportPanelProps {
  studyId: number;
}
const FORMAT_OPTIONS: Array<{
  value: string;
  label: string;
  description: string;
}> = stryMutAct_9fa48("1594") ? [] : (stryCov_9fa48("1594"), [{
  value: 'svg_only',
  label: 'SVG Only',
  description: 'ZIP of all generated chart SVG files'
}, {
  value: 'json_only',
  label: 'JSON Only',
  description: 'Full study data as a single JSON file'
}, {
  value: 'csv_json',
  label: 'CSV + JSON',
  description: 'Tabular extractions CSV + full study JSON (ZIP)'
}, {
  value: 'full_archive',
  label: 'Full Archive',
  description: 'SVGs, CSV, and JSON in one ZIP'
}]);
export default function ExportPanel({
  studyId
}: ExportPanelProps) {
  if (stryMutAct_9fa48("1611")) {
    {}
  } else {
    stryCov_9fa48("1611");
    const [selectedFormat, setSelectedFormat] = useState('full_archive');
    const [job, setJob] = useState<ExportJob | null>(null);
    const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(stryMutAct_9fa48("1613") ? true : (stryCov_9fa48("1613"), false));
    const [error, setError] = useState<string | null>(null);
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // Start polling when a job is enqueued
    useEffect(() => {
      if (stryMutAct_9fa48("1614")) {
        {}
      } else {
        stryCov_9fa48("1614");
        if (stryMutAct_9fa48("1617") ? false : stryMutAct_9fa48("1616") ? true : stryMutAct_9fa48("1615") ? job : (stryCov_9fa48("1615", "1616", "1617"), !job)) return;
        if (stryMutAct_9fa48("1620") ? jobStatus?.status === 'completed' && jobStatus?.status === 'failed' : stryMutAct_9fa48("1619") ? false : stryMutAct_9fa48("1618") ? true : (stryCov_9fa48("1618", "1619", "1620"), (stryMutAct_9fa48("1622") ? jobStatus?.status !== 'completed' : stryMutAct_9fa48("1621") ? false : (stryCov_9fa48("1621", "1622"), (stryMutAct_9fa48("1623") ? jobStatus.status : (stryCov_9fa48("1623"), jobStatus?.status)) === 'completed')) || (stryMutAct_9fa48("1626") ? jobStatus?.status !== 'failed' : stryMutAct_9fa48("1625") ? false : (stryCov_9fa48("1625", "1626"), (stryMutAct_9fa48("1627") ? jobStatus.status : (stryCov_9fa48("1627"), jobStatus?.status)) === 'failed')))) return;
        pollRef.current = setInterval(async () => {
          if (stryMutAct_9fa48("1629")) {
            {}
          } else {
            stryCov_9fa48("1629");
            try {
              if (stryMutAct_9fa48("1630")) {
                {}
              } else {
                stryCov_9fa48("1630");
                const status = await api.get<JobStatus>(`/api/v1/jobs/${job.job_id}`);
                setJobStatus(status);
                if (stryMutAct_9fa48("1634") ? status.status === 'completed' && status.status === 'failed' : stryMutAct_9fa48("1633") ? false : stryMutAct_9fa48("1632") ? true : (stryCov_9fa48("1632", "1633", "1634"), (stryMutAct_9fa48("1636") ? status.status !== 'completed' : stryMutAct_9fa48("1635") ? false : (stryCov_9fa48("1635", "1636"), status.status === 'completed')) || (stryMutAct_9fa48("1639") ? status.status !== 'failed' : stryMutAct_9fa48("1638") ? false : (stryCov_9fa48("1638", "1639"), status.status === 'failed')))) {
                  if (stryMutAct_9fa48("1641")) {
                    {}
                  } else {
                    stryCov_9fa48("1641");
                    clearInterval(pollRef.current!);
                  }
                }
              }
            } catch {
              // Ignore transient poll errors
            }
          }
        }, 2000);
        return () => {
          if (stryMutAct_9fa48("1642")) {
            {}
          } else {
            stryCov_9fa48("1642");
            if (stryMutAct_9fa48("1644") ? false : stryMutAct_9fa48("1643") ? true : (stryCov_9fa48("1643", "1644"), pollRef.current)) clearInterval(pollRef.current);
          }
        };
      }
    }, stryMutAct_9fa48("1645") ? [] : (stryCov_9fa48("1645"), [job, stryMutAct_9fa48("1646") ? jobStatus.status : (stryCov_9fa48("1646"), jobStatus?.status)]));
    const handleExport = async () => {
      if (stryMutAct_9fa48("1647")) {
        {}
      } else {
        stryCov_9fa48("1647");
        setError(null);
        setJob(null);
        setJobStatus(null);
        setIsSubmitting(stryMutAct_9fa48("1648") ? false : (stryCov_9fa48("1648"), true));
        try {
          if (stryMutAct_9fa48("1649")) {
            {}
          } else {
            stryCov_9fa48("1649");
            const result = await api.post<ExportJob>(`/api/v1/studies/${studyId}/export`, {
              format: selectedFormat
            });
            setJob(result);
          }
        } catch (err: unknown) {
          if (stryMutAct_9fa48("1652")) {
            {}
          } else {
            stryCov_9fa48("1652");
            setError(err instanceof Error ? err.message : 'Failed to start export job');
          }
        } finally {
          if (stryMutAct_9fa48("1654")) {
            {}
          } else {
            stryCov_9fa48("1654");
            setIsSubmitting(stryMutAct_9fa48("1655") ? true : (stryCov_9fa48("1655"), false));
          }
        }
      }
    };
    const handleDownload = () => {
      if (stryMutAct_9fa48("1656")) {
        {}
      } else {
        stryCov_9fa48("1656");
        if (stryMutAct_9fa48("1659") ? false : stryMutAct_9fa48("1658") ? true : stryMutAct_9fa48("1657") ? job : (stryCov_9fa48("1657", "1658", "1659"), !job)) return;
        const url = `/api/v1/studies/${studyId}/export/${job.job_id}/download`;
        const a = document.createElement('a');
        a.href = url;
        a.click();
      }
    };
    const handleReset = () => {
      if (stryMutAct_9fa48("1662")) {
        {}
      } else {
        stryCov_9fa48("1662");
        setJob(null);
        setJobStatus(null);
        setError(null);
        if (stryMutAct_9fa48("1664") ? false : stryMutAct_9fa48("1663") ? true : (stryCov_9fa48("1663", "1664"), pollRef.current)) clearInterval(pollRef.current);
      }
    };
    return <div style={panelStyle}>
      <h3 style={headingStyle}>Export Study</h3>

      {/* Format selector */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
        marginBottom: '1rem'
      }}>
        {FORMAT_OPTIONS.map(stryMutAct_9fa48("1670") ? () => undefined : (stryCov_9fa48("1670"), opt => <label key={opt.value} style={radioLabelStyle(stryMutAct_9fa48("1673") ? selectedFormat !== opt.value : stryMutAct_9fa48("1672") ? false : stryMutAct_9fa48("1671") ? true : (stryCov_9fa48("1671", "1672", "1673"), selectedFormat === opt.value))}>
            <input type="radio" name="export_format" value={opt.value} checked={stryMutAct_9fa48("1676") ? selectedFormat !== opt.value : stryMutAct_9fa48("1675") ? false : stryMutAct_9fa48("1674") ? true : (stryCov_9fa48("1674", "1675", "1676"), selectedFormat === opt.value)} onChange={stryMutAct_9fa48("1677") ? () => undefined : (stryCov_9fa48("1677"), () => setSelectedFormat(opt.value))} style={{
            marginRight: '0.625rem'
          }} disabled={stryMutAct_9fa48("1682") ? !!job && jobStatus?.status !== 'completed' || jobStatus?.status !== 'failed' : stryMutAct_9fa48("1681") ? false : stryMutAct_9fa48("1680") ? true : (stryCov_9fa48("1680", "1681", "1682"), (stryMutAct_9fa48("1684") ? !!job || jobStatus?.status !== 'completed' : stryMutAct_9fa48("1683") ? true : (stryCov_9fa48("1683", "1684"), (stryMutAct_9fa48("1685") ? !job : (stryCov_9fa48("1685"), !(stryMutAct_9fa48("1686") ? job : (stryCov_9fa48("1686"), !job)))) && (stryMutAct_9fa48("1688") ? jobStatus?.status === 'completed' : stryMutAct_9fa48("1687") ? true : (stryCov_9fa48("1687", "1688"), (stryMutAct_9fa48("1689") ? jobStatus.status : (stryCov_9fa48("1689"), jobStatus?.status)) !== 'completed')))) && (stryMutAct_9fa48("1692") ? jobStatus?.status === 'failed' : stryMutAct_9fa48("1691") ? true : (stryCov_9fa48("1691", "1692"), (stryMutAct_9fa48("1693") ? jobStatus.status : (stryCov_9fa48("1693"), jobStatus?.status)) !== 'failed')))} />
            <div>
              <div style={{
              fontWeight: 600,
              fontSize: '0.875rem',
              color: '#111827'
            }}>{opt.label}</div>
              <div style={{
              fontSize: '0.75rem',
              color: '#6b7280'
            }}>{opt.description}</div>
            </div>
          </label>))}
      </div>

      {/* Action buttons */}
      {(stryMutAct_9fa48("1703") ? !job && jobStatus?.status === 'failed' : stryMutAct_9fa48("1702") ? false : stryMutAct_9fa48("1701") ? true : (stryCov_9fa48("1701", "1702", "1703"), (stryMutAct_9fa48("1704") ? job : (stryCov_9fa48("1704"), !job)) || (stryMutAct_9fa48("1706") ? jobStatus?.status !== 'failed' : stryMutAct_9fa48("1705") ? false : (stryCov_9fa48("1705", "1706"), (stryMutAct_9fa48("1707") ? jobStatus.status : (stryCov_9fa48("1707"), jobStatus?.status)) === 'failed')))) ? <button onClick={handleExport} disabled={isSubmitting} style={isSubmitting ? disabledBtnStyle : primaryBtnStyle}>
          {isSubmitting ? 'Starting…' : 'Export'}
        </button> : (stryMutAct_9fa48("1713") ? jobStatus?.status !== 'completed' : stryMutAct_9fa48("1712") ? false : stryMutAct_9fa48("1711") ? true : (stryCov_9fa48("1711", "1712", "1713"), (stryMutAct_9fa48("1714") ? jobStatus.status : (stryCov_9fa48("1714"), jobStatus?.status)) === 'completed')) ? <div style={{
        display: 'flex',
        gap: '0.5rem',
        alignItems: 'center'
      }}>
          <button onClick={handleDownload} style={downloadBtnStyle}>
            ↓ Download
          </button>
          <button onClick={handleReset} style={secondaryBtnStyle}>
            New Export
          </button>
          {stryMutAct_9fa48("1722") ? jobStatus.progress_detail?.size_bytes != null || <span style={{
          fontSize: '0.75rem',
          color: '#6b7280'
        }}>
              {formatBytes(jobStatus.progress_detail.size_bytes)}
            </span> : stryMutAct_9fa48("1721") ? false : stryMutAct_9fa48("1720") ? true : (stryCov_9fa48("1720", "1721", "1722"), (stryMutAct_9fa48("1724") ? jobStatus.progress_detail?.size_bytes == null : stryMutAct_9fa48("1723") ? true : (stryCov_9fa48("1723", "1724"), (stryMutAct_9fa48("1725") ? jobStatus.progress_detail.size_bytes : (stryCov_9fa48("1725"), jobStatus.progress_detail?.size_bytes)) != null)) && <span style={{
          fontSize: '0.75rem',
          color: '#6b7280'
        }}>
              {formatBytes(jobStatus.progress_detail.size_bytes)}
            </span>)}
        </div> : <ProgressBar pct={stryMutAct_9fa48("1729") ? jobStatus?.progress_pct && 0 : (stryCov_9fa48("1729"), (stryMutAct_9fa48("1730") ? jobStatus.progress_pct : (stryCov_9fa48("1730"), jobStatus?.progress_pct)) ?? 0)} />}

      {/* Status messages */}
      {stryMutAct_9fa48("1733") ? error || <p style={{
        marginTop: '0.75rem',
        color: '#dc2626',
        fontSize: '0.8125rem'
      }}>{error}</p> : stryMutAct_9fa48("1732") ? false : stryMutAct_9fa48("1731") ? true : (stryCov_9fa48("1731", "1732", "1733"), error && <p style={{
        marginTop: '0.75rem',
        color: '#dc2626',
        fontSize: '0.8125rem'
      }}>{error}</p>)}
      {stryMutAct_9fa48("1740") ? jobStatus?.status === 'failed' || <p style={{
        marginTop: '0.75rem',
        color: '#dc2626',
        fontSize: '0.8125rem'
      }}>
          Export failed: {jobStatus.error_message ?? 'Unknown error'}
        </p> : stryMutAct_9fa48("1739") ? false : stryMutAct_9fa48("1738") ? true : (stryCov_9fa48("1738", "1739", "1740"), (stryMutAct_9fa48("1742") ? jobStatus?.status !== 'failed' : stryMutAct_9fa48("1741") ? true : (stryCov_9fa48("1741", "1742"), (stryMutAct_9fa48("1743") ? jobStatus.status : (stryCov_9fa48("1743"), jobStatus?.status)) === 'failed')) && <p style={{
        marginTop: '0.75rem',
        color: '#dc2626',
        fontSize: '0.8125rem'
      }}>
          Export failed: {stryMutAct_9fa48("1749") ? jobStatus.error_message && 'Unknown error' : (stryCov_9fa48("1749"), jobStatus.error_message ?? 'Unknown error')}
        </p>)}
      {stryMutAct_9fa48("1753") ? jobStatus?.status === 'completed' || <p style={{
        marginTop: '0.5rem',
        color: '#16a34a',
        fontSize: '0.8125rem'
      }}>
          Export ready — click Download to save.
        </p> : stryMutAct_9fa48("1752") ? false : stryMutAct_9fa48("1751") ? true : (stryCov_9fa48("1751", "1752", "1753"), (stryMutAct_9fa48("1755") ? jobStatus?.status !== 'completed' : stryMutAct_9fa48("1754") ? true : (stryCov_9fa48("1754", "1755"), (stryMutAct_9fa48("1756") ? jobStatus.status : (stryCov_9fa48("1756"), jobStatus?.status)) === 'completed')) && <p style={{
        marginTop: '0.5rem',
        color: '#16a34a',
        fontSize: '0.8125rem'
      }}>
          Export ready — click Download to save.
        </p>)}
    </div>;
  }
}

// ---------------------------------------------------------------------------
// ProgressBar sub-component
// ---------------------------------------------------------------------------

function ProgressBar({
  pct
}: {
  pct: number;
}) {
  if (stryMutAct_9fa48("1762")) {
    {}
  } else {
    stryCov_9fa48("1762");
    return <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: '0.25rem'
      }}>
        <span style={{
          fontSize: '0.75rem',
          color: '#6b7280'
        }}>Exporting…</span>
        <span style={{
          fontSize: '0.75rem',
          color: '#6b7280'
        }}>{pct}%</span>
      </div>
      <div style={{
        height: '6px',
        background: '#e2e8f0',
        borderRadius: '9999px',
        overflow: 'hidden'
      }}>
        <div style={{
          height: '100%',
          width: `${pct}%`,
          background: '#2563eb',
          borderRadius: '9999px',
          transition: 'width 0.3s ease'
        }} />
      </div>
    </div>;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatBytes(bytes: number): string {
  if (stryMutAct_9fa48("1784")) {
    {}
  } else {
    stryCov_9fa48("1784");
    if (stryMutAct_9fa48("1788") ? bytes >= 1024 : stryMutAct_9fa48("1787") ? bytes <= 1024 : stryMutAct_9fa48("1786") ? false : stryMutAct_9fa48("1785") ? true : (stryCov_9fa48("1785", "1786", "1787", "1788"), bytes < 1024)) return `${bytes} B`;
    if (stryMutAct_9fa48("1793") ? bytes >= 1024 * 1024 : stryMutAct_9fa48("1792") ? bytes <= 1024 * 1024 : stryMutAct_9fa48("1791") ? false : stryMutAct_9fa48("1790") ? true : (stryCov_9fa48("1790", "1791", "1792", "1793"), bytes < (stryMutAct_9fa48("1794") ? 1024 / 1024 : (stryCov_9fa48("1794"), 1024 * 1024)))) return `${(stryMutAct_9fa48("1796") ? bytes * 1024 : (stryCov_9fa48("1796"), bytes / 1024)).toFixed(1)} KB`;
    return `${(stryMutAct_9fa48("1798") ? bytes * (1024 * 1024) : (stryCov_9fa48("1798"), bytes / (stryMutAct_9fa48("1799") ? 1024 / 1024 : (stryCov_9fa48("1799"), 1024 * 1024)))).toFixed(1)} MB`;
  }
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const panelStyle: React.CSSProperties = {
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
  padding: '1.25rem',
  background: '#fff'
};
const headingStyle: React.CSSProperties = {
  margin: '0 0 1rem',
  fontSize: '1rem',
  fontWeight: 600,
  color: '#111827'
};
const radioLabelStyle = stryMutAct_9fa48("1809") ? () => undefined : (stryCov_9fa48("1809"), (() => {
  const radioLabelStyle = (selected: boolean): React.CSSProperties => ({
    display: 'flex',
    alignItems: 'flex-start',
    padding: '0.625rem 0.875rem',
    border: `1px solid ${selected ? '#3b82f6' : '#e2e8f0'}`,
    borderRadius: '0.375rem',
    cursor: 'pointer',
    background: selected ? '#eff6ff' : '#fff'
  });
  return radioLabelStyle;
})());
const primaryBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1.25rem',
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 600
};
const disabledBtnStyle: React.CSSProperties = {
  ...primaryBtnStyle,
  background: '#93c5fd',
  cursor: 'not-allowed'
};
const downloadBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1.25rem',
  background: '#16a34a',
  color: '#fff',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 600
};
const secondaryBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  background: 'transparent',
  color: '#374151',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem'
};