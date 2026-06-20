"""Pytest config: put the artifact root on sys.path.

This lets the tests and the `stages/` package import `pipeline`, `latency`,
and `barge_in` as top-level modules whether pytest is invoked from the artifact
root or elsewhere. Stdlib only.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
