# Module 3: Dataset Craft

M1 ran a fine-tuning loop. M2 asked whether it was working. This module steps back one stage
further: before a single epoch runs, the data has already determined how good the model can get.

A fine-tune is bounded by its dataset. The model cannot learn a behavior the data does not
demonstrate, and it will learn the wrong behavior if the data is noisy enough to teach it. The
validation signal M2 made you trust is only trustworthy if the validation set is clean, held out
correctly, and free of examples the model has already seen in training. That cleanliness is not
a property data arrives with. It is something you enforce, with code, before training starts.
The thesis of this module: data quality is the first quality gate, and the gate is a script.

## Four Lessons

1. **Quality over Quantity** (`quality-over-quantity`): why a small, clean dataset beats a large,
   noisy one. You score an example set on coverage, correctness, and consistency, then cut it to
   its highest-quality subset and defend why smaller is better.

2. **The JSONL Contract** (`the-jsonl-contract`): the fine-tuning data format in full. One JSON
   object per line, a `messages` array of `{role, content}` objects, roles restricted to
   `system`, `user`, and `assistant`. You write examples, run `check_dataset.py` against them,
   and fix every named failure until the validator exits 0.

3. **Deduplication and Leakage** (`deduplication-and-leakage`): exact duplicates inflate your
   example count and teach nothing new; a copy of a training example in the validation set
   inflates the signal M2 depends on. You plant both failure modes in a dataset, run `curate.py`
   to remove them, and confirm the leakage gate passes.

4. **Building the Curation Gate** (`building-the-curation-gate`): the module's gated deliverable.
   You run `curate.py` on a raw JSONL file to produce clean train and val splits plus a manifest,
   then run `check_dataset.py` on each output and `--check-leak` across them. All gates must
   exit 0. The manifest is your proof.

## What This Module Feeds Forward

The clean-dataset contract you produce here is what M4 consumes. The fine-tune build in M4
expects `train.jsonl` and `val.jsonl` that have already passed the format gate, the dedup gate,
and the leakage gate; it will not validate those things again. M6 closes the loop from the
portfolio side: the data-curation script you productionize there is the same `curate.py` workflow
this module teaches, made repeatable for new data. Install the discipline now. Retrofitting it
after M4 runs is not possible without retraining.
