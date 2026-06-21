# Stress-Test Log — Just Python

Per-book log for the stress-test experiment (defined in this folder's `README.md`). Full reasoning + the cross-book verdict live in
`FINDINGS.md` (Findings 01–03); this file is the Just-Python-specific record using the README template.

## Track 1: Just Python M2 "NumPy in Depth" — plan → author → verify → build → ship

- **Stage touched:** M2 end to end. Plan drafted + locked (`GATE-LOCK-PLAN`), authored by the tiered fleet
  (1 Opus handler → 4 Sonnet workers), verified against the live MS-Learn connector, built (`mdbook` +
  exercise gates), shipped (`GATE-APPROVE-SHIP`). Conductor: this session. Pushed to main on ship.
- **Cold-proceed?** **Y.** Self-routed from `HANDOFF.md` → `CLAUDE.md` → `CONTEXT.md` → book `CONTEXT.md`
  → pipeline + contracts, and ran the whole stage with no human re-brief. The only human touches were the
  three gates by ID (`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`) — which is the design, not a re-orientation.
- **Structure did:**
  - **Author/verify split caught fabricated MS-Learn citations** the Sonnet workers invented (e.g. L2
    "critical for…Azure ML batch pipelines"; four bare contiguity markers in L4, a topic MS Learn does not
    cover). The mandatory, *staged* VERIFY-against-connector pass is what caught it. **Single strongest piece
    of structure-vs-baseline evidence in the test.**
  - **Spawn isolation** kept 4 cold workers on bounded slices, one writer per file, never touching shared
    state (`SUMMARY.md`, `measure.py`, `exercises/CLAUDE.md`); the conductor folded shared state. It also
    kept the numpy-docs ore in disposable worker context — the **conductor never loaded a line of it.**
  - **Contracts enforced consistency:** all 4 lessons in M1's voice (M1 = the exemplar in every brief), the
    de-dup boundary held (use M1's view/copy, don't re-derive), every lesson shipped `## Core concepts` + a
    machine-checkable exercise, `measure.py` extended by real import.
  - **Plan/contract layering caught two drifts:** the blueprint's stale "dtypes under M2" (would have
    duplicated M1), and a stale `measure.py` path in `exercises/CLAUDE.md`. Neither was caught by route-lint
    (both semantic, not structural edges).
- **Baseline would have done:** the lesson *prose* (NumPy curriculum is canonical; Claude writes it well).
  **Content quality ≈ built-in.**
- **Net attributable to structure:** the catches (fabricated citations, stale path, de-dup), the
  cross-worker single-voice consistency, and the conductor's clean context (ore pushed to workers).
- **Strain / overhead:** the **handler tier was mild overhead** this round — one 4-worker cluster, no
  concurrent gate to justify the extra tier (it did catch one worker factual error on first pass). VERIFY +
  conductor review were real labor, but that labor caught the fabrications, so earned.
- **Context economy:** lean. Conductor read the ~8 module2 files + a handful of exemplars/contracts; never
  opened the 767 MB vault; never read the numpy-docs ore (spawn boundary held it in workers).
- **Drift caught:** fabricated MS-Learn citations (VERIFY + connector), stale throughline path (contract
  cross-check), over-claimed L4 timing ratio (conductor review; corrected 2.26x→hardware-dependent, real
  machine 1.02x).

**Verdict for this track:** the method earned real, specific credit at the stage that matters most
(authoring), via a catch a human eye skims past and a baseline ships. It did **not** write the prose — that
is built-in. One tier (handler) was overhead. See `FINDINGS.md` for the rolled-up verdict.

## Track 1 (cont.): Just Python M3 "Pandas for AI Pipelines" — shipped 2026-06-21

- **Stage:** Full M3 build, **conductor-direct (no handler tier — the orchestration A/B)**. 4 Sonnet workers
  managed directly; conductor review + VERIFY + BUILD/TEST. Pushed on ship.
- **Cold-proceed?** Y.
- **Reproduced result:** VERIFY caught fabricated MS-Learn authority **again** (L2 invented an Azure-ML
  module; L3 invented an "Azure-ML evaluation pattern"). 2-for-2 with M2 — cold parallel authoring fabricates
  authority systematically; the staged VERIFY closes it systematically. The strongest structure-vs-baseline
  signal, now reproduced rather than a one-off.
- **The A/B result:** conductor-direct matched the handler run on quality. Handler tier = optional overhead
  for a single ≤4-worker cluster with no concurrent gate. `ORCHESTRATION.md` updated (handler when concurrent
  gates or multiple clusters, not by worker count). The test improving the architecture, not just grading it.
- **BUILD/TEST caught what self-reports missed:** L1's hardcoded `frame_bytes` numbers were wrong for current
  pandas (249→224) and falsely "platform-stable"; L4's final assert referenced the wrong variable. Running
  the gate, not trusting the report, caught both.
- **Honest correction:** the distillation machinery stayed **unexercised** — `pandas-docs` is reference-grade,
  so JP M1–M3 all bypassed `ingredients/dossiers`. Truly stressing distillation needs a code-ore book.
- **Content ≈ built-in; catches + cross-worker consistency + context-economy ≈ structure** (unchanged).

**Next informative test:** either **JP M4 (Vectorization Discipline)** — the first module to *reuse*
`measure.py`'s M2/M3 extensions off disk, which finally tests the artifact-chaining claim for real — or a
**second book cold-start** (the "multiple books" HOLDS criterion). The `ingredients/dossiers` distillation
machinery still wants a code-ore book to be exercised at all.
