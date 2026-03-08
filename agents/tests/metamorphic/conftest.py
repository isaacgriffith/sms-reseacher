"""Metamorphic test infrastructure for SMS Researcher agents.

Metamorphic testing (MT) validates software by defining *metamorphic
relations* (MRs) — properties that must hold between pairs of inputs
and their outputs — rather than specifying exact expected outputs.

This is particularly valuable for LLM-backed agents where the output
space is too large for exhaustive oracle testing.

## Alternative Framework

`GeMTest <https://github.com/tum-i4/gemtest>`_ provides a more
structured MT framework with automatic MR generation.  The tests in
this package use ``hypothesis`` for property-based input generation,
which integrates more naturally with pytest.  GeMTest is a viable
drop-in replacement if more advanced MR composition is needed.

## Metamorphic Relations Implemented

- **Screener**: Label-preserving transformation MR — synonym substitution
  in the abstract must not change the inclusion/exclusion decision.
- **Extractor**: Field-order permutation MR — the order in which fields
  are listed must not affect the extracted values.
- **Synthesiser**: Paper-order permutation MR — permuting the order of
  paper summaries must produce semantically equivalent synthesis.
"""

from hypothesis import settings as hypothesis_settings

# Configure hypothesis for deterministic, fast test runs
hypothesis_settings.register_profile("ci", max_examples=20, deadline=5000)
hypothesis_settings.register_profile("dev", max_examples=5, deadline=10000)
hypothesis_settings.load_profile("dev")
