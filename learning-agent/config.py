"""Two-version switches. GATE_MODE selects the gate policy; a key selects the writer.

  GATE_MODE=substring (default) -> Version A: existing behavior, no key needed.
  GATE_MODE=both      + a key   -> Version B: Citations writer + coverage gate.
  GATE_MODE=citations           -> coverage gate ON but writer falls back to SDK
                                    unless a key is also present (gate-only strict mode).
"""
from __future__ import annotations
import os

_VALID = {"substring", "citations", "both"}


def gate_mode() -> str:
    m = os.getenv("GATE_MODE", "substring").strip().lower()
    return m if m in _VALID else "substring"


def citations_enabled() -> bool:
    """True iff the WRITER should call the Citations API (needs an API key)."""
    return gate_mode() in {"citations", "both"} and bool(os.getenv("ANTHROPIC_API_KEY"))
