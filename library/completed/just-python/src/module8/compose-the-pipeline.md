# Compose the Pipeline

Your M6 wrangler and your M7 eval engine live in sibling directories. The capstone does not copy them; it imports them off disk and chains them.

## What You Build

You build `artifact_adapter.py`, which loads `wrangle.py` and `eval_engine.py` by file path using `importlib`, and `pipeline.py`, which calls them in sequence and returns a typed `ExamRun` that the rubric grades. The pipeline never re-implements what the earlier artifacts own.

## Why Off-Disk Import

A direct `import wrangle` only works if `wrangle.py` is on `sys.path`. Your M6 artifact lives at `exercises/module6/wrangle.py`, and your M7 artifact lives at `exercises/module7/eval_engine.py`: sibling directories that the exam must not restructure. `importlib.util.spec_from_file_location` imports a module from an absolute path, no `sys.path` surgery required. This is the same move Sans Python M8 made with `fleet_adapter.py`: the exam proves the composition is real because it cannot run without the real artifact. Rebuilding `wrangle` inside the exam would pass silently even if your M6 work were broken.

## The Adapter

`artifact_adapter.py` resolves both paths relative to `pipeline.py`'s location and returns the two imported modules as a tuple.

```python
# artifact_adapter.py
import importlib.util
import pathlib
import sys


def _load_module(name: str, path: pathlib.Path):
    """Load a Python module from an absolute file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Register before exec so the module's own dataclasses and type hints
    # resolve: Python looks the module up in sys.modules by name during exec.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_artifacts(pipeline_file: str):
    """Return (wrangle_module, eval_engine_module) loaded off disk.

    Resolution is anchored to the pipeline file so the paths stay
    correct regardless of where the caller runs from.
    """
    here = pathlib.Path(pipeline_file).parent
    wrangle = _load_module(
        "wrangle",
        (here / ".." / "module6" / "wrangle.py").resolve(),
    )
    eval_engine = _load_module(
        "eval_engine",
        (here / ".." / "module7" / "eval_engine.py").resolve(),
    )
    return wrangle, eval_engine
```

`spec_from_file_location` takes a name (used for the module's `__name__`) and an absolute path. `.resolve()` collapses the `..` segments so the path is unambiguous; the sibling exercise dirs `module6/` and `module7/` sit one level up from `module8/`. Registering the module in `sys.modules` before `exec_module` is not optional: a frozen dataclass resolves its own annotations by looking its module up by name, and an unregistered module fails with a `NoneType` error at import. If either file is missing, the import fails immediately with a clear error rather than a silent `AttributeError` three calls later.

## The Pipeline Shape

`pipeline.py` declares one result dataclass and one entry function. The shape is locked; the rubric reads the field names directly.

```python
# pipeline.py (shape; your task is to fill the body)
import pathlib
from dataclasses import dataclass

import pandas as pd

import artifact_adapter


@dataclass(frozen=True)
class ExamConfig:
    corpus_path: str
    predictions_path: str
    output_dir: str
    version: str = "1.0"


@dataclass
class ExamRun:
    report_path: str
    n_clean: int
    metrics: list
    composed_modules: list
    version: str


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

`composed_modules` carries the proof: a list like `["wrangle.py", "eval_engine.py"]` shows that both modules were imported off disk, not reimplemented. The rubric checks this field. `default_config` lives at module scope, not inside `__main__`, so the smoke gate in lesson 4 can import it directly.

## The Data Flow

`run_pipeline` executes five steps in order. Each step uses only the contract the prior module already established.

**Step 1: wrangle the corpus.**
Build a `WrangleConfig` from the wrangle module and point it at `sample_corpus.jsonl`. Call `wrangle.run(wrangle_config)`. It returns a `WrangleStats`; capture `stats.rows_out`. On the locked sample this is 10.

```python
wrangle_mod, eval_mod = artifact_adapter.load_artifacts(__file__)

out = pathlib.Path(config.output_dir)
out.mkdir(parents=True, exist_ok=True)
clean_path = str(out / "clean.parquet")

WrangleConfig = wrangle_mod.WrangleConfig
wrangle_config = WrangleConfig(
    input_path=config.corpus_path,
    output_path=clean_path,
)
stats = wrangle_mod.run(wrangle_config)
n_clean = stats.rows_out          # 10 on the locked sample
```

**Step 2: read the clean Parquet.**
`wrangle.run` emits Parquet to `wrangle_config.output_path`. Read it back with `pd.read_parquet` to recover the `{id, label}` columns.

```python
import pandas as pd

clean_df = pd.read_parquet(clean_path)   # columns: id, text, label, score (wrangle keeps text)
```

**Step 3: merge predictions with labels.**
Read `sample_predictions.csv` (columns `id`, `prediction`). Merge on `id` with the clean frame to produce a frame with columns `id`, `prediction`, `label`. Write it to a temp CSV; this is the eval engine's input.

```python
preds = pd.read_csv(config.predictions_path)
eval_input = preds.merge(clean_df[["id", "label"]], on="id", how="inner")

tmp_csv = str(out / "eval_input.csv")
eval_input.to_csv(tmp_csv, index=False)
```

The merge is inner: any prediction without a clean label is dropped. This matches the M7 engine's expectation that every row has both columns.

**Step 4: run the eval engine.**
Build an `EvalConfig` from the eval module. Call `eval_mod.run(eval_config)`. It returns `list[ClassMetrics]`.

```python
EvalConfig = eval_mod.EvalConfig
eval_config = EvalConfig(
    input_path=tmp_csv,
    output_path=str(out / "eval_report.md"),
)
metrics = eval_mod.run(eval_config)   # list[ClassMetrics]
```

**Step 5: write the integrated report.**
The eval engine already writes a per-class table. The integrated report adds the dataset name, the metric name, the table, the macro-average row, and the headline finding: the weakest class by F1.

```python
weakest = min(metrics, key=lambda m: m.f1)

rows = "\n".join(
    f"| {m.cls} | {m.precision:.3f} | {m.recall:.3f} | {m.f1:.3f} | {m.support} |"
    for m in metrics
)
macro_p = sum(m.precision for m in metrics) / len(metrics)
macro_r = sum(m.recall    for m in metrics) / len(metrics)
macro_f = sum(m.f1        for m in metrics) / len(metrics)

report_md = f"""# Integrated Evaluation Report

**Dataset:** sample_corpus.jsonl ({n_clean} clean rows after wrangling)
**Metric:** per-class precision / recall / F1

| class | precision | recall | f1 | support |
|---|---|---|---|---|
{rows}
| **macro avg** | **{macro_p:.3f}** | **{macro_r:.3f}** | **{macro_f:.3f}** | **{n_clean}** |

**Headline finding:** `{weakest.cls}` is the weakest class (F1 = {weakest.f1:.3f}, recall = {weakest.recall:.3f}).
Review training support for `{weakest.cls}` before promoting this model.
"""

integrated_path = str(out / "report.md")
pathlib.Path(integrated_path).write_text(report_md, encoding="utf-8")
```

**Step 6: return `ExamRun`.**

```python
return ExamRun(
    report_path=integrated_path,
    n_clean=n_clean,
    metrics=metrics,
    composed_modules=["wrangle.py", "eval_engine.py"],
    version=config.version,
)
```

## The Integrated Report

The report names the dataset and the metric, shows the per-class table, the macro-average row, and states the weakest class. This is what goes in a model card before a model card has a model card section. On the locked sample data (10 clean rows, the prediction set from lesson 1's exercise), the weakest class will be the one with the lowest F1; the exact class depends on your `sample_predictions.csv`, so the pipeline computes it rather than hardcoding it.

Reproducible pipelines in Azure ML follow the same shape: data prep and scoring are separate, reusable steps whose outputs chain together ([learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment?view=azureml-api-2](https://learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment?view=azureml-api-2)). What you are building here is the same idea at exercise scale: each prior artifact is a reusable step, and the pipeline is the chain.

## The main Block

```python
if __name__ == "__main__":
    result = run_pipeline(default_config)
    print(f"n_clean          : {result.n_clean}")
    print(f"composed_modules : {result.composed_modules}")
    print(f"report           : {result.report_path}")
    print(f"version          : {result.version}")
```

`default_config` is already defined at module scope (above), so `run_pipeline(default_config)` here and `from pipeline import default_config` in the smoke gate both see the same object. `python pipeline.py` exits 0, prints the four summary lines, and writes `outputs/report.md`. That is the acceptance gate. No model call. No internet. The artifacts you already built do the work.

## Core Concepts

- `importlib.util.spec_from_file_location` imports a module from an absolute file path, with no `sys.path` manipulation; anchoring the path to `__file__` makes the resolution portable across machines.
- The capstone composes prior artifacts off disk rather than rebuilding them: if M6's wrangler is broken, the pipeline fails at import time, which is the correct failure, not a silent wrong answer.
- Merging predictions with clean labels on `id` is the join the eval engine requires: it produces the `{id, prediction, label}` frame that `EvalConfig` names its columns for.
- `ExamRun.composed_modules` is not metadata; it is proof: the rubric reads it to confirm both artifacts were imported, not reimplemented.

<div class="claude-handoff" data-exercise="exercises/module8/compose-the-pipeline/">

**Build It in Claude Code:** Build `exercises/module8/artifact_adapter.py` and `exercises/module8/pipeline.py` to the locked shape above. The gate is green when `python pipeline.py` exits 0, writes `outputs/report.md`, and a smoke check confirms `ExamRun.n_clean == 10` and `ExamRun.composed_modules == ["wrangle.py", "eval_engine.py"]`.

</div>
