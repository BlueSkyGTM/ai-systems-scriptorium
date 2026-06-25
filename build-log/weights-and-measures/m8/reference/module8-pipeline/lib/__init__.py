"""Vendored modules for the Module 8 pipeline.

Each module embodies one earlier module's technique, vendored here so the capstone is a
self-contained, GitHub-postable artifact:

    m3_curate   - dataset curation (validate / dedupe / split)
    m4_tune     - the reusable fine-tune loop
    m6_train    - the classifier model and its training
    m5_eval     - the eval gate (accuracy + macro-F1 vs baseline)
    m7_regress  - the behavioral regression suite (pinned golden cases)

pipeline.py composes them; it is the only new code.
"""

# The vendoring registry: the five sealed modules the conductor composes, in pipeline
# order. The conductor imports these but never edits them.
VENDORED = ("m3_curate", "m4_tune", "m6_train", "m5_eval", "m7_regress")

