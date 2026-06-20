"""Fleet adapter — resolve and import the SHIPPED Module 7 governed fleet.

The exam does not contain a fleet. It points the *real* M7 artifact-03 fleet at a
production problem, the same way Module 8 reuses it: a control plane reading a
registry to know what it governs. This module is the seam that finds that fleet on
disk and imports its real entry points (`load_fleet`, `ship_feature` via the
returned `Fleet`).

Resolution walks up from this file looking for the canonical M7 path:

    .../library/completed/sans-python/exercises/module7/03-governed-multi-agent-fleet/

When found, that directory is prepended to ``sys.path`` so its in-package imports
(`fleet`, `governance.*`, `agents.*`, `mock_llm`, `policy`, `schema`) resolve
exactly as they do on the M7 smoke path — no rebuild, no fork, no copy.

If the fleet is not found, ``resolve_fleet_dir`` raises ``FleetNotFound`` with the
paths it searched, so the failure is a clear message and not an opaque
``ImportError`` three frames deep.

Standard library only. Importing the fleet pulls in *its* code, which is itself
stdlib-only on the smoke path (PyYAML and jsonschema are optional, behind guards).
"""

from __future__ import annotations

import os
import sys

# The canonical location of the shipped M7 governed fleet, relative to the repo's
# migration root. The exam reuses THIS, never a copy.
M7_FLEET_RELPATH = os.path.join(
    "exercises", "module7", "03-governed-multi-agent-fleet"
)


class FleetNotFound(Exception):
    """The shipped M7 governed fleet could not be located on disk. The exam
    cannot run without the real fleet — this is not a thing to mock around."""


def resolve_fleet_dir(start: str | None = None) -> str:
    """Walk up from ``start`` (default: this file) to find the M7 fleet directory.

    Returns the absolute path to ``exercises/module7/03-governed-multi-agent-fleet``.
    Raises ``FleetNotFound`` (listing the candidates it tried) if no such directory
    exists above this file — a clear error, not a deep ImportError.
    """
    here = os.path.dirname(os.path.abspath(start or __file__))
    tried: list[str] = []
    node = here
    while True:
        candidate = os.path.join(node, M7_FLEET_RELPATH)
        tried.append(candidate)
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "fleet.py")):
            return candidate
        parent = os.path.dirname(node)
        if parent == node:  # reached the filesystem root
            break
        node = parent
    raise FleetNotFound(
        "could not locate the shipped M7 governed fleet "
        "(exercises/module7/03-governed-multi-agent-fleet/fleet.py).\n"
        "searched:\n  - " + "\n  - ".join(tried) + "\n"
        "the exam reuses the REAL fleet; check out the full course repo so this path exists."
    )


def load_real_fleet(kill_switch_path: str, registry_path: str | None = None,
                    on_event=None):
    """Import the REAL M7 fleet and build one. Returns its ``Fleet`` instance.

    This is the reuse seam: it calls the shipped ``fleet.load_fleet`` — the very
    M8 entry point the finale wrote — so the exam operates the same orchestrator,
    governance package, and agents that pass the M7 gate. No fleet code is defined
    here; it is imported.
    """
    fleet_dir = resolve_fleet_dir()
    if fleet_dir not in sys.path:
        sys.path.insert(0, fleet_dir)
    # Imported from the shipped artifact, not redefined. If these names ever move,
    # the exam should fail loudly rather than silently shadow them.
    from fleet import load_fleet  # type: ignore  # noqa: E402
    return load_fleet(
        kill_switch_path=kill_switch_path,
        registry_path=registry_path,
        on_event=on_event,
    )


def fleet_module():
    """Return the imported ``fleet`` module (after ensuring it is on the path).

    Lets callers reach the real ``Fleet`` / ``FleetRun`` types without re-deriving
    the resolution logic."""
    fleet_dir = resolve_fleet_dir()
    if fleet_dir not in sys.path:
        sys.path.insert(0, fleet_dir)
    import fleet  # type: ignore  # noqa: E402
    return fleet
