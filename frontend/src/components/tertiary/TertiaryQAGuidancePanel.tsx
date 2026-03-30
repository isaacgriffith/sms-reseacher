/**
 * TertiaryQAGuidancePanel — read-only info banner describing the six
 * mandatory secondary-study quality assessment dimensions used in Tertiary
 * Studies.
 *
 * Render this component above the existing {@link QualityChecklistEditor}
 * when the current study type is `TERTIARY`.
 *
 * @module TertiaryQAGuidancePanel
 */

import React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

// ---------------------------------------------------------------------------
// QA dimension definitions
// ---------------------------------------------------------------------------

interface QaDimension {
  /** Short label shown in the accordion summary. */
  label: string;
  /** Explanatory description shown when expanded. */
  description: string;
}

const QA_DIMENSIONS: QaDimension[] = [
  {
    label: 'Protocol Documentation Completeness',
    description:
      'Assesses whether the secondary study published a documented protocol or research ' +
      'plan before data collection began. A fully pre-registered or transparently reported ' +
      'protocol reduces the risk of reporting bias.',
  },
  {
    label: 'Search Strategy Adequacy',
    description:
      'Evaluates whether the search strategy is reported in sufficient detail to be ' +
      'reproducible — covering the databases searched, keywords or search strings used, ' +
      'and the date range of the search.',
  },
  {
    label: 'Inclusion / Exclusion Criteria Clarity',
    description:
      'Checks that the study explicitly states which types of primary studies were ' +
      'included or excluded, and that the criteria are unambiguous and consistently ' +
      'applied throughout the selection process.',
  },
  {
    label: 'Quality Assessment Approach',
    description:
      'Determines whether the secondary study applied a structured quality appraisal ' +
      'to its primary studies using explicit, reported criteria (e.g. a validated ' +
      'checklist or scoring rubric).',
  },
  {
    label: 'Synthesis Method Appropriateness',
    description:
      'Judges whether the chosen synthesis method (meta-analysis, narrative synthesis, ' +
      'thematic analysis, etc.) is justified and appropriate for the research questions ' +
      'and the nature of the included primary studies.',
  },
  {
    label: 'Validity Threats Discussion',
    description:
      'Assesses whether the secondary study identifies and discusses limitations and ' +
      'threats to both internal validity (selection bias, data extraction errors) and ' +
      'external validity (generalisability of findings).',
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * TertiaryQAGuidancePanel renders an informational banner listing and
 * explaining the six mandatory secondary-study QA dimensions.
 *
 * No props required — the panel is self-contained.
 */
export default function TertiaryQAGuidancePanel() {
  return (
    <Box sx={{ mb: 3 }}>
      <Alert severity="info" sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
          Secondary-Study Quality Assessment
        </Typography>
        <Typography variant="body2">
          This Tertiary Study uses the six mandatory dimensions below to appraise each
          included secondary study (SLR, SMS, or Rapid Review). Expand a dimension for
          guidance on how to score it.
        </Typography>
      </Alert>

      {QA_DIMENSIONS.map((dim, idx) => (
        <Accordion key={idx} disableGutters elevation={0} sx={{ border: '1px solid', borderColor: 'divider', mb: 0.5 }}>
          <AccordionSummary
            expandIcon={<span>▾</span>}
            aria-controls={`qa-dim-${idx}-content`}
            id={`qa-dim-${idx}-header`}
          >
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {idx + 1}. {dim.label}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary">
              {dim.description}
            </Typography>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
}
