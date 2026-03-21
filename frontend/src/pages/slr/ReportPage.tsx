/**
 * ReportPage — SLR report export page (feature 007, Phase 8).
 *
 * Allows the user to select a report format and download the generated SLR
 * report. The download button is disabled with a tooltip until synthesis is
 * complete.
 */

import { useState } from 'react';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormLabel from '@mui/material/FormLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { downloadSLRReport } from '../../services/slr/reportApi';

interface ReportPageProps {
  /** The integer study ID. */
  studyId: number;
  /** Whether the synthesis phase has been completed. */
  synthesisComplete: boolean;
}

const FORMAT_OPTIONS = [
  { value: 'markdown', label: 'Markdown' },
  { value: 'latex', label: 'LaTeX' },
  { value: 'json', label: 'JSON' },
  { value: 'csv', label: 'CSV' },
];

/**
 * Page component for exporting the SLR report in a chosen format.
 *
 * @param props - {@link ReportPageProps}
 */
export default function ReportPage({ studyId, synthesisComplete }: ReportPageProps) {
  const [format, setFormat] = useState('markdown');
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownload = async () => {
    setDownloadError(null);
    setIsDownloading(true);
    try {
      await downloadSLRReport(studyId, format);
    } catch (err) {
      setDownloadError(err instanceof Error ? err.message : 'Download failed');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <Box data-testid="report-page">
      <Typography variant="h6" sx={{ mb: 2 }}>
        Export SLR Report
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Generate and download the full systematic literature review report. Complete the
        synthesis phase first to enable this feature.
      </Typography>

      <FormControl component="fieldset" sx={{ mb: 3 }}>
        <FormLabel component="legend">Export Format</FormLabel>
        <RadioGroup
          row
          value={format}
          onChange={(e) => setFormat(e.target.value)}
          aria-label="Export format"
        >
          {FORMAT_OPTIONS.map((opt) => (
            <FormControlLabel
              key={opt.value}
              value={opt.value}
              control={<Radio />}
              label={opt.label}
            />
          ))}
        </RadioGroup>
      </FormControl>

      {downloadError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setDownloadError(null)}>
          {downloadError}
        </Alert>
      )}

      <Tooltip
        title={synthesisComplete ? '' : 'Complete synthesis first'}
        placement="right"
      >
        <span>
          <Button
            variant="contained"
            disabled={!synthesisComplete || isDownloading}
            onClick={handleDownload}
            data-testid="download-report-btn"
          >
            {isDownloading ? 'Downloading…' : 'Download Report'}
          </Button>
        </span>
      </Tooltip>
    </Box>
  );
}
