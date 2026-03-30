/**
 * ThreatToValidityList — read-only list of RR threats to validity (feature 008).
 *
 * Displays each {@link Threat} as a labelled chip/badge and description row.
 * Intended to be embedded in forms and pages that need to surface the
 * current threat inventory to the researcher.
 *
 * @module ThreatToValidityList
 */

import React from 'react';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Typography from '@mui/material/Typography';
import type { Threat } from '../../services/rapid/protocolApi';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link ThreatToValidityList}. */
interface ThreatToValidityListProps {
  /** List of threats to display. */
  threats: Threat[];
}

// ---------------------------------------------------------------------------
// Threat type display helpers
// ---------------------------------------------------------------------------

const THREAT_LABELS: Record<string, string> = {
  single_source: 'Single Source',
  year_range: 'Year Range',
  language: 'Language',
  geography: 'Geography',
  study_design: 'Study Design',
  single_reviewer: 'Single Reviewer',
  qa_skipped: 'QA Skipped',
  qa_simplified: 'QA Simplified',
  context_restriction: 'Context Restriction',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Renders an ordered list of Rapid Review threats-to-validity.
 *
 * Each item shows a type chip and the human-readable description.
 * Renders a muted "No threats recorded yet." message when the list is empty.
 *
 * @param threats - List of {@link Threat} objects to display.
 */
export default function ThreatToValidityList({
  threats,
}: ThreatToValidityListProps): React.ReactElement {
  if (threats.length === 0) {
    return (
      <Typography variant="body2" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
        No threats recorded yet.
      </Typography>
    );
  }

  return (
    <Box component="ul" sx={{ m: 0, p: 0, listStyle: 'none' }}>
      {threats.map((threat) => (
        <Box
          component="li"
          key={threat.id}
          sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 1 }}
        >
          <Chip
            label={THREAT_LABELS[threat.threat_type] ?? threat.threat_type}
            size="small"
            color="warning"
            variant="outlined"
            sx={{ flexShrink: 0, mt: 0.25 }}
          />
          <Box>
            <Typography variant="body2">{threat.description}</Typography>
            {threat.source_detail != null && (
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {threat.source_detail}
              </Typography>
            )}
          </Box>
        </Box>
      ))}
    </Box>
  );
}
