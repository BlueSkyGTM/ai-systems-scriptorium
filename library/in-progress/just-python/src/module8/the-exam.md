# The Exam

Module 6 cleaned a corpus and shipped `wrangle.py`. Module 7 judged a model and shipped `eval_engine.py`. The final exam chains both into one graded pipeline: two inputs in, one machine-graded report out.

## What This Module Covers

The capstone is not a new build. The rule of the exam is simple enough to state twice so you cannot miss it: compose the artifacts you already built; do not rebuild them. You write one driver script that calls `wrangle.py` then hands the clean output to `eval_engine.py`, and a rubric checker grades the result against six acceptance criteria in code, not opinion.

## Arc of Lessons

| Lesson | Title | What You Do |
|--------|-------|-------------|
| 1 | The Exam | Understand what the exam is and why this is the take-home that matters |
| 2 | Compose the Pipeline | Wire `wrangle.py` and `eval_engine.py` into a single `pipeline.py` driver |
| 3 | The Rubric and Grading | Author `rubric.py`, the six-criterion acceptance checker |
| 4 | Run, Test, and Ship | Build the smoke gate, ship the skill write-up, complete the book |

## What the Exam Is

You are handed two files: a raw JSONL corpus and a CSV of batch model predictions. The corpus goes through `wrangle.py` (the M6 artifact): it deduplicates on `id`, drops null labels, and normalizes text. The clean frame feeds `eval_engine.py` (the M7 artifact): it computes per-class precision, recall, and F1 and renders a Markdown report. The rubric checker grades the combined run.

The result is one GitHub repo with three runnable scripts and a graded report. That is the take-home a hiring manager runs: `python smoke.py`, green gate, per-class metrics, done. No notebook, no manual steps, no "it worked on my machine" disclaimer.

## Why This Is the Take-Home That Matters

A single accuracy number hides which class a model fails. Any engineer can compute `correct / total`. The engineer who composes a wrangler and an eval engine into a reproducible, tested pipeline, then grades the output per class with a rubric expressed in code, is showing something a number cannot: she built the infrastructure, not the result alone.

The Sans Python M8 capstone drew the same distinction from the other side: the fleet builds software, you operate and judge it. Here the pipeline runs data; you compose and grade it. The shape is the same: reuse the artifacts, apply the rubric, let the code decide pass or fail ([learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment](https://learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment?view=azureml-api-2)).

## The Six Acceptance Criteria

The rubric checker in Lesson 3 grades against these six, one verdict per criterion:

| # | Criterion | Passes When |
|---|-----------|-------------|
| R1 | RUNS | the pipeline runs end to end and writes `report.md` |
| R2 | SCHEMA-VALID | `wrangle.py` drops the duplicate and the null; 10 rows survive |
| R3 | METRICS-CORRECT | per-class precision, recall, and F1 match the locked oracle |
| R4 | COMPOSED | the run imports `wrangle.py` and `eval_engine.py` off disk; nothing rebuilt |
| R5 | PROBLEM-FRAMED | the report names the dataset, the metric, and the weakest class |
| R6 | TESTED+VERSIONED | the run declares a version; the smoke gate proves the negative case |

The rubric in the guide and the rubric in the checker are one specification in two forms. They must match: a criterion that passes in code but is missing from the prose, or documented but not checked, is not a criterion; it is a comment. Data quality failures that reach an eval engine are silent multipliers: a duplicate that passes the clean gate inflates a class count; a null label that slips through breaks a per-class metric ([learn.microsoft.com/fabric/data-science/semantic-link-validate-data](https://learn.microsoft.com/fabric/data-science/semantic-link-validate-data)).

## The Lineage

`wrangle.py` and `eval_engine.py` are not prerequisites you happened to build on the way here. They are the exam inputs. The compounding has been real: M6's clean-and-deduplicate decision determines which rows the M7 eval engine sees; M7's per-class metric math determines what the M8 rubric can grade. You cannot compose artifacts you do not have on disk, which is why the exam begins only after both are shipped and passing their own gates.

The exam is not the summit of a mountain you sprint up at the end. It is the node where the three prior portfolio artifacts connect; and the proof that a pipeline is only as honest as the data that flows through it.

## Core Concepts

- The final exam composes `wrangle.py` and `eval_engine.py` from disk; rewriting either is a sign of misreading the task, and the rubric will flag it.
- Six acceptance criteria, expressed both in prose and in `rubric.py`, define done; a criterion documented but not checked in code is not a criterion.
- Data quality failures compound silently: a duplicate the clean stage misses inflates a metric; a null label it misses breaks one; the wrangler is the gate that makes the eval trustworthy.
- One GitHub repo, three runnable scripts, and a graded Markdown report is the artifact a hiring manager runs; that is what this pipeline produces.

<div class="claude-handoff" data-exercise="exercises/module8/the-exam/">

**Build It in Claude Code:** Create the two exam input files that the pipeline will consume. Open the exercise for this lesson, read the brief, and create `sample_corpus.jsonl` (12 raw rows) and `sample_predictions.csv` (10 locked prediction rows) exactly as specified. Then write `exam_brief.md` describing the task in your own words. Acceptance check: both data files parse without error, `sample_corpus.jsonl` has 12 lines, `sample_predictions.csv` has 10 data rows.

</div>
