/**
 * ResultsPage: displays all generated charts as SVG images with download
 * buttons, the interactive domain model graph, and an export format selector.
 */
// @ts-nocheck


import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import ChartGallery from '../components/results/ChartGallery';
import DomainModelViewer from '../components/results/DomainModelViewer';
import ExportPanel from '../components/results/ExportPanel';

interface DomainModel {
  id: number;
  version: number;
  concepts: Array<{ name: string; definition: string; attributes: string[] }> | null;
  relationships: Array<{ from: string; to: string; label: string; type: string }> | null;
  svg_content: string | null;
  generated_at: string;
}

interface Chart {
  id: number;
  chart_type: string;
  version: number;
  chart_data: Record<string, number> | null;
  svg_content: string | null;
  generated_at: string;
}

interface ResultsSummary {
  domain_model: DomainModel | null;
  charts: Chart[];
}

interface GenerateJobResponse {
  job_id: string;
  study_id: number;
}

type TabId = 'charts' | 'domain_model' | 'export';

export default function ResultsPage() {
  const { studyId } = useParams<{ studyId: string }>();
  const numericStudyId = Number(studyId);
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<TabId>('charts');

  const { data: results, isLoading, error } = useQuery<ResultsSummary>({
    queryKey: ['results', numericStudyId],
    queryFn: () => api.get<ResultsSummary>(`/api/v1/studies/${numericStudyId}/results`),
    enabled: !!numericStudyId,
  });

  const generateMutation = useMutation({
    mutationFn: () =>
      api.post<GenerateJobResponse>(`/api/v1/studies/${numericStudyId}/results/generate`, {}),
    onSuccess: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['results', numericStudyId] });
      }, 3000);
    },
  });

  const charts = results?.charts ?? [];
  const domainModel = results?.domain_model ?? null;

  return (
    <div style={{ maxWidth: '72rem', margin: '0 auto', padding: '1.5rem' }}>
      {/* Page header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.25rem', color: '#111827' }}>Results</h2>
        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          style={generateMutation.isPending ? disabledBtnStyle : primaryBtnStyle}
        >
          {generateMutation.isPending ? 'Queued…' : 'Generate Results'}
        </button>
      </div>

      {generateMutation.isSuccess && (
        <div style={bannerStyle}>
          Result generation job queued (job #{generateMutation.data?.job_id}). Charts will appear shortly.
        </div>
      )}
      {generateMutation.isError && (
        <div style={errorBannerStyle}>Failed to enqueue generation job. Try again.</div>
      )}

      {isLoading && <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Loading results…</p>}
      {error && (
        <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>Failed to load results.</p>
      )}

      {/* Tabs */}
      <div style={tabBarStyle}>
        {([
          { id: 'charts', label: `Charts (${charts.length})` },
          { id: 'domain_model', label: 'Domain Model' },
          { id: 'export', label: 'Export' },
        ] as Array<{ id: TabId; label: string }>).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={activeTab === tab.id ? activeTabStyle : inactiveTabStyle}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div style={{ marginTop: '1.25rem' }}>
        {activeTab === 'charts' && (
          <ChartGallery studyId={numericStudyId} charts={charts} />
        )}

        {activeTab === 'domain_model' && domainModel && (
          <DomainModelViewer domainModel={domainModel} />
        )}
        {activeTab === 'domain_model' && !domainModel && !isLoading && (
          <div style={emptyStyle}>
            Domain model not generated yet. Click <strong>Generate Results</strong> above.
          </div>
        )}

        {activeTab === 'export' && (
          <ExportPanel studyId={numericStudyId} />
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

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

const bannerStyle: React.CSSProperties = {
  marginBottom: '1rem',
  padding: '0.625rem 1rem',
  background: '#eff6ff',
  color: '#1d4ed8',
  border: '1px solid #bfdbfe',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
};

const errorBannerStyle: React.CSSProperties = {
  ...bannerStyle,
  background: '#fef2f2',
  color: '#dc2626',
  border: '1px solid #fecaca',
};

const tabBarStyle: React.CSSProperties = {
  display: 'flex',
  gap: '0.25rem',
  borderBottom: '1px solid #e2e8f0',
};

const tabBase: React.CSSProperties = {
  padding: '0.5rem 1rem',
  background: 'transparent',
  border: 'none',
  borderBottom: '2px solid transparent',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 500,
  marginBottom: '-1px',
};

const activeTabStyle: React.CSSProperties = {
  ...tabBase,
  color: '#2563eb',
  borderBottom: '2px solid #2563eb',
};

const inactiveTabStyle: React.CSSProperties = {
  ...tabBase,
  color: '#6b7280',
};

const emptyStyle: React.CSSProperties = {
  padding: '2rem',
  textAlign: 'center',
  color: '#6b7280',
  fontSize: '0.875rem',
  border: '1px dashed #d1d5db',
  borderRadius: '0.5rem',
};
