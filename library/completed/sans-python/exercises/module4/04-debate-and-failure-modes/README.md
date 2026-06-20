# Exercise 04 — Debate & Failure Modes

**Goal** — Run a debate between the `module4-fleet/` agents in both full-mesh and star topology, confirm the star matches accuracy at far lower token cost, then add a failure-mode tagger that labels traces with the five recurring MAST modes.

**Why** — Debate is the AI Engineer's accuracy lever and MAST is the MLOps engineer's reliability map; an Production AI Engineer wires debate sparse and treats every failure as a design input, not a model complaint.

**Steps**

1. In `module4-fleet/`, implement a debate over the harness agents: N instances (start with N=3) each propose an answer to a question with a checkable ground truth, then critique and revise over R rounds (start with R=2) until they converge.
2. Implement two topologies behind a flag:
   - **Full-mesh** — every agent reads every other agent each round.
   - **Star** — every agent reads one hub agent each round.
   Count critique operations and total tokens for each.
3. Run both on the same set of questions and record: accuracy (against ground truth) and token cost per topology. Confirm star ≈ full-mesh on accuracy at a fraction of the operations and tokens.
4. Build `module4-fleet/failure_tagger.py`: a deterministic tagger that reads a run trace and labels it with any of the five recurring MAST modes it detects — **hallucinated action** (a tool/step that doesn't exist), **scope creep** (work outside the assigned task), **cascading error** (a wrong input trusted downstream), **context loss** (a handoff that dropped required detail), **tool misuse** (wrong args or wrong tool).
5. **Trigger one on purpose.** Inject a fault into a run — e.g., feed the writer a hallucinated "fact" from the researcher — and confirm the tagger flags the right mode (cascading error or context loss).
6. Write `module4-fleet/FAILURES.md` (4–6 sentences): which mode you triggered, why a better base model would *not* fix it, and which governance capability (from the rest of the module) is the design answer.

**Done when**

- Debate runs in both topologies; a printed table shows star matching full-mesh accuracy at clearly lower token cost (real numbers).
- `failure_tagger.py` labels a trace with at least one of the five MAST modes and is verified against a deliberately injected fault.
- `FAILURES.md` argues, concretely, that the triggered failure is a design flaw, not a model limitation — and names its governance fix.

**Stretch** — Run heterogeneous debate: swap one debating agent's model (or its system prompt/temperature) so the panel isn't a monoculture. Measure whether decorrelated errors improve consensus accuracy over the homogeneous panel on the same questions.
