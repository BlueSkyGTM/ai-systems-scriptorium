# FINDINGS — Does the Method Complete the Books?

Running verdict log for the experiment defined in the root `HANDOFF.md` and this folder's `README.md`.
Verdict scale: `HOLDS` / `PARTIAL` / `MOSTLY-BUILT-IN`. Do not flatter the method.

## Verdict so far: PARTIAL, leaning HOLDS on the parts the structure actually owns (3 data points)

Three findings. Orientation (01) was the easy case. The M2 plan (02) showed structure earning credit on
consistency + context-economy. The M2 authoring stage (03) is the decisive one, and it produced the single
strongest piece of evidence in the test: **the author/verify split caught fabricated authority that a
single-pass baseline would have shipped.** The honest shape of the verdict is now clear and stable across
data points: **lesson content quality ≈ Claude's built-in capability; the catches, the cross-worker
consistency, and the context-economy ≈ the structure.** The structure is not ceremony, but it is also not
what writes the prose. One sub-claim weakened: the handler tier was mild overhead this round (no concurrent
gate to justify it).

---

## Finding 01 — Cold-start orientation

- **Stage touched:** Session boot. Read `HANDOFF.md`, then self-routed to a correct state model of the repo.
- **Cold-proceed?** **YES.** Evidence: from `HANDOFF.md` alone I went `CLAUDE.md` → `CONTEXT.md` →
  `CATALOG.md` → `build-log/stress-test/README.md` → `platform/HUMAN-GATES.md` and arrived at an accurate
  picture — what's shipped (Sans Python), what's in progress (Just Python, M1 shipped, M2 next), the 5
  named planned books + 2 unresolved stubs, and exactly which decisions are gated to Ray — with no human
  re-orientation. The handoff's instruction "if you can run from this file plus the repo's structure, that
  is the first data point" is satisfied for orientation.
- **Structure did:** The `CONTEXT.md` intent→route table is a real lookup, not prose. It gave an explicit
  **load / do-NOT-load** list per intent, which (a) told me to skip the 767 MB `vault` and (b) named the
  exact files that constitute "status." `HUMAN-GATES.md` gave me a closed, ID'd list of where I must stop —
  so I know *before acting* that advancing Just Python M2 hits `GATE-LOCK-PLAN` and starting any planned
  book hits `GATE-NAME-BOOK`. That is the structure doing work: I knew the gate map without trial and error.
- **Baseline would have done:** A lot of this. Plain Claude + a single good `CLAUDE.md` would also orient by
  reading the obvious top-level files. The decisive advantage here is small. Honest read: **the well-written
  `HANDOFF.md` is carrying most of the cold-start**, and a handoff file is not unique to this architecture —
  any project can leave one. The router's marginal contribution over "just read the repo" is the *explicit
  don't-load list* and the *closed gate registry*; both saved steps, neither was essential to orient.
- **Net attributable to structure:** Marginal-but-real at orientation. The don't-load column actively
  steered context economy (below); the gate registry converted "discover the gates by hitting them" into
  "read them once up front." Estimate: a handful of saved tool-calls and one avoided misstep (authoring
  against `vault`). Not yet evidence the method *completes books* — only that it boots an agent cleanly.
- **Strain / overhead:** None yet. Orientation cost ~6 small reads.
- **Context economy:** **Stayed lean.** ~6 files, all small top-level routers/registries. Never opened
  `vault/`. The don't-load column is the mechanism that kept me out of the 767 MB ore. Real win, but a
  cheap one — I hadn't yet been tempted toward the vault.
- **Drift caught:** N/A at orientation (no `route-lint` run, no structural change made).

**Open question this finding cannot answer:** orientation is the case most favorable to the architecture and
least favorable to distinguishing it from baseline. The test only becomes informative when a book is pushed
through plan → author → verify → build, where consistency-enforcement and spawn-isolation either earn their
keep or prove to be ceremony. That evidence does not exist yet.

---

## Finding 02 — Just Python M2 plan (plan stage only; stopped at GATE-LOCK-PLAN)

- **Stage touched:** Just Python M2 "NumPy in Depth" — drafted `build-log/just-python/m2/PLAN.md` to
  lock-ready, ran route-lint (green), updated the build-progress ledger. Stopped at the gate; no authoring.
- **Cold-proceed?** **YES.** Produced a lock-ready PLAN from structure alone: book `README.md` (module map),
  `m1/PLAN.md` (format template + the recorded M1/M2 boundary), the three contracts, the shipped M1 lessons
  (voice + `measure.py` throughline state), and a filename-only confirmation of the vault ore. No re-brief.
- **Structure did (specific):**
  - **Pre-recorded boundary.** `m1/PLAN.md` settled-decision #2 (dtypes + strides/view mental model → M1;
    broadcasting/indexing/ufuncs/layout API → M2) converted a judgment call into a lookup. The plan didn't
    have to *re-derive* where M1 stops; it inherited the line.
  - **Contract-forced discipline.** STANDARDS Part 1 forced an explicit no-forward-dependency ordering
    check; Part 3 forced the throughline to be *real import-and-extend* (`measure.py` gains two probes that
    M4 imports off disk) rather than a restated artifact, and forced honoring the `exercises/CLAUDE.md`
    coaching contract. A baseline plan would likely list good lessons but not spontaneously impose
    "artifacts chain by import, capstone composes not rebuilds, progress is artifact-measured."
  - **Context economy, concretely.** Planned a full 5-lesson NumPy module **without loading one line of
    NumPy documentation.** The don't-load discipline + the "PLAN names a source *slice*, the worker reads it
    at author time" convention let the conductor plan against section *names* (`basics.ufuncs`,
    `basics.broadcasting`, …), confirmed real by a filename-only Glob. Never opened the 767 MB vault.
- **Baseline would have done:** Most of the lesson *topics*. ufuncs / broadcasting / advanced-indexing /
  layout is fairly canonical NumPy curriculum; a competent agent + one CLAUDE.md lands there too. Honest
  split: **topics ≈ baseline; consistency-enforcement + context-economy = structure.**
- **Net attributable to structure:** (a) the M1/M2 boundary came pre-resolved and recorded, not
  rediscovered; (b) the artifact-chaining + coaching-contract discipline was contractually required, not
  optional taste; (c) the module was planned without ingesting the ore. None of the three are things a
  baseline agent reliably does on its own — they are exactly the anti-drift properties the lineup needs.
- **Strain / overhead:** Low but non-zero. Reading 5 contract/exemplar files before drafting is more
  up-front load than baseline would bother with — but that load *is* the consistency mechanism, so it's
  earned. One genuine tax: the blueprint's module table is stale (see Drift), so the plan had to spend a
  paragraph reconciling blueprint-vs-M1-PLAN. Doc layering created a small reconciliation cost.
- **Context economy:** **Stayed lean.** Added ~7 small reads (book README, M1 PLAN, 2 contracts, 2 M1
  artifacts, coaching contract) + 2 filename-only Globs. Zero vault content loaded.
- **Drift caught:** **Yes, a real one.** The blueprint's M2 row still lists "dtypes" and "memory layout" —
  but M1 already shipped `dtypes-and-what-they-cost` and the strides/view mental model. Planning M2 straight
  from the blueprint would have **re-taught dtypes** (a duplicate lesson). The layered record
  (blueprint → M1 PLAN settled-decision → shipped M1 lessons) surfaced it. **Honest nuance:** route-lint did
  *not* catch this — it's a semantic overlap, not a structural edge — so credit is the *contract/plan
  layering*, not the linter. And a careful baseline agent reading the shipped M1 lessons would also notice.
  The structure's real contribution is making the boundary **explicit and recorded** so it's caught every
  time, not contingent on the agent being careful that day.

---

## Finding 03 — Just Python M2 authoring (AUTHOR + VERIFY + BUILD/TEST; stopped at GATE-APPROVE-SHIP)

- **Stage touched:** Full M2 build. Tiered fleet (1 Opus handler -> 4 Sonnet workers) drafted 4 lessons +
  4 exercises; conductor ran the STYLE/STANDARDS review gate, VERIFY against the live MS-Learn connector,
  authored the overview, folded shared state (`SUMMARY.md`, `exercises/CLAUDE.md`), and ran BUILD/TEST
  (`mdbook build` clean; all 4 exercise gates pass deterministically). Stopped at the gate.
- **Cold-proceed?** **YES.** The fleet authored from briefs + contracts + the M1 exemplars; the conductor
  ran verify/build straight from the pipeline. No human re-brief at any point in the stage.
- **Structure did (the core measurement):**
  - **HEADLINE: the author/verify split caught fabricated authority.** The Sonnet workers, drafting under
    pressure, invented plausible-sounding MS-Learn citations that *no real page backs* — e.g. L2's "critical
    for memory-efficient large-scale feature processing in Azure Machine Learning batch pipelines" and four
    bare contiguity/cache markers in L4 (a topic MS Learn does not cover at all). The pipeline's **separate
    VERIFY stage** exists for exactly this: AUTHOR is instructed to leave `[MS-Learn:]` markers *unresolved*
    so a distinct pass resolves them against ground truth. Querying the real connector showed the actual
    coverage (the "Explore and Analyze Data with Python" module grounds NumPy at the pattern level;
    memory-layout is pure numpy-docs territory). I replaced the fabrications with one grounded, verified URL
    per lesson and dropped the rest (12 markers -> honest citations). **A single-pass "write 4 NumPy lessons"
    baseline would very likely have shipped the fabricated citations**, because nothing forces the
    author-then-verify-against-source separation. This is an error a human eye skims past (the fake citations
    read as authoritative) and the staged process caught mechanically.
  - **Spawn isolation kept workers clean and bounded.** 4 cold workers, one writer per file, never touched
    `SUMMARY.md` / `measure.py` / `exercises/CLAUDE.md` (shared state, conductor-folded). No race, no
    cross-contamination, consistent voice.
  - **Contract-enforced consistency held.** All 4 lessons matched M1's voice (M1 lessons were the exemplar in
    every brief), the de-dup boundary held (each cites M1's view/copy without re-deriving), every lesson
    shipped `## Core concepts` + a machine-checkable exercise, and the `measure.py` throughline was extended
    by real import, not restated.
  - **Second drift caught:** the stale `exercises/CLAUDE.md` throughline path (`exercises/module1/measure.py`
    vs the real `.../the-cost-of-a-python-list/measure.py`) surfaced when I cross-checked the coaching note
    against the M1 exercise. route-lint did NOT catch it (semantic, not a structural edge) — the catch came
    from the contract requiring the throughline note to name the real artifact.
- **Baseline would have done:** The lesson *prose* is strong, and a competent baseline writes comparable
  NumPy lessons. Honest split: **content quality ≈ built-in; the catches (fabricated citations, stale path,
  de-dup) and the cross-worker consistency ≈ structure.**
- **Strain / overhead:** The **handler tier was mild overhead this round** — a single 4-worker cluster with
  no concurrent gate to service, so the tier's main rationale (keeping the human loop alive during execution)
  wasn't active. It did earn part of its keep: the handler's first-pass review caught a worker's factual
  error (a wrong `view.nbytes` value in the broadcasting lesson) before it reached the conductor. VERIFY and
  the conductor review were real labor (querying the connector, 17 edits, reading 8 files) but that labor is
  what caught the fabrications, so it is earned, not waste.
- **Context economy:** **Spawn isolation paid for context economy directly.** The workers read the numpy-docs
  ore (their bounded job); the **conductor never loaded a line of numpy-docs** — the spawn boundary kept the
  reference ore in disposable worker context while the conductor's context stayed on contracts + review +
  the 8 module2 files. Never opened the 767 MB vault.
- **Drift caught:** Two (this stage): the fabricated MS-Learn citations (VERIFY + connector) and the stale
  throughline path (contract cross-check). Plus the L4 over-claimed fixed timing ratio (2.26x stated as if
  guaranteed; real hardware showed ~1.02x) — corrected to hardware-dependent framing. That last one is a
  conductor-review catch a careful baseline reviewer could also make; credited to the method only weakly.
