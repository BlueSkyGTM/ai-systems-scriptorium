# Exercise: The Instruct Artifact

## Goal

Stand up the `module7-instruct/` skeleton and define the fixed sequence format the whole
artifact agrees on.

## Why

An instruction-tuning artifact succeeds differently from a classifier: success is "added a
skill without breaking the old ones." That definition only makes sense once the data
format and the three-script contract (`tune.py`, `regress.py`, `smoke.py`) are pinned.

## What You Are Building

The directory layout plus the vocabulary and the fixed sequence format
`<bos> VERB NAME <sep> RESPONSE NAME <eos>`.

## Steps

1. Create `tune.py`, `regress.py`, `smoke.py`, `tests/`, `outputs/`, and a `README.md`.

2. Define the small word-level vocab: specials (`<pad> <bos> <sep> <eos>`), three verbs
   (`greet thank bye`), three responses (`hello thanks goodbye`), and ten names.

3. Write `encode_example(verb, name)` producing the fixed 7-token sequence.

4. Decide the skill split: the base will learn `thank` and `bye`; the LoRA adapter will add
   `greet`. Write that decision into the README so the regression suite has a target.
