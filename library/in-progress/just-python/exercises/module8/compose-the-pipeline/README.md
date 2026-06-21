# Exercise: Compose the Pipeline

A data wrangler that cleans a corpus and an eval engine that scores predictions are useful on their own. Chained together, with the predictions merged against the clean labels and a single report written at the end, they become an integrated quality check: one command, one report, one answer about which class the model cannot get right. That is the artifact a reviewer reads before a model ships.

This exercise wires your M6 and M7 artifacts together without touching them. The pipeline imports them off disk and calls their existing entry points. Nothing is reimplemented.

**Goal:** Build `exercises/module8/artifact_adapter.py` and `exercises/module8/pipeline.py` to the locked shape. The gate is green when `python pipeline.py` exits 0 and writes `outputs/report.md`, and a smoke check confirms `ExamRun.n_clean == 10` and `ExamRun.composed_modules == ["wrangle.py", "eval_engine.py"]`.

**Why:** An AI engineer who can compose prior artifacts off disk, chain their contracts, and emit a graded report is doing what a production MLOps pipeline does: separate, reusable steps whose outputs chain. Rebuilding the wrangler inside the exam would prove nothing about your M6 work; importing it proves everything.

## Before You Touch Code

Read the lesson at `src/module8/compose-the-pipeline.md`. Then check whether `exercises/module8/artifact_adapter.py` or `exercises/module8/pipeline.py` already exist; if they do, read them before adding anything.

You need two inputs from the lesson-1 exercise (`exercises/module8/the-exam/`):

- `exercises/module8/sample_corpus.jsonl`: the raw corpus (10+ rows, columns `id`, `text`, `label`; some dupes and nulls)
- `exercises/module8/sample_predictions.csv`: the batch-inference output (columns `id`, `prediction`)

Both live in `exercises/module8/`. If either is absent, the lesson-1 exercise builds them; do that first.

You also need the two prior artifacts:

- `exercises/module6/wrangle.py`: provides `WrangleConfig` and `run(config) -> WrangleStats`
- `exercises/module7/eval_engine.py`: provides `EvalConfig` and `run(config) -> list[ClassMetrics]`

Read both files before writing `artifact_adapter.py`. You are calling their public contracts; understanding the signatures is the pre-condition.

## The Two Files You Build

### artifact_adapter.py

Location: `exercises/module8/artifact_adapter.py`

`artifact_adapter.py` has one public function. Its signature:

```python
def load_artifacts(pipeline_file: str) -> tuple:
    """Return (wrangle_module, eval_engine_module) loaded off disk.

    Anchors resolution to pipeline_file so the paths are correct
    regardless of the working directory.
    """
```

The implementation uses `importlib.util.spec_from_file_location`. It resolves the paths relative to the directory that contains `pipeline.py` (passed in as `pipeline_file`). The wrangle module lives one level up at `module6/wrangle.py`; the eval engine at `module7/eval_engine.py`. Use `.resolve()` on the path before passing it to `spec_from_file_location` so `..` segments collapse cleanly.

A private helper `_load_module(name, path)` that wraps the `importlib` idiom keeps the function body readable. One detail the lesson covers and you must not skip: register the module in `sys.modules[name]` before calling `exec_module`, or a frozen dataclass in the loaded file fails to resolve its own annotations.

Do not add `sys.path` entries. The whole point of `spec_from_file_location` is that you do not need them (`sys.modules` registration is a different thing: it names the module so its annotations resolve, it does not change the import search path).

### pipeline.py

Location: `exercises/module8/pipeline.py`

`pipeline.py` has the locked shape below. Build it in this order: the dataclass, then `run_pipeline`, then the `if __name__ == "__main__":` block.

```python
import pathlib
from dataclasses import dataclass
import artifact_adapter

@dataclass(frozen=True)
class ExamConfig:
    corpus_path: str
    predictions_path: str
    output_dir: str
    version: str = "1.0"

@dataclass
class ExamRun:
    report_path: str           # absolute path to outputs/report.md
    n_clean: int               # WrangleStats.rows_out; expected 10 on the sample
    metrics: list              # list[ClassMetrics] returned by eval_engine.run
    composed_modules: list     # proof: ["wrangle.py", "eval_engine.py"]
    version: str               # "1.0"

def run_pipeline(config: ExamConfig) -> ExamRun:
    ...

_HERE = pathlib.Path(__file__).parent
default_config = ExamConfig(
    corpus_path=str(_HERE / "sample_corpus.jsonl"),
    predictions_path=str(_HERE / "sample_predictions.csv"),
    output_dir=str(_HERE / "outputs"),
)

if __name__ == "__main__":
    run_pipeline(default_config)
```

`default_config` lives at module scope, not inside `__main__`, so lesson 4's smoke gate can `from pipeline import default_config`.

## The Data Flow

Implement `run_pipeline` in five steps. The lesson walks through the code for each; read it before writing the body. The signatures and field names below are the spec; the lesson shows how to fill them.

**Step 1: wrangle.** Call `artifact_adapter.load_artifacts(__file__)` to get `(wrangle_mod, eval_mod)`. Build a `WrangleConfig` from `wrangle_mod.WrangleConfig` pointing at `sample_corpus.jsonl`; set `output_path` to `outputs/clean.parquet`. Call `wrangle_mod.run(wrangle_config)`. Capture `stats.rows_out` as `n_clean`.

**Step 2: read the clean Parquet.** Call `pd.read_parquet(wrangle_config.output_path)` to recover the frame with `id` and `label`.

**Step 3: merge predictions with labels.** Read `sample_predictions.csv` (columns `id`, `prediction`). Merge with the clean frame on `id` (inner join) to produce a frame with columns `id`, `prediction`, `label`. Write it to `outputs/eval_input.csv`. This is the eval engine's input.

**Step 4: run the eval engine.** Build an `EvalConfig` from `eval_mod.EvalConfig` pointing at `outputs/eval_input.csv`; set `output_path` to `outputs/eval_report.md`. Call `eval_mod.run(eval_config)`. Capture the returned `list[ClassMetrics]` as `metrics`.

**Step 5: write the integrated report.** Build `outputs/report.md`. It must include:
- The dataset name and clean row count
- The per-class table (class, precision, recall, F1, support) for every class in `metrics`
- A macro-average row (mean of each column across classes)
- The headline finding: the weakest class by F1 and its score

Return:

```python
return ExamRun(
    report_path=str(pathlib.Path(config.output_dir) / "report.md"),
    n_clean=n_clean,
    metrics=metrics,
    composed_modules=["wrangle.py", "eval_engine.py"],
    version=config.version,
)
```

## The `if __name__ == "__main__":` Block

`default_config` is defined at module scope (see the shape above), anchored with `pathlib.Path(__file__).parent` so it points at the files in `exercises/module8/`. The block just calls `run_pipeline(default_config)`. On exit 0, print at minimum:

```
n_clean          : 10
composed_modules : ['wrangle.py', 'eval_engine.py']
report           : <path to outputs/report.md>
version          : 1.0
```

Anchoring `default_config` to `__file__` (not hardcoded strings) keeps `python pipeline.py` working from any working directory.

## Done When

`python exercises/module8/pipeline.py` (run from the repo root, or `python pipeline.py` from `exercises/module8/`) exits 0 and prints the four summary lines.

`outputs/report.md` exists and contains:
- A per-class table with at least the `precision`, `recall`, `f1`, and `support` columns
- A macro-average row
- The weakest class and its F1

A smoke check (the rubric and `smoke.py` are other lessons in this module; you will add to them there) confirms:

```
result.n_clean == 10
result.composed_modules == ["wrangle.py", "eval_engine.py"]
result.version == "1.0"
pathlib.Path(result.report_path).exists()
```

The pipeline must not contain any reimplementation of `WrangleConfig`, `run` (wrangle), `EvalConfig`, `ClassMetrics`, or `run` (eval): those belong to the artifacts. If you find yourself rewriting wrangle or eval logic inside `pipeline.py`, stop; you are solving the wrong problem.

## Stretch

Add a column-presence assertion after the merge step: confirm the merged frame has exactly the columns `["id", "prediction", "label"]` before writing it to CSV. If `sample_predictions.csv` is missing an `id` column, the merge produces empty output silently; the assertion turns that into a loud failure at the right place.

Then confirm the weakest class in the headline finding is not tied: if two classes share the minimum F1, pick the one with the lower support. Document the tiebreak in a comment.
