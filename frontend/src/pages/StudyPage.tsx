/**
 * Study page: phase router rendering phase 1–5 tabs based on unlocked_phases.
 */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import PICOForm from '../components/phase1/PICOForm';
import SeedPapers from '../components/phase1/SeedPapers';
import CriteriaForm from '../components/phase2/CriteriaForm';
import SearchStringEditor from '../components/phase2/SearchStringEditor';
import TestRetest from '../components/phase2/TestRetest';
import JobProgressPanel from '../components/jobs/JobProgressPanel';
import PaperQueue from '../components/phase2/PaperQueue';
import DatabaseSelectionPanel from '../components/studies/DatabaseSelectionPanel';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

interface StudyDetail {
  id: number;
  name: string;
  topic: string | null;
  study_type: string;
  status: string;
  current_phase: number;
  motivation: string | null;
  research_objectives: string[];
  research_questions: string[];
  snowball_threshold: number;
  unlocked_phases: number[];
  created_at: string;
  updated_at: string;
}

const PHASE_META = [
  { phase: 1, label: 'Scoping', icon: '🎯' },
  { phase: 2, label: 'Search', icon: '🔍' },
  { phase: 3, label: 'Screening', icon: '📋' },
  { phase: 4, label: 'Extraction', icon: '📊' },
  { phase: 5, label: 'Reporting', icon: '📄' },
];

export default function StudyPage() {
  const { studyId } = useParams<{ studyId: string }>();
  const [activePhase, setActivePhase] = useState(1);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const { data: study, isLoading, error } = useQuery<StudyDetail>({
    queryKey: ['study', studyId],
    queryFn: () => api.get<StudyDetail>(`/api/v1/studies/${studyId}`),
    enabled: !!studyId,
  });

  if (isLoading) return <Typography>Loading study…</Typography>;
  if (error || !study) return <Typography sx={{ color: 'red' }}>Failed to load study.</Typography>;

  const unlocked = new Set(study.unlocked_phases);

  return (
    <Box>
      {/* Study header */}
      <Box sx={{ marginBottom: '1.5rem' }}>
        <Typography variant="h5" sx={{ margin: '0 0 0.25rem' }}>{study.name}</Typography>
        {study.topic && (
          <Typography sx={{ margin: '0 0 0.5rem', color: '#64748b' }}>{study.topic}</Typography>
        )}
        <Box sx={{ display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#64748b' }}>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b' }}>{study.study_type}</Typography>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b' }}>·</Typography>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b', textTransform: 'capitalize' }}>{study.status}</Typography>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b' }}>·</Typography>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b' }}>Snowball threshold: {study.snowball_threshold}</Typography>
        </Box>
      </Box>

      {/* Phase tabs */}
      <Box
        sx={{
          display: 'flex',
          gap: '0',
          marginBottom: '2rem',
          borderBottom: '2px solid #e2e8f0',
        }}
      >
        {PHASE_META.map(({ phase, label, icon }) => {
          const isUnlocked = unlocked.has(phase);
          const isActive = activePhase === phase;
          return (
            <Button
              key={phase}
              onClick={() => isUnlocked && setActivePhase(phase)}
              sx={{
                padding: '0.625rem 1rem',
                background: 'transparent',
                border: 'none',
                borderBottom: isActive ? '2px solid #2563eb' : '2px solid transparent',
                marginBottom: '-2px',
                cursor: isUnlocked ? 'pointer' : 'not-allowed',
                color: isActive ? '#2563eb' : isUnlocked ? '#374151' : '#9ca3af',
                fontWeight: isActive ? 600 : 400,
                fontSize: '0.875rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.375rem',
                borderRadius: 0,
                minWidth: 'auto',
                textTransform: 'none',
              }}
            >
              <span>{icon}</span>
              <span>
                Phase {phase}: {label}
              </span>
              {!isUnlocked && <span style={{ fontSize: '0.75rem' }}>🔒</span>}
            </Button>
          );
        })}
      </Box>

      {/* Phase content */}
      {activePhase === 1 && study.id && (
        <Box>
          {/* Research context summary */}
          {(study.research_questions.length > 0 || study.research_objectives.length > 0) && (
            <Box sx={{ marginBottom: '2rem', padding: '1rem', background: '#f8fafc', borderRadius: '0.5rem' }}>
              {study.research_objectives.length > 0 && (
                <Box sx={{ marginBottom: '0.75rem' }}>
                  <Typography variant="subtitle2" sx={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}>Research Objectives</Typography>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                    {study.research_objectives.map((o, i) => (
                      <li key={i} style={{ fontSize: '0.875rem', color: '#4b5563' }}>{o}</li>
                    ))}
                  </ul>
                </Box>
              )}
              {study.research_questions.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" sx={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}>Research Questions</Typography>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                    {study.research_questions.map((q, i) => (
                      <li key={i} style={{ fontSize: '0.875rem', color: '#4b5563' }}>{q}</li>
                    ))}
                  </ul>
                </Box>
              )}
            </Box>
          )}

          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <PICOForm studyId={study.id} />
            <SeedPapers studyId={study.id} />
          </Box>
        </Box>
      )}

      {activePhase === 2 && study.id && (
        <Box>
          <Box sx={{ marginBottom: '2rem' }}>
            <DatabaseSelectionPanel studyId={study.id} />
          </Box>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
            <CriteriaForm studyId={study.id} />
            <SearchStringEditor studyId={study.id} />
          </Box>
          <TestRetest studyId={study.id} />
        </Box>
      )}

      {activePhase === 3 && study.id && (
        <Box>
          <Box sx={{ marginBottom: '1.5rem' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <Typography variant="subtitle1" sx={{ margin: 0, fontSize: '1rem', color: '#111827' }}>Full Paper Search</Typography>
              <Button
                variant="contained"
                size="small"
                onClick={async () => {
                  try {
                    const res = (await api.post(
                      `/api/v1/studies/${study.id}/searches`,
                      { databases: ['acm', 'ieee', 'scopus'], phase_tag: 'initial-search' }
                    )) as { job_id: string; search_execution_id: number };
                    setActiveJobId(res.job_id);
                  } catch {
                    // error handled by user
                  }
                }}
                sx={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
              >
                Run Full Search
              </Button>
            </Box>
            <JobProgressPanel jobId={activeJobId} />
          </Box>
          <PaperQueue studyId={study.id} />
        </Box>
      )}

      {activePhase > 3 && (
        <Box sx={{ color: '#64748b' }}>
          <Typography>Phase {activePhase} content will be available in a future sprint.</Typography>
        </Box>
      )}
    </Box>
  );
}
