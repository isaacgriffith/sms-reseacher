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
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Typography from '@mui/material/Typography';
import ProtocolEditorPage from './slr/ProtocolEditorPage';
import QualityAssessmentPage from './slr/QualityAssessmentPage';
import SynthesisPage from './slr/SynthesisPage';
import ReportPage from './slr/ReportPage';
import GreyLiteraturePage from './slr/GreyLiteraturePage';
import { usePhases } from '../hooks/slr/useProtocol';
import InterRaterPanel from '../components/slr/InterRaterPanel';
import DiscussionFlowPanel from '../components/slr/DiscussionFlowPanel';
import { useInterRaterRecords } from '../hooks/slr/useInterRater';
import RRProtocolEditorPage from './rapid/ProtocolEditorPage';
import RRSearchConfigPage from './rapid/SearchConfigPage';
import RRQualityConfigPage from './rapid/QualityConfigPage';
import RRNarrativeSynthesisPage from './rapid/NarrativeSynthesisPage';
import RREvidenceBriefingPage from './rapid/EvidenceBriefingPage';
import ProtocolGraph from '../components/protocols/ProtocolGraph';
import ProtocolNodePanel from '../components/protocols/ProtocolNodePanel';
import ExecutionStateView from '../components/protocols/ExecutionStateView';
import { useProtocolAssignment, useProtocolDetail, useResetProtocol } from '../hooks/protocols/useProtocol';
import type { ProtocolNode } from '../services/protocols/protocolsApi';

// ---------------------------------------------------------------------------
// SLR Screening View (Phase 3 for SLR studies)
// ---------------------------------------------------------------------------

interface SLRScreeningViewProps {
  studyId: number;
}

/**
 * Phase 3 screening view for SLR studies.
 * Shows the paper queue, inter-rater agreement panel, and discussion flow
 * when Kappa is below threshold.
 */
function SLRScreeningView({ studyId }: SLRScreeningViewProps) {
  const { data: irrData } = useInterRaterRecords(studyId);
  const records = irrData?.records ?? [];
  // Most recent record that is below threshold triggers the discussion panel
  const lowKappaRecord =
    [...records].reverse().find((r) => !r.threshold_met && r.phase === 'pre_discussion') ?? null;

  return (
    <Box>
      <PaperQueue studyId={studyId} />
      <Box sx={{ mt: 3 }}>
        <InterRaterPanel studyId={studyId} />
      </Box>
      {lowKappaRecord && (
        <Box sx={{ mt: 2 }}>
          <DiscussionFlowPanel studyId={studyId} record={lowKappaRecord} disagreements={[]} />
        </Box>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// StudyDetail interface
// ---------------------------------------------------------------------------

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
  { phase: 0, label: 'Protocol', icon: '🔗' },
  { phase: 1, label: 'Scoping', icon: '🎯' },
  { phase: 2, label: 'Search', icon: '🔍' },
  { phase: 3, label: 'Screening', icon: '📋' },
  { phase: 4, label: 'Extraction', icon: '📊' },
  { phase: 5, label: 'Reporting', icon: '📄' },
  { phase: 6, label: 'Report', icon: '📑' },
  { phase: 7, label: 'Grey Literature', icon: '📚' },
];

export default function StudyPage() {
  const { studyId } = useParams<{ studyId: string }>();
  const [activePhase, setActivePhase] = useState(1);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<ProtocolNode | null>(null);
  const [protocolTab, setProtocolTab] = useState<'graph' | 'execution'>('graph');
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const resetMutation = useResetProtocol();

  const {
    data: study,
    isLoading,
    error,
  } = useQuery<StudyDetail>({
    queryKey: ['study', studyId],
    queryFn: () => api.get<StudyDetail>(`/api/v1/studies/${studyId}`),
    enabled: !!studyId,
  });

  // For SLR studies, use the SLR phase gate to determine unlocked phases
  const isSLR = study?.study_type === 'SLR';
  const isRapid = study?.study_type === 'Rapid';
  const { data: slrPhases } = usePhases(isSLR && study?.id ? study.id : 0);

  // Protocol tab data (always available)
  const { data: assignment } = useProtocolAssignment(study?.id ?? 0);
  const { data: protocol } = useProtocolDetail(assignment?.protocol_id ?? 0);

  if (isLoading) return <Typography>Loading study…</Typography>;
  if (error || !study) return <Typography sx={{ color: 'red' }}>Failed to load study.</Typography>;

  // SLR studies use the SLR phase gate; SMS studies use the study's unlocked_phases
  // Phases 6 (Report) and 7 (Grey Literature) are always unlocked for SLR studies
  // Phase 0 (Protocol) is always unlocked for all study types
  const unlockedPhaseList =
    isSLR && slrPhases ? [...slrPhases.unlocked_phases, 6, 7] : study.unlocked_phases;
  const unlocked = new Set([0, ...unlockedPhaseList]);

  return (
    <Box>
      {/* Study header */}
      <Box sx={{ marginBottom: '1.5rem' }}>
        <Typography variant="h5" sx={{ margin: '0 0 0.25rem' }}>
          {study.name}
        </Typography>
        {study.topic && (
          <Typography sx={{ margin: '0 0 0.5rem', color: '#64748b' }}>{study.topic}</Typography>
        )}
        <Box sx={{ display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#64748b' }}>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b' }}>
            {study.study_type}
          </Typography>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b' }}>
            ·
          </Typography>
          <Typography
            component="span"
            sx={{ fontSize: '0.875rem', color: '#64748b', textTransform: 'capitalize' }}
          >
            {study.status}
          </Typography>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b' }}>
            ·
          </Typography>
          <Typography component="span" sx={{ fontSize: '0.875rem', color: '#64748b' }}>
            Snowball threshold: {study.snowball_threshold}
          </Typography>
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

      {/* Reset to Default confirmation dialog */}
      <Dialog open={resetDialogOpen} onClose={() => setResetDialogOpen(false)}>
        <DialogTitle>Reset Protocol to Default?</DialogTitle>
        <DialogContent>
          <Typography>
            This will replace the current protocol with the default template for this study type
            and clear all execution state. This cannot be undone while the study is executing.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialogOpen(false)}>Cancel</Button>
          <Button
            color="error"
            variant="contained"
            disabled={resetMutation.isPending}
            onClick={() => {
              if (!study.id) return;
              resetMutation.mutate(study.id, {
                onSuccess: () => setResetDialogOpen(false),
              });
            }}
          >
            {resetMutation.isPending ? 'Resetting…' : 'Reset'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Phase content */}
      {activePhase === 0 && study.id && (
        <Box>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                size="small"
                variant={protocolTab === 'graph' ? 'contained' : 'outlined'}
                onClick={() => setProtocolTab('graph')}
              >
                Graph
              </Button>
              <Button
                size="small"
                variant={protocolTab === 'execution' ? 'contained' : 'outlined'}
                onClick={() => setProtocolTab('execution')}
              >
                Execution
              </Button>
            </Box>
            <Button
              size="small"
              color="warning"
              variant="outlined"
              onClick={() => setResetDialogOpen(true)}
            >
              Reset to Default
            </Button>
          </Box>
          {protocolTab === 'graph' && (
            <>
              {protocol ? (
                <>
                  <ProtocolGraph
                    protocol={protocol}
                    onNodeClick={(node) => setSelectedNode(node)}
                    width={860}
                    height={500}
                  />
                  <ProtocolNodePanel node={selectedNode} onClose={() => setSelectedNode(null)} />
                </>
              ) : (
                <Typography sx={{ color: 'text.secondary' }}>Loading protocol graph…</Typography>
              )}
            </>
          )}
          {protocolTab === 'execution' && (
            <ExecutionStateView studyId={study.id} isAdmin={false} />
          )}
        </Box>
      )}

      {activePhase === 1 && study.id && isSLR && <ProtocolEditorPage studyId={study.id} />}

      {activePhase === 1 && study.id && isRapid && <RRProtocolEditorPage studyId={study.id} />}

      {activePhase === 1 && study.id && !isSLR && !isRapid && (
        <Box>
          {/* Research context summary */}
          {(study.research_questions.length > 0 || study.research_objectives.length > 0) && (
            <Box
              sx={{
                marginBottom: '2rem',
                padding: '1rem',
                background: '#f8fafc',
                borderRadius: '0.5rem',
              }}
            >
              {study.research_objectives.length > 0 && (
                <Box sx={{ marginBottom: '0.75rem' }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}
                  >
                    Research Objectives
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                    {study.research_objectives.map((o, i) => (
                      <li key={i} style={{ fontSize: '0.875rem', color: '#4b5563' }}>
                        {o}
                      </li>
                    ))}
                  </ul>
                </Box>
              )}
              {study.research_questions.length > 0 && (
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}
                  >
                    Research Questions
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                    {study.research_questions.map((q, i) => (
                      <li key={i} style={{ fontSize: '0.875rem', color: '#4b5563' }}>
                        {q}
                      </li>
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

      {activePhase === 2 && study.id && isRapid && <RRSearchConfigPage studyId={study.id} />}

      {activePhase === 2 && study.id && !isRapid && (
        <Box>
          <Box sx={{ marginBottom: '2rem' }}>
            <DatabaseSelectionPanel studyId={study.id} />
          </Box>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '2rem',
              marginBottom: '2rem',
            }}
          >
            <CriteriaForm studyId={study.id} />
            <SearchStringEditor studyId={study.id} />
          </Box>
          <TestRetest studyId={study.id} />
        </Box>
      )}

      {activePhase === 3 && study.id && !isSLR && (
        <Box>
          <Box sx={{ marginBottom: '1.5rem' }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '1rem',
              }}
            >
              <Typography
                variant="subtitle1"
                sx={{ margin: 0, fontSize: '1rem', color: '#111827' }}
              >
                Full Paper Search
              </Typography>
              <Button
                variant="contained"
                size="small"
                onClick={async () => {
                  try {
                    const res = (await api.post(`/api/v1/studies/${study.id}/searches`, {
                      databases: ['acm', 'ieee', 'scopus'],
                      phase_tag: 'initial-search',
                    })) as { job_id: string; search_execution_id: number };
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

      {activePhase === 3 && study.id && isSLR && <SLRScreeningView studyId={study.id} />}

      {activePhase === 4 && study.id && isSLR && (
        <QualityAssessmentPage studyId={study.id} reviewerId={0} />
      )}

      {activePhase === 4 && study.id && isRapid && <RRQualityConfigPage studyId={study.id} />}

      {activePhase === 4 && study.id && !isSLR && !isRapid && (
        <Box sx={{ color: '#64748b' }}>
          <Typography>Phase 4 content will be available in a future sprint.</Typography>
        </Box>
      )}

      {activePhase === 5 && study.id && isSLR && <SynthesisPage studyId={study.id} />}

      {activePhase === 5 && study.id && isRapid && <RRNarrativeSynthesisPage studyId={study.id} />}

      {activePhase === 5 && study.id && !isSLR && !isRapid && (
        <Box sx={{ color: '#64748b' }}>
          <Typography>Phase 5 content will be available in a future sprint.</Typography>
        </Box>
      )}

      {activePhase === 6 && study.id && isSLR && (
        <ReportPage studyId={study.id} synthesisComplete={unlocked.has(5)} />
      )}

      {activePhase === 6 && study.id && isRapid && <RREvidenceBriefingPage studyId={study.id} />}

      {activePhase === 7 && study.id && isSLR && <GreyLiteraturePage studyId={study.id} />}

      {(activePhase === 6 || activePhase === 7) && study.id && !isSLR && !isRapid && (
        <Box sx={{ color: '#64748b' }}>
          <Typography>This feature is only available for SLR studies.</Typography>
        </Box>
      )}
    </Box>
  );
}
