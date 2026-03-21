/**
 * ProtocolReviewReport — displays the AI protocol review result.
 *
 * Renders issues grouped by section with severity chips.
 * Shows a loading skeleton while status === "under_review".
 * Shows an empty-state message when review_report is null.
 *
 * @module ProtocolReviewReport
 */

import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Skeleton from '@mui/material/Skeleton';
import Alert from '@mui/material/Alert';
import type { ReviewProtocol, ProtocolIssue } from '../../services/slr/protocolApi';

// ---------------------------------------------------------------------------
// Severity chip colour mapping
// ---------------------------------------------------------------------------

type Severity = 'critical' | 'major' | 'minor';

const SEVERITY_COLOUR: Record<Severity, 'error' | 'warning' | 'info'> = {
  critical: 'error',
  major: 'warning',
  minor: 'info',
};

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface IssueItemProps {
  issue: ProtocolIssue;
}

/** Renders a single protocol issue with a severity chip. */
function IssueItem({ issue }: IssueItemProps) {
  const colour = SEVERITY_COLOUR[issue.severity as Severity] ?? 'info';
  return (
    <Box sx={{ mb: 2, pl: 2, borderLeft: `3px solid`, borderColor: `${colour}.main` }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
        <Chip
          label={issue.severity}
          color={colour}
          size="small"
          sx={{ textTransform: 'capitalize' }}
        />
        <Typography variant="caption" sx={{ color: '#6b7280', textTransform: 'capitalize' }}>
          {issue.section.replace(/_/g, ' ')}
        </Typography>
      </Box>
      <Typography variant="body2" sx={{ mb: 0.5 }}>
        {issue.description}
      </Typography>
      <Typography variant="body2" sx={{ color: '#374151', fontStyle: 'italic' }}>
        Suggestion: {issue.suggestion}
      </Typography>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Props and component
// ---------------------------------------------------------------------------

interface ProtocolReviewReportProps {
  /** Current protocol data. */
  protocol: ReviewProtocol | null;
}

/**
 * ProtocolReviewReport renders the AI review result for an SLR protocol.
 *
 * States:
 * - Loading: `status === "under_review"` — shows skeleton.
 * - No report: `review_report === null` — shows empty-state alert.
 * - Report present: renders issues list and overall assessment.
 *
 * @param protocol - The current protocol, or null if none created yet.
 */
const ProtocolReviewReport = React.memo(function ProtocolReviewReport({
  protocol,
}: ProtocolReviewReportProps) {
  if (protocol?.status === 'under_review') {
    return (
      <Box aria-label="Review loading">
        <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
          AI Review in Progress
        </Typography>
        <Skeleton variant="text" width="60%" sx={{ mb: 1 }} />
        <Skeleton variant="text" width="80%" sx={{ mb: 1 }} />
        <Skeleton variant="rectangular" height={80} />
      </Box>
    );
  }

  if (!protocol || !protocol.review_report) {
    return (
      <Alert severity="info" data-testid="review-empty-state">
        No review report yet. Submit the protocol for AI review to receive feedback.
      </Alert>
    );
  }

  const { issues, overall_assessment } = protocol.review_report;

  // Group issues by section
  const grouped = issues.reduce<Record<string, ProtocolIssue[]>>((acc, issue) => {
    const key = issue.section;
    if (!acc[key]) acc[key] = [];
    acc[key].push(issue);
    return acc;
  }, {});

  const hasIssues = issues.length > 0;

  return (
    <Box>
      <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
        AI Protocol Review
      </Typography>

      {hasIssues ? (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" sx={{ mb: 2, color: '#374151' }}>
            {issues.length} issue{issues.length !== 1 ? 's' : ''} found
          </Typography>
          {Object.entries(grouped).map(([section, sectionIssues]) => (
            <Box key={section} sx={{ mb: 2 }}>
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  mb: 1,
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  color: '#6b7280',
                  letterSpacing: '0.05em',
                }}
              >
                {section.replace(/_/g, ' ')}
              </Typography>
              {sectionIssues.map((issue, idx) => (
                <IssueItem key={idx} issue={issue} />
              ))}
            </Box>
          ))}
        </Box>
      ) : (
        <Alert severity="success" sx={{ mb: 2 }}>
          No issues found — the protocol meets all review criteria.
        </Alert>
      )}

      <Divider sx={{ mb: 2 }} />

      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
        Overall Assessment
      </Typography>
      <Typography variant="body2" sx={{ color: '#374151', whiteSpace: 'pre-wrap' }}>
        {overall_assessment}
      </Typography>
    </Box>
  );
});

export default ProtocolReviewReport;
