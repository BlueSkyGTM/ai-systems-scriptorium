# Module 6: Data Wrangling Artifact

## What This Module Covers

Modules 1 through 5 taught the pieces. Module 6 is the first time you ship one production artifact that uses all of them: `wrangle.py`, a data-cleaning pipeline that turns a raw JSONL corpus into a validated, typed Parquet dataset. This is the Composition phase of the book, and the artifact is the take-home a hiring manager actually runs.

Unlike the earlier modules, M6 is not a set of independent lessons. It is one pipeline built in four stages, each lesson adding the next, ending in a green test gate. The artifact is held to the strong-project bar: a real entry point, a README that frames the business problem first, a `pytest` smoke gate that proves it (including a deliberate failure case), and a skill write-up that turns the script into a portfolio piece.

## Arc of Lessons

| Lesson | Title | Stage of `wrangle.py` |
|--------|-------|-----------------------|
| 1 | Ingest the Corpus | Read raw JSONL into a typed DataFrame; a frozen `@dataclass` config holds the contract |
| 2 | Clean and Deduplicate | Dedup on the key, drop null-text rows, fill null scores, normalize text with the `.str` accessor |
| 3 | Reshape and Validate | Select to the schema and assert it: required columns, no null leakage, correct dtypes; a violation raises at the gate |
| 4 | Emit, Test, and Ship | Write Parquet, compose the stages in `run`, then the `pytest` smoke gate and the skill write-up |

## Throughline Artifact

`wrangle.py` is the portfolio artifact, and the first one that **composes** everything before it: M3's Pandas I/O and cleaning, M5's idioms (a frozen `@dataclass` config, a `WrangleStats` record, type hints, the vectorized `.str` accessor), following made-with-ml's real `data.py` shape. The acceptance gate is `smoke.py`: it asserts the row accounting (8 in, 6 out, 1 duplicate and 1 null dropped), that the Parquet round-trips with the right types (checked with `pandas.api.types` predicates so a round-trip's `str` dtype passes), and that a malformed corpus raises at the validation gate. The skill write-up in `outputs/skill-data-wrangling.md` is the portfolio surface. The data this pipeline produces is what Module 7's evaluation engine consumes.

## Prerequisites

- Modules 1 through 5, especially M3 (Pandas) and M5 (idioms: dataclasses, type hints, the `.str` accessor). M6 composes them; it does not re-teach them.
- A Python 3.11+ environment with pandas, numpy, and pyarrow (`pip install pandas numpy pyarrow`). pyarrow is required for the Parquet output; `emit` fails with a clear install hint if it is absent.
