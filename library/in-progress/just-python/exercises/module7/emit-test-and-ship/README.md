# Exercise: Emit, Test, and Ship

A model that scores 0.8 accuracy on a three-class problem can still fail completely on one of those classes. If the failing class has low support, the 0.2 error spreads across the other two classes and the aggregate number looks acceptable. The per-class evaluation table is what tells the truth: it shows, class by class, exactly where the model is losing. This artifact builds the evaluation engine that produces that table as a Markdown report, proves the numbers with a `pytest` gate, and ships the skill write-up that makes the work legible to a reviewer.

**Goal:** Finish `exercises/module7/eval_engine.py` by adding `run` and the `if __name__ == "__main__":` block; write `exercises/module7/smoke.py` with a happy-path test and a negative-case test; and fill in `exercises/module7/outputs/skill-evaluation-engine.md`. The gate is green when `python eval_engine.py` exits 0 and writes the Markdown report, and `pytest smoke.py` passes both tests.

**Why:** The per-class table is what goes in a model card and in a PR before a model ships. Building the engine that produces it, and proving it with a gate, is the difference between a script that runs and an artifact that is trusted.

## Before You Touch Code

Read the lesson at `src/module7/emit-test-and-ship.md`. Then open `exercises/module7/eval_engine.py` and read its current state. It already contains:

- `EvalConfig` (frozen dataclass: `input_path`, `output_path`, `pred_col="prediction"`, `label_col="label"`)
- `load_predictions(path, config) -> pd.DataFrame` (L1: loads the CSV and validates it has the required columns)
- `confusion_counts(df, cls, config) -> tuple[int, int, int]` (L2: returns TP, FP, FN for a single class)
- `ClassMetrics` (dataclass: `cls`, `precision`, `recall`, `f1`, `support`) (L3)
- `per_class_metrics(df, config) -> list[ClassMetrics]` (L3: calls `confusion_counts` for each class and returns the list)
- `to_markdown_table(metrics) -> str` (L3: formats `list[ClassMetrics]` as a Markdown table with a macro-avg row)
- The locked predictions CSV at `exercises/module7/predictions.csv` (10 rows, built in L1)

You are adding `run` and `main` to `eval_engine.py`. Read the file before adding anything.

## The Locked Sample and Expected Numbers

`predictions.csv` has 10 rows: `id`, `prediction`, `label`. The locked expected metrics are:

| class | precision | recall | f1 | support |
|---|---|---|---|---|
| cat | 0.750 | 0.750 | 0.750 | 4 |
| dog | 0.667 | 0.500 | 0.571 | 4 |
| bird | 0.667 | 1.000 | 0.800 | 2 |
| macro avg | 0.694 | 0.750 | 0.707 | 10 |

Your `smoke.py` asserts these numbers to a tolerance of 0.001.

## Steps

### 1. Add run

`run` wires the given stages in sequence, writes the report, and returns the metrics list. Add it as a module-level function after the existing stages.

```python
def run(config: EvalConfig) -> list[ClassMetrics]:
    df = load_predictions(config.input_path, config)
    metrics = per_class_metrics(df, config)
    report = to_markdown_table(metrics)
    pathlib.Path(config.output_path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(config.output_path).write_text(report, encoding="utf-8")
    return metrics
```

`run` does not recompute or reimplement anything the given stages own. It composes.

### 2. Add main

Add an `if __name__ == "__main__":` block that runs the engine with a default config pointing at `predictions.csv` and prints the per-class summary to the terminal.

```python
if __name__ == "__main__":
    import pathlib as _pathlib

    _here = _pathlib.Path(__file__).parent
    default_config = EvalConfig(
        input_path=str(_here / "predictions.csv"),
        output_path=str(_here / "outputs" / "evaluation-report.md"),
    )
    metrics = run(default_config)
    for m in metrics:
        print(f"{m.cls}: P={m.precision:.3f} R={m.recall:.3f} F1={m.f1:.3f} (n={m.support})")
```

Running `python eval_engine.py` from `exercises/module7/` should exit 0, print one line per class, and write `outputs/evaluation-report.md`.

### 3. Write smoke.py

Create `exercises/module7/smoke.py`. It must be runnable as:

```
python -m pytest exercises/module7/smoke.py -v
```

from the repo root, or as `python smoke.py` from `exercises/module7/`.

**Test 1: happy path**

```python
import pytest
import pathlib
import sys

_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE))

from eval_engine import EvalConfig, run

PRED_PATH = str(_HERE / "predictions.csv")

def test_engine_happy_path(tmp_path):
    config = EvalConfig(
        input_path=PRED_PATH,
        output_path=str(tmp_path / "report.md"),
    )
    metrics = run(config)
    by_class = {m.cls: m for m in metrics}

    # cat: P=0.750 R=0.750 F1=0.750 support=4
    assert abs(by_class["cat"].precision - 0.750) < 0.001
    assert abs(by_class["cat"].recall    - 0.750) < 0.001
    assert abs(by_class["cat"].f1        - 0.750) < 0.001
    assert by_class["cat"].support == 4

    # dog: P=0.667 R=0.500 F1=0.571 support=4
    assert abs(by_class["dog"].precision - 0.667) < 0.001
    assert abs(by_class["dog"].recall    - 0.500) < 0.001
    assert abs(by_class["dog"].f1        - 0.571) < 0.001
    assert by_class["dog"].support == 4

    # bird: P=0.667 R=1.000 F1=0.800 support=2
    assert abs(by_class["bird"].precision - 0.667) < 0.001
    assert abs(by_class["bird"].recall    - 1.000) < 0.001
    assert abs(by_class["bird"].f1        - 0.800) < 0.001
    assert by_class["bird"].support == 2

    # output file was written and contains class names
    report_path = pathlib.Path(config.output_path)
    assert report_path.exists(), "report .md was not written"
    report_text = report_path.read_text(encoding="utf-8")
    for cls in ("cat", "dog", "bird"):
        assert cls in report_text, f"class '{cls}' missing from report"
```

Use a tolerance of 0.001, not equality. Floating-point division is not exact across environments.

**Test 2: negative case**

```python
def test_engine_negative_case(tmp_path):
    """A predictions file missing the label column must make run raise."""
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text(
        "prediction\ncat\ndog\nbird\n",
        encoding="utf-8",
    )
    bad_config = EvalConfig(
        input_path=str(bad_csv),
        output_path=str(tmp_path / "report.md"),
    )
    with pytest.raises(Exception):
        run(bad_config)
```

Use `pytest.raises(Exception)` rather than a specific subclass. The exception type is an implementation detail of `load_predictions`, which is a given stage you did not write. The test proves the gate fires.

### 4. Write outputs/skill-evaluation-engine.md

Create `exercises/module7/outputs/skill-evaluation-engine.md`. The `outputs/` directory may not exist; create it.

Use this template. Fill in the bracketed sections with your own answers after you run the engine.

```markdown
# Skill: Evaluation Engine

## What I Built

`eval_engine.py` is a four-stage evaluation pipeline: `load_predictions` reads
a CSV of model predictions and ground-truth labels; `confusion_counts` computes
TP, FP, and FN for a single class; `per_class_metrics` assembles a
`list[ClassMetrics]` across all classes; and `to_markdown_table` formats the
result as a Markdown table with a macro-avg row. `run` composes all four stages,
writes the report to `config.output_path`, and returns the metrics list.

## The Business Problem

[Describe in 2–3 sentences: why accuracy alone is not enough, what a failing class
looks like in the per-class table, and how this engine surfaces it.]

## Lineage

The per-class groupby logic in this module extends the M3 `groupby-merge-apply`
pattern: M3 built per-class accuracy via `groupby + agg`; M7 builds precision,
recall, and F1 from the confusion counts directly. The evaluation table this
engine writes is the same artifact a model card or a PR reviewer would read.

## What I Learned

[2–3 bullet points: one about composing stages with a return value vs. side
effects only; one about float tolerance in pytest; one about what the per-class
table reveals that accuracy hides.]

## How to Run It

```
cd exercises/module7
python eval_engine.py          # runs the engine; exits 0; writes outputs/evaluation-report.md
python -m pytest smoke.py -v   # runs both tests; must pass
```

## Skills Demonstrated

- Per-class evaluation metrics: precision, recall, F1, support (no sklearn)
- Composing a multi-stage pipeline with a typed return value (list[ClassMetrics])
- Pytest smoke testing: locked-metric happy path + negative-case gate
- Markdown report generation for model cards and PR review
- Dataclasses as typed intermediate results (M5 pattern applied at M7 scale)
```

## Done When

`python eval_engine.py` exits 0, prints one line per class, and writes `outputs/evaluation-report.md`.

`python -m pytest exercises/module7/smoke.py -v` (from the repo root) reports:

```
PASSED  smoke.py::test_engine_happy_path
PASSED  smoke.py::test_engine_negative_case
2 passed
```

`test_engine_happy_path` asserts the locked per-class P/R/F1 for `cat`, `dog`, and `bird` to a tolerance of 0.001, confirms the `outputs/` report was written, and confirms it contains each class name.

`test_engine_negative_case` confirms that a predictions file missing the `label` column makes the engine raise.

No external dependencies beyond `pandas` and `numpy`. No `sklearn`, no `pyarrow` needed. Toleranced float assertions are the production pattern for numeric smoke tests.

## Expected Output (python eval_engine.py)

```
cat:  P=0.750 R=0.750 F1=0.750 (n=4)
dog:  P=0.667 R=0.500 F1=0.571 (n=4)
bird: P=0.667 R=1.000 F1=0.800 (n=2)
```

The report lands at `exercises/module7/outputs/evaluation-report.md`.

## Stretch

Add a third assertion to `test_engine_happy_path`: compute the macro-average F1 from the returned `metrics` list yourself (sum the F1 values, divide by the class count) and assert it is within 0.001 of 0.707. This tests that your derivation matches the locked expected value and documents the macro-avg formula in code.

Then add a second negative case: a predictions file where the `prediction` column name is misspelled as `pred`. Assert that `run` raises when the column the config names as `pred_col` is absent. This tests that `EvalConfig`'s `pred_col` field is actually enforced by `load_predictions`, not silently ignored.
