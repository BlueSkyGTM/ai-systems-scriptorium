# Exercise: Streaming vs Batch

**Goal**: Build a `decide_mode` classifier that routes a source to the streaming or batch leg based on its freshness SLO, and assert that a set of example sources classify correctly.

**Why**: The streaming pipeline you build across Module 4 only makes sense for sources with a seconds-scale SLO; classifying sources before building the pipeline is how you avoid over-engineering the batch sources.

---

## Steps

This exercise seeds `module4-streaming/`. Create the directory if it does not exist; do not modify `module2-ingestion/` or `module3-orchestration/`.

**1. Create `module4-streaming/decide.py`.**

Implement this function exactly (signature is locked):

```python
def decide_mode(required_freshness_seconds: int) -> str:
    """Return 'stream' if the SLO is seconds-scale (<= 60s), else 'batch'."""
```

The threshold is 60 seconds: at or below, the source streams; above, it batches. No external dependencies; standard library only.

**2. Classify example sources in `module4-streaming/examples.py`.**

Define a list of `(source_name, required_freshness_seconds)` tuples and call `decide_mode` on each. Print one line per source showing the name, SLO in seconds, and the routing decision. Include at least these four:

- A nightly reference corpus: 86400 seconds (24 hours) -> `batch`
- A live compliance feed: 5 seconds -> `stream`
- A price-update feed: 10 seconds -> `stream`
- A monthly audit log: 2592000 seconds (30 days) -> `batch`

Running `python examples.py` should print the classifications without error.

**3. Write `module4-streaming/tests/test_decide.py`.**

Assert each of the four example sources produces the expected mode. A fifth assertion: `decide_mode(60)` returns `"stream"` (boundary case, inclusive). A sixth: `decide_mode(61)` returns `"batch"` (just above threshold).

**4. Add `module4-streaming/smoke.py`.**

Run `pytest tests/test_decide.py` as a subprocess and assert exit code is 0. This is the acceptance gate.

---

## Done When

- `python -m pytest module4-streaming/tests/test_decide.py` passes all assertions; offline, no installs beyond `pytest`.
- `python module4-streaming/examples.py` prints four classified sources without error.
- `python module4-streaming/smoke.py` exits 0.

---

## Stretch

Add a borderline source (e.g., a near-real-time dashboard feed at 90 seconds). Justify the routing decision in a comment inside `examples.py`: explain whether 90 seconds is genuinely batch-friendly or whether the 60-second threshold is too conservative for this source. This is the judgment call the lesson describes; the comment is the engineering record of it.
