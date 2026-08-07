/**
 * Study page: study header, phase tabs, the protocol tab, and the per-phase
 * body for the study's type.
 *
 * Phase bodies live in `components/studies/studyTypeDispatch.tsx`. This page
 * owns what every study type shares — fetching the study, gating which phases
 * are open, the protocol tab, and the reset dialog — and delegates the rest.
 */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Typography from '@mui/material/Typography';
import { usePhases } from '../hooks/slr/useProtocol';
import ProtocolGraph from '../components/protocols/ProtocolGraph';
import ProtocolNodePanel from '../components/protocols/ProtocolNodePanel';
import ExecutionStateView from '../components/protocols/ExecutionStateView';
import {
  useProtocolAssignment,
  useProtocolDetail,
  useResetProtocol,
} from '../hooks/protocols/useProtocol';
import type { ProtocolNode } from '../services/protocols/protocolsApi';
import { renderStudyPhase } from '../components/studies/studyTypeDispatch';
import type { StudyDetail } from '../components/studies/studyTypeDispatch';

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

  // Phase *gating*, not phase rendering: SLR studies take their unlocked
  // phases from the SLR phase-gate endpoint rather than from the study row.
  // Which body each phase shows is decided by the dispatch map, not here.
  const usesSlrPhaseGate = study?.study_type === 'SLR';
  const { data: slrPhases } = usePhases(usesSlrPhaseGate && study?.id ? study.id : 0);

  // Protocol tab data (always available)
  const { data: assignment, isPending: assignmentPending } = useProtocolAssignment(study?.id ?? 0);
  const { data: protocol, isPending: protocolPending } = useProtocolDetail(
    assignment?.protocol_id ?? 0,
  );
  // The assignment endpoint 404s when a study has no protocol assigned. Without
  // this distinction the graph pane showed "Loading…" forever instead of
  // saying nothing is assigned.
  const protocolLoading = assignmentPending || (assignment != null && protocolPending);

  if (isLoading) return <Typography>Loading study…</Typography>;
  if (error || !study) return <Typography sx={{ color: 'red' }}>Failed to load study.</Typography>;

  // SLR studies use the SLR phase gate; other types use the study's own list.
  // Phases 6 (Report) and 7 (Grey Literature) are always unlocked for SLRs.
  // Phase 0 (Protocol) is always unlocked for every study type.
  const unlockedPhaseList =
    usesSlrPhaseGate && slrPhases ? [...slrPhases.unlocked_phases, 6, 7] : study.unlocked_phases;
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
              // Locked phases were only styled as unavailable (cursor + 🔒),
              // leaving them focusable and announcing nothing to assistive
              // technology. disabled gives them real semantics.
              disabled={!isUnlocked}
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
            This will replace the current protocol with the default template for this study type and
            clear all execution state. This cannot be undone while the study is executing.
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

      {/* Phase 0 — the protocol tab, common to every study type */}
      {activePhase === 0 && study.id && (
        <Box>
          <Box
            sx={{
              display: 'flex',
              gap: 1,
              mb: 2,
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
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
              ) : protocolLoading ? (
                <Typography sx={{ color: 'text.secondary' }}>Loading protocol graph…</Typography>
              ) : (
                <Typography sx={{ color: 'text.secondary' }}>
                  No protocol is assigned to this study. Choose one from the Protocol Library.
                </Typography>
              )}
            </>
          )}
          {protocolTab === 'execution' && (
            // Mark Complete / Approve are LEAD-only server-side, so gate them on
            // the caller's actual role. This was hardcoded to false, which made
            // both actions unreachable for every user.
            <ExecutionStateView studyId={study.id} isAdmin={study.viewer_role === 'lead'} />
          )}
        </Box>
      )}

      {/* Phases 1–7 — dispatched on study type */}
      {activePhase > 0 &&
        renderStudyPhase(study.study_type, activePhase, {
          study,
          activeJobId,
          onJobStarted: setActiveJobId,
          unlocked,
        })}
    </Box>
  );
}
