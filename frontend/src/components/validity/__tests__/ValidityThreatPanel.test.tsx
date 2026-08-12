/**
 * Unit tests for ValidityThreatPanel (TFIX11).
 *
 * The behaviour under test is a disclosure, not a gate. The corpus permits a
 * lone researcher and asks only that the bias be recorded, so the tests below
 * check that acknowledgement is treated as a complete answer everywhere — in
 * the summary count, in the per-threat chip, and in what gets sent to the API.
 */

import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ValidityThreatPanel from '../ValidityThreatPanel';

vi.mock('../../../services/api', () => ({
  api: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}));

import { api } from '../../../services/api';

const mockApi = api as unknown as {
  get: ReturnType<typeof vi.fn>;
  patch: ReturnType<typeof vi.fn>;
};

// TFIX15. `validity_category` is null on both, because ch.09 220-223 states
// only three Ampatzoglou→Petersen pairings and neither TV7 nor TV16 is among
// them. `is_applicable: true` marks these as the derived-applicable rows —
// the panel now also receives unchecked and ruled-out entries.
const TV7 = {
  threat_id: 'tv7',
  label: 'TV7 — Study inclusion/exclusion',
  phase: 'study_selection',
  validity_category: null,
  category_source: null,
  description: 'Inclusion and exclusion decisions were made by a single human reviewer.',
  source_detail: '1 human reviewer',
  mitigation: null,
  acknowledgement: null,
  is_addressed: false,
  is_applicable: true,
  applicability_is_derived: true,
};

const TV16_ADDRESSED = {
  threat_id: 'tv16',
  label: 'TV16 — Researcher bias',
  phase: 'data',
  validity_category: null,
  category_source: null,
  description: 'A single researcher interpreted and synthesised the results.',
  source_detail: '1 human reviewer',
  mitigation: null,
  acknowledgement: 'Sole author; accepted deliberately.',
  is_addressed: true,
  is_applicable: true,
  applicability_is_derived: true,
};

/** A catalogue entry nobody has checked yet — the step-3 population. */
const TV3_UNCHECKED = {
  threat_id: 'tv3',
  label: 'TV3 — Missing non-English papers',
  phase: 'study_selection',
  validity_category: null,
  category_source: null,
  description: 'Only a real threat where an active community publishes in another language.',
  source_detail: null,
  mitigation: null,
  acknowledgement: null,
  is_addressed: false,
  is_applicable: null,
  applicability_is_derived: false,
};

function renderPanel(studyId = 7) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <ValidityThreatPanel studyId={studyId} />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe('ValidityThreatPanel', () => {
  it('lists each derived threat with its catalogue label', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7, TV16_ADDRESSED] });

    renderPanel();

    expect(await screen.findByText(/TV7 — Study inclusion\/exclusion/)).toBeInTheDocument();
    expect(screen.getByText(/TV16 — Researcher bias/)).toBeInTheDocument();
  });

  it('says so when a threat has no reporting category yet', async () => {
    // TFIX15. This asserted "Theoretical validity" for TV7. ch.09 220-223
    // states three Ampatzoglou→Petersen pairings and TV7 is not one of them —
    // 206-210 warns the rest of the cross-mapping "must be verified against
    // the PDF before being quoted". The chip now says the category is unfiled
    // rather than showing a heading the corpus does not support.
    mockApi.get.mockResolvedValue({ threats: [TV7] });

    renderPanel();

    expect(await screen.findByText('Category not filed')).toBeInTheDocument();
  });

  it('counts only unaddressed threats in the warning', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7, TV16_ADDRESSED] });

    renderPanel();

    expect(await screen.findByText(/1 of 2 threats/)).toBeInTheDocument();
  });

  it('tells the user that acknowledging is a complete answer', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7] });

    renderPanel();

    expect(
      await screen.findByText(/acknowledging that a threat is not mitigated is a complete answer/i),
    ).toBeInTheDocument();
  });

  it('reports success once every threat is addressed', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV16_ADDRESSED] });

    renderPanel();

    expect(
      await screen.findByText(/Every identified threat has been addressed/),
    ).toBeInTheDocument();
  });

  it('states plainly when no threats were derived', async () => {
    mockApi.get.mockResolvedValue({ threats: [] });

    renderPanel();

    expect(
      await screen.findByText(
        /No threats have been derived from this study's current configuration/,
      ),
    ).toBeInTheDocument();
  });

  it('sends an acknowledgement to the API', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7] });
    mockApi.patch.mockResolvedValue({ ...TV7, acknowledgement: 'Accepted', is_addressed: true });
    const user = userEvent.setup();

    renderPanel(7);
    await user.click(await screen.findByText(/TV7 — Study inclusion\/exclusion/));
    await user.type(screen.getByLabelText(/Acknowledgement/), 'Accepted');
    await user.click(screen.getByRole('button', { name: 'Save' }));

    await waitFor(() => {
      expect(mockApi.patch).toHaveBeenCalledWith('/api/v1/studies/7/validity/threats/tv7', {
        mitigation: '',
        acknowledgement: 'Accepted',
      });
    });
  });

  it('sends a mitigation to the API', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7] });
    mockApi.patch.mockResolvedValue({ ...TV7, mitigation: 'Cross-checked', is_addressed: true });
    const user = userEvent.setup();

    renderPanel(7);
    await user.click(await screen.findByText(/TV7 — Study inclusion\/exclusion/));
    await user.type(screen.getByLabelText(/Mitigation/), 'Cross-checked');
    await user.click(screen.getByRole('button', { name: 'Save' }));

    await waitFor(() => {
      expect(mockApi.patch).toHaveBeenCalledWith('/api/v1/studies/7/validity/threats/tv7', {
        mitigation: 'Cross-checked',
        acknowledgement: '',
      });
    });
  });

  it('pre-fills the editors with what was already recorded', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV16_ADDRESSED] });
    const user = userEvent.setup();

    renderPanel();
    await user.click(await screen.findByText(/TV16 — Researcher bias/));

    expect(screen.getByLabelText(/Acknowledgement/)).toHaveValue(
      'Sole author; accepted deliberately.',
    );
  });

  it('surfaces a load failure rather than rendering an empty panel', async () => {
    mockApi.get.mockRejectedValue(new Error('boom'));

    renderPanel();

    expect(await screen.findByText(/Could not load threats to validity/)).toBeInTheDocument();
  });
});

/**
 * TFIX15 — Ampatzoglou step 3, "check every threat for whether it pertains to
 * the study" (ch.09 169).
 *
 * The catalogue now arrives whole, so the panel has to distinguish three
 * populations. The distinction that matters most is unchecked (`null`) versus
 * ruled out (`false`): collapsing them would either lock every study behind 33
 * unanswered questions or quietly report unexamined threats as dismissed.
 */
describe('ValidityThreatPanel — step 3 applicability', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('lists threats nobody has checked yet', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7, TV3_UNCHECKED] });

    renderPanel();

    expect(await screen.findByTestId('unchecked-tv3')).toBeInTheDocument();
    expect(screen.getByText(/TV3 — Missing non-English papers/)).toBeInTheDocument();
  });

  it('says how many of the catalogue remain unchecked', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7, TV3_UNCHECKED] });

    renderPanel();

    expect(
      await screen.findByText(/1 of 2 catalogue threats have not been checked/),
    ).toBeInTheDocument();
  });

  it('offers both answers, so ruling a threat out is as easy as accepting it', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV3_UNCHECKED] });

    renderPanel();

    expect(
      await screen.findByRole('button', { name: /Applies to this study/ }),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Does not apply/ })).toBeInTheDocument();
  });

  it('records the answer against the threat', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV3_UNCHECKED] });
    mockApi.patch.mockResolvedValue({ ...TV3_UNCHECKED, is_applicable: false });
    const user = userEvent.setup();

    renderPanel();
    await user.click(await screen.findByRole('button', { name: /Does not apply/ }));

    expect(mockApi.patch).toHaveBeenCalledWith('/api/v1/studies/7/validity/threats/tv3', {
      is_applicable: false,
    });
  });

  it('does not count unchecked threats as outstanding step-4 work', async () => {
    // An unchecked threat is unknown, not unaddressed. Counting it would tell
    // the researcher the report is blocked by something nobody has decided
    // applies — and the gate does not in fact block on it.
    mockApi.get.mockResolvedValue({ threats: [TV16_ADDRESSED, TV3_UNCHECKED] });

    renderPanel();

    expect(
      await screen.findByText(/Every identified threat has been addressed/),
    ).toBeInTheDocument();
  });

  it('shows no step-3 checklist once everything has been checked', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7, TV16_ADDRESSED] });

    renderPanel();

    await screen.findByText(/TV7 — Study inclusion/);
    expect(screen.queryByTestId('step-three-checklist')).not.toBeInTheDocument();
  });
});
