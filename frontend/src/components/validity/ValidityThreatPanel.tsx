/**
 * ValidityThreatPanel: discloses the study's identified threats to validity
 * and lets the researcher record Ampatzoglou's step-4 outcome for each.
 *
 * TFIX11. The corpus permits single-reviewer studies explicitly — one person
 * seeing every paper is "a known bias, accepted deliberately" — and asks only
 * that the trade-off be recorded "rather than pretending it does not exist".
 * So this panel never blocks anything. What it does is make the study say so,
 * and offer the two ways of saying it.
 *
 * The two outcomes are presented side by side, at equal weight, on purpose. A
 * UI that framed acknowledgement as the lesser option would push a lone
 * researcher towards claiming a mitigation they did not perform — which is
 * worse than the bias it pretends to fix.
 *
 * Rapid Reviews never surface here: they use Cartaxo's disclosure regime and
 * already have SingleReviewerWarningBanner.
 */

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { api } from '../../services/api';

/** One identified threat as returned by the API. */
export interface ValidityThreat {
  threat_id: string;
  /** The chapter's short name, sent by the server from the catalogue. */
  label: string;
  /** Which of ch.09's three categories the threat belongs to. */
  phase: string;
  /**
   * Petersen & Gencel heading, or `null` when unfiled. Most threats arrive
   * unfiled: ch.09 sources only three pairings and warns the rest must be
   * checked against the PDF before being quoted.
   */
  validity_category: string | null;
  category_source: string | null;
  description: string;
  source_detail: string | null;
  mitigation: string | null;
  acknowledgement: string | null;
  is_addressed: boolean;
  /**
   * Step 3. `null` means nobody has checked this threat yet — deliberately
   * distinct from `false`, which means it was checked and ruled out.
   */
  is_applicable: boolean | null;
  /** True when the platform computed applicability, so the user is not asked. */
  applicability_is_derived: boolean;
}

interface ValidityThreatListResponse {
  threats: ValidityThreat[];
}

/** Props for {@link ValidityThreatPanel}. */
export interface ValidityThreatPanelProps {
  /** The integer study ID. */
  studyId: number;
}

/**
 * Human-readable labels for the Ampatzoglou catalogue entries the platform
 * derives. Kept beside the ids rather than sent from the server so the panel
 * renders something meaningful even if a new id arrives before this is updated.
 */
const THREAT_LABELS: Record<string, string> = {
  tv7: 'TV7 — Study inclusion/exclusion',
  tv13_4: 'TV13.4 — Unverified data extraction',
  tv16: 'TV16 — Researcher bias',
};

/** Petersen & Gencel reporting categories, for display. */
const CATEGORY_LABELS: Record<string, string> = {
  descriptive: 'Descriptive validity',
  theoretical: 'Theoretical validity',
  generalizability_internal: 'Generalizability (internal)',
  generalizability_external: 'Generalizability (external)',
  interpretive: 'Interpretive validity',
  repeatability: 'Repeatability',
};

/**
 * Panel listing derived threats to validity with per-threat step-4 editors.
 *
 * @param props - {@link ValidityThreatPanelProps}
 */
export default function ValidityThreatPanel({ studyId }: ValidityThreatPanelProps) {
  const queryClient = useQueryClient();
  const [drafts, setDrafts] = useState<
    Record<string, { mitigation: string; acknowledgement: string }>
  >({});

  const { data, isLoading, isError } = useQuery({
    queryKey: ['validity-threats', studyId],
    queryFn: () =>
      api.get<ValidityThreatListResponse>(`/api/v1/studies/${studyId}/validity/threats`),
  });

  const saveMutation = useMutation({
    mutationFn: ({
      threatId,
      mitigation,
      acknowledgement,
    }: {
      threatId: string;
      mitigation: string;
      acknowledgement: string;
    }) =>
      api.patch<ValidityThreat>(`/api/v1/studies/${studyId}/validity/threats/${threatId}`, {
        mitigation,
        acknowledgement,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['validity-threats', studyId] });
    },
  });

  // TFIX15 / step 3. Answering applicability is a separate act from recording a
  // step-4 outcome, and the server marks the row human-decided so the next
  // derivation pass cannot silently overwrite the answer.
  const applicabilityMutation = useMutation({
    mutationFn: ({ threatId, isApplicable }: { threatId: string; isApplicable: boolean }) =>
      api.patch<ValidityThreat>(`/api/v1/studies/${studyId}/validity/threats/${threatId}`, {
        is_applicable: isApplicable,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['validity-threats', studyId] });
    },
  });

  if (isLoading) {
    return <Typography variant="body2">Loading threats to validity…</Typography>;
  }

  if (isError) {
    return <Alert severity="error">Could not load threats to validity.</Alert>;
  }

  const threats = data?.threats ?? [];

  // No derived threats is the ordinary case for a two-reviewer study. Saying
  // nothing at all would be indistinguishable from the panel having failed to
  // load, so state the finding rather than rendering an empty box.
  if (threats.length === 0) {
    return (
      <Paper sx={{ p: 2 }} data-testid="validity-threat-panel">
        <Typography variant="h6" gutterBottom>
          Threats to validity
        </Typography>
        <Typography variant="body2" color="text.secondary">
          No threats have been derived from this study&apos;s current configuration.
        </Typography>
      </Paper>
    );
  }

  // TFIX15 / Ampatzoglou step 3. The catalogue arrives whole, so the panel has
  // three populations rather than one: threats that apply and need a step-4
  // outcome, threats nobody has checked yet, and threats checked and ruled out.
  // Only the first can block a report — an unchecked threat is unknown, not
  // outstanding, and treating the two alike would lock every study behind 33
  // questions the moment the page loaded.
  const applicable = threats.filter((t) => t.is_applicable === true);
  const unchecked = threats.filter((t) => t.is_applicable === null);
  const unaddressed = applicable.filter((t) => !t.is_addressed).length;

  const draftFor = (threat: ValidityThreat) =>
    drafts[threat.threat_id] ?? {
      mitigation: threat.mitigation ?? '',
      acknowledgement: threat.acknowledgement ?? '',
    };

  const setDraft = (threatId: string, field: 'mitigation' | 'acknowledgement', value: string) => {
    setDrafts((prev) => {
      const threat = threats.find((t) => t.threat_id === threatId);
      const current = prev[threatId] ?? {
        mitigation: threat?.mitigation ?? '',
        acknowledgement: threat?.acknowledgement ?? '',
      };
      return { ...prev, [threatId]: { ...current, [field]: value } };
    });
  };

  return (
    <Paper sx={{ p: 2 }} data-testid="validity-threat-panel">
      <Typography variant="h6" gutterBottom>
        Threats to validity
      </Typography>

      {unaddressed > 0 ? (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {unaddressed} of {threats.length} threats have neither a mitigation nor an
          acknowledgement. Reports and exports stay locked until each one has one or the other —
          acknowledging that a threat is not mitigated is a complete answer.
        </Alert>
      ) : (
        <Alert severity="success" sx={{ mb: 2 }}>
          Every identified threat has been addressed.
        </Alert>
      )}

      {unchecked.length > 0 ? (
        <Box sx={{ mb: 2 }} data-testid="step-three-checklist">
          <Alert severity="info" sx={{ mb: 1 }}>
            {unchecked.length} of {threats.length} catalogue threats have not been checked yet.
            Ampatzoglou&apos;s step 3 asks whether each one pertains to this study; the platform has
            already answered the ones its configuration decides.
          </Alert>
          <Stack spacing={1}>
            {unchecked.map((threat) => (
              <Paper
                key={threat.threat_id}
                variant="outlined"
                sx={{ p: 1.5 }}
                data-testid={`unchecked-${threat.threat_id}`}
              >
                <Typography variant="subtitle2">{threat.label}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {threat.description}
                </Typography>
                <Stack direction="row" spacing={1}>
                  <Button
                    size="small"
                    variant="outlined"
                    disabled={applicabilityMutation.isPending}
                    onClick={() =>
                      applicabilityMutation.mutate({
                        threatId: threat.threat_id,
                        isApplicable: true,
                      })
                    }
                  >
                    Applies to this study
                  </Button>
                  <Button
                    size="small"
                    variant="text"
                    disabled={applicabilityMutation.isPending}
                    onClick={() =>
                      applicabilityMutation.mutate({
                        threatId: threat.threat_id,
                        isApplicable: false,
                      })
                    }
                  >
                    Does not apply
                  </Button>
                </Stack>
              </Paper>
            ))}
          </Stack>
        </Box>
      ) : null}

      {applicable.map((threat) => {
        const draft = draftFor(threat);
        return (
          <Accordion key={threat.threat_id} data-testid={`threat-${threat.threat_id}`}>
            <AccordionSummary>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ width: '100%' }}>
                <Typography sx={{ flexGrow: 1 }}>
                  {threat.label || THREAT_LABELS[threat.threat_id] || threat.threat_id}
                </Typography>
                <Chip
                  size="small"
                  variant={threat.validity_category ? 'filled' : 'outlined'}
                  label={
                    threat.validity_category
                      ? (CATEGORY_LABELS[threat.validity_category] ?? threat.validity_category)
                      : 'Category not filed'
                  }
                />
                <Chip
                  size="small"
                  color={threat.is_addressed ? 'success' : 'warning'}
                  label={threat.is_addressed ? 'Addressed' : 'Not addressed'}
                />
              </Stack>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" paragraph>
                {threat.description}
              </Typography>
              {threat.source_detail ? (
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                  Derived from: {threat.source_detail}
                </Typography>
              ) : null}

              <TextField
                label="Mitigation"
                helperText="An action taken to reduce this threat."
                fullWidth
                multiline
                minRows={2}
                sx={{ mb: 2 }}
                value={draft.mitigation}
                onChange={(e) => setDraft(threat.threat_id, 'mitigation', e.target.value)}
              />
              <TextField
                label="Acknowledgement"
                helperText="Or state that the threat is accepted and not fully mitigated. Either one is enough."
                fullWidth
                multiline
                minRows={2}
                sx={{ mb: 2 }}
                value={draft.acknowledgement}
                onChange={(e) => setDraft(threat.threat_id, 'acknowledgement', e.target.value)}
              />

              <Box>
                <Button
                  variant="contained"
                  disabled={saveMutation.isPending}
                  onClick={() =>
                    saveMutation.mutate({
                      threatId: threat.threat_id,
                      mitigation: draft.mitigation,
                      acknowledgement: draft.acknowledgement,
                    })
                  }
                >
                  Save
                </Button>
              </Box>
            </AccordionDetails>
          </Accordion>
        );
      })}
    </Paper>
  );
}
