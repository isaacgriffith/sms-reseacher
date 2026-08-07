/**
 * Study-type → phase-renderer dispatch for the study workspace.
 *
 * `StudyPage` previously chose phase content through eleven paired `isSLR` /
 * `isRapid` checks. That shape is a Principle III violation (type-switching),
 * and it is how the Tertiary workspace became unreachable: a new study type
 * falls through every `!isSLR && !isRapid` branch and silently renders the
 * mapping-study workspace instead of failing.
 *
 * This mirrors the backend's `_PHASE_GATE_DISPATCH`, which maps `StudyType` to
 * a gate function. Adding a study type here means adding a map entry — and an
 * omission produces a blank phase, which a test catches, rather than a
 * plausible-looking wrong workspace, which no test catches.
 *
 * Behaviour is preserved exactly, including two cells that look like mistakes
 * and are not:
 *
 * - **Rapid has no phase 7.** Grey literature is SLR-only, and the "SLR studies
 *   only" notice is shown for mapping studies alone, so Rapid renders nothing.
 * - **SLR shares the mapping study's phase 2.** The original branch keyed on
 *   `!isRapid`, not on the study type.
 *
 * Both are pinned by `StudyPage.dispatch.test.tsx`.
 */

import type { ReactNode } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

import PICOForm from '../phase1/PICOForm';
import SeedPapers from '../phase1/SeedPapers';
import CriteriaForm from '../phase2/CriteriaForm';
import SearchStringEditor from '../phase2/SearchStringEditor';
import TestRetest from '../phase2/TestRetest';
import PaperQueue from '../phase2/PaperQueue';
import FullSearchControl from '../phase2/FullSearchControl';
import SnowballControls from '../phase2/SnowballControls';
import JobProgressPanel from '../jobs/JobProgressPanel';
import DatabaseSelectionPanel from './DatabaseSelectionPanel';
import InterRaterPanel from '../slr/InterRaterPanel';
import DiscussionFlowPanel from '../slr/DiscussionFlowPanel';
import { useInterRaterRecords } from '../../hooks/slr/useInterRater';
import SLRProtocolEditorPage from '../../pages/slr/ProtocolEditorPage';
import QualityAssessmentPage from '../../pages/slr/QualityAssessmentPage';
import SynthesisPage from '../../pages/slr/SynthesisPage';
import ReportPage from '../../pages/slr/ReportPage';
import GreyLiteraturePage from '../../pages/slr/GreyLiteraturePage';
import RRProtocolEditorPage from '../../pages/rapid/ProtocolEditorPage';
import RRSearchConfigPage from '../../pages/rapid/SearchConfigPage';
import RRQualityConfigPage from '../../pages/rapid/QualityConfigPage';
import RRNarrativeSynthesisPage from '../../pages/rapid/NarrativeSynthesisPage';
import RREvidenceBriefingPage from '../../pages/rapid/EvidenceBriefingPage';

/** A study as returned by `GET /api/v1/studies/{id}`. */
export interface StudyDetail {
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
  /** The current user's role on this study — "lead" or "member". */
  viewer_role: string;
  created_at: string;
  updated_at: string;
}

/** Everything a phase renderer may need from the hosting page. */
export interface PhaseContext {
  /** The study being displayed. */
  study: StudyDetail;
  /** Id of the background job whose progress is being shown, if any. */
  activeJobId: string | null;
  /** Called when a renderer starts a job whose progress the page should show. */
  onJobStarted: (jobId: string) => void;
  /** Phases currently unlocked, used to gate content within a phase. */
  unlocked: Set<number>;
}

/** Renders one phase's body for one study type. */
type PhaseRenderer = (ctx: PhaseContext) => ReactNode;

/** Phase number → renderer, for a single study type. */
export type PhaseMap = Record<number, PhaseRenderer>;

// ---------------------------------------------------------------------------
// SLR screening (phase 3)
// ---------------------------------------------------------------------------

interface SLRScreeningViewProps {
  studyId: number;
}

/**
 * Phase 3 screening view for SLR studies.
 *
 * Shows the paper queue, the inter-rater agreement panel, and the discussion
 * flow when Kappa is below threshold.
 *
 * @param props - The study to screen.
 */
function SLRScreeningView({ studyId }: SLRScreeningViewProps) {
  const { data: irrData } = useInterRaterRecords(studyId);
  const records = irrData?.records ?? [];
  // Most recent record below threshold triggers the discussion panel
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
// Renderers shared by more than one study type
// ---------------------------------------------------------------------------

/** Phase 1 for mapping studies: research context, then PICO and seed papers. */
function renderScoping({ study }: PhaseContext): ReactNode {
  return (
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
  );
}

/**
 * Phase 2 search setup. Shared by mapping studies and SLRs — the original
 * branch keyed on `!isRapid`, so both types land here.
 */
function renderSearchSetup({ study }: PhaseContext): ReactNode {
  return (
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
  );
}

/**
 * Phase 3 search-and-screen. Shared by mapping studies and Rapid reviews — the
 * original branch keyed on `!isSLR`.
 */
function renderSearchAndScreen({ study, activeJobId, onJobStarted }: PhaseContext): ReactNode {
  return (
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
          <Typography variant="subtitle1" sx={{ margin: 0, fontSize: '1rem', color: '#111827' }}>
            Full Paper Search
          </Typography>
          <FullSearchControl studyId={study.id} onJobStarted={onJobStarted} />
        </Box>
        <Box sx={{ marginBottom: '1rem' }}>
          <Typography
            variant="subtitle2"
            sx={{ margin: '0 0 0.5rem', fontSize: '0.875rem', color: '#374151' }}
          >
            Snowball Sampling
          </Typography>
          <SnowballControls studyId={study.id} onJobStarted={onJobStarted} />
        </Box>
        <JobProgressPanel jobId={activeJobId} />
      </Box>
      <PaperQueue studyId={study.id} />
    </Box>
  );
}

/**
 * Builds a "not yet available" placeholder for a phase.
 *
 * @param phase - Phase number named in the message.
 * @returns A renderer producing the placeholder.
 */
function futureSprintPlaceholder(phase: number): PhaseRenderer {
  return () => (
    <Box sx={{ color: '#64748b' }}>
      <Typography>Phase {phase} content will be available in a future sprint.</Typography>
    </Box>
  );
}

/** Notice shown when a mapping study opens an SLR-only phase. */
function renderSlrOnlyNotice(): ReactNode {
  return (
    <Box sx={{ color: '#64748b' }}>
      <Typography>This feature is only available for SLR studies.</Typography>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Per-study-type maps
// ---------------------------------------------------------------------------

/**
 * Systematic Mapping Study.
 *
 * Also the fallback for any type without its own map, which currently means
 * Tertiary — the reason its workspace is unreachable (G19). Task T024 gives
 * Tertiary an entry of its own.
 */
const MAPPING_STUDY_PHASES: PhaseMap = {
  1: renderScoping,
  2: renderSearchSetup,
  3: renderSearchAndScreen,
  4: futureSprintPlaceholder(4),
  5: futureSprintPlaceholder(5),
  6: renderSlrOnlyNotice,
  7: renderSlrOnlyNotice,
};

/** Systematic Literature Review. */
const SLR_PHASES: PhaseMap = {
  1: ({ study }) => <SLRProtocolEditorPage studyId={study.id} />,
  2: renderSearchSetup,
  3: ({ study }) => <SLRScreeningView studyId={study.id} />,
  4: ({ study }) => <QualityAssessmentPage studyId={study.id} reviewerId={0} />,
  5: ({ study }) => <SynthesisPage studyId={study.id} />,
  6: ({ study, unlocked }) => <ReportPage studyId={study.id} synthesisComplete={unlocked.has(5)} />,
  7: ({ study }) => <GreyLiteraturePage studyId={study.id} />,
};

/**
 * Rapid Review.
 *
 * No phase 7: grey literature is SLR-only, and the "SLR studies only" notice is
 * shown for mapping studies alone. A Rapid review therefore renders nothing at
 * phase 7 — preserved deliberately, and asserted in the dispatch tests.
 */
const RAPID_PHASES: PhaseMap = {
  1: ({ study }) => <RRProtocolEditorPage studyId={study.id} />,
  2: ({ study }) => <RRSearchConfigPage studyId={study.id} />,
  3: renderSearchAndScreen,
  4: ({ study }) => <RRQualityConfigPage studyId={study.id} />,
  5: ({ study }) => <RRNarrativeSynthesisPage studyId={study.id} />,
  6: ({ study }) => <RREvidenceBriefingPage studyId={study.id} />,
};

/** Study type → its phase map. Mirrors the backend's `_PHASE_GATE_DISPATCH`. */
export const STUDY_TYPE_PHASES: Record<string, PhaseMap> = {
  SMS: MAPPING_STUDY_PHASES,
  SLR: SLR_PHASES,
  Rapid: RAPID_PHASES,
};

/** Used for a study type with no map of its own. */
export const DEFAULT_PHASE_MAP: PhaseMap = MAPPING_STUDY_PHASES;

/**
 * Renders the body of one phase for one study type.
 *
 * @param studyType - The study's `study_type` value.
 * @param phase - Active phase number. Phase 0 is the protocol tab, which is
 *   common to every study type and stays with the hosting page.
 * @param ctx - Data and callbacks the renderer may need.
 * @returns The phase body, or `null` when this type has no content for it.
 */
export function renderStudyPhase(studyType: string, phase: number, ctx: PhaseContext): ReactNode {
  if (!ctx.study.id) return null;
  const renderer = (STUDY_TYPE_PHASES[studyType] ?? DEFAULT_PHASE_MAP)[phase];
  return renderer ? renderer(ctx) : null;
}
