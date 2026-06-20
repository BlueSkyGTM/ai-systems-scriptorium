"""The task spec — what the student fills, parsed for the driver and the rubric.

The exam's input is a markdown task spec (``spec_template.md`` filled in, or
``sample_spec.md``). It names the chosen track, the reference architecture from the
20 Ch16 case studies, the feature the fleet ships, and the acceptance criteria the
student judges the result against. Stdlib only — a tiny field parser, not a YAML
or front-matter dependency.

The spec is the contract the fleet is pointed at. Keep it honest: an empty field
is a missing answer, and the rubric will mark it.

Spec format (the fields the parser reads from ``**Field:** value`` lines, and the
``## Acceptance criteria`` list):

    **Track:** agentic-system
    **Reference architecture:** #07 Autonomous Coding Agent
    **Version:** 1.0.0
    **Feature:** addition operator
    **Business problem:** one line framing why this system exists

    ## Acceptance criteria
    - the acceptance suite passes
    - the run stays under the team budget
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

# The three exam tracks, each anchored to Ch16 case studies (see the guide
# 02-reference-architectures.md). A spec must declare one of these.
TRACKS = ("eval-gated-ci-cd", "multi-tenant-rag", "agentic-system")


class SpecError(Exception):
    """A spec that cannot be parsed. The exam cannot start without a valid spec."""


@dataclass
class TaskSpec:
    """A parsed task spec — the exam's input.

    - ``track``                  one of TRACKS (the chosen exam track).
    - ``reference_architecture`` the Ch16 case study being replicated.
    - ``feature``                what the fleet ships (the ``ship_feature`` input).
    - ``business_problem``       one line: why this system exists (README framing).
    - ``version``                the spec's version (the artifact is versioned).
    - ``acceptance_criteria``    the bar the produced system is judged against.
    """

    track: str
    reference_architecture: str
    feature: str
    business_problem: str
    version: str
    acceptance_criteria: list = field(default_factory=list)
    raw_path: str = ""

    def has_framing(self) -> bool:
        """The README/problem-framing bar: a named track, a reference architecture,
        and a one-line business problem are all present."""
        return bool(self.track and self.reference_architecture and self.business_problem)

    def is_versioned(self) -> bool:
        return bool(self.version)

    def declares_tests(self) -> bool:
        """The artifact declares an acceptance suite / verification it must pass."""
        return len(self.acceptance_criteria) > 0


_FIELD_RE = re.compile(r"^\*\*(?P<key>[^:*]+):\*\*\s*(?P<val>.*)$")


def parse_spec(text: str, raw_path: str = "") -> TaskSpec:
    """Parse the spec markdown into a ``TaskSpec``. Raises ``SpecError`` if the
    required fields are absent — a half-filled template is not a runnable spec."""
    fields: dict = {}
    criteria: list = []
    in_criteria = False

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.lower().startswith("## acceptance criteria"):
            in_criteria = True
            continue
        if in_criteria:
            if stripped.startswith("#"):  # a new section ends the list
                in_criteria = False
            elif stripped.startswith("- ") or stripped.startswith("* "):
                item = stripped[2:].strip()
                # Skip an unfilled template placeholder line.
                if item and not item.startswith("<") and not item.startswith("("):
                    criteria.append(item)
                continue

        m = _FIELD_RE.match(stripped)
        if m:
            key = m.group("key").strip().lower().replace(" ", "_")
            fields[key] = m.group("val").strip()

    track = _normalize_track(fields.get("track", ""))
    spec = TaskSpec(
        track=track,
        reference_architecture=fields.get("reference_architecture", ""),
        feature=fields.get("feature", "") or "addition operator",
        business_problem=fields.get("business_problem", ""),
        version=fields.get("version", ""),
        acceptance_criteria=criteria,
        raw_path=raw_path,
    )
    if not track:
        raise SpecError(
            f"spec is missing a valid Track (one of {TRACKS}); "
            f"got {fields.get('track', '<none>')!r}"
        )
    return spec


def _normalize_track(value: str) -> str:
    """Coerce a human-written track name to a canonical TRACKS value, else ''."""
    v = value.strip().lower().replace("_", "-").replace(" ", "-")
    if v in TRACKS:
        return v
    # tolerate common phrasings
    if "eval" in v and "ci" in v:
        return "eval-gated-ci-cd"
    if "rag" in v:
        return "multi-tenant-rag"
    if "agent" in v:
        return "agentic-system"
    return ""


def load_spec(path: str) -> TaskSpec:
    if not os.path.isfile(path):
        raise SpecError(f"no spec at {path!r}")
    with open(path, encoding="utf-8") as f:
        return parse_spec(f.read(), raw_path=path)
