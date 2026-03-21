/**
 * API client for SLR report export (feature 007, Phase 8).
 *
 * Downloads the SLR report as a file using fetch + URL.createObjectURL
 * so the browser triggers a native file-save dialog.
 */

/**
 * Download an SLR report for a study in the specified format.
 * Triggers a browser file download via URL.createObjectURL.
 *
 * @param studyId - The integer study ID.
 * @param format - One of "markdown", "latex", "json", or "csv".
 * @returns Promise that resolves when the download has been triggered.
 * @throws Error if the HTTP request fails.
 */
export async function downloadSLRReport(studyId: number, format: string): Promise<void> {
  const token = localStorage.getItem('access_token') || '';
  const resp = await fetch(
    `/api/v1/slr/studies/${studyId}/export/slr-report?format=${format}`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  );
  if (!resp.ok) throw new Error(`Download failed: ${resp.status}`);
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `slr-report-${studyId}.${format === 'latex' ? 'tex' : format}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
