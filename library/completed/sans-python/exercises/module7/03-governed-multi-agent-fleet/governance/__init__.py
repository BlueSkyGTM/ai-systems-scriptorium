"""The fleet governance layer — the operator console, as code.

Five concerns, each a file you can diff (M4 lessons 12/13):

- ``fleet_budget``  — per-agent TaskBudgets under one team ceiling (economics).
- ``inbox``         — the shared HITL inbox; the merge needs human approval.
- ``audit``         — every action -> a correlation id + the four-clause record.
- ``killswitch``    — one switch the operator owns; no agent can write it.

The registry (../registry.yaml) names what is governed; this package governs it.
Two of these — fleet_budget and inbox — are the single-agent controls from M4
lessons 06 and 08 pointed at many agents, not rebuilt.
"""
