/**
 * BriefingPreview — read-only display of evidence briefing content sections
 * (feature 008).
 *
 * @module BriefingPreview
 */

import React from 'react';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import type { BriefingDetail, PublicBriefing } from '../../services/rapid/briefingApi';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** A single threat-to-validity item. */
interface ThreatItem {
  threat_type: string;
  description: string;
  source_detail: string | null;
}

/** Props for {@link BriefingPreview}. */
interface BriefingPreviewProps {
  /** The briefing to render — either an authenticated detail or public version. */
  briefing: BriefingDetail | PublicBriefing;
  /**
   * Optional threats-to-validity items. Shown in the Target Audience section
   * when provided.
   */
  threats?: ThreatItem[];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Renders a structured, read-only preview of an evidence briefing.
 *
 * Sections rendered:
 * 1. Title
 * 2. Summary
 * 3. Findings per research question
 * 4. Target Audience (with optional threats list)
 * 5. Reference to Complementary Material (if present)
 * 6. Institution Logos (if present)
 *
 * @param briefing - The briefing data to display.
 * @param threats - Optional array of threats-to-validity to display.
 */
export default function BriefingPreview({
  briefing,
  threats,
}: BriefingPreviewProps): React.ReactElement {
  const findingEntries = Object.entries(briefing.findings);

  return (
    <Box>
      {/* Title */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h5">{briefing.title}</Typography>
      </Paper>

      {/* Summary */}
      {briefing.summary && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Summary
          </Typography>
          <Typography variant="body1">{briefing.summary}</Typography>
        </Paper>
      )}

      {/* Findings per research question */}
      {findingEntries.length > 0 && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Findings
          </Typography>
          {findingEntries.map(([rqIndex, text], idx) => (
            <Box key={rqIndex}>
              {idx > 0 && <Divider sx={{ my: 1.5 }} />}
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                RQ {rqIndex}
              </Typography>
              <Typography variant="body2">{text}</Typography>
            </Box>
          ))}
        </Paper>
      )}

      {/* Target Audience */}
      {briefing.target_audience && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Target Audience
          </Typography>
          <Typography variant="body2">{briefing.target_audience}</Typography>

          {/* Threats to validity */}
          {threats && threats.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Threats to Validity
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {threats.map((t, i) => (
                  <Chip
                    key={i}
                    label={`${t.threat_type}: ${t.description}`}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
        </Paper>
      )}

      {/* Reference to complementary material */}
      {briefing.reference_complementary && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Reference to Complementary Material
          </Typography>
          <Typography variant="body2">{briefing.reference_complementary}</Typography>
        </Paper>
      )}

      {/* Institution logos */}
      {briefing.institution_logos.length > 0 && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Institution Logos
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {briefing.institution_logos.map((logoPath, i) => (
              <Chip key={i} label={logoPath} size="small" variant="outlined" />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
}
