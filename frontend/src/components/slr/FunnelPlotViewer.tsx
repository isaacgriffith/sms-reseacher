/**
 * FunnelPlotViewer — renders an SVG funnel plot or loading/empty state.
 *
 * @module FunnelPlotViewer
 */

import React, { memo } from 'react';
import Box from '@mui/material/Box';
import Skeleton from '@mui/material/Skeleton';
import Typography from '@mui/material/Typography';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface FunnelPlotViewerProps {
  /** SVG string from the synthesis result, or null when unavailable. */
  funnelPlotSvg: string | null;
  /** When true renders a loading skeleton instead of the plot. */
  isLoading?: boolean;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Renders a funnel plot SVG inline, or a skeleton / empty-state message.
 *
 * Uses `dangerouslySetInnerHTML` to embed the SVG produced server-side so
 * that all SVG attributes (viewBox, fonts) are preserved exactly.
 *
 * @param props - {@link FunnelPlotViewerProps}
 */
function FunnelPlotViewer({ funnelPlotSvg, isLoading = false }: FunnelPlotViewerProps) {
  if (isLoading) {
    return (
      <Skeleton
        variant="rectangular"
        height={300}
        aria-label="Loading funnel plot"
        data-testid="funnel-plot-skeleton"
      />
    );
  }

  if (!funnelPlotSvg) {
    return (
      <Typography
        variant="body2"
        color="text.secondary"
        data-testid="funnel-plot-empty"
      >
        No funnel plot available. Run a meta-analysis synthesis to generate one.
      </Typography>
    );
  }

  return (
    <Box
      data-testid="funnel-plot-svg"
      dangerouslySetInnerHTML={{ __html: funnelPlotSvg }}
      sx={{ overflowX: 'auto' }}
    />
  );
}

export default memo(FunnelPlotViewer);
