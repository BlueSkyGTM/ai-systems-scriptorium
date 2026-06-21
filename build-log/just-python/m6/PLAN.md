# Module 6 — Data Wrangling Artifact — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared — Ray locked as drafted: all 4 decisions
accepted — 5 lessons, pre-specified canonical `wrangle.py`, ship the skill write-up, connector + conductor
smoke gate).** **SHIPPED 2026-06-21 (`GATE-APPROVE-SHIP` cleared).** Sixth authoring stage for Just Python, and the **first portfolio
module** (the Composition phase, STANDARDS Part 1 ramp). M1–M5 shipped. M6 turns the
blueprint's sixth module into a finished mdBook chapter + a runnable portfolio artifact, under
AUTHOR → VERIFY → BUILD/TEST → SHIP. Do not author until Ray locks.

## The stage in one line

M1–M5 taught the pieces; M6 is the first time the reader ships one production artifact that uses all of them.
They build `wrangle.py`: a data-cleaning pipeline that ingests a raw JSONL corpus, cleans and deduplicates it
with Pandas (M3), applies the idioms (M5), reshapes and schema-validates it, and emits a typed Parquet file,
with a `pytest` smoke gate that proves it. Seam: this is the take-home. It is the artifact a reader puts in a
GitHub repo and a hiring manager runs.

## Settled decisions (from the blueprint + the contracts)

1. **Portfolio shape, not a lesson toolkit (STANDARDS Part 2 is the bar).** M6 is held to the full
   strong-project rubric: a **real entry point** (`python exercises/module6/wrangle.py` exits 0), a **README
   that frames the business problem before the code**, a **concrete machine-checkable acceptance gate** (a
   `smoke.py`/`pytest` that verifies row counts, dtypes, and no null leakage), **the negative case tested**
   (a deficient input fails the gate it offends), a **clean versioned layout with no secrets**, and a
   **shipped skill write-up** (`exercises/module6/outputs/skill-data-wrangling.md`). A book that skips any of
   these does not graduate to ship.
2. **Composition is the point (STANDARDS Part 3).** `wrangle.py` **reuses** what the reader built: M3's
   Pandas I/O + cleaning, M5's idioms (a `@dataclass` schema, comprehensions/generators for streaming, type
   hints throughout), and the made-with-ml `data.py` patterns the blueprint names. It composes; it does not
   re-teach. This is the Composition rung the contract reserves for M6–M8.
3. **Pre-specified artifact structure to avoid the M4 divergence.** M4 showed four cold workers each
   inventing a different shape for one shared file. M6 fixes that **up front**: this PLAN fixes `wrangle.py`'s
   canonical structure (stages + function signatures, below), and each worker builds its stage to that spec.
   The conductor owns final assembly + the smoke gate.
4. **The artifact is learner-built (not committed), like `measure.py`.** The exercises instruct the learner to
   build `wrangle.py` / `smoke.py` / the skill write-up; the conductor verifies a reference build runs end to
   end (BUILD/TEST), then discards it. Nothing reference-only is committed into the book.
5. **Ore = made-with-ml `data.py` + pandas-docs + the connector.** The applied spine is made-with-ml's real
   data pipeline (load → clean_text → split → tokenize); pandas-docs `io`/`missing_data`/`reshaping` is the
   mechanics; Microsoft Learn (queried at author time) is the production-pattern grounding.

## The canonical `wrangle.py` structure (locked here so workers build to one design)

A typed, staged pipeline. Each lesson builds one stage; the `main()` runs them in order.

```
@dataclass(frozen=True) WrangleConfig   # input path, output path, dtypes, dedup keys (M5 dataclass)
def ingest(path) -> DataFrame           # read JSONL corpus, dtypes on load            (L1)
def clean(df) -> DataFrame              # dedup + NaN handling + text normalize        (L2)
def reshape_and_validate(df, schema) -> DataFrame   # reshape + assert schema/dtypes   (L3)
def emit(df, path) -> None              # write validated Parquet                       (L4)
def run(config) -> WrangleStats         # compose the four stages; return a stats record (dataclass)
if __name__ == "__main__": run(default_config)   # exits 0
```

## Proposed M6 split (5 lessons; each builds one stage of the one artifact)

| # | Lesson (slug) | One idea / stage | Kind | Source slice |
|---|---------------|------------------|------|--------------|
| 0 | `00-overview` | The portfolio artifact: a production data-cleaning pipeline that composes M1–M5. What a hiring manager runs. | concept | conductor-integrated |
| 1 | `ingest-the-corpus` | Read a raw JSONL corpus into a typed DataFrame, dtypes controlled on load; a `@dataclass` config holds the contract. | build | pandas-docs `io`; made-with-ml `data.py` load |
| 2 | `clean-and-deduplicate` | Dedup, handle missing values, normalize text with the vectorized `.str` accessor; the corpus-prep pass that decides what reaches the model. | build | pandas-docs `missing_data`/`duplicates`/`text`; made-with-ml `clean_text` |
| 3 | `reshape-and-validate` | Reshape to the target schema and assert it: dtypes, required columns, no null leakage; a schema check is the gate, not a hope. | build | pandas-docs `reshaping`; M5 dataclass schema |
| 4 | `emit-test-and-ship` | Emit validated Parquet, write the `pytest` smoke gate (including the negative case), and ship the skill write-up; the artifact is done when the gate is green. | build | pandas-docs `io` (Parquet); STANDARDS Part 2 rubric |

Each lesson ends in a Claude Code exercise (`exercises/module6/<slug>/README.md`) that builds its stage of
`wrangle.py` to the canonical structure above. The L4 exercise also produces `smoke.py` and
`outputs/skill-data-wrangling.md`.

## The compounding throughline (STANDARDS Part 3)

`wrangle.py` is the M6 portfolio artifact and the first one that **composes** rather than extends: it imports
nothing from `measure.py` by necessity, but it **reuses every skill** built so far (M3 Pandas, M5 idioms) and
follows the made-with-ml `data.py` shape. M7's evaluation engine and M8's exam then build on the data
`wrangle.py` produces. The skill write-up (`outputs/skill-data-wrangling.md`) is the portfolio surface and the
`progression/` signal.

## Sources (three-source rule, non-negotiable)

1. **Ingredient:** made-with-ml `madewithml/data.py` (the real load/clean/split pipeline) + the reader's M3/M5
   work; pandas-docs `io`/`missing_data`/`reshaping` for mechanics. Read at author time.
2. **Microsoft Learn** via the connector — workers query it at author time to ground the production data-prep
   pattern in a real page with a real URL; no bare markers, no fabrication, state plainly if no page fits.
3. **Editorial seam framing** — "this is the take-home": the artifact a reader ships to prove they can turn a
   raw corpus into a validated dataset.

## The fleet plan (conductor-direct; shared artifact pre-specified)

- **Conductor (Opus, this session):** locks the plan (with the canonical `wrangle.py` structure), dispatches 4
   Sonnet workers, authors `00-overview`, **assembles + runs the reference `wrangle.py` + `smoke.py`** as the
   BUILD/TEST gate, and runs the STYLE/STANDARDS review (Part 2 rubric included) on every draft.
- **Workers (Sonnet, parallel):** lessons 1–4, one per stage, one writer per lesson file + its exercise
   README, each building its stage **to the locked `wrangle.py` structure**. Briefs carry AUTHORING +
   STANDARDS (esp. Part 2) + STYLE + the M1–M5 exemplars + the made-with-ml `data.py` slice + the MS-Learn
   connector instruction. Workers never touch `SUMMARY.md` or `exercises/CLAUDE.md` (conductor-folded).

## Open decisions to pressure-test (lock these with Ray)

1. **Granularity / stages.** 5 lessons mapping ingest / clean / reshape-validate / emit-test-ship (proposed).
   Recommendation: **5** — four pipeline stages + overview, each a build lesson, culminating in the green gate.
2. **The canonical `wrangle.py` structure** (above). Confirm the staged, typed, `@dataclass`-config shape, so
   the four workers build to one design (the M4 fix). Recommendation: **lock it as drafted.**
3. **Skill write-up.** Confirm M6 ships `exercises/module6/outputs/skill-data-wrangling.md` (the portfolio
   surface, STANDARDS Part 2). Recommendation: **yes** — it is required for a portfolio module to graduate.
4. **Connector at author time + conductor-built smoke gate.** Confirm workers use the connector, and the
   conductor assembles + runs the reference `wrangle.py` + `smoke.py` (incl. the negative case) as BUILD/TEST.
   Recommendation: **yes.**

On lock: the fleet authors M6, VERIFY gates it against STYLE + the live connector, BUILD/TEST assembles and
runs the reference `wrangle.py` + `smoke.py` (the rubric's acceptance gate, negative case included) plus
`mdbook build`, and the stage stops at `GATE-APPROVE-SHIP` before folding into `src/`.
