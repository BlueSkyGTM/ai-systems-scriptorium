# The Rubric

The rubric is code, not prose. You cannot talk your way past it.

A write-up claims the pipeline passed every gate. The rubric checks. Five criteria, each falsifiable, each enforced by inspecting the artifact on disk. If the eval gate never ran, criterion three fails. Rewording the README changes nothing.

The grading instrument opens with its contract:

```python
"""rubric.py — the Module 8 grader, expressed in code.

A rubric in prose can be argued with. A rubric in code cannot: it reads the pipeline's
manifest and scores five criteria, then exits READY (0) or NEEDS WORK (1).

    1. data curated       - duplicates were removed and the split is disjoint
    2. model trained      - training accuracy cleared the floor
    3. eval gate enforced - the eval gate actually ran and passed
    4. regression enforced- every pinned golden case passed
    5. artifact logged    - the manifest was written
"""
```

Each criterion names a concrete fact in the manifest: a deduped dataset, a training accuracy above the floor, a PASS record from the eval gate, a PASS record from the regression suite, a written manifest. None of them ask whether the write-up sounds convincing.

The criteria are a dict, not a feeling:

```python
criteria = {
    "data_curated":        bool(curated.get("dupes_removed", 0) > 0 and curated.get("disjoint")),
    "model_trained":       bool(trained.get("train_acc", 0.0) >= TRAIN_ACC_FLOOR),
    "eval_gate_enforced":  bool(eval_s is not None and eval_s.get("passed")),
    "regression_enforced": bool(regress is not None and regress.get("passed")),
    "artifact_logged":     bool(manifest.get("logged")),
}
```

The thresholds the pipeline must meet are pinned in code:

```python
TRAIN_ACC_FLOOR = 0.80   # rubric.py: training accuracy must clear this
MARGIN_PP = 0.05         # m5_eval.py: beat the baseline by >= 5pp on both metrics
```

The exit is binary. Zero means every criterion passed. One means at least one failed. There is no partial credit.

The proof that the rubric cannot be gamed lives in smoke.py. Two scenarios, both asserted:

```python
Proves the composition and the grader, in both directions:
  1. Full pipeline run: every stage produces its summary; the manifest is written.
  2. rubric.py grades that run READY (all five criteria pass).
  3. Deficient run (eval gate skipped): the pipeline still completes...
  4. ...but rubric.py grades it NEEDS WORK, tripping exactly the eval-gate criterion.
```

The deficient path is the falsification test. Skip the eval gate, run the rubric, watch the `eval_gate_enforced` criterion fail. The rubric does not read your explanation for why you skipped it. It checks the manifest. No PASS record, no pass.

## Core Concepts

1. The rubric grades the artifact, not the write-up; each criterion inspects files on disk or rows in sqlite.
2. Five criteria, each falsifiable: data curated, model trained, eval gate enforced, regression enforced, artifact logged.
3. The exit is binary: 0 (READY) requires all five to pass; 1 (NEEDS WORK) means at least one failed.
4. The deficient-run test in smoke.py proves the rubric catches a skipped eval gate by asserting exit 1.

<div class="claude-handoff" data-exercise="exercises/module8/the-rubric/">
**Build It in Claude Code** · Exercise · exercises/module8/the-rubric/
</div>

The moment a rubric accepts prose as evidence, it stops being a rubric; a Production AI Engineer makes the verdict unfakeable by putting the evaluator in code.