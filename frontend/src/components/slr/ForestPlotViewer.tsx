/**
 * ForestPlotViewer — renders an SVG forest plot or loading/empty state.
 *
 * @module ForestPlotViewer
 */

import React, { memo } from 'react';
import Box from '@mui/material/Box';
import Skeleton from '@mui/material/Skeleton';
import Typography from '@mui/material/Typography';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface ForestPlotViewerProps {
  /** SVG string from the synthesis result, or null when unavailable. */
  forestPlotSvg: string | null;
  /** When true renders a loading skeleton instead of the plot. */
  isLoading?: boolean;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Renders a forest plot SVG inline, or a skeleton / empty-state message.
 *
 * Uses `dangerouslySetInnerHTML` to embed the SVG produced server-side so
 * that all SVG attributes (viewBox, fonts) are preserved exactly.
 *
 * @param props - {@link ForestPlotViewerProps}
 */
function ForestPlotViewer({ forestPlotSvg, isLoading = false }: ForestPlotViewerProps) {
  if (isLoading) {
    return (
      <Skeleton
        variant="rectangular"
        height={300}
        aria-label="Loading forest plot"
        data-testid="forest-plot-skeleton"
      />
    );
  }

  if (!forestPlotSvg) {
    return (
      <Typography
        variant="body2"
        color="text.secondary"
        data-testid="forest-plot-empty"
      >
        No forest plot available. Run a descriptive synthesis to generate one.
      </Typography>
    );
  }

  return (
    <Box
      data-testid="forest-plot-svg"
      dangerouslySetInnerHTML={{ __html: forestPlotSvg }}
      sx={{ overflowX: 'auto' }}
    />
  );
}

export default memo(ForestPlotViewer);
