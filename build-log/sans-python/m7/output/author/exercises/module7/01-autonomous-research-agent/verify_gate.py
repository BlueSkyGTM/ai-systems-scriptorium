"""Verification gate — a sub-agent does not get its finding into the answer for free.

The M6 gate ran the tests and refused to call a coding task done on the model's
say-so. The same instinct, one level up: a research sub-agent that "answers" its
sub-question is optimistic, not done. Before its finding reaches the synthesis
step, this deterministic gate checks the finding against the sandbox's evidence —
no model, no judgment. The default is REJECT.

This is the M3 CRITIC pattern (Module 3, learning-from-failure): route
verification through an external check the generator cannot hallucinate around.
Here the external check is the evidence the sub-agent actually retrieved in its
sandbox. A finding is ACCEPTed only when every claim it makes cites a source
that exists in that evidence. A claim with no citation, or a citation to a
source the sub-agent never retrieved, is a rejection — the MAST "verification
gap" closed with code.

The supervisor reads this verdict; the trace reads this verdict; the tests read
this verdict. One source of truth for whether a finding may be synthesized.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# A citation marker in a finding looks like [S1] / [S2] — a source id the
# sub-agent must back with evidence it retrieved.
_CITATION = re.compile(r"\[([A-Za-z]+\d+)\]")


@dataclass
class Verdict:
    accepted: bool
    detail: str
    cited: list = field(default_factory=list)     # source ids the finding cites
    grounded: list = field(default_factory=list)  # of those, which exist in evidence

    @property
    def label(self) -> str:
        return "ACCEPT" if self.accepted else "REJECT"


def verify(finding: str, evidence_ids) -> Verdict:
    """ACCEPT a finding only when every citation it makes is grounded in evidence.

    ``finding``      — the sub-agent's answer text, expected to cite sources as [S1].
    ``evidence_ids`` — the set of source ids the sub-agent retrieved in its sandbox.

    Default REJECT covers three failures the synthesis must never inherit:
      - a finding with no citation at all (an unsupported assertion),
      - a finding that cites a source id absent from the retrieved evidence (a
        fabricated citation — the cascading-error seed),
      - an empty finding.
    """
    text = (finding or "").strip()
    if not text:
        return Verdict(False, "empty finding")

    cited = _CITATION.findall(text)
    if not cited:
        return Verdict(False, "finding cites no source", cited=[])

    have = set(evidence_ids)
    grounded = [c for c in cited if c in have]
    ungrounded = [c for c in cited if c not in have]

    if ungrounded:
        return Verdict(
            False,
            f"finding cites sources not in evidence: {', '.join(sorted(set(ungrounded)))}",
            cited=cited,
            grounded=grounded,
        )

    return Verdict(
        True,
        f"all {len(set(cited))} citation(s) grounded in retrieved evidence",
        cited=cited,
        grounded=grounded,
    )
