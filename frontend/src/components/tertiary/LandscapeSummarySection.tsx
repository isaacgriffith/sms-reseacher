/**
 * LandscapeSummarySection — collapsible display of the three Landscape of
 * Secondary Studies sub-fields from a Tertiary Study report.
 *
 * Renders the timeline summary, research question evolution, and synthesis
 * method shifts as MUI Accordion panels so each sub-section can be
 * independently expanded or collapsed.
 *
 * @module LandscapeSummarySection
 */

import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
import Typography from '@mui/material/Typography';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Landscape of Secondary Studies section of a Tertiary Study report. */
export interface LandscapeSection {
  /** Aggregated study period coverage across included secondary studies. */
  timeline_summary: string;
  /** How research questions have shifted across the reviewed secondary studies. */
  research_question_evolution: string;
  /** Summary of synthesis methods used and how they have changed. */
  synthesis_method_shifts: string;
}

/** Props for {@link LandscapeSummarySection}. */
export interface LandscapeSummarySectionProps {
  /** Landscape section data from the generated Tertiary Report. */
  landscape: LandscapeSection;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * LandscapeSummarySection displays the three landscape sub-fields as
 * collapsible MUI Accordion panels.
 *
 * @param landscape - The landscape section data to display.
 */
export default function LandscapeSummarySection({ landscape }: LandscapeSummarySectionProps) {
  return (
    <>
      <LandscapePanel
        title="Timeline of Secondary Studies"
        content={landscape.timeline_summary}
        defaultExpanded
      />
      <LandscapePanel
        title="Research Question Evolution"
        content={landscape.research_question_evolution}
      />
      <LandscapePanel
        title="Synthesis Method Shifts"
        content={landscape.synthesis_method_shifts}
      />
    </>
  );
}

// ---------------------------------------------------------------------------
// Sub-component
// ---------------------------------------------------------------------------

interface LandscapePanelProps {
  title: string;
  content: string;
  defaultExpanded?: boolean;
}

/**
 * A single collapsible accordion panel for one landscape sub-field.
 *
 * @param title - Panel heading text.
 * @param content - Body text to display when expanded.
 * @param defaultExpanded - Whether the panel is open by default.
 */
function LandscapePanel({ title, content, defaultExpanded = false }: LandscapePanelProps) {
  return (
    <Accordion defaultExpanded={defaultExpanded}>
      <AccordionSummary
        expandIcon={<ExpandIcon />}
        aria-controls={`${title}-content`}
        id={`${title}-header`}
      >
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
          {content}
        </Typography>
      </AccordionDetails>
    </Accordion>
  );
}

// ---------------------------------------------------------------------------
// Simple expand icon (avoids importing from @mui/icons-material)
// ---------------------------------------------------------------------------

/** Minimal SVG chevron used as the accordion expand icon. */
function ExpandIcon() {
  return (
    <svg
      aria-hidden="true"
      focusable="false"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      style={{ fill: 'currentColor' }}
    >
      <path d="M7 10l5 5 5-5z" />
    </svg>
  );
}
