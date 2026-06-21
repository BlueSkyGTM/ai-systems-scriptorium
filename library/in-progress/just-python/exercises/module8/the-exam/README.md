# Exercise: The Exam Inputs

**Goal:** Create the two input files the M8 exam pipeline will consume: a raw JSONL corpus and a locked CSV of model predictions. Then write a brief in your own words describing the task.

**Why:** A reproducible pipeline needs deterministic inputs. The hiring manager who clones your repo and runs `python smoke.py` sees one of two things: a pipeline that works on a fixed, versioned corpus, or one that requires you to stand next to it and explain. Your job here is to create the inputs that make the first thing true.

## The Business Problem

A three-class text classifier has been run in batch over a corpus of short product descriptions. The predictions are in a CSV. The corpus is in JSONL. Neither file is clean: the corpus has a duplicate record and a row with a null label. Before any metric is computed, `wrangle.py` must scrub the corpus; then `eval_engine.py` judges the predictions against the surviving rows.

This exercise creates those two files and a brief that names the task. The pipeline that consumes them is Lesson 2's job. You are building the inputs the pipeline will run against.

## The Two Files to Create

Create both files inside `exercises/module8/`:

### `sample_corpus.jsonl`

Twelve raw rows, one JSON object per line, schema `{"id": int, "text": str, "label": str or null}`. The rows are the locked oracle; do not alter `id` or `label` values or the rubric's row-count assertion will fail.

```
{"id": 1, "text": "purrs constantly, very affectionate", "label": "cat"}
{"id": 2, "text": "fetches the ball every single time", "label": "dog"}
{"id": 3, "text": "loud bark, loves the park", "label": "dog"}
{"id": 4, "text": "bright feathers, perches on shoulder", "label": "bird"}
{"id": 5, "text": "kneads blankets and sleeps all day", "label": "cat"}
{"id": 6, "text": "sits in the sun and grooms itself", "label": "cat"}
{"id": 7, "text": "repeats words and mimics whistles", "label": "bird"}
{"id": 8, "text": "tail wagging, greets you at the door", "label": "dog"}
{"id": 9, "text": "hides under furniture when startled", "label": "cat"}
{"id": 10, "text": "gnaws the leash, digs in the yard", "label": "dog"}
{"id": 3, "text": "loud bark, loves the park", "label": "dog"}
{"id": 11, "text": "prefers heights, watches from above", "label": null}
```

Row 11 in the file (the second `id: 3`) is an exact duplicate of row 3. `wrangle.py` drops it on `id`. Row 12 (id 11) carries a null label; `wrangle.py` drops it on `dropna`. Net: 12 rows in, 10 clean rows out.

### `sample_predictions.csv`

Ten rows of locked predictions, header `id,prediction`, one row per surviving corpus record. These are the model's outputs before you know how well it did; the rubric tells you after.

```
id,prediction
1,cat
2,cat
3,dog
4,bird
5,cat
6,dog
7,bird
8,dog
9,cat
10,bird
```

Do not alter these values. The rubric asserts a specific per-class outcome: dog recall of 0.500 (the weakest class), and the checker will fail R3 (METRICS-CORRECT) if the predictions shift.

### `exam_brief.md`

Write a brief in your own words, one or two paragraphs, covering:

- What the task is: chain `wrangle.py` and `eval_engine.py`, compose, do not rebuild.
- What the two inputs are and what each one contributes.
- The "compose, do not rebuild" rule, stated plainly.
- The six acceptance criteria by name: RUNS, SCHEMA-VALID, METRICS-CORRECT, COMPOSED, PROBLEM-FRAMED, TESTED+VERSIONED.
- The expected headline finding: dog is the weakest class, recall 0.500.

The brief is for you, not for the rubric. Write it as if you are handing the task to a colleague who has not read the lesson. If you cannot state the compose rule and the six criteria without looking, write the brief again.

## What the Clean Pass Looks Like

After `wrangle.py` runs on `sample_corpus.jsonl`:

- 12 rows in.
- Drop 1 duplicate (`id: 3` appears twice; the second copy goes).
- Drop 1 null-label row (`id: 11`).
- 10 rows survive.

Those 10 rows match the 10 prediction rows in `sample_predictions.csv` by `id`. That alignment is not coincidence; it is the contract between the wrangler and the eval engine.

## Done When

Both data files exist and parse without error. Verify with:

```sh
python -c "
import json, csv, pathlib

corpus = pathlib.Path('exercises/module8/sample_corpus.jsonl').read_text().strip().splitlines()
assert len(corpus) == 12, f'Expected 12 corpus lines, got {len(corpus)}'
for line in corpus:
    json.loads(line)  # every line parses

with open('exercises/module8/sample_predictions.csv') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 10, f'Expected 10 prediction rows, got {len(rows)}'

print('[PASS] sample_corpus.jsonl: 12 lines, all valid JSON')
print('[PASS] sample_predictions.csv: 10 data rows')
"
```

`exam_brief.md` exists and names all six criteria and the expected headline finding.

## What Comes Next

Lesson 2 wires `wrangle.py` and `eval_engine.py` into `pipeline.py`, using the files you created here as inputs. Lesson 3 authors the rubric checker. Your inputs are the contract both depend on; do not move or rename the files after this exercise.
