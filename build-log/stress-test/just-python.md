# Stress-Test Log — Just Python

Per-book log for the experiment in the root `HANDOFF.md`. Full reasoning + the cross-book verdict live in
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

**Next informative test:** M3 (Pandas) — a different ore vein (`made-with-ml`, needs a real
vault→ingredients distillation pass, unlike M1/M2's reference-grade numpy-docs). That pass is where the
ingredients/dossier machinery either earns its keep or proves to be ceremony. Not yet run.
