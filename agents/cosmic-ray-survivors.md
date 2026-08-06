# cosmic-ray Mutation Testing — Surviving Mutants

> **Note.** This report comes from the 2026-03-15 session, which ran before
> `scripts/run-mutation-safe.sh` existed and therefore mutated the real working
> tree. That session leaked 60+ mutants into `backend/src` (see
> `backend/cosmic-ray-survivors.md`). This package scans clean —
> `python3 scripts/check_mutation_artifacts.py` reports no artifacts — but the
> score below was produced by the same unsafe process. Re-run via the wrapper
> before relying on it.

> Package: `agents`
> Final score: **100%** (1191/1191 mutants killed)
> Run date: 2026-03-15

No surviving mutants. All 1191 mutations were killed by the existing test suite.
