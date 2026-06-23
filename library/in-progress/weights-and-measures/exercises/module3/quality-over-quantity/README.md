# Exercise: Quality over Quantity

## Goal

Score a messy example set on coverage, correctness, and consistency. Cut it to the
highest-quality subset. Justify, in writing, why fewer examples is the right call.

## Why

The instinct when building a fine-tune dataset is to gather as many examples as possible.
That instinct is wrong in the direction that costs the most: low-quality examples do not just
fail to help, they actively teach the wrong behavior. A malformed answer trains the model to
produce malformed answers. A duplicate trains it to weight one pattern more heavily than the
data justifies. A correctly formatted but factually wrong example trains it to be wrong
confidently. The Azure OpenAI fine-tuning guidance is direct on this: doubling the dataset size
can raise quality linearly, but pruning to the highest-quality examples comes first. You cannot
fix a bad corpus by training longer.

## What You Are Working With

The file `messy_examples.jsonl` contains 20 chat examples in the fine-tuning format. Some are
good. Some have problems in one or more of three dimensions:

- **Coverage**: the example demonstrates a behavior you want the model to learn.
- **Correctness**: the assistant turn gives the right answer in the right register.
- **Consistency**: the format, style, and length match the other examples in the set.

## Steps

1. Create `exercises/module3/quality-over-quantity/messy_examples.jsonl` with 20 examples. Mix
   in at least three coverage gaps (examples that repeat a behavior already covered), three
   correctness failures (wrong or misleading assistant turns), and three consistency failures
   (mismatched style, length, or register).

2. Create `exercises/module3/quality-over-quantity/score.py`. For each example in
   `messy_examples.jsonl`, print a row with the 1-based line number and your rating on each
   dimension (0 or 1) plus an optional one-phrase note:

   ```
   line  coverage  correctness  consistency  note
      1         1            1            1
      2         1            0            1  wrong capital city
      3         0            1            1  duplicate behavior
   ```

   You may hard-code the scores; the point is to make your reasoning explicit.

3. Define your cut threshold. Print only the examples that score 1 on all three dimensions to
   `kept.jsonl`. Print the count:

   ```
   kept 11 / 20 examples
   ```

4. Run `python exercises/spine/check_dataset.py kept.jsonl`. It must exit 0. If it does not,
   fix the examples in `kept.jsonl` until it passes.

## Done When

`python score.py` exits 0 and prints:

- The score table for all 20 examples.
- The kept count.
- Confirmation that `kept.jsonl` passes `check_dataset.py`.

Then write `NOTES.md` in this directory answering one question in three to five sentences: given
that you have 11 clean examples and could gather 200 messy ones in the same time, why is 11
the right starting point?

## Estimated Time

30 to 45 minutes.

## Stretch

Re-run `check_dataset.py` on `messy_examples.jsonl` before scoring. Note which named failures
the validator catches automatically and which failures (wrong answer, duplicate behavior,
inconsistent style) it cannot catch. Write one sentence explaining what human review covers
that the validator cannot.
