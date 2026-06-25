# The Diagnostic Queries

Each defect leaves a trace in the data the pipeline produced. Finding it is the diagnostic skill every prior module pointed toward.

## Symptoms, Not Names

The broken pipeline ships three faults, and you are never told their names. You get symptoms: a source flagged stale right after a load, a lineage chain that stops short, a gate that should scream but stays quiet. Six checks turn those symptoms into findings. Each returns a finding dict, and its `found` flag is what the grader reads:

```python
def diagnose(db_path: str, result: dict) -> list[dict]:
    return [check(db_path, result) for check in ALL_CHECKS]
```

`found=True` means the defect is present. Run the six against a broken run and all three defects light up; run them against a fixed run and they go dark. None of them read source code. They read the artifacts the code produced.

## Defect One: The Future-Dated Clock

The freshness check measures against a hardcoded `"2099-01-01"` "now". Two checks catch it.

`q1_future_now` reads the timestamp the freshness check used and compares it to a sane threshold. A finding looks like a "now" decades ahead of the wall clock. It traces to a defect because no real batch runs in 2099: the value is a literal, not the real processing time. This is the failure Module 2 warned about when it defined the freshness SLO. A gate measured against the wrong "now" measures nothing.

`q2_stale_despite_load` confirms the symptom: the source reports stale even though `corpus_loads` shows a load moments ago. A freshly loaded source that reads ancient is the proof the comparison anchor is wrong.

## Defect Two: The Missing Verdict

`capture_lineage` skips recording the eval verdict, so the lineage chain renders incomplete. Two checks catch it.

`q3_missing_verdict` runs the Module 1 lineage idea as a diagnostic: a left join from `answers` to `eval_verdicts` finds answers with no verdict row. A finding is any answer id with a null verdict. If no verdict edge exists, the function that writes it never ran.

`q4_chain_incomplete` walks the full chain, answer to retrieval to chunk to source, and looks for the verdict at the end. A finding is a chain that reaches the source document but never reaches a verdict. A complete chain must explain why the document was admitted; one with no verdict cannot.

## Defect Three: The Quiet Gate

The freshness gate swallows the breach. It logs a warning and returns instead of raising, so a stale corpus ships in silence.

`q5_silent_gate` compares the freshness verdict to the gate's behaviour: the source is stale, yet the gate reported `blocked=False` and the run continued. A finding is exactly that mismatch. A gate that tolerates a stale source is not a gate; it is a log line.

`q6_summary` rolls the targeted defects into a count, so a single call answers "is this pipeline defective at all."

## What The Six Checks Share

Every check follows the same shape: read one trace, ask one question, return one finding. The grader applies its six criteria, and the contract is plain:

```python
The Module 8 grader. Six criteria, each worth one point.
```

The pipeline lied in its unit tests. The artifacts do not lie. The checks read the artifacts.

## Core Concepts

1. A defect leaves its trace in the data it produced, not in the code that produced it.
2. A freshness check measured against a hardcoded clock reports nothing useful about real staleness.
3. A lineage chain missing its verdict cannot explain why a document was admitted.
4. A gate that swallows a breach instead of raising converts a hard failure into a silent one the batch survives.

<div class="claude-handoff" data-exercise="exercises/module8/the-diagnostic-queries/">
**Build It in Claude Code** · Exercise · exercises/module8/the-diagnostic-queries/
</div>

The Production AI Engineer who trusts artifacts over code finds the bug before the regulator does.
