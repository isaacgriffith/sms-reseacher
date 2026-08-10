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

const TV7 = {
  threat_id: 'tv7',
  validity_category: 'theoretical',
  description: 'Inclusion and exclusion decisions were made by a single human reviewer.',
  source_detail: '1 human reviewer',
  mitigation: null,
  acknowledgement: null,
  is_addressed: false,
};

const TV16_ADDRESSED = {
  threat_id: 'tv16',
  validity_category: 'interpretive',
  description: 'A single researcher interpreted and synthesised the results.',
  source_detail: '1 human reviewer',
  mitigation: null,
  acknowledgement: 'Sole author; accepted deliberately.',
  is_addressed: true,
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

  it('shows the reporting category each threat is filed under', async () => {
    mockApi.get.mockResolvedValue({ threats: [TV7] });

    renderPanel();

    expect(await screen.findByText('Theoretical validity')).toBeInTheDocument();
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
