/**
 * TertiaryStudyPage — top-level dashboard for a Tertiary Study.
 *
 * Renders a phase-gate tab bar driven by the study's unlocked phases,
 * and routes to the appropriate content panel for each phase:
 *
 * - Phase 1 (Protocol):           TertiaryProtocolForm + validate action
 * - Phase 2 (Search & Import):    placeholder for seed import (Phase 4 tasks)
 * - Phase 3 (Screening):          standard paper queue (existing component)
 * - Phase 4 (Quality Assessment): standard QA (existing component)
 * - Phase 5 (Synthesis & Report): placeholder (Phase 7 tasks)
 *
 * Uses TanStack Query for protocol GET/PUT/validate mutations.
 *
 * @module TertiaryStudyPage
 */

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Typography from '@mui/material/Typography';
import TertiaryProtocolForm from '../components/tertiary/TertiaryProtocolForm';
import SeedImportPanel from '../components/tertiary/SeedImportPanel';
import TertiaryExtractionForm from '../components/tertiary/TertiaryExtractionForm';
import TertiaryReportPage from './TertiaryReportPage';
import PaperQueue from '../components/phase2/PaperQueue';
import {
  useTertiaryProtocol,
  useUpdateTertiaryProtocol,
  useValidateTertiaryProtocol,
} from '../hooks/tertiary/useProtocol';
import { useExtractions, useUpdateExtraction, useAiAssist } from '../hooks/tertiary/useExtractions';
import {
  startSynthesis,
  listSynthesisResults,
  type SynthesisResult,
} from '../services/slr/synthesisApi';
import type { TertiaryProtocolUpdate } from '../services/tertiary/protocolApi';
import type { TertiaryExtraction, TertiaryExtractionUpdate } from '../services/tertiary/extractionApi';

// ---------------------------------------------------------------------------
// Phase metadata
// ---------------------------------------------------------------------------

const PHASE_META = [
  { phase: 1, label: 'Protocol' },
  { phase: 2, label: 'Search & Import' },
  { phase: 3, label: 'Screening' },
  { phase: 4, label: 'Quality Assessment' },
  { phase: 5, label: 'Synthesis & Report' },
];

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link TertiaryStudyPage}. */
export interface TertiaryStudyPageProps {
  /** Integer study ID. */
  studyId: number;
  /** Set of unlocked phase numbers from the phase gate. */
  unlockedPhases: Set<number>;
  /** Research group ID — required for listing available import sources. */
  groupId: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * TertiaryStudyPage renders the full dashboard for a Tertiary Study.
 *
 * @param studyId - The study to display.
 * @param unlockedPhases - Phase numbers that are currently accessible.
 */
export default function TertiaryStudyPage({
  studyId,
  unlockedPhases,
  groupId,
}: TertiaryStudyPageProps) {
  const [activePhase, setActivePhase] = useState(1);

  return (
    <Box>
      <PhaseTabs
        activePhase={activePhase}
        unlockedPhases={unlockedPhases}
        onSelect={setActivePhase}
      />
      <Box sx={{ mt: 2 }}>
        {activePhase === 1 && <Phase1Panel studyId={studyId} />}
        {activePhase === 2 && <Phase2Panel studyId={studyId} groupId={groupId} />}
        {activePhase === 3 && <Phase3Panel studyId={studyId} />}
        {activePhase === 4 && <Phase4Panel studyId={studyId} />}
        {activePhase === 5 && <Phase5Panel studyId={studyId} />}
      </Box>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Phase 1 panel — Protocol editor
// ---------------------------------------------------------------------------

interface Phase1PanelProps {
  studyId: number;
}

/**
 * Phase 1 content: protocol form + validate action button.
 *
 * @param studyId - The Tertiary Study ID.
 */
function Phase1Panel({ studyId }: Phase1PanelProps) {
  const { data: protocol, isLoading, error } = useTertiaryProtocol(studyId);
  const updateMutation = useUpdateTertiaryProtocol(studyId);
  const validateMutation = useValidateTertiaryProtocol(studyId);

  if (isLoading) {
    return <CircularProgress size={24} />;
  }
  if (error) {
    return <Alert severity="error">Failed to load protocol.</Alert>;
  }

  const isValidated = protocol?.status === 'validated';

  function handleSave(data: TertiaryProtocolUpdate) {
    updateMutation.mutate(data);
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Tertiary Study Protocol
      </Typography>

      {updateMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to save: {(updateMutation.error as Error)?.message}
        </Alert>
      )}
      {validateMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to validate: {(validateMutation.error as Error)?.message}
        </Alert>
      )}
      {validateMutation.isSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Protocol validated. Phase 2 is now unlocked.
        </Alert>
      )}

      <TertiaryProtocolForm
        protocol={protocol ?? null}
        isSaving={updateMutation.isPending}
        onSave={handleSave}
      />

      {!isValidated && (
        <>
          <Divider sx={{ my: 2 }} />
          <ValidateButton
            isValidating={validateMutation.isPending}
            hasProtocol={!!protocol}
            onValidate={() => validateMutation.mutate()}
          />
        </>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Validate button sub-component
// ---------------------------------------------------------------------------

interface ValidateButtonProps {
  isValidating: boolean;
  hasProtocol: boolean;
  onValidate: () => void;
}

/**
 * Validate button for approving the Tertiary Study protocol.
 *
 * @param isValidating - Whether validation is in progress.
 * @param hasProtocol - Whether a protocol record exists.
 * @param onValidate - Callback to trigger validation.
 */
function ValidateButton({ isValidating, hasProtocol, onValidate }: ValidateButtonProps) {
  return (
    <Button
      variant="contained"
      color="success"
      disabled={!hasProtocol || isValidating}
      onClick={onValidate}
    >
      {isValidating ? 'Validating…' : 'Validate Protocol'}
    </Button>
  );
}

// ---------------------------------------------------------------------------
// Phase 2 panel — Search & Import
// ---------------------------------------------------------------------------

interface Phase2PanelProps {
  studyId: number;
  groupId: number;
}

/**
 * Phase 2 content: seed import panel.
 *
 * @param studyId - The Tertiary Study ID.
 * @param groupId - The research group ID for listing source studies.
 */
function Phase2Panel({ studyId, groupId }: Phase2PanelProps) {
  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Search &amp; Import
      </Typography>
      <SeedImportPanel studyId={studyId} groupId={groupId} />
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Phase 3 panel — Screening
// ---------------------------------------------------------------------------

interface Phase3PanelProps {
  studyId: number;
}

/**
 * Phase 3 content: candidate paper queue for screening seed-imported secondary
 * studies. Reuses the existing PaperQueue component, which supports
 * accept/reject/duplicate decisions and phase-tag filtering.
 *
 * @param studyId - The Tertiary Study ID.
 */
function Phase3Panel({ studyId }: Phase3PanelProps) {
  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Screening
      </Typography>
      <PaperQueue studyId={studyId} />
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Phase 4 panel — Quality Assessment & Extraction
// ---------------------------------------------------------------------------

interface Phase4PanelProps {
  studyId: number;
}

/**
 * Phase 4 content: extraction list with per-record form and AI-assist button.
 *
 * @param studyId - The Tertiary Study ID.
 */
function Phase4Panel({ studyId }: Phase4PanelProps) {
  const [selected, setSelected] = useState<TertiaryExtraction | null>(null);
  const { data: extractions = [], isLoading, error } = useExtractions(studyId);
  const updateMutation = useUpdateExtraction(studyId);
  const aiAssistMutation = useAiAssist(studyId);

  if (isLoading) return <CircularProgress size={24} />;
  if (error) return <Alert severity="error">Failed to load extractions.</Alert>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Quality Assessment &amp; Extraction
        </Typography>
        <Button
          variant="outlined"
          disabled={aiAssistMutation.isPending || extractions.length === 0}
          onClick={() => aiAssistMutation.mutate()}
        >
          {aiAssistMutation.isPending ? 'Running AI Pre-fill…' : 'AI Pre-fill'}
        </Button>
      </Box>

      {aiAssistMutation.isSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          AI extraction job queued for {aiAssistMutation.data.paper_count} paper(s). Refresh to see results.
        </Alert>
      )}

      {extractions.length === 0 ? (
        <Alert severity="info">
          No accepted papers yet. Import seed papers in Phase 2 and screen them in Phase 3 first.
        </Alert>
      ) : (
        <ExtractionList
          extractions={extractions}
          selected={selected}
          onSelect={setSelected}
          isSaving={updateMutation.isPending}
          onSave={(data: TertiaryExtractionUpdate) => {
            if (selected) {
              updateMutation.mutate({ extractionId: selected.id, data });
            }
          }}
        />
      )}
    </Box>
  );
}

/**
 * Renders a list of extraction records; clicking one opens the form.
 */
function ExtractionList({
  extractions,
  selected,
  onSelect,
  isSaving,
  onSave,
}: {
  extractions: TertiaryExtraction[];
  selected: TertiaryExtraction | null;
  onSelect: (e: TertiaryExtraction) => void;
  isSaving: boolean;
  onSave: Parameters<typeof TertiaryExtractionForm>[0]['onSave'];
}) {
  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: selected ? '280px 1fr' : '1fr', gap: 2 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {extractions.map((e) => (
          <Box
            key={e.id}
            onClick={() => onSelect(e)}
            sx={{
              p: 1.5,
              border: '1px solid',
              borderColor: selected?.id === e.id ? 'primary.main' : 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              bgcolor: selected?.id === e.id ? 'primary.light' : 'transparent',
              '&:hover': { bgcolor: 'action.hover' },
            }}
          >
            <Typography variant="body2" noWrap sx={{ fontWeight: 600 }}>
              {e.paper_title ?? `Paper #${e.candidate_paper_id}`}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {e.extraction_status}
            </Typography>
          </Box>
        ))}
      </Box>

      {selected && (
        <TertiaryExtractionForm
          extraction={selected}
          isSaving={isSaving}
          onSave={onSave}
        />
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Phase 5 panel — Synthesis & Report
// ---------------------------------------------------------------------------

interface Phase5PanelProps {
  studyId: number;
}

/**
 * Phase 5 content: synthesis approach selector, Run Synthesis button, and
 * TertiaryReportPage once synthesis is complete.
 *
 * @param studyId - The Tertiary Study ID.
 */
function Phase5Panel({ studyId }: Phase5PanelProps) {
  const [approach, setApproach] = useState<'narrative' | 'thematic'>('narrative');

  const synthesisMutation = useMutation<SynthesisResult, Error, 'narrative' | 'thematic'>({
    mutationFn: (selectedApproach) =>
      startSynthesis(studyId, { approach: selectedApproach, parameters: {} }),
  });

  const latestId = synthesisMutation.data?.id ?? null;

  const { data: pollResult } = useQuery({
    queryKey: ['synthesis-poll', latestId],
    queryFn: () => listSynthesisResults(studyId),
    enabled: latestId !== null,
    refetchInterval: (query) => {
      const results = query.state.data;
      const latest = results?.results?.find((r: SynthesisResult) => r.id === latestId);
      if (latest?.status === 'completed' || latest?.status === 'failed') return false;
      return 3000;
    },
  });

  const latestResult = pollResult?.results?.find((r: SynthesisResult) => r.id === latestId);
  const isCompleted = latestResult?.status === 'completed';
  const isFailed = latestResult?.status === 'failed';
  const isRunning =
    synthesisMutation.isPending ||
    (latestId !== null && !isCompleted && !isFailed);

  if (isCompleted) {
    return (
      <Box>
        <Alert severity="success" sx={{ mb: 2 }}>
          Synthesis complete. Report is ready.
        </Alert>
        <TertiaryReportPage studyId={studyId} />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Synthesis &amp; Report
      </Typography>

      {synthesisMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to start synthesis: {synthesisMutation.error?.message}
        </Alert>
      )}
      {isFailed && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Synthesis failed: {latestResult?.error_message ?? 'Unknown error.'}
        </Alert>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Select
          size="small"
          value={approach}
          onChange={(e) => setApproach(e.target.value as 'narrative' | 'thematic')}
          disabled={isRunning}
          sx={{ minWidth: 180 }}
        >
          <MenuItem value="narrative">Narrative Synthesis</MenuItem>
          <MenuItem value="thematic">Thematic Analysis</MenuItem>
        </Select>

        <Button
          variant="contained"
          disabled={isRunning}
          onClick={() => synthesisMutation.mutate(approach)}
        >
          {isRunning ? (
            <>
              <CircularProgress size={16} sx={{ mr: 1 }} />
              Running…
            </>
          ) : (
            'Run Synthesis'
          )}
        </Button>
      </Box>

      {isRunning && latestId !== null && (
        <Alert severity="info">
          Synthesis is running in the background. This page will update when complete.
        </Alert>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Phase tab bar
// ---------------------------------------------------------------------------

interface PhaseTabsProps {
  activePhase: number;
  unlockedPhases: Set<number>;
  onSelect: (phase: number) => void;
}

/**
 * Phase navigation tabs for the Tertiary Study dashboard.
 *
 * @param activePhase - Currently active phase number.
 * @param unlockedPhases - Set of unlocked phase numbers.
 * @param onSelect - Callback when a tab is clicked.
 */
function PhaseTabs({ activePhase, unlockedPhases, onSelect }: PhaseTabsProps) {
  return (
    <Box sx={{ display: 'flex', borderBottom: '2px solid #e2e8f0', mb: 2 }}>
      {PHASE_META.map(({ phase, label }) => {
        const isUnlocked = unlockedPhases.has(phase);
        const isActive = activePhase === phase;
        return (
          <Button
            key={phase}
            onClick={() => isUnlocked && onSelect(phase)}
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
              borderRadius: 0,
              minWidth: 'auto',
              textTransform: 'none',
              gap: '0.25rem',
            }}
          >
            Phase {phase}: {label}
            {!isUnlocked && <span style={{ fontSize: '0.75rem' }}>🔒</span>}
          </Button>
        );
      })}
    </Box>
  );
}


