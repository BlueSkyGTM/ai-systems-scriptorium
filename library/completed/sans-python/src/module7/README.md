# Module 7: Multi-Agent Artifacts

Single agents from Module 6 composed into **governed teams**; the structural last boss of the teaching arc,
where Module 4 becomes proof. The principle here is **elevate, don't author**: you reuse the M6 artifacts as
*nodes* and the M4 fleet/loop layer as *governance*, rather than rebuilding either. Each artifact passes the
same offline BUILD→TEST gate as M6; but now the smoke run proves a *team* coordinates, not a single agent.

| # | Artifact | Competency it proves | Composes |
|---|----------|----------------------|----------|
| 01 | **Autonomous research agent** | plan→execute→verify tree search with sub-agents + sandbox | M6 worker (01) + M4 supervisor-worker/ReWOO + M3 verification gate |
| 02 | **DevOps K8s troubleshooting agent** | supervisor + read-only specialists, HITL gate before any change | M6 read-only discipline + M4 supervisor + M4 HITL + audit |
| 03 | **Governed multi-agent fleet** (FINALE) | a SWE team (architect / coders / reviewer / tester via A2A) wrapped in the fleet layer — registry, budgets, HITL inbox, audit, kill-switches | M6 coding agent (01) as coder nodes + M4 fleet (12/13) + M4 A2A (02) |

**Finale principle; elevate, don't author:** the fleet artifact reuses an existing multi-agent project and
layers fleet governance onto it (DRY), not a from-scratch fleet build. A fleet of agents run as governed
infrastructure = AI Platform Engineering; the thesis, full circle.

Each artifact exposes the **operator surfaces** the Module 8 student drives; budget, kill-switch, HITL gate,
audit, acceptance eval. The finale (03) is the full console: its registry is the contract Module 8 edits to
point the governed fleet at a production problem.

**→ This governed team builds the system in Module 8.**
