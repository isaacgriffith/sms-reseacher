/**
 * TertiaryReportPage — displays the generated Tertiary Study report and
 * provides download buttons for JSON, CSV, and Markdown export formats.
 *
 * Uses TanStack Query to fetch the report from
 * GET /api/v1/tertiary/studies/{id}/report?format=json.
 * Download buttons open the same endpoint with the appropriate format param.
 *
 * @module TertiaryReportPage
 */

import { useQuery } from '@tanstack/react-query';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import { z } from 'zod';
import { api } from '../services/api';
import LandscapeSummarySection from '../components/tertiary/LandscapeSummarySection';
import type { LandscapeSection } from '../components/tertiary/LandscapeSummarySection';

// ---------------------------------------------------------------------------
// Zod schema for the report JSON response
// ---------------------------------------------------------------------------

const LandscapeSectionSchema = z.object({
  timeline_summary: z.string(),
  research_question_evolution: z.string(),
  synthesis_method_shifts: z.string(),
});

const TertiaryReportSchema = z.object({
  study_id: z.number(),
  study_name: z.string(),
  generated_at: z.string(),
  background: z.string(),
  review_questions: z.array(z.string()),
  protocol_summary: z.string(),
  inclusion_exclusion_decisions: z.string(),
  quality_assessment_results: z.string(),
  extracted_data: z.string(),
  synthesis_results: z.string(),
  landscape_of_secondary_studies: LandscapeSectionSchema,
  recommendations: z.string(),
});

type TertiaryReport = z.infer<typeof TertiaryReportSchema>;

// ---------------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------------

async function fetchReport(studyId: number): Promise<TertiaryReport> {
  const raw = await api.get<unknown>(`/api/v1/tertiary/studies/${studyId}/report?format=json`);
  return TertiaryReportSchema.parse(raw);
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/** Props for {@link TertiaryReportPage}. */
export interface TertiaryReportPageProps {
  /** Integer study ID. */
  studyId: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * TertiaryReportPage fetches and renders the full Tertiary Study report.
 *
 * @param studyId - The study to display the report for.
 */
export default function TertiaryReportPage({ studyId }: TertiaryReportPageProps) {
  const { data: report, isLoading, error } = useQuery({
    queryKey: ['tertiary-report', studyId],
    queryFn: () => fetchReport(studyId),
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load report: {(error as Error).message}
      </Alert>
    );
  }

  if (!report) return null;

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto', mt: 2, px: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            {report.study_name}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Generated: {report.generated_at}
          </Typography>
        </Box>
        <DownloadButtons studyId={studyId} />
      </Box>

      <ReportSection title="Background" content={report.background} />
      <ReviewQuestionsSection questions={report.review_questions} />
      <ReportSection title="Protocol Summary" content={report.protocol_summary} />
      <ReportSection
        title="Inclusion / Exclusion Decisions"
        content={report.inclusion_exclusion_decisions}
      />
      <ReportSection
        title="Quality Assessment Results"
        content={report.quality_assessment_results}
      />
      <ReportSection title="Extracted Data" content={report.extracted_data} />
      <ReportSection title="Synthesis Results" content={report.synthesis_results} />

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
        Landscape of Secondary Studies
      </Typography>
      <LandscapeSummarySection
        landscape={report.landscape_of_secondary_studies as LandscapeSection}
      />

      <Divider sx={{ my: 3 }} />
      <ReportSection title="Recommendations" content={report.recommendations} />
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface ReportSectionProps {
  title: string;
  content: string;
}

/**
 * A single titled report section.
 *
 * @param title - Section heading.
 * @param content - Section body text.
 */
function ReportSection({ title, content }: ReportSectionProps) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
        {content}
      </Typography>
    </Box>
  );
}

interface ReviewQuestionsSectionProps {
  questions: string[];
}

/**
 * Renders the list of research questions as a numbered list.
 *
 * @param questions - Research questions from the protocol.
 */
function ReviewQuestionsSection({ questions }: ReviewQuestionsSectionProps) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
        Research Questions
      </Typography>
      {questions.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          (none recorded)
        </Typography>
      ) : (
        <Box component="ol" sx={{ pl: 2.5, m: 0 }}>
          {questions.map((q, i) => (
            <Typography component="li" key={i} variant="body2" color="text.secondary">
              {q}
            </Typography>
          ))}
        </Box>
      )}
    </Box>
  );
}

interface DownloadButtonsProps {
  studyId: number;
}

/**
 * Download buttons for JSON, CSV, and Markdown export formats.
 *
 * Each button opens the report endpoint with the appropriate format param.
 *
 * @param studyId - The study ID for building download URLs.
 */
function DownloadButtons({ studyId }: DownloadButtonsProps) {
  const base = `/api/v1/tertiary/studies/${studyId}/report`;

  function handleDownload(format: 'json' | 'csv' | 'markdown') {
    window.open(`${base}?format=${format}`, '_blank', 'noopener,noreferrer');
  }

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Button size="small" variant="outlined" onClick={() => handleDownload('json')}>
        JSON
      </Button>
      <Button size="small" variant="outlined" onClick={() => handleDownload('csv')}>
        CSV
      </Button>
      <Button size="small" variant="outlined" onClick={() => handleDownload('markdown')}>
        Markdown
      </Button>
    </Box>
  );
}
