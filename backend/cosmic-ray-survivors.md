# cosmic-ray Mutation Testing — Surviving Mutants

> **⚠ This report is unreliable. Do not cite the score below.**
>
> The run that produced it executed against the real working tree — the
> isolation wrapper did not exist yet — and left 60+ mutants behind in
> `backend/src`, which were then committed in `ecc32de`. The score counts
> mutants cosmic-ray applied and reverted; it says nothing about the ones it
> failed to revert, and those were, by construction, undetectable by the suite.
>
> The artifacts were removed on 2026-08-06 (see the root `CHANGELOG.md`) and
> three guards now prevent recurrence (see `CLAUDE.md` → Mutation Testing).
> **Re-run `./scripts/run-mutation-safe.sh backend` for a trustworthy score.**

> Package: `backend`
> Final score: **100%** (3130/3130 mutants killed) — see the warning above
> Note: `backend/src/backend/services/visualization.py` excluded (contains lambda expressions incompatible with cosmic-ray 8.4.4's `get_definition_name`)
> Run date: 2026-03-15

No surviving mutants. All 3130 mutations in non-excluded files were killed by the existing test suite.
