# Module 1 — The Shape of Data — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared via Ray's "go").** Locked as proposed:
overview + 2 lessons; the growing from-scratch `ml/` package gated by `pytest` as the throughline; Iris
as the M1 dataset; from-scratch NumPy with scikit-learn only as data source + test oracle. Plus the
standing mandate (2026-06-21): **Haiku fetch tier pulls raw facts from the vault; Sonnet authors use
coding tools; the conductor owns + tests every code artifact first (code is the schema, prose is the
handoff) — "code, don't write" wherever the knowledge is code-shaped.** First authoring stage for Machine
Math (graduated to
`library/in-progress/machine-math` 2026-06-21, `GATE-NAME-BOOK` cleared: title **Machine Math**, slug
`machine-math`). M1 turns the blueprint's Module 1 opener + the `aefs` math/ML ore into finished mdBook
lessons + Claude Code exercises, in the locked Style Contract voice, at the STANDARDS difficulty bar,
under AUTHOR → VERIFY → BUILD/TEST → SHIP. Scope is the already-vetted draft in `draft/` (low
wasted-work risk, which is why the lock is cheap here); authoring upgrades that draft, grounds it in the
named ore, hardens the code under a real test gate, and brings it to ship quality. Stops at
`GATE-APPROVE-SHIP` before folding into `src/` and `exercises/`.

## The stage in one line

M1 installs the book's core reframing: **a dataset row is a point in space, and every classic-ML
algorithm reasons about the geometry of those points.** It pairs the linear-algebra primitives (vectors,
matrices, the dot product, the three distance metrics, feature scaling) with the first algorithm that
cannot function without them, k-nearest neighbors. Seam: a Production AI Engineer who has shipped
retrieval and embeddings has been doing distance-in-feature-space all along; M1 makes that geometry
explicit and turns it into from-scratch code an interviewer can read.

## Settled decisions (from the blueprint + the contracts + the ore)

1. **Stage = module.** Same module-as-stage ICM shape as Sans Python, Just Python, Local Metal, and
   Answer Engineering: M1 reads its sources, writes `build-log/machine-math/m1/output/{author,verify,ship}/`,
   and hands the locked voice + the throughline artifact forward to M2.
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md` (difficulty
   ramp + strong-project rubric + the artifact contract), `STYLE.md` (voice, zero em-dashes). Every
   worker brief carries all three plus a canonical voice exemplar (Local Metal's `module3` runnable-code
   lessons + Just Python's `why-numpy-exists.md`, until Machine Math locks its own) — cold workers do not
   inherit them.
3. **The blueprint's Module-1 split is M1's spine.** M1 establishes feature-space geometry and gives the
   reader the first working algorithm (k-NN) as a from-scratch NumPy build. The math each later module
   needs (calculus in M2, information theory in M3, probability in M5) is held for that module; M1 does
   not pre-empt it. No forward dependencies (STANDARDS ramp rule).
4. **This is a code book: the done-when is a real test gate, not a document validator.** Unlike Answer
   Engineering (whose career artifact is a structured document gated by `check_prep.py`), Machine Math's
   artifacts are runnable from-scratch implementations. The M1 acceptance gate is `pytest` over the
   reader's from-scratch code, mirroring Just Python's `smoke.py` + `pytest` bar (STANDARDS Part 2).
5. **From-scratch in NumPy; scikit-learn only as data source and test oracle.** The algorithm is written
   by hand so the math is visible (the thesis). scikit-learn is allowed for two narrow jobs: loading the
   Iris dataset, and serving as the reference the test asserts against (the from-scratch k-NN must match
   sklearn's labels within tolerance). The minimum deps are `numpy` + `scikit-learn`; everything else is
   standard library. Logged as a Tier-2 narrowing of STANDARDS' "standard library plus the minimum deps."
6. **Ground every claim in named, real sources — no fabrication.** The math grounds on the `aefs` ore
   (distilled first, below); the production framing grounds on Microsoft Learn via the connector (Azure
   AI Search / Cosmos DB similarity metrics for the distance lesson; Azure AutoML k-NN for the algorithm
   lesson). Workers USE the connector and cite a real, verified URL inline — no bare `[MS-Learn: …]`
   markers left unresolved, no citations from memory (the Just Python M2/M3 fix). The draft already
   carries five such markers; VERIFY resolves each to a live URL or cuts it.

## Ore processing (the first move — author against ingredients, not raw vault)

The `aefs` math and ML phases are raw ore, never distilled (root CLAUDE.md forbids authoring directly
against `vault/`). So M1 opens with a distillation pass that produces the book's first ingredients,
reused by M2–M7:

- `ingredients/source/machine-math/aefs-linear-algebra-and-distances.md` — vectors, matrices, the dot
  product as a similarity probe, the three distance metrics, and feature scaling, distilled from
  `aefs` Phase 01 lessons `01-linear-algebra-intuition`, `02-vectors-matrices-operations`,
  `14-norms-and-distances` (each carries `code/` + `docs/` to ground the math).
- `ingredients/source/machine-math/aefs-knn-and-feature-space.md` — the k-NN algorithm, lazy learning,
  k as the bias-variance knob, metric choice as a modeling decision, and the curse of dimensionality,
  distilled from `aefs` Phase 02 lessons `01-what-is-machine-learning` and `06-knn-and-distances`.
- `ingredients/dossiers/machine-math-m1.md` — the keep/cut/frame ruling for M1: what of the ore belongs
  in M1 vs. held for M2 (gradient descent), M5 (evaluation/probability), M6 (PCA/dimensionality
  reduction). PCA is explicitly deferred to M6 where its linear-algebra story completes; ANN/HNSW is
  out of scope (named as the production cousin, not taught).

This is a Tier-2 narrowing of AUTHORING's `ingredients/source/moduleN/` convention: the book scopes its
ingredients under `ingredients/source/machine-math/` (book-named, not Sans-Python-module-numbered)
because the ore is book-specific. Same pattern Answer Engineering used; logged here so it is intentional,
not drift.

## Locked M1 split (overview + 2 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | Every ML algorithm treats a row as a point in feature space; this module builds that geometry and the first algorithm (k-NN) that is pure geometry. | concept | blueprint M1 + draft `00-overview` |
| 1 | `feature-vectors` | A row is a vector; the dot product measures direction-similarity; Euclidean / cosine / Manhattan answer three different "how far?" questions; scaling decides which feature gets a vote. | concept→code | `aefs` P01 L01/L02/L14 + MS-Learn distance metrics |
| 2 | `knn-voting` | k-NN is lazy: store, measure distance, rank, vote; k is the bias-variance knob; the metric is a hypothesis about the data; the curse of dimensionality is why embeddings exist. | build | `aefs` P02 L06 + MS-Learn AutoML k-NN |

Each lesson ends in a Claude Code exercise (`exercises/module1/<slug>/README.md`) with a machine-checkable
done-when (the `pytest` gate, below).

## The compounding throughline (STANDARDS Part 3)

Machine Math's throughline is a **growing from-scratch `ml/` package** — the from-scratch implementations
ARE the math made executable, and they are what an interviewer can read. Each module contributes a file;
the M7 portfolio capstone composes them (imports `metrics.py` + `features.py` off disk to evaluate a real
gradient-boosted model and write the model card that maps each result to its math). The planned spine:

| Module | Throughline file(s) | Reuses |
|--------|--------------------|--------|
| **M1** | `ml/distances.py`, `ml/knn.py` | — |
| M2 | `ml/linreg.py`, `ml/gradient_descent.py` | distances scaling helper |
| M3 | `ml/tree.py` (entropy / Gini / info gain) | — |
| M4 | `ml/ensemble.py` (bagging + boosting from residuals) | `tree.py` |
| M5 | `ml/metrics.py` (AUC-ROC, P/R/F1, MAE/RMSE from scratch) | all model outputs |
| M6 | `ml/features.py` (scaling, encoding), `ml/naive_bayes.py` | `metrics.py` |
| M7 | `pipeline.py` (sklearn + LightGBM model, **graded by the from-scratch `metrics.py`**) + model card | composes M5 + M6 off disk |

M1 seeds:

- `ml/distances.py` — `euclidean`, `cosine`, `manhattan` as pure NumPy functions, plus `minmax_scale` /
  `zscore`. (Exercise 1 builds this.)
- `ml/knn.py` — the from-scratch `KNNClassifier` (`fit` = store; `predict` = distance, rank, vote),
  metric-pluggable, importing `distances.py`. (Exercise 2 builds this; the draft already contains the
  reference implementation, which the conductor will own and test.)
- `exercises/module1/<slug>/test_*.py` — the acceptance gate: from-scratch distances match a reference
  to tolerance; the from-scratch k-NN matches scikit-learn's `KNeighborsClassifier` labels on the Iris
  held-out split within tolerance, and held-out accuracy clears a floor (e.g. ≥ 0.90 at k=5 Euclidean
  after scaling). `pytest` exit 0 is the done-when. **The negative case is tested** (STANDARDS Part 2):
  an unscaled run measurably degrades accuracy / disagrees with the scaled reference, proving why scaling
  is not optional.
- `exercises/CLAUDE.md` — the coaching contract (STANDARDS Part 3, required to graduate): read the lesson
  and the exercise, **find the `ml/` package and read its current state before adding to it** (it is
  continuing a build), coach without solving (a stub, a signature, a failing test — never the finished
  implementation).

## Sources (three-source rule)

1. **Distilled ingredient:** the two new `ingredients/source/machine-math/` files + the M1 dossier
   (produced by the ore-distillation pass above), grounding every math claim in the `aefs` lesson it
   came from.
2. **Authoritative external grounding — Microsoft Learn via the connector.** The distance-metric lesson
   grounds on Azure AI Search vector similarity + Azure Cosmos DB distance functions; the k-NN lesson on
   Azure AutoML `ClassificationModels.Knn` / `RegressionModels.Knn`. Workers USE the connector and cite a
   real, verified URL inline. The five draft markers are treated as claims to verify, not citations to
   trust.
3. **Editorial seam framing** — "why does a Production AI Engineer need this?" in every lead (the
   retrieval / embeddings tie-in is the natural hook: vector search is k-NN at scale).

## The fleet plan (orchestration)

Per `platform/ORCHESTRATION.md` and the Just Python A/B result (handler tier only for concurrent gates or
multiple clusters, not by worker count): **conductor-direct, no handler tier.** One small cluster, single
gate.

- **Round 1 (critical path):** one ore-distillation Sonnet worker produces the two ingredient files + the
  M1 dossier from the named `aefs` lessons. In parallel, the conductor writes and **runs** the from-scratch
  `ml/distances.py`, `ml/knn.py`, and the `pytest` gate against real Iris, locking byte-identical code
  before any prose worker sees it (the Local Metal "conductor owns + tests every code artifact" pattern
  that produced near-zero drift). Book scaffold (`book.toml`, `theme/`, `src/README.md`, `src/SUMMARY.md`)
  is already in place from graduation.
- **Round 2 (parallel):** Lesson-1 worker (`feature-vectors`), Lesson-2 worker (`knn-voting`), and an
  exercises worker, each briefed with all three contracts + the voice exemplar + the distilled ingredient
  + the locked code + the connector instruction.
- **Conductor** authors `00-overview`, integrates `SUMMARY.md`, runs `pytest` + `mdbook build` itself, and
  runs the Zinsser + STYLE + STANDARDS review gate on every draft before it lands. No worker draft ships
  unreviewed; no code ships untested by the conductor.

## Open decisions for the lock (GATE-LOCK-PLAN)

1. **Lesson granularity.** Proposed: **overview + 2 lessons** (matches the vetted draft; feature-space
   geometry and k-NN are two distinct, load-bearing ideas, and this is a Foundations-phase opener, like
   Answer Engineering's lean 2-lesson M1). Alternative if you want M1 beefier: split a third lesson out of
   the back half of `feature-vectors` ("Scaling and the Curse of Dimensionality" as its own lesson),
   giving overview + 3 lessons + 3 exercises. **Recommend 2.**
2. **Throughline artifact shape.** Proposed: the growing from-scratch `ml/` package gated by `pytest`
   (table above), with the M7 capstone composing `metrics.py` + `features.py`. This is the central design
   lock for the whole book; confirming it here sets the spine M2–M7 extend.
3. **M1 dataset.** Proposed: **UCI Iris** (150 rows, 4 numeric features), as in the draft — small enough
   that exact k-NN geometry stays legible. The portfolio dataset (M7) is a larger tabular set (UCI Adult
   Income or a Titanic variant); that choice is M7's lock, not M1's.
4. **Dependency policy.** Proposed: from-scratch NumPy for all algorithms; scikit-learn permitted only as
   dataset source + test oracle (decision 5 above). Confirm this is the standing rule for the book.

On lock: the fleet distills the ore + authors M1 against the locked code, VERIFY gates it (voice + claims
+ MS-Learn markers resolve + the `pytest` gate runs green), BUILD/TEST runs `mdbook build` + `pytest`
from the exercises' real paths, and the stage stops at `GATE-APPROVE-SHIP` before folding into `src/` and
`exercises/`.
