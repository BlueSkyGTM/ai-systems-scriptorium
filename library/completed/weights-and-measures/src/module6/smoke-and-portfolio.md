# Smoke and Portfolio

The smoke test does not test the model; it tests that the artifact behaves like an artifact. Every assertion in `smoke.py` is a claim your portfolio makes about itself, and the write-up in `outputs/skill-classifier.md` translates that contract for an interviewer.

## The Smoke Contract

Your smoke test has two sides: a happy path and a negative case.

The happy path proves the loop runs end to end:

- Run `train.py` on a 300-sample fixture
- Run `eval.py` on the 120-sample held-out fixture
- All 20 assertions pass in a few seconds on CPU
- Fixed random seeds

The negative case is the assertion most candidates skip:

- Test the negative case: untrained model must fail the gate
- Exit 0 on all assertions including the negative case

Feed an untrained model into the gate. It cannot beat the majority-class baseline by five points, so `eval.py` exits non-zero. Your smoke test catches that exit code and counts it as a pass. The artifact must fail when it should fail. That is the contract.

## The Portfolio Translation

The write-up turns those assertions into a story. Open `outputs/skill-classifier.md` and you find a structured stub:

```markdown
# Skill Classifier: Tuned vs. Baseline

**Artifact:** 5-class support-ticket classifier with a reproducible eval gate.
**Status:** Stub. Fill in the bracketed sections after your first green `python smoke.py` run.
**Module:** M6, Artifact: Tuned Classifier with Eval Gate (`Weights and Measures`).
```

Section 1 frames the business cost before any result appears:

```markdown
## 1. Problem Statement

Customer support tickets arrive untagged into a shared inbox. Routing them by hand
costs roughly 30 seconds per ticket and misroutes about 1 in 8. The goal of this
artifact is to ship a **tiny, auditable classifier** that:

1. Beats a naive majority-class baseline by a meaningful margin (at least 5pp on both
   exact-match accuracy and macro-F1).
2. Refuses to ship if it can't prove it: the eval script exits non-zero and blocks
   downstream pipelines.
3. Runs end-to-end on a laptop CPU in seconds, so the whole loop
   (train, eval, gate) fits inside a CI step.
```

Each bracketed TODO in the stub maps to a smoke assertion. You fill them in after a green run, not before. The write-up is evidence, not aspiration.

## Run Both Layers

Run the smoke test, then the pytest suite:

```
python smoke.py && python -m pytest tests/ -v
```

The smoke test covers the end-to-end loop. The pytest suite in `tests/test_classifier.py` is a focused subset of those assertions, checking individual components: model forward pass, dataset loading, gate logic, seed reproducibility. Together they give two independent signals that the artifact holds.

The directory structure mirrors the contract:

```
module6-classifier/
├── train.py                  # Fine-tune a tiny text classifier -> outputs/checkpoint.pt
├── eval.py                   # Gated eval: tuned vs. majority-class baseline
├── smoke.py                  # End-to-end smoke test (incl. negative case)
├── tests/
│   └── test_classifier.py    # pytest subset of the smoke assertions
├── outputs/                  # checkpoint.pt, train.jsonl, test.jsonl, mlruns.db
│   └── skill-classifier.md   # portfolio write-up
└── README.md
```

## Same Pattern, Different Domain

This artifact pattern, train then gate then write-up, is the same one you build in Module 6: Just Python. The domain shifts; the contract does not. A smoke test always asserts both directions: the artifact succeeds when it should, and it fails when it must.

## Core Concepts

1. A smoke test asserts artifact behavior, not model quality; the happy path proves the loop runs and the negative path proves the gate blocks an untrained model.
2. The portfolio write-up is a structured translation of the smoke contract; every TODO maps to an assertion that already passed.
3. The negative case is mandatory: if an untrained model does not trigger a non-zero exit from the gate, the smoke test itself fails.
4. Run the smoke test and pytest suite together to get both the end-to-end signal and the component-level signal in one command.

<div class="claude-handoff" data-exercise="exercises/module6/smoke-and-portfolio/">
**Build It in Claude Code** · Exercise · exercises/module6/smoke-and-portfolio/
</div>

The question every interviewer asks is "how do you know it ships clean?"; a Production AI Engineer answers with a smoke test that fails on purpose and a write-up that fills in only after the gate passes.