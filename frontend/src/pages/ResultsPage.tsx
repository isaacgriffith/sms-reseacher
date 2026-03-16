/**
 * ResultsPage: displays all generated charts as SVG images with download
 * buttons, the interactive domain model graph, and an export format selector.
 */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import ChartGallery from '../components/results/ChartGallery';
import DomainModelViewer from '../components/results/DomainModelViewer';
import ExportPanel from '../components/results/ExportPanel';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Alert from '@mui/material/Alert';

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
    <Container maxWidth={false} sx={{ maxWidth: '72rem', margin: '0 auto', padding: '1.5rem' }}>
      {/* Page header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <Typography variant="h5" sx={{ margin: 0, fontSize: '1.25rem', color: '#111827' }}>Results</Typography>
        <Button
          variant="contained"
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          sx={{ padding: '0.5rem 1.25rem', fontSize: '0.875rem', fontWeight: 600 }}
        >
          {generateMutation.isPending ? 'Queued…' : 'Generate Results'}
        </Button>
      </Box>

      {generateMutation.isSuccess && (
        <Alert severity="info" sx={{ marginBottom: '1rem' }}>
          Result generation job queued (job #{generateMutation.data?.job_id}). Charts will appear shortly.
        </Alert>
      )}
      {generateMutation.isError && (
        <Alert severity="error" sx={{ marginBottom: '1rem' }}>Failed to enqueue generation job. Try again.</Alert>
      )}

      {isLoading && <Typography sx={{ color: '#6b7280', fontSize: '0.875rem' }}>Loading results…</Typography>}
      {error && (
        <Typography sx={{ color: '#ef4444', fontSize: '0.875rem' }}>Failed to load results.</Typography>
      )}

      {/* Tabs */}
      <Box sx={{ display: 'flex', gap: '0.25rem', borderBottom: '1px solid #e2e8f0' }}>
        {([
          { id: 'charts', label: `Charts (${charts.length})` },
          { id: 'domain_model', label: 'Domain Model' },
          { id: 'export', label: 'Export' },
        ] as Array<{ id: TabId; label: string }>).map((tab) => (
          <Button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            sx={{
              padding: '0.5rem 1rem',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === tab.id ? '2px solid #2563eb' : '2px solid transparent',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: 500,
              marginBottom: '-1px',
              color: activeTab === tab.id ? '#2563eb' : '#6b7280',
              borderRadius: 0,
              minWidth: 'auto',
              textTransform: 'none',
            }}
          >
            {tab.label}
          </Button>
        ))}
      </Box>

      {/* Tab content */}
      <Box sx={{ marginTop: '1.25rem' }}>
        {activeTab === 'charts' && (
          <ChartGallery studyId={numericStudyId} charts={charts} />
        )}

        {activeTab === 'domain_model' && domainModel && (
          <DomainModelViewer domainModel={domainModel} />
        )}
        {activeTab === 'domain_model' && !domainModel && !isLoading && (
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
            No domain model available yet. Click <strong>Generate Results</strong> above.
          </Box>
        )}

        {activeTab === 'export' && (
          <ExportPanel studyId={numericStudyId} />
        )}
      </Box>
    </Container>
  );
}
