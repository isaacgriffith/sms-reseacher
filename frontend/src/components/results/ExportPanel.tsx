/**
 * ExportPanel: lets the researcher select an export format, trigger the ARQ
 * export job, poll for completion via the jobs endpoint, and download the result.
 */

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
  progress_detail: { download_url?: string; size_bytes?: number; format?: string } | null;
  error_message: string | null;
}

interface ExportPanelProps {
  studyId: number;
}

const FORMAT_OPTIONS: Array<{ value: string; label: string; description: string }> = [
  { value: 'svg_only', label: 'SVG Only', description: 'ZIP of all generated chart SVG files' },
  { value: 'json_only', label: 'JSON Only', description: 'Full study data as a single JSON file' },
  { value: 'csv_json', label: 'CSV + JSON', description: 'Tabular extractions CSV + full study JSON (ZIP)' },
  { value: 'full_archive', label: 'Full Archive', description: 'SVGs, CSV, and JSON in one ZIP' },
];

export default function ExportPanel({ studyId }: ExportPanelProps) {
  const [selectedFormat, setSelectedFormat] = useState('full_archive');
  const [job, setJob] = useState<ExportJob | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Start polling when a job is enqueued
  useEffect(() => {
    if (!job) return;
    if (jobStatus?.status === 'completed' || jobStatus?.status === 'failed') return;

    pollRef.current = setInterval(async () => {
      try {
        const status = await api.get<JobStatus>(`/api/v1/jobs/${job.job_id}`);
        setJobStatus(status);
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollRef.current!);
        }
      } catch {
        // Ignore transient poll errors
      }
    }, 2000);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [job, jobStatus?.status]);

  const handleExport = async () => {
    setError(null);
    setJob(null);
    setJobStatus(null);
    setIsSubmitting(true);
    try {
      const result = await api.post<ExportJob>(`/api/v1/studies/${studyId}/export`, {
        format: selectedFormat,
      });
      setJob(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start export job');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownload = () => {
    if (!job) return;
    const url = `/api/v1/studies/${studyId}/export/${job.job_id}/download`;
    const a = document.createElement('a');
    a.href = url;
    a.click();
  };

  const handleReset = () => {
    setJob(null);
    setJobStatus(null);
    setError(null);
    if (pollRef.current) clearInterval(pollRef.current);
  };

  return (
    <div style={panelStyle}>
      <h3 style={headingStyle}>Export Study</h3>

      {/* Format selector */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' }}>
        {FORMAT_OPTIONS.map((opt) => (
          <label key={opt.value} style={radioLabelStyle(selectedFormat === opt.value)}>
            <input
              type="radio"
              name="export_format"
              value={opt.value}
              checked={selectedFormat === opt.value}
              onChange={() => setSelectedFormat(opt.value)}
              style={{ marginRight: '0.625rem' }}
              disabled={!!job && jobStatus?.status !== 'completed' && jobStatus?.status !== 'failed'}
            />
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.875rem', color: '#111827' }}>{opt.label}</div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{opt.description}</div>
            </div>
          </label>
        ))}
      </div>

      {/* Action buttons */}
      {!job || jobStatus?.status === 'failed' ? (
        <button
          onClick={handleExport}
          disabled={isSubmitting}
          style={isSubmitting ? disabledBtnStyle : primaryBtnStyle}
        >
          {isSubmitting ? 'Starting…' : 'Export'}
        </button>
      ) : jobStatus?.status === 'completed' ? (
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button onClick={handleDownload} style={downloadBtnStyle}>
            ↓ Download
          </button>
          <button onClick={handleReset} style={secondaryBtnStyle}>
            New Export
          </button>
          {jobStatus.progress_detail?.size_bytes != null && (
            <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
              {formatBytes(jobStatus.progress_detail.size_bytes)}
            </span>
          )}
        </div>
      ) : (
        <ProgressBar pct={jobStatus?.progress_pct ?? 0} />
      )}

      {/* Status messages */}
      {error && (
        <p style={{ marginTop: '0.75rem', color: '#dc2626', fontSize: '0.8125rem' }}>{error}</p>
      )}
      {jobStatus?.status === 'failed' && (
        <p style={{ marginTop: '0.75rem', color: '#dc2626', fontSize: '0.8125rem' }}>
          Export failed: {jobStatus.error_message ?? 'Unknown error'}
        </p>
      )}
      {jobStatus?.status === 'completed' && (
        <p style={{ marginTop: '0.5rem', color: '#16a34a', fontSize: '0.8125rem' }}>
          Export ready — click Download to save.
        </p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// ProgressBar sub-component
// ---------------------------------------------------------------------------

function ProgressBar({ pct }: { pct: number }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
        <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Exporting…</span>
        <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>{pct}%</span>
      </div>
      <div style={{ height: '6px', background: '#e2e8f0', borderRadius: '9999px', overflow: 'hidden' }}>
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            background: '#2563eb',
            borderRadius: '9999px',
            transition: 'width 0.3s ease',
          }}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const panelStyle: React.CSSProperties = {
  border: '1px solid #e2e8f0',
  borderRadius: '0.5rem',
  padding: '1.25rem',
  background: '#fff',
};

const headingStyle: React.CSSProperties = {
  margin: '0 0 1rem',
  fontSize: '1rem',
  fontWeight: 600,
  color: '#111827',
};

const radioLabelStyle = (selected: boolean): React.CSSProperties => ({
  display: 'flex',
  alignItems: 'flex-start',
  padding: '0.625rem 0.875rem',
  border: `1px solid ${selected ? '#3b82f6' : '#e2e8f0'}`,
  borderRadius: '0.375rem',
  cursor: 'pointer',
  background: selected ? '#eff6ff' : '#fff',
});

const primaryBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1.25rem',
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 600,
};

const disabledBtnStyle: React.CSSProperties = {
  ...primaryBtnStyle,
  background: '#93c5fd',
  cursor: 'not-allowed',
};

const downloadBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1.25rem',
  background: '#16a34a',
  color: '#fff',
  border: 'none',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 600,
};

const secondaryBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  background: 'transparent',
  color: '#374151',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  cursor: 'pointer',
  fontSize: '0.875rem',
};
