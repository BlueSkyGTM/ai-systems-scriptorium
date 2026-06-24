"""Vendored library package for Module 8 pipeline.

This package contains vendored (copied, unmodified) implementations of the
Modules 3-7 building blocks. Per the vendoring contract (same pattern as
DC M7), these files are treated as read-only dependencies: the pipeline
imports from them but never edits them.

Modules
-------
- ``m3_curate`` : dataset curation (validate + dedupe + split → JSONL)
- ``m4_tune``   : LoRA adapter fine-tune (CPU, torch-only)
- ``m5_eval``   : exact-match + F1 evaluation gate
- ``m6_train``  : classifier / model training glue
- ``m7_regress``: behavioral regression suite

All modules are CPU-runnable in well under 60 seconds total. No HuggingFace
transformers dependency; only stdlib + torch (+ optional sklearn baselines).
"""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from typing import Dict

__version__ = "8.0.0"

# Vendored submodule registry. Order matches the pipeline flow:
#   curate → tune → eval → (classify) → regress
_VENDORED: Dict[str, str] = {
    "m3_curate":  "lib.m3_curate",
    "m4_tune":    "lib.m4_tune",
    "m5_eval":    "lib.m5_eval",
    "m6_train":   "lib.m6_train",
    "m7_regress": "lib.m7_regress",
}


def _load(name: str, dotted: str) -> ModuleType:
    """Lazily import a vendored submodule and bind it on this package."""
    if dotted not in sys.modules:
        sys.modules[dotted] = importlib.import_module(dotted)
    mod = sys.modules[dotted]
    setattr(sys.modules[__name__], name, mod)
    return mod


# Eagerly load so that ``from lib import m3_curate`` works on first import.
# We deliberately swallow ImportError here only for the purpose of making
# the package importable in environments where a single vendored module
# has not yet been populated (e.g., during scaffold). Downstream code that
# actually needs a missing module will hit a clear AttributeError at use.
for _short, _dotted in _VENDORED.items():
    try:
        _load(_short, _dotted)
    except ImportError:
        pass

__all__ = sorted(_VENDORED.keys()) + ["__version__"]