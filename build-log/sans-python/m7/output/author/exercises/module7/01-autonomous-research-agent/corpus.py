"""The fixture corpus — a fixed, no-egress evidence set the sandboxes search.

A handful of documents, each with an id a finding can cite as [S1], a title, the
evidence text, and the keywords the deterministic search matches on. This is the
local stand-in for a vetted retrieval index; it ships with the artifact so the
smoke run and tests are offline and reproducible.
"""

from __future__ import annotations

CORPUS = [
    {
        "id": "S1",
        "title": "MAST: Multi-Agent System Failure Taxonomy (Cemri et al., 2025)",
        "text": (
            "An analysis of 1,600+ traces found multi-agent failures sort into three "
            "families: specification (~42%), coordination (~37%), and verification gaps "
            "(~21%). These are design flaws, not base-model limitations."
        ),
        "keywords": ["multi-agent", "failure", "specification", "coordination",
                     "verification", "mast"],
    },
    {
        "id": "S2",
        "title": "CRITIC: verification through external tools (Gou et al., 2023)",
        "text": (
            "Routing a generator's output through an external check it cannot "
            "hallucinate around — a test runner, a retriever, a calculator — closes the "
            "verification gap. A finding grounded in retrieved evidence is trustworthy in "
            "a way a model's self-report is not."
        ),
        "keywords": ["verification", "gate", "external", "check", "critic",
                     "grounding", "reliability"],
    },
    {
        "id": "S3",
        "title": "Fleet governance: budgets and kill switches (Module 4)",
        "text": (
            "A fleet's cost and risk are bounded by operator surfaces: a shared budget "
            "that stops the team on breach, and a kill switch every agent reads but none "
            "can write. These are deterministic controls, not model judgment."
        ),
        "keywords": ["budget", "kill-switch", "operator", "control", "fleet",
                     "cost", "governance"],
    },
]
