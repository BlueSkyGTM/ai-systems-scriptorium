"""Research sandbox — the isolated, no-egress evidence surface a sub-agent reads.

The M6 sandbox ran untrusted test code in a child process under a timeout. A
research sub-agent's "execution" is retrieval: it searches a corpus for evidence.
The capstone's autonomous research agent runs each experiment "in a sandboxed
environment with no network egress and strict resource limits" — the same
principle, applied to reading instead of running. A sub-agent here cannot reach
the open internet; it can only query the fixed corpus it was handed.

Framed honestly: this is a dev-time guardrail, not an OS security boundary. It
bounds *what a sub-agent can see* (a fixed corpus, no live network) and returns
evidence as structured records the verify gate can check citations against. In
production the corpus is a vetted index behind a read-only tool; the in-memory
fixture is the local stand-in. The seam is the same either way: the sub-agent
calls ``search()`` and reads ``Evidence`` records.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    """One retrieved source the sub-agent may cite. ``id`` is what a finding
    references as [S1]; the gate checks that the id was actually retrieved."""

    id: str
    title: str
    text: str


class ResearchSandbox:
    """A no-egress corpus a sub-agent searches. Read-only; no network.

    Construction takes a fixed list of documents. ``search`` does a deterministic
    keyword scan (stdlib only) and returns the matching evidence in a stable
    order, so the same sub-question always yields the same evidence — the
    determinism the offline gate needs.
    """

    def __init__(self, documents):
        # documents: list of dicts {id, title, text, keywords}
        self._docs = list(documents)

    def search(self, query: str, limit: int = 3) -> list:
        """Return up to ``limit`` Evidence records whose keywords match the query.

        A no-egress, deterministic retrieval: scores each doc by how many of its
        keywords appear in the lowercased query, ties broken by document order.
        """
        q = query.lower()
        scored = []
        for i, doc in enumerate(self._docs):
            hits = sum(1 for kw in doc.get("keywords", []) if kw.lower() in q)
            if hits:
                scored.append((-hits, i, doc))
        scored.sort()
        return [
            Evidence(id=doc["id"], title=doc["title"], text=doc["text"])
            for _neg, _i, doc in scored[:limit]
        ]
