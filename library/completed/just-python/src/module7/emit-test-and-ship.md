# Emit, Test, and Ship

Accuracy 0.8 is a number that hides things. The class your model never gets right still drags that number up if the other classes are large enough. The evaluation engine is done when `run` composes the stages into a per-class Markdown report, and a `pytest` gate proves the numbers, including the case the engine must refuse.

## What You Build

You build `run`, the composer that wires the four stages into a single callable; the `if __name__ == "__main__":` block that writes the report and exits 0; a `smoke.py` pytest gate with a happy path and a negative case; and `outputs/skill-evaluation-engine.md`, the write-up that turns the artifact into a portfolio piece.

## The run Composer

The earlier lessons gave you the pieces. `load_predictions` reads the CSV. `per_class_metrics` slices by class and returns a `list[ClassMetrics]`. `to_markdown_table` formats that list as a Markdown table. `run` chains them in order and writes the report to disk.

```python
def run(config: EvalConfig) -> list[ClassMetrics]:
    df = load_predictions(config.input_path, config)
    metrics = per_class_metrics(df, config)
    report = to_markdown_table(metrics)
    pathlib.Path(config.output_path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(config.output_path).write_text(report, encoding="utf-8")
    return metrics
```

`run` does not recompute anything the earlier stages own. It loads, computes, formats, writes. The earlier stages are given; `run` trusts them.

The return value matters. A function that writes a file and returns nothing forces a caller to re-read the file to inspect the result. Returning `list[ClassMetrics]` lets `smoke.py` assert the numbers directly, without touching the filesystem again.

## The main Block

The `if __name__ == "__main__":` block wires the engine to a default config and runs it. This is the real entry point: `python eval_engine.py` should exit 0 and write the report.

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

The print loop gives you a human-readable summary in the terminal and confirms the engine ran without opening the output file.

## The Per-Class Table: What Goes in a Model Card

The report `run` writes is a Markdown table of per-class precision, recall, F1, and support. That is the artifact a reviewer reads before a PR merges and the first table in any model card that follows responsible AI practice.

Azure AI Language Services defines class-level evaluation this way: precision measures how many of the predicted classes are correctly labeled; recall measures how many of the actual class instances were found; F1 balances the two ([learn.microsoft.com/azure/ai-services/language-service/custom-text-classification/concepts/evaluation-metrics](https://learn.microsoft.com/azure/ai-services/language-service/custom-text-classification/concepts/evaluation-metrics)). The per-class breakdown is the form that surfaces the failing class. A macro-averaged F1 of 0.707 on the sample data masks the fact that `dog` has an F1 of 0.571: support 4, precision 0.667, recall 0.500. That class is underperforming. Accuracy alone would not tell you which one.

The table produced by `to_markdown_table` for the locked sample looks like this:

| class | precision | recall | f1 | support |
|---|---|---|---|---|
| bird | 0.667 | 1.000 | 0.800 | 2 |
| cat | 0.750 | 0.750 | 0.750 | 4 |
| dog | 0.667 | 0.500 | 0.571 | 4 |
| **macro avg** | **0.694** | **0.750** | **0.707** | **10** |

That table is what `smoke.py` asserts. It is also what a teammate reads in a PR before a model ships.

## The Smoke Test

A smoke test answers one question: does the engine produce the right numbers without catching fire? Two test functions cover both directions.

`test_engine_happy_path` runs the engine on `predictions.csv` and asserts the locked per-class P/R/F1 to a tolerance of 0.001, confirms the output `.md` file was written, and confirms it contains the class names.

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

The tolerance is 0.001, not an equality check on floats. Floating-point division across different Python versions can produce results like `0.6666666666666667`; asserting `== 0.667` fails. Asserting within 0.001 of a three-decimal target is the production pattern.

`test_engine_negative_case` proves the engine rejects a predictions file that is missing the `label` column. The engine must raise; the gate must fire.

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

`pytest.raises(Exception)` rather than a specific subclass: `load_predictions` is a given, and its exact exception type is an implementation detail you did not write. The test proves the gate fires.

## The README and the Skill Write-Up

The exercise README frames the business problem before the code. The opening paragraph explains why accuracy hides the failing class and why a per-class report is the artifact that tells the truth. That framing is the STANDARDS Part 2 "README frames the business problem" criterion: it answers "why does this exist" before "what does it do."

`outputs/skill-evaluation-engine.md` is the portfolio surface. It documents what the engine does, the business problem it solves, the lineage back to M3's `groupby`-based per-class accuracy work, and how to run it. The write-up is not filler; it is the translation layer between a script and a hire.

## The Standards Check

| Criterion | Where it lives |
|---|---|
| Real entry point | `python eval_engine.py` runs the engine and exits 0 |
| README frames the business problem | `exercises/module7/emit-test-and-ship/README.md` opens with the accuracy-hiding-the-failing-class problem |
| Machine-checkable acceptance gate | `pytest smoke.py` passes both tests; `python eval_engine.py` exits 0 |
| The negative case is tested | `test_engine_negative_case` asserts a malformed predictions file raises |
| Versioned, clean layout; no secrets | report goes to `outputs/`; no keys; no committed credentials |
| Ships a skill artifact | `outputs/skill-evaluation-engine.md` is a required output |

The gate is green when `python eval_engine.py` exits 0, writes `outputs/evaluation-report.md`, and `pytest smoke.py` reports two tests passed.

The difference between an evaluation script and an evaluation engine is not the code; it is the gate. A script runs on good input. An engine proves it runs on good input and rejects the bad.

## Core Concepts

- `run` is the composer: it calls `load_predictions`, `per_class_metrics`, and `to_markdown_table` in sequence, writes the report to `config.output_path`, and returns `list[ClassMetrics]` so callers can assert the numbers without re-reading the file.
- Per-class precision, recall, and F1 are the table a model card requires; macro-averaged accuracy hides the class the model cannot predict, and that hidden class is the one that fails in production.
- A smoke test earns its name with two functions: the happy path locks the expected numbers; the negative case proves the engine rejects a malformed input, which is what separates a gate from a script.
- Float comparisons in tests use a tolerance (`abs(result - expected) < 0.001`), not equality; floating-point division across environments is not exact.

<div class="claude-handoff" data-exercise="exercises/module7/emit-test-and-ship/">

**Build It in Claude Code:** Finish `exercises/module7/eval_engine.py` by adding `run` and the `if __name__ == "__main__":` block; write `smoke.py` with the happy-path and negative-case tests; and fill out `outputs/skill-evaluation-engine.md`. The gate is green when `python eval_engine.py` exits 0, writes the Markdown report, and `pytest smoke.py` passes both tests.

</div>
