# Exercise: Signals and Thresholds

**Goal:** Start the module-5 throughline file `ROUTING.md`. Record your routing policy with
four signals, concrete thresholds, and a prose rule that ties them together.

**Why:** The first four portfolio files document the metal, the runtime, the model stack, and
the latency baseline. `ROUTING.md` is the fifth. It records the decision layer: which requests
go local, which escalate to cloud, and why. A hiring manager reading it can see the exact
thresholds you chose and trace each number back to a measurement. The next lesson ("Record the
Policy") ships `check_routing.py`, the validator that enforces the file's structure. This
exercise creates the file that validator will read.

---

## Files You Are Editing

The throughline file lives here and stays here:

```
exercises/module5/signals-and-thresholds/ROUTING.md
```

Do not move or rename this file. The next lesson's `check_routing.py` validator reads it from
this exact path, and Module 6 reads it from here when wiring the router into Claude Code.

---

## Steps

### Step 1: Create ROUTING.md

Create the file at `exercises/module5/signals-and-thresholds/ROUTING.md` using exactly this
template. Fill in your own thresholds where the reference values appear:

```markdown
# Routing Policy

How requests are routed between the local rig and the cloud. Read by check_routing.py.

## Signals

| Signal | Threshold | Routes To |
|--------|-----------|-----------|
| Context size | over 8192 tokens | cloud |
| Latency budget | under 2000 ms, fits local | local |
| Sensitivity | private / on-machine | local |
| Stakes | high-stakes one-off | cloud |

## Targets

Local model: qwen2.5-coder:14b (8K practical context)
Cloud model: claude (frontier, 1M-token context)

## Policy

Route to local when the request fits the local context window and is cost-sensitive,
latency-tolerant, or privacy-sensitive. Escalate to cloud when the context exceeds the local
window or the task is high-stakes and wants the best answer regardless of cost. Sensitive data
never leaves the machine.
```

Keep the three section headers exactly as shown: `## Signals`, `## Targets`, `## Policy`.
The validator checks for all three. The column order in the Signals table must be Signal,
Threshold, Routes To.

---

## Note for Readers Without Hardware Yet

The thresholds above are the reference build's: 8192 tokens for context, 2000 ms for
latency, based on a 16 GB card running `qwen2.5-coder:14b` at Q4_K_M. If you have not run
your own Module 4 latency baseline yet, use the reference values. The validator checks that
the file is complete and the sections are present; it checks structure, not whether your
numbers match the reference build's.

---

## Done When

The file `exercises/module5/signals-and-thresholds/ROUTING.md` exists and contains:

- A `## Signals` table with at least four rows: Context size, Latency budget, Sensitivity,
  and Stakes, each with a Threshold and a Routes To value.
- A `## Targets` section naming the local model and the cloud model by their actual
  identifiers.
- A `## Policy` section with at least one sentence of prose.

Full validation arrives with `check_routing.py` in the next lesson, "Record the Policy."
That lesson also runs the validator end to end.

---

## Stretch

Add a fifth row to the `## Signals` table for a cost ceiling: a dollar amount per request
above which you would refuse to route to cloud and fall back to local instead. Decide your
own threshold. The validator will check any row you add by confirming it has a Threshold and
a Routes To value; it does not require a specific signal name, so a fifth row is checked
automatically when `check_routing.py` ships next lesson.
